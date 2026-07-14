from datetime import datetime, timedelta, timezone

from app.extensions import db
from app.models import EventLog, PullRequest, PullRequestFile, Repository, SyncRun
from app.services.analysis_service import analyze_and_store
from app.services.event_service import log_event
from app.utils.file_flags import is_sensitive_path, is_test_file


BASE_TIME = datetime.now(timezone.utc).replace(microsecond=0)


DEMO_REPOSITORIES = [
    {"owner": "acme", "name": "payments-api", "full_name": "acme/payments-api", "source_type": "demo"},
    {"owner": "acme", "name": "developer-portal", "full_name": "acme/developer-portal", "source_type": "demo"},
]


DEMO_PULL_REQUESTS = [
    {
        "repo": "acme/payments-api",
        "number": 142,
        "title": "Refactor payout approval flow and tighten permission checks",
        "author": "maya",
        "state": "open",
        "created_at": BASE_TIME - timedelta(days=16),
        "updated_at": BASE_TIME - timedelta(days=1, hours=4),
        "first_review_at": None,
        "additions": 612,
        "deletions": 244,
        "files": [
            {"path": "backend/app/services/payouts.py", "additions": 180, "deletions": 72, "change_type": "modified"},
            {"path": "backend/app/services/permissions.py", "additions": 130, "deletions": 44, "change_type": "modified"},
            {"path": "backend/app/routes/payouts.py", "additions": 84, "deletions": 31, "change_type": "modified"},
            {"path": "backend/app/models/payment.py", "additions": 46, "deletions": 19, "change_type": "modified"},
            {"path": "backend/migrations/versions/004_add_payout_audit.py", "additions": 64, "deletions": 0, "change_type": "added"},
            {"path": ".github/workflows/backend-ci.yml", "additions": 18, "deletions": 7, "change_type": "modified"},
            {"path": "backend/app/utils/rbac.py", "additions": 90, "deletions": 25, "change_type": "modified"},
        ],
    },
    {
        "repo": "acme/payments-api",
        "number": 138,
        "title": "Add refund export endpoint and coverage for CSV serialization",
        "author": "jordan",
        "state": "closed",
        "created_at": BASE_TIME - timedelta(days=9),
        "updated_at": BASE_TIME - timedelta(days=7),
        "merged_at": BASE_TIME - timedelta(days=7),
        "first_review_at": BASE_TIME - timedelta(days=8, hours=8),
        "additions": 188,
        "deletions": 51,
        "files": [
            {"path": "backend/app/routes/refunds.py", "additions": 64, "deletions": 20, "change_type": "modified"},
            {"path": "backend/app/services/refund_exports.py", "additions": 72, "deletions": 15, "change_type": "modified"},
            {"path": "backend/tests/test_refund_exports.py", "additions": 38, "deletions": 4, "change_type": "added"},
            {"path": "backend/tests/test_refund_routes.py", "additions": 14, "deletions": 0, "change_type": "added"},
        ],
    },
    {
        "repo": "acme/payments-api",
        "number": 131,
        "title": "Split invoice scheduling job into smaller service modules",
        "author": "aria",
        "state": "closed",
        "created_at": BASE_TIME - timedelta(days=21),
        "updated_at": BASE_TIME - timedelta(days=18),
        "merged_at": BASE_TIME - timedelta(days=18),
        "first_review_at": BASE_TIME - timedelta(days=20, hours=18),
        "additions": 274,
        "deletions": 182,
        "files": [
            {"path": "backend/app/services/invoicing/scheduler.py", "additions": 88, "deletions": 66, "change_type": "modified"},
            {"path": "backend/app/services/invoicing/dispatch.py", "additions": 77, "deletions": 41, "change_type": "added"},
            {"path": "backend/app/services/invoicing/retries.py", "additions": 54, "deletions": 12, "change_type": "added"},
            {"path": "backend/tests/test_invoicing_scheduler.py", "additions": 55, "deletions": 8, "change_type": "added"},
        ],
    },
    {
        "repo": "acme/developer-portal",
        "number": 87,
        "title": "Ship repository insights dashboard and API usage cards",
        "author": "noah",
        "state": "open",
        "created_at": BASE_TIME - timedelta(days=4),
        "updated_at": BASE_TIME - timedelta(hours=18),
        "first_review_at": BASE_TIME - timedelta(days=3, hours=16),
        "additions": 326,
        "deletions": 94,
        "files": [
            {"path": "frontend/src/pages/repo-insights.tsx", "additions": 118, "deletions": 0, "change_type": "added"},
            {"path": "frontend/src/components/usage-card.tsx", "additions": 76, "deletions": 12, "change_type": "added"},
            {"path": "frontend/src/api/repositories.ts", "additions": 48, "deletions": 9, "change_type": "modified"},
            {"path": "backend/app/routes/insights.py", "additions": 64, "deletions": 19, "change_type": "modified"},
            {"path": "frontend/src/pages/repo-insights.test.tsx", "additions": 20, "deletions": 0, "change_type": "added"},
        ],
    },
    {
        "repo": "acme/developer-portal",
        "number": 79,
        "title": "Tighten environment configuration loading for preview deployments",
        "author": "maya",
        "state": "closed",
        "created_at": BASE_TIME - timedelta(days=13),
        "updated_at": BASE_TIME - timedelta(days=11),
        "merged_at": BASE_TIME - timedelta(days=11),
        "first_review_at": BASE_TIME - timedelta(days=12, hours=12),
        "additions": 94,
        "deletions": 37,
        "files": [
            {"path": "frontend/src/config/env.ts", "additions": 41, "deletions": 15, "change_type": "modified"},
            {"path": "frontend/src/utils/runtime-config.ts", "additions": 22, "deletions": 9, "change_type": "modified"},
            {"path": ".github/workflows/preview.yml", "additions": 15, "deletions": 6, "change_type": "modified"},
            {"path": "frontend/src/config/env.test.ts", "additions": 16, "deletions": 7, "change_type": "modified"},
        ],
    },
    {
        "repo": "acme/developer-portal",
        "number": 74,
        "title": "Fix flaky onboarding form validation race condition",
        "author": "jordan",
        "state": "closed",
        "created_at": BASE_TIME - timedelta(days=19),
        "updated_at": BASE_TIME - timedelta(days=17),
        "merged_at": BASE_TIME - timedelta(days=17),
        "first_review_at": BASE_TIME - timedelta(days=18, hours=20),
        "additions": 62,
        "deletions": 28,
        "files": [
            {"path": "frontend/src/components/onboarding-form.tsx", "additions": 22, "deletions": 11, "change_type": "modified"},
            {"path": "frontend/src/hooks/use-onboarding-validation.ts", "additions": 18, "deletions": 10, "change_type": "modified"},
            {"path": "frontend/src/components/onboarding-form.test.tsx", "additions": 22, "deletions": 7, "change_type": "modified"},
        ],
    },
    {
        "repo": "acme/payments-api",
        "number": 145,
        "title": "Prepare production config toggle for settlement partner rollout",
        "author": "sam",
        "state": "open",
        "created_at": BASE_TIME - timedelta(days=6),
        "updated_at": BASE_TIME - timedelta(hours=5),
        "first_review_at": None,
        "additions": 148,
        "deletions": 42,
        "files": [
            {"path": "backend/app/config/settings.py", "additions": 32, "deletions": 10, "change_type": "modified"},
            {"path": "backend/app/services/settlements/partner_router.py", "additions": 44, "deletions": 15, "change_type": "modified"},
            {"path": "backend/app/services/settlements/flags.py", "additions": 28, "deletions": 8, "change_type": "added"},
            {"path": "infra/terraform/settlements.tf", "additions": 25, "deletions": 5, "change_type": "modified"},
            {"path": "backend/tests/test_partner_router.py", "additions": 19, "deletions": 4, "change_type": "added"},
        ],
    },
]


