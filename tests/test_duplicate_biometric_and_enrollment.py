import io
import json

import numpy as np
from cryptography.fernet import Fernet

from app.biometric_models import BiometricProfile
from app.biometrics import encrypt_template
from app.face_enrollment import FaceEnrollmentResult
from app.models import Company, User, Worksite, db
from app.punch.service import find_duplicate_biometric
from app.rbac import AccessRole


def _admin_and_target(app):
    with app.app_context():
        company = Company(name="Empresa Biometria", slug="empresa-biometria")
        worksite = Worksite(name="Obra Biometria", company=company)
        admin = User(
            username="admin-biometria",
            access_role=AccessRole.ADMIN.value,
            company=company,
            worksite=worksite,
        )
        admin.set_password("secret")
        target = User(
            username="target-biometria",
            name="Pessoa Biometria",
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
        data={"username": "admin-biometria", "password": "secret"},
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


def test_enrollment_requires_capture_session_and_stores_multiframe_profile(
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
        "app.admin.routes.analyze_face_enrollment",
        lambda frames: FaceEnrollmentResult(
            True,
            "passed",
            encoding=np.zeros(128),
            best_frame_jpeg=b"synthetic-live-jpeg",
            duration_ms=600,
            valid_frames=8,
            quality_score=0.91,
            max_intra_distance=0.08,
        ),
    )

    capture_session = client.get(
        f"/admin/users/{target_id}/biometric/challenge"
    ).get_json()
    assert capture_session["action"] == "FACE_SCAN"
    assert capture_session["frame_count"] == 8

    data = {
        "challenge_id": capture_session["challenge_id"],
        "frames": [
            (io.BytesIO(b"frame"), f"frame-{index}.jpg")
            for index in range(8)
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
        assert profile.algorithm_version == "face_recognition-multiframe-3"
        assert profile.encrypted_template != json.dumps([0.0] * 128)
        assert (tmp_path / "private" / profile.image_object_key).read_bytes() == b"synthetic-live-jpeg"
