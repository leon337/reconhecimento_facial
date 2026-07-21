import io

import numpy as np
from PIL import Image
from werkzeug.datastructures import FileStorage

from app.passive_liveness import analyze_passive_face_liveness


def _jpeg(array):
    output = io.BytesIO()
    Image.fromarray(array.astype(np.uint8)).save(output, format="JPEG", quality=92)
    return output.getvalue()


def _moving_frames(count=6):
    base = np.indices((100, 100)).sum(axis=0) % 2
    frames = []
    for index in range(count):
        shifted = np.roll(base, index + 1, axis=1)
        rgb = np.repeat((shifted * 180 + 35)[:, :, None], 3, axis=2)
        frames.append(
            FileStorage(
                stream=io.BytesIO(_jpeg(rgb)),
                filename=f"frame-{index}.jpg",
            )
        )
    return frames


def _static_frames(count=6):
    pattern = np.indices((100, 100)).sum(axis=0) % 2
    rgb = np.repeat((pattern * 180 + 35)[:, :, None], 3, axis=2)
    payload = _jpeg(rgb)
    return [
        FileStorage(stream=io.BytesIO(payload), filename=f"frame-{index}.jpg")
        for index in range(count)
    ]


def _patch_face_recognition(monkeypatch):
    monkeypatch.setattr(
        "app.passive_liveness.face_recognition.face_locations",
        lambda image, number_of_times_to_upsample, model: [(10, 90, 90, 10)],
    )
    monkeypatch.setattr(
        "app.passive_liveness.face_recognition.face_encodings",
        lambda image, known_face_locations, num_jitters, model: [np.zeros(128)],
    )


def test_passive_sequence_returns_consolidated_encoding(app, monkeypatch):
    _patch_face_recognition(monkeypatch)

    with app.app_context():
        result = analyze_passive_face_liveness(_moving_frames())

    assert result.passed is True
    assert result.reason == "passed"
    assert result.encoding.shape == (128,)
    assert result.best_frame_jpeg
    assert result.blink_count == 0
    assert result.duration_ms < 8000


def test_identical_static_sequence_is_rejected(app, monkeypatch):
    _patch_face_recognition(monkeypatch)

    with app.app_context():
        result = analyze_passive_face_liveness(_static_frames())

    assert result.passed is False
    assert result.reason == "liveness_failed"


def test_inconsistent_face_encodings_are_rejected(app, monkeypatch):
    monkeypatch.setattr(
        "app.passive_liveness.face_recognition.face_locations",
        lambda image, number_of_times_to_upsample, model: [(10, 90, 90, 10)],
    )
    values = iter([0.0, 0.0, 1.0, 1.0, 2.0, 2.0])
    monkeypatch.setattr(
        "app.passive_liveness.face_recognition.face_encodings",
        lambda image, known_face_locations, num_jitters, model: [np.full(128, next(values))],
    )

    with app.app_context():
        result = analyze_passive_face_liveness(_moving_frames())

    assert result.passed is False
    assert result.reason == "inconsistent_face"