def _create_repository(data: dict) -> Repository:
    repository = Repository(
        owner=data["owner"],
        name=data["name"],
        full_name=data["full_name"],
        source_type=data["source_type"],
    )
    db.session.add(repository)
    db.session.flush()
    return repository


def _create_pull_request(repository: Repository, data: dict) -> PullRequest:
    additions = sum(file["additions"] for file in data["files"])
    deletions = sum(file["deletions"] for file in data["files"])
    pull_request = PullRequest(
        repository_id=repository.id,
        github_pr_number=data["number"],
        title=data["title"],
        author=data["author"],
        state=data["state"],
        url=f"https://github.com/{repository.full_name}/pull/{data['number']}",
        additions=additions,
        deletions=deletions,
        changed_files_count=len(data["files"]),
        created_at=data["created_at"],
        updated_at=data["updated_at"],
        merged_at=data.get("merged_at"),
        first_review_at=data.get("first_review_at"),
        analysis_status="pending",
        last_synced_at=data["updated_at"],
    )
    db.session.add(pull_request)
    db.session.flush()

    for file_data in data["files"]:
        db.session.add(
            PullRequestFile(
                pull_request_id=pull_request.id,
                path=file_data["path"],
                additions=file_data["additions"],
                deletions=file_data["deletions"],
                change_type=file_data["change_type"],
                is_sensitive=is_sensitive_path(file_data["path"]),
                is_test_file=is_test_file(file_data["path"]),
            )
        )

    db.session.flush()
    analyze_and_store(pull_request, analyzed_at=data["updated_at"])
    return pull_request


