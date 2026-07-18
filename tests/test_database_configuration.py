from sqlalchemy import inspect

from app.models import db
from main import create_app


def test_legacy_postgres_url_is_normalized(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_URL", "postgres://user:pass@localhost:5432/ponto")
    monkeypatch.setenv("SECRET_KEY", "test-secret")

    app = create_app(
        {
            "TESTING": True,
            "AUTO_CREATE_SCHEMA": False,
            "UPLOAD_FOLDER": str(tmp_path / "uploads"),
        }
    )

    assert app.config["SQLALCHEMY_DATABASE_URI"] == (
        "postgresql://user:pass@localhost:5432/ponto"
    )


def test_auto_create_schema_can_be_disabled(tmp_path):
    database_path = tmp_path / "controlled.db"
    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret",
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{database_path}",
            "AUTO_CREATE_SCHEMA": False,
            "UPLOAD_FOLDER": str(tmp_path / "uploads"),
        }
    )

    with app.app_context():
        assert inspect(db.engine).get_table_names() == []


def test_migrate_extension_is_registered(app):
    assert "migrate" in app.extensions
