from datetime import datetime, timezone

from app.extensions import db
from app.models import PullRequest, Repository, SyncRun
from app.services import sync_service
from app.services.sync_service import _upsert_pull_request


class FakeGitHubClient:
    def fetch_pull_request_files(self, owner, name, number):
        return [
            {
                "filename": "backend/app/services/orders.py",
                "additions": 32,
                "deletions": 8,
                "status": "modified",
            },
            {
                "filename": "backend/tests/test_orders.py",
                "additions": 18,
                "deletions": 2,
                "status": "added",
            },
        ]

    def fetch_first_review_at(self, owner, name, number):
        return datetime(2026, 7, 8, 13, 0, tzinfo=timezone.utc)


PAYLOAD = {
    "id": 9001,
    "number": 42,
    "title": "Add order validation",
    "user": {"login": "octocat"},
    "state": "open",
    "html_url": "https://github.com/acme/orders/pull/42",
    "created_at": "2026-07-08T12:00:00Z",
    "updated_at": "2026-07-08T14:00:00Z",
    "merged_at": None,
}


def test_new_pull_request_sync_creates_complete_record(app):
    with app.app_context():
        repository = Repository(owner="acme", name="orders", full_name="acme/orders", source_type="github")
        db.session.add(repository)
        db.session.commit()

        result = _upsert_pull_request(repository, PAYLOAD, FakeGitHubClient(), "acme", "orders")
        db.session.commit()

        pull_request = PullRequest.query.filter_by(repository_id=repository.id, github_pr_number=42).one()
        assert result["changed"] is True
        assert result["reanalyzed"] is True
        assert pull_request.title == "Add order validation"
        assert pull_request.changed_files_count == 2
        assert len(pull_request.files) == 2


def test_unchanged_pull_request_sync_is_idempotent_after_reload(app):
    with app.app_context():
        repository = Repository(owner="acme", name="orders", full_name="acme/orders", source_type="github")
        db.session.add(repository)
        db.session.commit()

        _upsert_pull_request(repository, PAYLOAD, FakeGitHubClient(), "acme", "orders")
        db.session.commit()
        original_file_ids = [file.id for file in PullRequest.query.one().files]
        original_analysis_count = len(PullRequest.query.one().analysis_results)
        db.session.remove()

        repository = Repository.query.filter_by(full_name="acme/orders").one()
        result = _upsert_pull_request(repository, PAYLOAD, FakeGitHubClient(), "acme", "orders")
        db.session.commit()

        pull_request = PullRequest.query.one()
        assert result["changed"] is False
        assert result["reanalyzed"] is False
        assert [file.id for file in pull_request.files] == original_file_ids
        assert len(pull_request.analysis_results) == original_analysis_count


def test_unexpected_sync_failure_is_recorded(client, app, monkeypatch):
    class BrokenGitHubClient:
        def fetch_repository(self, owner, name):
            return {
                "github_repo_id": 9001,
                "owner": owner,
                "name": name,
                "full_name": f"{owner}/{name}",
            }

        def fetch_pull_requests(self, owner, name, limit):
            raise RuntimeError("simulated parser failure")

    monkeypatch.setattr(sync_service, "GitHubClient", BrokenGitHubClient)

    response = client.post(
        "/api/repositories/sync",
        json={"source_type": "github", "owner": "acme", "name": "orders", "limit": 5},
    )

    assert response.status_code == 500
    assert response.get_json()["message"] == "An unexpected server error occurred."
    with app.app_context():
        sync_run = SyncRun.query.one()
        assert sync_run.status == "failed"
        assert sync_run.error_message == "An unexpected error interrupted the sync."
        assert sync_run.completed_at is not None
