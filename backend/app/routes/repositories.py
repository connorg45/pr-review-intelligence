from flask import Blueprint, jsonify, request

from app.models import Repository
from app.services.github_client import GitHubSyncError
from app.services.sync_service import sync_repository


repositories_bp = Blueprint("repositories", __name__)


@repositories_bp.get("/repositories")
def list_repositories():
    repositories = Repository.query.order_by(Repository.full_name.asc()).all()
    return jsonify({"items": [repository.to_dict() for repository in repositories]})


@repositories_bp.post("/repositories/sync")
def sync_repository_route():
    payload = request.get_json(silent=True) or {}
    try:
        result = sync_repository(
            source_type=payload.get("source_type", "github"),
            owner=payload.get("owner"),
            name=payload.get("name"),
            limit=payload.get("limit"),
        )
        return jsonify(result)
    except GitHubSyncError as exc:
        return jsonify({"message": str(exc)}), 400
