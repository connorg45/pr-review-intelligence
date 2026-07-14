from app.routes.config import config_bp
from app.routes.dashboard import dashboard_bp
from app.routes.demo import demo_bp
from app.routes.events import events_bp
from app.routes.health import health_bp
from app.routes.pull_requests import pull_requests_bp
from app.routes.repositories import repositories_bp


def register_blueprints(app):
    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(demo_bp, url_prefix="/api")
    app.register_blueprint(dashboard_bp, url_prefix="/api")
    app.register_blueprint(pull_requests_bp, url_prefix="/api")
    app.register_blueprint(repositories_bp, url_prefix="/api")
    app.register_blueprint(events_bp, url_prefix="/api")
    app.register_blueprint(config_bp, url_prefix="/api")
