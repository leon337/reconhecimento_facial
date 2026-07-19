import io

import pytest
from cryptography.fernet import Fernet
from werkzeug.datastructures import FileStorage

from app.biometric_models import BiometricProfile
from app.biometrics import (
    BiometricCryptoError,
    decrypt_template,
    encrypt_template,
    save_private_image,
)
from app.models import User, db


def test_template_is_encrypted_and_round_trips(app):
    key = Fernet.generate_key().decode()
    plaintext = "[0.1, 0.2, 0.3]"
    with app.app_context():
        app.config["BIOMETRIC_ENCRYPTION_KEY"] = key
        ciphertext = encrypt_template(plaintext)
        assert plaintext not in ciphertext
        assert decrypt_template(ciphertext) == plaintext


def test_missing_key_fails_closed(app):
    with app.app_context():
        app.config["BIOMETRIC_ENCRYPTION_KEY"] = None
        with pytest.raises(BiometricCryptoError, match="biometric_encryption_key_missing"):
            encrypt_template("[]")


def test_private_image_is_saved_outside_static(app, tmp_path):
    private_root = tmp_path / "private-biometrics"
    with app.app_context():
        app.config["BIOMETRIC_STORAGE_FOLDER"] = str(private_root)
        upload = FileStorage(stream=io.BytesIO(b"synthetic-image"), filename="sample.jpg")
        object_key, path = save_private_image(upload, ".jpg")
        assert path.parent == private_root
        assert path.name == object_key
        assert path.read_bytes() == b"synthetic-image"
        assert "static" not in path.parts


def test_biometric_profile_is_separate_from_user(app):
    key = Fernet.generate_key().decode()
    with app.app_context():
        app.config["BIOMETRIC_ENCRYPTION_KEY"] = key
        user = User(username="synthetic-biometric-user")
        user.set_password("secret")
        profile = BiometricProfile(
            user=user,
            encrypted_template=encrypt_template("[0.0]"),
            image_object_key="synthetic.jpg",
        )
        db.session.add_all([user, profile])
        db.session.commit()

        stored = BiometricProfile.query.one()
        assert stored.user_id == user.id
        assert stored.encrypted_template != "[0.0]"
        assert user.face_encoding is None
        assert user.photo_url is None
