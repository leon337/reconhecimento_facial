from pathlib import Path

from cryptography.fernet import Fernet

from main import create_app


def test_app_accepts_private_biometric_configuration(tmp_path):
    private_folder = tmp_path / "private" / "biometrics"
    key = Fernet.generate_key().decode()
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "BIOMETRIC_STORAGE_FOLDER": str(private_folder),
            "BIOMETRIC_ENCRYPTION_KEY": key,
            "UPLOAD_FOLDER": str(tmp_path / "legacy-uploads"),
            "WTF_CSRF_ENABLED": False,
        }
    )

    assert Path(app.config["BIOMETRIC_STORAGE_FOLDER"]) == private_folder
    assert private_folder.is_dir()
    assert app.config["BIOMETRIC_ENCRYPTION_KEY"] == key
