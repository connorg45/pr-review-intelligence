from __future__ import annotations

import re
from datetime import datetime, timezone

from flask import current_app

from app.extensions import db
from app.models import PullRequest, PullRequestFile, Repository, SyncRun
from app.services.analysis_service import analyze_and_store
from app.services.demo_seed import seed_demo_data
from app.services.event_service import log_event
from app.services.github_client import GitHubClient, GitHubSyncError
from app.utils.file_flags import is_sensitive_path, is_test_file
from app.utils.time import datetimes_equal, parse_github_datetime

REPO_PART_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+$")


def sync_repository(source_type: str, owner: str | None = None, name: str | None = None, limit: int | None = None) -> dict:
    normalized_source = (source_type or "github").lower()
    sync_limit = _normalize_limit(limit)

    if normalized_source == "demo":
        seeded = seed_demo_data(reset=False)
        return {
            "message": "Demo data is ready.",
            **seeded,
        }
    if normalized_source != "github":
        raise GitHubSyncError("source_type must be either 'demo' or 'github'.")

    owner, name = _normalize_repository_target(owner, name)

    client = GitHubClient()
    repository_payload = client.fetch_repository(owner, name)
    repository = Repository.query.filter_by(full_name=repository_payload["full_name"]).first()
    if not repository:
        repository = Repository(
            owner=repository_payload["owner"],
            name=repository_payload["name"],
            full_name=repository_payload["full_name"],
            source_type="github",
            github_repo_id=repository_payload["github_repo_id"],
        )
        db.session.add(repository)
        db.session.flush()
    else:
        repository.owner = repository_payload["owner"]
        repository.name = repository_payload["name"]
        repository.full_name = repository_payload["full_name"]
        repository.source_type = "github"
        repository.github_repo_id = repository_payload["github_repo_id"]
    db.session.commit()

    started_at = datetime.now(timezone.utc)
    sync_run = SyncRun(
        repository_id=repository.id,
        source_type="github",
        status="running",
        started_at=started_at,
        metadata_json={"owner": owner, "name": name, "limit": sync_limit},
    )
    db.session.add(sync_run)

    started_event = log_event(
        event_type="sync.started",
        message=f"GitHub sync started for {repository.full_name}.",
        repository_id=repository.id,
        metadata={"owner": owner, "name": name, "limit": sync_limit},
    )
    started_event.created_at = started_at
    db.session.commit()

    try:
        pull_requests = client.fetch_pull_requests(owner, name, sync_limit)
        processed_count = 0
        changed_count = 0
        reanalyzed_count = 0
        for payload in pull_requests:
            result = _upsert_pull_request(repository, payload, client, owner, name)
            processed_count += 1
            changed_count += 1 if result["changed"] else 0
            reanalyzed_count += 1 if result["reanalyzed"] else 0

        unchanged_count = processed_count - changed_count

        completed_at = datetime.now(timezone.utc)
        sync_run = db.session.get(SyncRun, sync_run.id)
        sync_run.status = "success"
        sync_run.completed_at = completed_at
        sync_run.pr_count = processed_count
        sync_run.metadata_json = {
            "owner": owner,
            "name": name,
            "limit": sync_limit,
            "changed_prs": changed_count,
            "unchanged_prs": unchanged_count,
            "reanalyzed_prs": reanalyzed_count,
        }
        repository.updated_at = completed_at

        completed_event = log_event(
            event_type="sync.completed",
            message=(
                f"GitHub sync completed for {repository.full_name}. "
                f"{processed_count} PRs processed, {changed_count} updated, {reanalyzed_count} reanalyzed."
            ),
            repository_id=repository.id,
            metadata={
                "owner": owner,
                "name": name,
                "pr_count": processed_count,
                "changed_prs": changed_count,
                "reanalyzed_prs": reanalyzed_count,
            },
        )
        completed_event.created_at = completed_at

        db.session.commit()
        return {
            "message": f"Synced {processed_count} pull requests from {repository.full_name}.",
            "repository": repository.to_dict(),
            "sync_run": sync_run.to_dict(),
            "processed_prs": processed_count,
            "changed_prs": changed_count,
            "reanalyzed_prs": reanalyzed_count,
            "unchanged_prs": unchanged_count,
        }
    except Exception as exc:
        db.session.rollback()
        failed_at = datetime.now(timezone.utc)
        sync_run = db.session.get(SyncRun, sync_run.id)
        sync_run.status = "failed"
        sync_run.completed_at = failed_at
        public_error = str(exc) if isinstance(exc, GitHubSyncError) else "An unexpected error interrupted the sync."
        sync_run.error_message = public_error

        failed_event = log_event(
            event_type="sync.failed",
            message=f"GitHub sync failed for {repository.full_name}: {public_error}",
            repository_id=repository.id,
            metadata={"owner": owner, "name": name, "error_type": type(exc).__name__},
        )
        failed_event.created_at = failed_at
        db.session.commit()
        raise


def _normalize_limit(limit: int | None) -> int:
    if limit is None:
        return current_app.config["DEFAULT_SYNC_LIMIT"]
    try:
        normalized = int(limit)
    except (TypeError, ValueError) as exc:
        raise GitHubSyncError("Sync limit must be a whole number between 1 and 50.") from exc
    if normalized < 1 or normalized > 50:
        raise GitHubSyncError("Sync limit must be between 1 and 50 pull requests.")
    return normalized


