import os
import site
from pathlib import Path

from flask import Flask

from app.admin.routes import bp as admin_bp
from app.models import db


def create_app() -> Flask:
    """Cria e configura a aplicação Flask."""
    app = Flask(
        __name__,
        static_folder="static",
        template_folder="templates",
    )

    basedir = Path(__file__).resolve().parent
    instance_dir = basedir / "instance"
    instance_dir.mkdir(exist_ok=True)

    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY",
        "development-only-change-me",
    )
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{instance_dir / 'ponto.db'}",
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    upload_folder = basedir / "static" / "uploads"
    upload_folder.mkdir(parents=True, exist_ok=True)
    app.config["UPLOAD_FOLDER"] = str(upload_folder)

    model_path = Path(site.getsitepackages()[0]) / "face_recognition_models"
    os.environ.setdefault("FACE_RECOGNITION_MODEL_LOCATION", str(model_path))

    db.init_app(app)
    app.register_blueprint(admin_bp, url_prefix="/admin")

    from app.punch import bp as punch_bp

    app.register_blueprint(punch_bp)

    with app.app_context():
        db.create_all()

    return app


# Objeto WSGI importável por Gunicorn: gunicorn main:app
app = create_app()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
