import os
import site
from pathlib import Path
from typing import Any

from flask import Flask
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

from app.admin.routes import bp as admin_bp
from app.models import db

csrf = CSRFProtect()
migrate = Migrate()


def _database_url(instance_dir: Path) -> str:
    """Retorna uma URL SQLAlchemy compatível com SQLite e PostgreSQL."""
    url = os.environ.get("DATABASE_URL")
    if not url:
        return f"sqlite:///{instance_dir / 'ponto.db'}"
    if url.startswith("postgres://"):
        return "postgresql://" + url.removeprefix("postgres://")
    return url


def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    """Cria e configura a aplicação Flask."""
    app = Flask(
        __name__,
        static_folder="static",
        template_folder="templates",
    )

    basedir = Path(__file__).resolve().parent
    instance_dir = basedir / "instance"
    instance_dir.mkdir(exist_ok=True)

    app_env = os.environ.get("APP_ENV", "development").lower()
    secret_key = os.environ.get("SECRET_KEY")
    if app_env == "production" and not secret_key:
        raise RuntimeError("SECRET_KEY é obrigatória em produção.")

    app.config.from_mapping(
        SECRET_KEY=secret_key or "development-only-change-me",
        SQLALCHEMY_DATABASE_URI=_database_url(instance_dir),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        AUTO_CREATE_SCHEMA=app_env != "production",
        UPLOAD_FOLDER=str(basedir / "static" / "uploads"),
        BIOMETRIC_STORAGE_FOLDER=str(instance_dir / "biometrics"),
        BIOMETRIC_ENCRYPTION_KEY=os.environ.get("BIOMETRIC_ENCRYPTION_KEY"),
        MAX_CONTENT_LENGTH=5 * 1024 * 1024,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=app_env == "production",
        WTF_CSRF_TIME_LIMIT=3600,
        PUNCH_DUPLICATE_WINDOW_SECONDS=60,
    )

    if test_config:
        app.config.update(test_config)

    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)
    Path(app.config["BIOMETRIC_STORAGE_FOLDER"]).mkdir(parents=True, exist_ok=True)

    model_path = Path(site.getsitepackages()[0]) / "face_recognition_models"
    os.environ.setdefault("FACE_RECOGNITION_MODEL_LOCATION", str(model_path))

    db.init_app(app)
    from app.biometric_models import BiometricProfile  # noqa: F401

    migrate.init_app(app, db)
    csrf.init_app(app)
    app.register_blueprint(admin_bp, url_prefix="/admin")

    from app.punch import bp as punch_bp

    app.register_blueprint(punch_bp)

    if app.config["AUTO_CREATE_SCHEMA"]:
        with app.app_context():
            db.create_all()

    return app


app = create_app()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
