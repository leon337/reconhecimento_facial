from pathlib import Path

from main import create_app


def test_operational_liveness_window_is_longer_but_under_two_seconds(tmp_path):
    application = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret",
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "UPLOAD_FOLDER": str(tmp_path / "uploads"),
            "BIOMETRIC_STORAGE_FOLDER": str(tmp_path / "biometrics"),
            "WTF_CSRF_ENABLED": False,
        }
    )

    assert application.config["LIVENESS_FRAME_COUNT"] == 10
    assert application.config["LIVENESS_CAPTURE_INTERVAL_MS"] == 200
    assert application.config["LIVENESS_FRAME_COUNT"] * application.config["LIVENESS_CAPTURE_INTERVAL_MS"] <= 2000
    assert application.config["LIVENESS_MIN_EAR_DELTA"] == 0.030
    assert application.config["LIVENESS_MAX_CLOSED_EYE_RATIO"] == 0.85


def test_camera_clients_use_server_supplied_frame_count():
    enrollment_script = Path("static/biometric_capture.js").read_text(encoding="utf-8")
    punch_script = Path("static/punch.js").read_text(encoding="utf-8")

    assert "challenge.frame_count" in enrollment_script
    assert "challenge.capture_interval_ms" in enrollment_script
    assert "challenge.frame_count" in punch_script
    assert "challenge.capture_interval_ms" in punch_script
