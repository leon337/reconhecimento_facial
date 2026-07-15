import os
import site
from pathlib import Path
from typing import Any

from flask import Flask

from app.admin.routes import bp as admin_bp
from app.models import db


def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    """Cria e configura a aplicação Flask.

    ``test_config`` permite substituir configurações sem acessar banco ou
    diretórios reais durante testes automatizados.
    """
    app = Flask(
        __name__,
        static_folder="static",
        template_folder="templates",
    )

    basedir = Path(__file__).resolve().parent
    instance_dir = basedir / "instance"
    instance_dir.mkdir(exist_ok=True)

    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "development-only-change-me"),
        SQLALCHEMY_DATABASE_URI=os.environ.get(
            "DATABASE_URL",
            f"sqlite:///{instance_dir / 'ponto.db'}",
        ),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        UPLOAD_FOLDER=str(basedir / "static" / "uploads"),
    )

    if test_config:
        app.config.update(test_config)

    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)

    model_path = Path(site.getsitepackages()[0]) / "face_recognition_models"
    os.environ.setdefault("FACE_RECOGNITION_MODEL_LOCATION", str(model_path))

    db.init_app(app)
    app.register_blueprint(admin_bp, url_prefix="/admin")

    from app.punch import bp as punch_bp

    app.register_blueprint(punch_bp)

    with app.app_context():
        db.create_all()

    return app


app = create_app()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
