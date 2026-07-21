from __future__ import annotations

import math
import secrets
import time
from dataclasses import dataclass
from io import BytesIO

import face_recognition
import numpy as np
from flask import current_app, session
from PIL import Image, ImageOps, UnidentifiedImageError

_CHALLENGE_SESSION_KEY = "liveness_challenges"


@dataclass(frozen=True)
class LivenessResult:
    passed: bool
    reason: str
    encoding: np.ndarray | None = None
    best_frame_jpeg: bytes | None = None
    duration_ms: int = 0
    blink_count: int = 0
    quality_score: float = 0.0


def issue_challenge(purpose: str, *, subject_id: int | None = None) -> dict:
    """Cria um desafio curto, de uso único e vinculado à sessão atual."""
    now = time.time()
    ttl = int(current_app.config.get("LIVENESS_CHALLENGE_TTL_SECONDS", 20))
    challenge_id = secrets.token_urlsafe(18)
    challenges = {
        key: value
        for key, value in session.get(_CHALLENGE_SESSION_KEY, {}).items()
        if float(value.get("expires_at", 0)) > now
    }
    challenges[challenge_id] = {
        "purpose": purpose,
        "subject_id": subject_id,
        "expires_at": now + ttl,
    }
    session[_CHALLENGE_SESSION_KEY] = challenges
    session.modified = True
    return {
        "challenge_id": challenge_id,
        "action": "BLINK_ONCE",
        "prompt": "Olhe para a câmera e pisque uma vez.",
        "expires_in_seconds": ttl,
        "frame_count": int(current_app.config.get("LIVENESS_FRAME_COUNT", 6)),
        "capture_interval_ms": int(current_app.config.get("LIVENESS_CAPTURE_INTERVAL_MS", 240)),
    }


def consume_challenge(
    challenge_id: str,
    purpose: str,
    *,
    subject_id: int | None = None,
) -> tuple[bool, str]:
    """Consome o desafio antes do processamento para impedir reutilização."""
    challenges = dict(session.get(_CHALLENGE_SESSION_KEY, {}))
    payload = challenges.pop(challenge_id, None)
    session[_CHALLENGE_SESSION_KEY] = challenges
    session.modified = True

    if payload is None:
        return False, "challenge_invalid"
    if float(payload.get("expires_at", 0)) <= time.time():
        return False, "challenge_expired"
    if payload.get("purpose") != purpose:
        return False, "challenge_purpose_mismatch"
    if payload.get("subject_id") != subject_id:
        return False, "challenge_subject_mismatch"
    return True, "ok"


def _eye_aspect_ratio(points) -> float:
    eye = np.asarray(points, dtype=float)
    if eye.shape != (6, 2):
        return 0.0
    horizontal = np.linalg.norm(eye[0] - eye[3])
    if horizontal <= 1e-6:
        return 0.0
    vertical_a = np.linalg.norm(eye[1] - eye[5])
    vertical_b = np.linalg.norm(eye[2] - eye[4])
    return float((vertical_a + vertical_b) / (2.0 * horizontal))


def _sharpness_score(image: np.ndarray) -> float:
    gray = image.astype(np.float32).mean(axis=2)
    gradient_x = np.diff(gray, axis=1)
    gradient_y = np.diff(gray, axis=0)
    return float((np.var(gradient_x) + np.var(gradient_y)) / 2.0)


def _load_frame(file_storage, max_dimension: int) -> tuple[np.ndarray, bytes]:
    raw = file_storage.read()
    if not raw:
        raise ValueError("empty_frame")
    try:
        image = Image.open(BytesIO(raw))
        image = ImageOps.exif_transpose(image).convert("RGB")
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise ValueError("invalid_frame") from exc

    image.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
    output = BytesIO()
    image.save(output, format="JPEG", quality=86, optimize=True)
    return np.asarray(image), output.getvalue()


