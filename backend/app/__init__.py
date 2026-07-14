from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import HTTPException

from app.config import Config
from app.extensions import db, migrate
from app.models import AnalysisResult, EventLog, PullRequest, PullRequestFile, Repository, SyncRun
from app.routes import register_blueprints
from app.services.demo_seed import seed_demo_data


def create_app(config_object=Config):
    frontend_dist = Path(__file__).resolve().parents[2] / "frontend" / "dist"
    app = Flask(__name__, static_folder=None)
    app.config.from_object(config_object)

    db.init_app(app)
    migrate.init_app(app, db)
    register_blueprints(app)

    with app.app_context():
        if app.config["AUTO_CREATE_DB"]:
            db.create_all()
        if app.config["AUTO_SEED_DEMO"] and Repository.query.count() == 0:
            try:
                seed_demo_data(reset=False)
            except IntegrityError:
                db.session.rollback()
                app.logger.info("Sample data was seeded by another application worker.")

    @app.before_request
    def enforce_write_policy():
        if (
            request.path.startswith("/api/")
            and request.method in {"POST", "PUT", "PATCH", "DELETE"}
            and not app.config["WRITE_OPERATIONS_ENABLED"]
        ):
            return (
                jsonify(
                    {
                        "message": "This deployment is read-only. Run a trusted local instance to use write operations.",
                        "status": 403,
                    }
                ),
                403,
            )

    @app.after_request
    def add_security_headers(response):
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'; "
            "object-src 'none'; script-src 'self'; connect-src 'self'; img-src 'self' data:; "
            "style-src 'self' 'unsafe-inline'",
        )
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        return response

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        if error.code == 404 and not request_targets_api():
            return serve_frontend("index.html")
        return jsonify({"message": error.description, "status": error.code}), error.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        app.logger.exception("Unhandled application error", exc_info=error)
        return jsonify({"message": "An unexpected server error occurred.", "status": 500}), 500

    def request_targets_api() -> bool:
        return request.path == "/api" or request.path.startswith("/api/")

    @app.get("/")
    @app.get("/<path:asset_path>")
    def serve_frontend(asset_path: str = "index.html"):
        if asset_path == "api" or asset_path.startswith("api/"):
            return jsonify({"message": "The requested API endpoint was not found.", "status": 404}), 404
        requested_file = frontend_dist / asset_path
        if asset_path != "index.html" and requested_file.is_file():
            return send_from_directory(frontend_dist, asset_path)
        if (frontend_dist / "index.html").is_file():
            return send_from_directory(frontend_dist, "index.html")
        return jsonify(
            {
                "message": "Frontend build not found. Run npm run build in frontend or use the Docker image.",
                "api_health": "/api/health",
            }
        ), 404

    return app
