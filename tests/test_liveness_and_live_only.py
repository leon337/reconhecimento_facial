import io
import json
from pathlib import Path

import numpy as np
from PIL import Image
from werkzeug.datastructures import FileStorage

from app.liveness import LivenessResult, analyze_blink_liveness, consume_challenge, issue_challenge
from app.models import User, db
from app.punch import routes


def _eye_points(ear):
    vertical = ear * 5.0
    return [
        (0.0, 0.0),
        (2.0, -vertical),
        (8.0, -vertical),
        (10.0, 0.0),
        (8.0, vertical),
        (2.0, vertical),
    ]


def _jpeg_frame():
    pattern = np.indices((100, 100)).sum(axis=0) % 2
    rgb = np.repeat((pattern * 255).astype(np.uint8)[:, :, None], 3, axis=2)
    output = io.BytesIO()
    Image.fromarray(rgb).save(output, format="JPEG", quality=90)
    return output.getvalue()


def _frames(count=6):
    payload = _jpeg_frame()
    return [
        FileStorage(stream=io.BytesIO(payload), filename=f"frame-{index}.jpg")
        for index in range(count)
    ]


def _multipart_frames(challenge_id, punch_type="ENTRADA"):
    return {
        "challenge_id": challenge_id,
        "tipo": punch_type,
        "frames": [
            (io.BytesIO(b"frame"), f"frame-{index}.jpg")
            for index in range(6)
        ],
    }


def test_liveness_challenge_is_short_lived_and_single_use(app):
    with app.test_request_context("/"):
        challenge = issue_challenge("punch")
        assert challenge["frame_count"] * challenge["capture_interval_ms"] <= 2000
        assert consume_challenge(challenge["challenge_id"], "punch") == (True, "ok")
        assert consume_challenge(challenge["challenge_id"], "punch") == (
            False,
            "challenge_invalid",
        )


def test_blink_liveness_returns_encoding(app, monkeypatch):
    ears = iter([0.30, 0.29, 0.14, 0.15, 0.28, 0.30])
    monkeypatch.setattr(
        "app.liveness.face_recognition.face_locations",
        lambda image, number_of_times_to_upsample, model: [(10, 90, 90, 10)],
    )

    def landmarks(image, face_locations, model):
        ear = next(ears)
        points = _eye_points(ear)
        return [{"left_eye": points, "right_eye": points}]

    monkeypatch.setattr("app.liveness.face_recognition.face_landmarks", landmarks)
    monkeypatch.setattr(
        "app.liveness.face_recognition.face_encodings",
        lambda image, known_face_locations, num_jitters, model: [np.zeros(128)],
    )

    with app.app_context():
        result = analyze_blink_liveness(_frames())

    assert result.passed is True
    assert result.reason == "passed"
    assert result.encoding.shape == (128,)
    assert result.best_frame_jpeg
    assert result.duration_ms < 8000


def test_static_eye_sequence_fails_liveness(app, monkeypatch):
    monkeypatch.setattr(
        "app.liveness.face_recognition.face_locations",
        lambda image, number_of_times_to_upsample, model: [(10, 90, 90, 10)],
    )
    points = _eye_points(0.30)
    monkeypatch.setattr(
        "app.liveness.face_recognition.face_landmarks",
        lambda image, face_locations, model: [{"left_eye": points, "right_eye": points}],
    )

    with app.app_context():
        result = analyze_blink_liveness(_frames())

    assert result.passed is False
    assert result.reason == "liveness_failed"


def test_operational_pages_do_not_offer_file_upload(client):
    punch_html = client.get("/punch").get_data(as_text=True)
    enrollment_template = Path("templates/admin/users_biometric.html").read_text(encoding="utf-8")
    punch_script = Path("static/punch.js").read_text(encoding="utf-8")
    enrollment_script = Path("static/biometric_capture.js").read_text(encoding="utf-8")

    assert 'type="file"' not in punch_html
    assert 'type="file"' not in enrollment_template
    assert "FileReader" not in punch_script
    assert "DataTransfer" not in enrollment_script
    assert "challenge" in punch_html


def test_punch_uses_passive_multiframe_and_identifies_employee(app, client, monkeypatch):
    with app.app_context():
        user = User(
            username="live-worker",
            name="Funcionário Vivo",
            face_encoding=json.dumps([0.0] * 128),
        )
        user.set_password("secret")
        db.session.add(user)
        db.session.commit()
        user_id = user.id

    monkeypatch.setattr(
        routes,
        "analyze_passive_face_liveness",
        lambda frames: LivenessResult(
            True,
            "passed",
            encoding=np.zeros(128),
            best_frame_jpeg=b"jpeg",
            duration_ms=500,
            blink_count=0,
            quality_score=0.9,
        ),
    )

    challenge = client.get("/punch/challenge").get_json()
    assert challenge["action"] == "PASSIVE_FACE_SEQUENCE"
    assert "pisque" not in challenge["prompt"].lower()

    response = client.post(
        "/punch",
        data=_multipart_frames(challenge["challenge_id"]),
        content_type="multipart/form-data",
    )

    assert response.status_code == 201
    payload = response.get_json()
    assert payload["user"]["id"] == user_id
    assert payload["liveness"]["passed"] is True
    assert payload["liveness"]["method"] == "passive_multiframe"
    assert payload["target_met"] is True

    replay = client.post(
        "/punch",
        data=_multipart_frames(challenge["challenge_id"]),
        content_type="multipart/form-data",
    )
    assert replay.status_code == 400
    assert replay.get_json()["code"] == "challenge_invalid"