def _normalize_repository_target(owner: str | None, name: str | None) -> tuple[str, str]:
    normalized_owner = (owner or "").strip().strip("/")
    normalized_name = (name or "").strip().strip("/")

    if not normalized_owner or not normalized_name:
        raise GitHubSyncError("Enter both a GitHub owner and repository name before syncing.")
    if "/" in normalized_owner or "/" in normalized_name:
        raise GitHubSyncError("Enter owner and repository separately. Do not include extra slashes.")
    if not REPO_PART_PATTERN.match(normalized_owner) or not REPO_PART_PATTERN.match(normalized_name):
        raise GitHubSyncError("GitHub owner and repository names may only contain letters, numbers, '.', '_' or '-'.")

    return normalized_owner, normalized_name


def _build_file_snapshot(files: list[PullRequestFile]) -> list[tuple]:
    return sorted(
        (
            file.path,
            file.additions,
            file.deletions,
            file.change_type,
            file.is_sensitive,
            file.is_test_file,
        )
        for file in files
    )


def _upsert_pull_request(repository: Repository, payload: dict, client: GitHubClient, owner: str, name: str) -> dict:
    pull_request = PullRequest.query.filter_by(
        repository_id=repository.id,
        github_pr_number=payload["number"],
    ).first()
    if not pull_request:
        pull_request = PullRequest(repository_id=repository.id, github_pr_number=payload["number"])
        db.session.add(pull_request)

    files_payload = client.fetch_pull_request_files(owner, name, payload["number"])
    incoming_files = [
        {
            "path": file_payload["filename"],
            "additions": file_payload.get("additions", 0),
            "deletions": file_payload.get("deletions", 0),
            "change_type": file_payload.get("status", "modified"),
            "is_sensitive": is_sensitive_path(file_payload["filename"]),
            "is_test_file": is_test_file(file_payload["filename"]),
        }
        for file_payload in files_payload
    ]
    computed_additions = payload.get("additions") or sum(file_payload["additions"] for file_payload in incoming_files)
    computed_deletions = payload.get("deletions") or sum(file_payload["deletions"] for file_payload in incoming_files)
    first_review_at = client.fetch_first_review_at(owner, name, payload["number"])
    incoming_file_snapshot = sorted(
        (
            file_payload["path"],
            file_payload["additions"],
            file_payload["deletions"],
            file_payload["change_type"],
            file_payload["is_sensitive"],
            file_payload["is_test_file"],
        )
        for file_payload in incoming_files
    )
    existing_file_snapshot = _build_file_snapshot(pull_request.files)

    changed = any(
        [
            pull_request.github_pr_id != payload["id"],
            pull_request.title != payload["title"],
            pull_request.author != payload["user"]["login"],
            pull_request.state != payload["state"],
            pull_request.url != payload["html_url"],
            not datetimes_equal(pull_request.created_at, parse_github_datetime(payload["created_at"])),
            not datetimes_equal(pull_request.updated_at, parse_github_datetime(payload["updated_at"])),
            not datetimes_equal(pull_request.merged_at, parse_github_datetime(payload.get("merged_at"))),
            not datetimes_equal(pull_request.first_review_at, first_review_at),
            pull_request.additions != computed_additions,
            pull_request.deletions != computed_deletions,
            pull_request.changed_files_count != len(incoming_files),
            existing_file_snapshot != incoming_file_snapshot,
        ]
    )

    pull_request.github_pr_id = payload["id"]
    pull_request.title = payload["title"]
    pull_request.author = payload["user"]["login"]
    pull_request.state = payload["state"]
    pull_request.url = payload["html_url"]
    pull_request.created_at = parse_github_datetime(payload["created_at"])
    pull_request.updated_at = parse_github_datetime(payload["updated_at"])
    pull_request.merged_at = parse_github_datetime(payload.get("merged_at"))
    pull_request.first_review_at = first_review_at
    pull_request.additions = computed_additions
    pull_request.deletions = computed_deletions
    pull_request.changed_files_count = len(incoming_files)
    pull_request.last_synced_at = datetime.now(timezone.utc)
    db.session.flush()

    if existing_file_snapshot != incoming_file_snapshot:
        for existing_file in list(pull_request.files):
            db.session.delete(existing_file)
        for file_payload in files_payload:
            db.session.add(
                PullRequestFile(
                    pull_request_id=pull_request.id,
                    path=file_payload["filename"],
                    additions=file_payload.get("additions", 0),
                    deletions=file_payload.get("deletions", 0),
                    change_type=file_payload.get("status", "modified"),
                    is_sensitive=is_sensitive_path(file_payload["filename"]),
                    is_test_file=is_test_file(file_payload["filename"]),
                )
            )

    db.session.flush()
    reanalyzed = changed or pull_request.latest_analysis is None
    if reanalyzed:
        pull_request.analysis_status = "pending"
        analyze_and_store(pull_request)
    else:
        pull_request.analysis_status = "completed"

    return {
        "pull_request": pull_request,
        "changed": changed,
        "reanalyzed": reanalyzed,
    }
