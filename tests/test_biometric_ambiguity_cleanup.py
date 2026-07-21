import json

import numpy as np
from cryptography.fernet import Fernet

from app.biometric_models import BiometricProfile
from app.biometrics import encrypt_template
from app.models import Company, User, Worksite, db
from app.punch.service import recognize_encoding
from app.rbac import AccessRole


def test_recognition_rejects_two_indistinguishable_profiles(app):
    with app.app_context():
        company = Company(name="Empresa Ambígua", slug="empresa-ambigua")
        worksite = Worksite(name="Obra Ambígua", code="AMB-01", company=company)
        first = User(
            username="ambiguous-first",
            company=company,
            worksite=worksite,
            face_encoding=json.dumps([0.0] * 128),
        )
        first.set_password("secret")
        second = User(
            username="ambiguous-second",
            company=company,
            worksite=worksite,
            face_encoding=json.dumps([0.0] * 128),
        )
        second.set_password("secret")
        db.session.add_all([company, worksite, first, second])
        db.session.commit()

        result = recognize_encoding(
            np.zeros(128),
            company_id=company.id,
            worksite_id=worksite.id,
        )

        assert result.user is None
        assert result.reason == "ambiguous_face"


def test_admin_can_remove_incorrect_biometric(app, client, tmp_path):
    key = Fernet.generate_key().decode()
    storage = tmp_path / "private"
    storage.mkdir()
    image_path = storage / "duplicate.jpg"
    image_path.write_bytes(b"synthetic-private-image")

    with app.app_context():
        app.config["BIOMETRIC_ENCRYPTION_KEY"] = key
        app.config["BIOMETRIC_STORAGE_FOLDER"] = str(storage)
        company = Company(name="Empresa Limpeza", slug="empresa-limpeza")
        worksite = Worksite(name="Obra Limpeza", code="LIM-01", company=company)
        admin = User(
            username="cleanup-admin",
            access_role=AccessRole.ADMIN.value,
            company=company,
            worksite=worksite,
        )
        admin.set_password("secret")
        target = User(
            username="cleanup-target",
            name="Pessoa Duplicada",
            company=company,
            worksite=worksite,
            face_encoding=json.dumps([0.0] * 128),
        )
        target.set_password("secret")
        profile = BiometricProfile(
            user=target,
            encrypted_template=encrypt_template(json.dumps([0.0] * 128)),
            image_object_key="duplicate.jpg",
        )
        db.session.add_all([company, worksite, admin, target, profile])
        db.session.commit()
        target_id = target.id

    login = client.post(
        "/admin/login",
        data={"username": "cleanup-admin", "password": "secret"},
    )
    assert login.status_code == 302

    response = client.post(
        f"/admin/users/{target_id}/biometric",
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Biometria removida" in response.data

    with app.app_context():
        target = db.session.get(User, target_id)
        assert target.biometric_profile is None
        assert target.face_encoding is None
        assert target.photo_url is None
    assert image_path.exists() is False
