from pathlib import Path

from main import create_app
from app.models import Company, User, Worksite, db
from scripts.bootstrap_local import BootstrapConfigurationError, bootstrap
from scripts.configure_local import fernet_key, render_env


def _pilot_env(monkeypatch, database_url: str):
    values = {
        "APP_ENV": "testing",
        "DATABASE_URL": database_url,
        "PILOT_COMPANY_NAME": "Potiguar Teste",
        "PILOT_COMPANY_SLUG": "potiguar-teste",
        "PILOT_WORKSITE_NAME": "Obra Teste",
        "PILOT_WORKSITE_CODE": "TESTE-01",
        "PILOT_ADMIN_USERNAME": "admin-teste",
        "PILOT_ADMIN_PASSWORD": "senha-segura-123",
        "PILOT_ADMIN_NAME": "Administrador Teste",
    }
    for key, value in values.items():
        monkeypatch.setenv(key, value)


def test_fernet_key_tem_formato_valido():
    import base64

    decoded = base64.urlsafe_b64decode(fernet_key().encode("ascii"))
    assert len(decoded) == 32


def test_render_env_nao_usa_placeholders():
    content, password = render_env("admin", "Potiguar", "Obra Piloto")
    assert "CHANGE_ME" not in content
    assert "PILOT_ADMIN_USERNAME=admin" in content
    assert password in content
    assert len(password) >= 12


def test_bootstrap_local_e_idempotente(tmp_path, monkeypatch):
    database_path = tmp_path / "pilot.db"
    database_url = f"sqlite:///{database_path}"
    _pilot_env(monkeypatch, database_url)

    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": database_url})
    with app.app_context():
        db.create_all()

    first = bootstrap()
    second = bootstrap()

    assert first["admin_created"] == "true"
    assert second["admin_created"] == "false"

    verification_app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": database_url})
    with verification_app.app_context():
        assert Company.query.count() == 1
        assert Worksite.query.count() == 1
        assert User.query.count() == 1
        user = User.query.one()
        assert user.check_password("senha-segura-123")
        assert user.access_role == "super_admin"


def test_bootstrap_rejeita_senha_curta(tmp_path, monkeypatch):
    database_url = f"sqlite:///{Path(tmp_path) / 'short.db'}"
    _pilot_env(monkeypatch, database_url)
    monkeypatch.setenv("PILOT_ADMIN_PASSWORD", "curta")

    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": database_url})
    with app.app_context():
        db.create_all()

    try:
        bootstrap()
    except BootstrapConfigurationError as error:
        assert "12 caracteres" in str(error)
    else:
        raise AssertionError("Senha curta deveria ser rejeitada")
