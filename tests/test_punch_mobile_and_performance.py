from io import BytesIO
from pathlib import Path

from PIL import Image

from app.punch.service import (
    MAX_RECOGNITION_IMAGE_DIMENSION,
    recognize_registered_user,
)


def test_punch_page_offers_front_camera_fallback(client):
    response = client.get("/punch")

    assert response.status_code == 200
    assert b'id="mobile-image"' in response.data
    assert b'capture="user"' in response.data
    assert b'id="submit-mobile-image"' in response.data
    assert b'id="start-camera"' in response.data


def test_punch_javascript_checks_secure_context_and_mobile_fallback():
    source = Path("static/punch.js").read_text(encoding="utf-8")

    assert "window.isSecureContext" in source
    assert "navigator.mediaDevices?.getUserMedia" in source
    assert "mobile-image" in source
    assert "Reconhecimento em andamento" in source


def test_recognition_normalizes_large_image_before_face_encoding(monkeypatch):
    captured_shape = {}

    def fake_face_encodings(image):
        captured_shape["value"] = image.shape
        return []

    monkeypatch.setattr(
        "app.punch.service.face_recognition.face_encodings",
        fake_face_encodings,
    )

    source = BytesIO()
    Image.new("RGB", (2400, 1200), "white").save(source, format="JPEG")
    source.seek(0)

    result = recognize_registered_user(source)

    assert result.reason == "no_face"
    height, width = captured_shape["value"][:2]
    assert max(width, height) <= MAX_RECOGNITION_IMAGE_DIMENSION
    assert (width, height) == (640, 320)


def test_recognition_rejects_invalid_mobile_image():
    result = recognize_registered_user(BytesIO(b"not-an-image"))

    assert result.user is None
    assert result.reason == "invalid_image"