def _create_sync_run(repository: Repository, started_at: datetime, completed_at: datetime, status: str, pr_count: int, metadata: dict | None = None, error_message: str | None = None) -> SyncRun:
    sync_run = SyncRun(
        repository_id=repository.id,
        source_type=repository.source_type,
        status=status,
        started_at=started_at,
        completed_at=completed_at,
        pr_count=pr_count,
        metadata_json=metadata or {},
        error_message=error_message,
    )
    db.session.add(sync_run)
    return sync_run


def _seed_records() -> dict:
    repositories: dict[str, Repository] = {}
    for repository_data in DEMO_REPOSITORIES:
        repository = _create_repository(repository_data)
        repositories[repository.full_name] = repository

    seeded_pull_requests = []
    for pr_data in DEMO_PULL_REQUESTS:
        seeded_pull_requests.append(_create_pull_request(repositories[pr_data["repo"]], pr_data))

    for repository in repositories.values():
        repo_prs = [pr for pr in seeded_pull_requests if pr.repository_id == repository.id]
        sync_start = min(pr.created_at for pr in repo_prs) - timedelta(hours=2)
        sync_end = max(pr.updated_at for pr in repo_prs) + timedelta(minutes=8)
        _create_sync_run(
            repository,
            started_at=sync_start,
            completed_at=sync_end,
            status="success",
            pr_count=len(repo_prs),
            metadata={"mode": "demo", "note": "Seeded realistic demo pull requests."},
        )
        started_event = log_event(
            event_type="sync.started",
            message=f"Sample sync started for {repository.full_name}.",
            repository_id=repository.id,
            metadata={"source_type": "demo"},
        )
        started_event.created_at = sync_start

        completed_event = log_event(
            event_type="sync.completed",
            message=f"Sample sync completed for {repository.full_name} with {len(repo_prs)} PRs.",
            repository_id=repository.id,
            metadata={"source_type": "demo", "pr_count": len(repo_prs)},
        )
        completed_event.created_at = sync_end

    failed_repo = repositories["acme/developer-portal"]
    _create_sync_run(
        failed_repo,
        started_at=BASE_TIME - timedelta(days=22),
        completed_at=BASE_TIME - timedelta(days=22, hours=-1),
        status="failed",
        pr_count=0,
        metadata={"source_type": "demo", "attempted_repo": failed_repo.full_name},
        error_message="Simulated timeout while fetching repository metadata.",
    )
    failed_event = log_event(
        event_type="sync.failed",
        message="Previous sync attempt for acme/developer-portal timed out while contacting GitHub.",
        repository_id=failed_repo.id,
        metadata={"source_type": "demo", "error_class": "TimeoutError"},
    )
    failed_event.created_at = BASE_TIME - timedelta(days=22, hours=-1)

    db.session.commit()

    return {
        "repositories": [repository.to_dict() for repository in Repository.query.order_by(Repository.full_name.asc()).all()],
        "pull_requests": [pr.to_list_dict() for pr in PullRequest.query.order_by(PullRequest.updated_at.desc()).all()],
        "created": True,
    }


def seed_demo_data(reset: bool = False) -> dict:
    if reset:
        demo_repositories = Repository.query.filter_by(source_type="demo").all()
        demo_repository_ids = [row.id for row in demo_repositories]
        if demo_repository_ids:
            EventLog.query.filter(EventLog.repository_id.in_(demo_repository_ids)).delete(synchronize_session=False)
            for repository in demo_repositories:
                db.session.delete(repository)
            db.session.commit()
        return _seed_records()

    existing_demo = Repository.query.filter_by(source_type="demo").count()
    if existing_demo:
        return {
            "repositories": [repository.to_dict() for repository in Repository.query.order_by(Repository.full_name.asc()).all()],
            "pull_requests": [pr.to_list_dict() for pr in PullRequest.query.order_by(PullRequest.updated_at.desc()).all()],
            "created": False,
        }

    return _seed_records()
