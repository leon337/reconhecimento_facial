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
        }
    )
    yield application


@pytest.fixture()
def client(app):
    return app.test_client()
