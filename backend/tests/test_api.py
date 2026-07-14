import pytest

from app.extensions import db
from app.models import PullRequest, Repository


def test_health_endpoint(client):
    response = client.get("/api/health")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "ok"
    assert payload["database"] == "connected"
    assert payload["version"] == "1.0.0"


def test_security_headers_are_set(client):
    response = client.get("/")

    assert "script-src 'self'" in response.headers["Content-Security-Policy"]
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "no-referrer"


@pytest.mark.parametrize(
    ("path", "payload"),
    [
        ("/api/demo/reset", None),
        ("/api/repositories/sync", {"source_type": "demo"}),
        ("/api/pull-requests/1/analyze", None),
    ],
)
def test_read_only_mode_blocks_write_operations(client, app, path, payload):
    app.config["WRITE_OPERATIONS_ENABLED"] = False

    response = client.post(path, json=payload)

    assert response.status_code == 403
    assert response.get_json()["status"] == 403


def test_unknown_api_route_returns_json_not_frontend(client):
    response = client.get("/api/not-a-real-endpoint")

    assert response.status_code == 404
    assert response.is_json
    assert response.get_json()["status"] == 404


def test_demo_reset_populates_demo_data(client, app):
    response = client.post("/api/demo/reset")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["created"] is True

    with app.app_context():
        assert Repository.query.count() >= 2
        assert PullRequest.query.count() >= 6


def test_demo_reset_preserves_synced_github_repositories(client, app):
    with app.app_context():
        repository = Repository(
            owner="octocat",
            name="hello-world",
            full_name="octocat/hello-world",
            source_type="github",
            github_repo_id=1296269,
        )
        db.session.add(repository)
        db.session.commit()

    response = client.post("/api/demo/reset")

    assert response.status_code == 200
    with app.app_context():
        preserved = Repository.query.filter_by(full_name="octocat/hello-world").one_or_none()
        assert preserved is not None
        assert Repository.query.filter_by(source_type="demo").count() == 2


def test_pull_request_list_returns_seeded_items(client):
    client.post("/api/demo/reset")

    response = client.get("/api/pull-requests")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["total"] >= 6
    assert payload["items"][0]["repository_name"]


def test_pull_request_list_supports_hash_prefixed_number_search(client):
    client.post("/api/demo/reset")

    response = client.get("/api/pull-requests", query_string={"search": "#142"})

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["total"] == 1
    assert payload["items"][0]["github_pr_number"] == 142


def test_demo_sync_endpoint_is_idempotent(client):
    client.post("/api/demo/reset")

    response = client.post("/api/repositories/sync", json={"source_type": "demo"})

    assert response.status_code == 200
    payload = response.get_json()
    assert "repositories" in payload


def test_sync_validation_rejects_missing_repository_parts(client):
    response = client.post("/api/repositories/sync", json={"source_type": "github", "owner": "acme"})

    assert response.status_code == 400
    payload = response.get_json()
    assert "Enter both" in payload["message"]


def test_sync_validation_rejects_out_of_range_limit(client):
    response = client.post(
        "/api/repositories/sync",
        json={"source_type": "github", "owner": "acme", "name": "demo", "limit": 99},
    )

    assert response.status_code == 400
    payload = response.get_json()
    assert "between 1 and 50" in payload["message"]


def test_event_limit_validation_returns_json_error(client):
    response = client.get("/api/events", query_string={"limit": "many"})

    assert response.status_code == 400
    assert "whole number" in response.get_json()["message"]


def test_persisted_pull_request_can_be_reanalyzed(client, app):
    client.post("/api/demo/reset")

    with app.app_context():
        pull_request_id = PullRequest.query.first().id
        db.session.remove()

    response = client.post(f"/api/pull-requests/{pull_request_id}/analyze")

    assert response.status_code == 200
    assert response.get_json()["analysis"]["risk_level"] in {"low", "medium", "high"}
