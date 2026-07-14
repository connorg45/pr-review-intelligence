from flask import Blueprint, current_app, jsonify
from sqlalchemy import text

from app.extensions import db


health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
def health_check():
    try:
        db.session.execute(text("SELECT 1"))
        database_status = "connected"
        status_code = 200
    except Exception:
        current_app.logger.exception("Database health check failed")
        database_status = "unavailable"
        status_code = 503

    return (
        jsonify(
            {
                "status": "ok" if status_code == 200 else "degraded",
                "service": "pr-review-intelligence-api",
                "version": current_app.config["APP_VERSION"],
                "database": database_status,
                "github_configured": bool(current_app.config.get("GITHUB_TOKEN")),
            }
        ),
        status_code,
    )
