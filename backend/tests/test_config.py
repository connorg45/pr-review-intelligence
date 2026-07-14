from sqlalchemy.exc import IntegrityError

import app as app_module
from app import create_app
from app.config import TestingConfig, _database_url, _trusted_hosts


def test_render_postgres_url_uses_psycopg_driver(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:secret@db.example.com/app")

    assert _database_url() == "postgresql+psycopg://user:secret@db.example.com/app"


def test_trusted_hosts_are_trimmed_and_empty_values_removed(monkeypatch):
    monkeypatch.setenv("TRUSTED_HOSTS", "app.example.com, localhost, ")

    assert _trusted_hosts() == ["app.example.com", "localhost", "127.0.0.1"]


def test_app_startup_tolerates_another_worker_winning_seed_race(monkeypatch):
    class AutoSeedTestingConfig(TestingConfig):
        AUTO_SEED_DEMO = True

    def raise_duplicate_seed(*args, **kwargs):
        raise IntegrityError("insert repository", {}, Exception("duplicate"))

    monkeypatch.setattr(app_module, "seed_demo_data", raise_duplicate_seed)

    application = create_app(AutoSeedTestingConfig)

    assert application is not None
