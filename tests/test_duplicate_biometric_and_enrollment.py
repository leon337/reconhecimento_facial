import io
import json

import numpy as np
from cryptography.fernet import Fernet

from app.biometric_models import BiometricProfile
from app.biometrics import encrypt_template
from app.liveness import LivenessResult
from app.models import Company, User, Worksite, db
from app.punch.service import find_duplicate_biometric
from app.rbac import AccessRole


def _admin_and_target(app):
    with app.app_context():
        company = Company(name="Empresa Liveness", slug="empresa-liveness")
        worksite = Worksite(name="Obra Liveness", company=company)
        admin = User(
            username="admin-liveness",
            access_role=AccessRole.ADMIN.value,
            company=company,
            worksite=worksite,
        )
        admin.set_password("secret")
        target = User(
            username="target-liveness",
            name="Pessoa Liveness",
            access_role=AccessRole.OPERATOR.value,
            company=company,
            worksite=worksite,
        )
        target.set_password("secret")
        db.session.add_all([company, worksite, admin, target])
        db.session.commit()
        return target.id


def _login(client):
    return client.post(
        "/admin/login",
        data={"username": "admin-liveness", "password": "secret"},
    )


def test_duplicate_face_is_rejected_within_company(app):
    key = Fernet.generate_key().decode()
    with app.app_context():
        app.config["BIOMETRIC_ENCRYPTION_KEY"] = key
        company = Company(name="Empresa Duplicada", slug="empresa-duplicada")
        first = User(username="first-face", company=company)
        first.set_password("secret")
        second = User(username="second-face", company=company)
        second.set_password("secret")
        profile = BiometricProfile(
            user=first,
            encrypted_template=encrypt_template(json.dumps([0.0] * 128)),
            image_object_key="synthetic.jpg",
        )
        db.session.add_all([company, first, second, profile])
        db.session.commit()

        result = find_duplicate_biometric(
            np.zeros(128),
            company_id=company.id,
            exclude_user_id=second.id,
            tolerance=0.45,
        )

        assert result.user.id == first.id
        assert result.reason == "duplicate_face"


def test_enrollment_requires_challenge_and_stores_live_profile(
    app,
    client,
    monkeypatch,
    tmp_path,
):
    target_id = _admin_and_target(app)
    key = Fernet.generate_key().decode()
    with app.app_context():
        app.config["BIOMETRIC_ENCRYPTION_KEY"] = key
        app.config["BIOMETRIC_STORAGE_FOLDER"] = str(tmp_path / "private")

    assert _login(client).status_code == 302
    monkeypatch.setattr(
        "app.admin.routes.analyze_blink_liveness",
        lambda frames: LivenessResult(
            True,
            "passed",
            encoding=np.zeros(128),
            best_frame_jpeg=b"synthetic-live-jpeg",
            duration_ms=600,
            blink_count=1,
            quality_score=0.91,
        ),
    )

    challenge = client.get(
        f"/admin/users/{target_id}/biometric/challenge"
    ).get_json()
    data = {
        "challenge_id": challenge["challenge_id"],
        "frames": [
            (io.BytesIO(b"frame"), f"frame-{index}.jpg")
            for index in range(6)
        ],
    }
    response = client.post(
        f"/admin/users/{target_id}/biometric",
        data=data,
        content_type="multipart/form-data",
    )

    assert response.status_code == 302
    with app.app_context():
        profile = BiometricProfile.query.filter_by(user_id=target_id).one()
        assert profile.algorithm_version == "face_recognition-liveness-2"
        assert profile.encrypted_template != json.dumps([0.0] * 128)
        assert (tmp_path / "private" / profile.image_object_key).read_bytes() == b"synthetic-live-jpeg"
