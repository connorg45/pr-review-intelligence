import os


def _as_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _database_url() -> str:
    value = os.getenv("DATABASE_URL", "sqlite:///pr_review_intelligence.db")
    if value.startswith("postgres://"):
        return value.replace("postgres://", "postgresql+psycopg://", 1)
    if value.startswith("postgresql://"):
        return value.replace("postgresql://", "postgresql+psycopg://", 1)
    return value


def _trusted_hosts() -> list[str] | None:
    value = os.getenv("TRUSTED_HOSTS") or os.getenv("RENDER_EXTERNAL_HOSTNAME", "")
    hosts = [host.strip() for host in value.split(",") if host.strip()]
    if hosts:
        hosts.extend(host for host in ("localhost", "127.0.0.1") if host not in hosts)
    return hosts or None


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = _database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
    GITHUB_API_BASE_URL = os.getenv("GITHUB_API_BASE_URL", "https://api.github.com")
    DEFAULT_SYNC_LIMIT = int(os.getenv("DEFAULT_SYNC_LIMIT", "15"))
    AUTO_CREATE_DB = _as_bool(os.getenv("AUTO_CREATE_DB"), True)
    AUTO_SEED_DEMO = _as_bool(os.getenv("AUTO_SEED_DEMO"), True)
    WRITE_OPERATIONS_ENABLED = _as_bool(os.getenv("WRITE_OPERATIONS_ENABLED"), False)
    TRUSTED_HOSTS = _trusted_hosts()
    APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
    MAX_CONTENT_LENGTH = 1024 * 1024


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SQLALCHEMY_ENGINE_OPTIONS = {}
    AUTO_CREATE_DB = True
    AUTO_SEED_DEMO = False
    WRITE_OPERATIONS_ENABLED = True
    TRUSTED_HOSTS = None
