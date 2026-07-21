import pytest

from main import create_app


@pytest.fixture()
def app(tmp_path):
    upload_folder = tmp_path / "uploads"
    application = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret",
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "UPLOAD_FOLDER": str(upload_folder),
            "WTF_CSRF_ENABLED": False,
            "LIVENESS_FRAME_COUNT": 6,
            "LIVENESS_CAPTURE_INTERVAL_MS": 240,
            "LIVENESS_MIN_EAR_DELTA": 0.035,
            "LIVENESS_MAX_CLOSED_EYE_RATIO": 0.82,
        }
    )
    yield application


@pytest.fixture()
def client(app):
    return app.test_client()