def analyze_blink_liveness(frame_files) -> LivenessResult:
    """Valida uma piscada em uma sequência curta e retorna a codificação facial.

    A implementação é deliberadamente leve para o piloto local: quadros reduzidos,
    detector HOG, um único encoding e nenhum jitter adicional.
    """
    started = time.monotonic()
    frames = list(frame_files)
    expected = int(current_app.config.get("LIVENESS_FRAME_COUNT", 6))
    if len(frames) != expected:
        return LivenessResult(False, "invalid_frame_count")

    max_dimension = int(current_app.config.get("LIVENESS_MAX_FRAME_DIMENSION", 480))
    observations = []

    try:
        for file_storage in frames:
            image, jpeg = _load_frame(file_storage.stream, max_dimension)
            locations = face_recognition.face_locations(
                image,
                number_of_times_to_upsample=0,
                model="hog",
            )
            if not locations:
                return LivenessResult(False, "no_face")
            if len(locations) != 1:
                return LivenessResult(False, "multiple_faces")

            landmarks_list = face_recognition.face_landmarks(
                image,
                face_locations=locations,
                model="small",
            )
            if len(landmarks_list) != 1:
                return LivenessResult(False, "landmarks_unavailable")

            landmarks = landmarks_list[0]
            left_ear = _eye_aspect_ratio(landmarks.get("left_eye", []))
            right_ear = _eye_aspect_ratio(landmarks.get("right_eye", []))
            ear = (left_ear + right_ear) / 2.0
            top, right, bottom, left = locations[0]
            face_area = max(0, bottom - top) * max(0, right - left)
            frame_area = max(1, image.shape[0] * image.shape[1])
            observations.append(
                {
                    "image": image,
                    "jpeg": jpeg,
                    "location": locations[0],
                    "ear": ear,
                    "brightness": float(image.mean()),
                    "sharpness": _sharpness_score(image),
                    "face_ratio": float(face_area / frame_area),
                }
            )
    except (ValueError, OSError, TypeError):
        return LivenessResult(False, "invalid_frame")

    ears = [item["ear"] for item in observations]
    max_ear = max(ears)
    min_ear = min(ears)
    blink_delta = max_ear - min_ear
    blink_ratio = min_ear / max_ear if max_ear > 1e-6 else 1.0
    min_delta = float(current_app.config.get("LIVENESS_MIN_EAR_DELTA", 0.035))
    max_closed_ratio = float(current_app.config.get("LIVENESS_MAX_CLOSED_EYE_RATIO", 0.82))

    if blink_delta < min_delta or blink_ratio > max_closed_ratio:
        return LivenessResult(
            False,
            "liveness_failed",
            duration_ms=int((time.monotonic() - started) * 1000),
        )

    best = max(observations, key=lambda item: item["ear"])
    min_brightness = float(current_app.config.get("LIVENESS_MIN_BRIGHTNESS", 35))
    max_brightness = float(current_app.config.get("LIVENESS_MAX_BRIGHTNESS", 225))
    min_sharpness = float(current_app.config.get("LIVENESS_MIN_SHARPNESS", 8))
    min_face_ratio = float(current_app.config.get("LIVENESS_MIN_FACE_RATIO", 0.05))

    if not min_brightness <= best["brightness"] <= max_brightness:
        return LivenessResult(False, "poor_lighting")
    if best["sharpness"] < min_sharpness:
        return LivenessResult(False, "blurry_frame")
    if best["face_ratio"] < min_face_ratio:
        return LivenessResult(False, "face_too_small")

    encodings = face_recognition.face_encodings(
        best["image"],
        known_face_locations=[best["location"]],
        num_jitters=1,
        model="small",
    )
    if len(encodings) != 1:
        return LivenessResult(False, "encoding_failed")

    quality = min(
        1.0,
        max(0.0, best["face_ratio"] / 0.2) * 0.4
        + max(0.0, min(1.0, best["sharpness"] / 40.0)) * 0.3
        + max(0.0, 1.0 - abs(best["brightness"] - 130.0) / 130.0) * 0.3,
    )
    duration_ms = int((time.monotonic() - started) * 1000)
    return LivenessResult(
        True,
        "passed",
        encoding=encodings[0],
        best_frame_jpeg=best["jpeg"],
        duration_ms=duration_ms,
        blink_count=1,
        quality_score=round(quality, 3),
    )
