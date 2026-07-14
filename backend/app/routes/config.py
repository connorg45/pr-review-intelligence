from flask import Blueprint, current_app, jsonify

from app.models import Repository


config_bp = Blueprint("config", __name__)


@config_bp.get("/config")
def get_config():
    repositories = Repository.query.order_by(Repository.full_name.asc()).all()
    return jsonify(
        {
            "github": {
                "configured": bool(current_app.config.get("GITHUB_TOKEN")),
                "api_base_url": current_app.config["GITHUB_API_BASE_URL"],
            },
            "app": {
                "demo_mode_available": True,
                "default_sync_limit": current_app.config["DEFAULT_SYNC_LIMIT"],
                "auto_seed_demo": current_app.config["AUTO_SEED_DEMO"],
                "write_operations_enabled": current_app.config["WRITE_OPERATIONS_ENABLED"],
            },
            "repositories": [repository.to_dict() for repository in repositories],
        }
    )
