import io
from pathlib import Path

import numpy as np
from PIL import Image
from werkzeug.datastructures import FileStorage

from app.face_enrollment import analyze_face_enrollment


def _jpeg_frame():
    pattern = np.indices((120, 120)).sum(axis=0) % 2
    rgb = np.repeat((pattern * 255).astype(np.uint8)[:, :, None], 3, axis=2)
    output = io.BytesIO()
    Image.fromarray(rgb).save(output, format="JPEG", quality=90)
    return output.getvalue()


def _frames(count=8):
    payload = _jpeg_frame()
    return [
        FileStorage(stream=io.BytesIO(payload), filename=f"frame-{index}.jpg")
        for index in range(count)
    ]


def test_multiframe_enrollment_consolidates_consistent_face(app, monkeypatch):
    encodings = iter([np.full(128, index * 0.001) for index in range(8)])
    monkeypatch.setattr(
        "app.face_enrollment.face_recognition.face_locations",
        lambda image, number_of_times_to_upsample, model: [(10, 110, 110, 10)],
    )
    monkeypatch.setattr(
        "app.face_enrollment.face_recognition.face_encodings",
        lambda image, known_face_locations, num_jitters, model: [next(encodings)],
    )

    with app.app_context():
        result = analyze_face_enrollment(_frames())

    assert result.passed is True
    assert result.reason == "passed"
    assert result.encoding.shape == (128,)
    assert result.valid_frames == 8
    assert result.best_frame_jpeg
    assert result.duration_ms < 10000


def test_multiframe_enrollment_rejects_inconsistent_faces(app, monkeypatch):
    values = iter([0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 2.0, 2.0])
    monkeypatch.setattr(
        "app.face_enrollment.face_recognition.face_locations",
        lambda image, number_of_times_to_upsample, model: [(10, 110, 110, 10)],
    )
    monkeypatch.setattr(
        "app.face_enrollment.face_recognition.face_encodings",
        lambda image, known_face_locations, num_jitters, model: [np.full(128, next(values))],
    )

    with app.app_context():
        result = analyze_face_enrollment(_frames())

    assert result.passed is False
    assert result.reason == "inconsistent_face"


def test_enrollment_ui_does_not_require_blink_or_file_upload():
    template = Path("templates/admin/users_biometric.html").read_text(encoding="utf-8")
    script = Path("static/biometric_capture.js").read_text(encoding="utf-8")
    routes = Path("app/admin/routes.py").read_text(encoding="utf-8")

    assert 'type="file"' not in template
    assert "pisque" not in template.lower()
    assert "pisque" not in script.lower()
    assert "analyze_blink_liveness" not in routes
    assert "analyze_face_enrollment" in routes
    assert "Capturar dados faciais e cadastrar" in template


def test_enrollment_client_uses_eight_frame_default():
    script = Path("static/biometric_capture.js").read_text(encoding="utf-8")
    routes = Path("app/admin/routes.py").read_text(encoding="utf-8")

    assert "captureSession.frame_count || 8" in script
    assert 'ENROLLMENT_FRAME_COUNT", 8' in routes
    assert 'ENROLLMENT_CAPTURE_INTERVAL_MS", 160' in routes
