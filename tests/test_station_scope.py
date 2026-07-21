import io
import json

import numpy as np

from app.liveness import LivenessResult
from app.models import Company, User, Worksite, db
from app.punch import routes


def _frames(challenge_id, company_id):
    return {
        "challenge_id": challenge_id,
        "tipo": "ENTRADA",
        "company_id": str(company_id),
        "frames": [
            (io.BytesIO(b"frame"), f"frame-{index}.jpg")
            for index in range(6)
        ],
    }


def test_live_punch_uses_server_station_scope_and_ignores_client_scope(
    app,
    client,
    monkeypatch,
):
    with app.app_context():
        company_a = Company(name="Empresa A", slug="empresa-a")
        company_b = Company(name="Empresa B", slug="empresa-b")
        worksite_a = Worksite(name="Obra A", code="A-01", company=company_a)
        worksite_b = Worksite(name="Obra B", code="B-01", company=company_b)
        user_a = User(
            username="worker-a",
            name="Funcionário A",
            company=company_a,
            worksite=worksite_a,
            face_encoding=json.dumps([0.0] * 128),
        )
        user_a.set_password("secret")
        user_b = User(
            username="worker-b",
            name="Funcionário B",
            company=company_b,
            worksite=worksite_b,
            face_encoding=json.dumps([0.0] * 128),
        )
        user_b.set_password("secret")
        db.session.add_all([company_a, company_b, worksite_a, worksite_b, user_a, user_b])
        db.session.commit()
        company_b_id = company_b.id
        user_a_id = user_a.id

    app.config["PUNCH_COMPANY_SLUG"] = "empresa-a"
    app.config["PUNCH_WORKSITE_CODE"] = "A-01"
    monkeypatch.setattr(
        routes,
        "analyze_passive_face_liveness",
        lambda frames: LivenessResult(
            True,
            "passed",
            encoding=np.zeros(128),
            best_frame_jpeg=b"jpeg",
            duration_ms=400,
            blink_count=0,
            quality_score=0.9,
        ),
    )

    challenge = client.get("/punch/challenge").get_json()
    response = client.post(
        "/punch",
        data=_frames(challenge["challenge_id"], company_b_id),
        content_type="multipart/form-data",
    )

    assert response.status_code == 201
    assert response.get_json()["user"]["id"] == user_a_id


def test_pilot_station_fails_closed_without_company_scope(app, client, monkeypatch):
    monkeypatch.setenv("APP_ENV", "pilot")
    monkeypatch.delenv("PILOT_COMPANY_SLUG", raising=False)
    monkeypatch.delenv("PUNCH_COMPANY_SLUG", raising=False)
    app.config.pop("PUNCH_COMPANY_SLUG", None)
    app.config.pop("PUNCH_WORKSITE_CODE", None)

    challenge = client.get("/punch/challenge").get_json()
    response = client.post(
        "/punch",
        data={
            "challenge_id": challenge["challenge_id"],
            "tipo": "ENTRADA",
            "frames": [
                (io.BytesIO(b"frame"), f"frame-{index}.jpg")
                for index in range(6)
            ],
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 503
    assert response.get_json()["code"] == "station_scope_missing"
