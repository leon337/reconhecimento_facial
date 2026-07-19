import json

from cryptography.fernet import Fernet

from app.biometric_models import BiometricProfile
from app.biometrics import encrypt_template
from app.models import User, db
from app.punch.service import _template_for_user


def test_recognition_reads_encrypted_profile_first(app):
    key = Fernet.generate_key().decode()
    protected = json.dumps([0.1] * 128)
    legacy = json.dumps([0.2] * 128)

    with app.app_context():
        app.config["BIOMETRIC_ENCRYPTION_KEY"] = key
        user = User(username="protected-user", face_encoding=legacy)
        user.set_password("secret")
        profile = BiometricProfile(
            user=user,
            encrypted_template=encrypt_template(protected),
            image_object_key="synthetic.jpg",
        )
        db.session.add_all([user, profile])
        db.session.commit()

        assert _template_for_user(user) == protected


def test_recognition_preserves_legacy_fallback(app):
    legacy = json.dumps([0.3] * 128)
    with app.app_context():
        user = User(username="legacy-user", face_encoding=legacy)
        user.set_password("secret")
        db.session.add(user)
        db.session.commit()

        assert _template_for_user(user) == legacy
