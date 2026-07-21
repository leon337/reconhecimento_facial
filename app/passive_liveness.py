from __future__ import annotations

import time

import face_recognition
import numpy as np
from flask import current_app

from app.liveness import LivenessResult, _load_frame, _sharpness_score


def _quality_score(brightness: float, sharpness: float, face_ratio: float) -> float:
    return min(
        1.0,
        max(0.0, min(1.0, face_ratio / 0.20)) * 0.40
        + max(0.0, min(1.0, sharpness / 40.0)) * 0.30
        + max(0.0, 1.0 - abs(brightness - 130.0) / 130.0) * 0.30,
    )


def _frame_motion_score(previous: np.ndarray, current: np.ndarray) -> float:
    height = min(previous.shape[0], current.shape[0])
    width = min(previous.shape[1], current.shape[1])
    if height <= 0 or width <= 0:
        return 0.0

    previous_gray = previous[:height:6, :width:6].astype(np.float32).mean(axis=2)
    current_gray = current[:height:6, :width:6].astype(np.float32).mean(axis=2)
    return float(np.mean(np.abs(current_gray - previous_gray)) / 255.0)


def analyze_passive_face_liveness(frame_files) -> LivenessResult:
    """Valida presença facial por sequência ao vivo sem exigir piscada.

    O método exige um único rosto, qualidade mínima, vetores consistentes e
    variação natural entre quadros. Ele reduz falsos bloqueios por piscada,
    mas não substitui um sensor certificado de profundidade ou infravermelho.
    """

    started = time.monotonic()
    frames = list(frame_files)
    expected = int(current_app.config.get("PUNCH_LIVE_FRAME_COUNT", 6))
    minimum_valid = int(current_app.config.get("PUNCH_LIVE_MIN_VALID_FRAMES", 4))
    if len(frames) != expected:
        return LivenessResult(False, "invalid_frame_count")

    max_dimension = int(current_app.config.get("LIVENESS_MAX_FRAME_DIMENSION", 480))
    min_brightness = float(current_app.config.get("LIVENESS_MIN_BRIGHTNESS", 35))
    max_brightness = float(current_app.config.get("LIVENESS_MAX_BRIGHTNESS", 225))
    min_sharpness = float(current_app.config.get("LIVENESS_MIN_SHARPNESS", 6))
    min_face_ratio = float(current_app.config.get("LIVENESS_MIN_FACE_RATIO", 0.045))
    max_intra_distance = float(current_app.config.get("PUNCH_MAX_INTRA_DISTANCE", 0.36))
    min_motion_score = float(current_app.config.get("PUNCH_MIN_PASSIVE_MOTION_SCORE", 0.0015))

    observations: list[dict] = []
    saw_face = False
    saw_multiple_faces = False

    try:
        for file_storage in frames:
            image, jpeg = _load_frame(file_storage.stream, max_dimension)
            locations = face_recognition.face_locations(
                image,
                number_of_times_to_upsample=0,
                model="hog",
            )
            if not locations:
                continue
            saw_face = True
            if len(locations) != 1:
                saw_multiple_faces = True
                continue

            top, right, bottom, left = locations[0]
            face_area = max(0, bottom - top) * max(0, right - left)
            frame_area = max(1, image.shape[0] * image.shape[1])
            brightness = float(image.mean())
            sharpness = _sharpness_score(image)
            face_ratio = float(face_area / frame_area)

            if not min_brightness <= brightness <= max_brightness:
                continue
            if sharpness < min_sharpness or face_ratio < min_face_ratio:
                continue

            encodings = face_recognition.face_encodings(
                image,
                known_face_locations=[locations[0]],
                num_jitters=1,
                model="small",
            )
            if len(encodings) != 1:
                continue

            observations.append(
                {
                    "image": image,
                    "jpeg": jpeg,
                    "encoding": np.asarray(encodings[0], dtype=float),
                    "quality": _quality_score(brightness, sharpness, face_ratio),
                }
            )
    except (ValueError, OSError, TypeError):
        return LivenessResult(False, "invalid_frame")

    if len(observations) < minimum_valid:
        if saw_multiple_faces:
            reason = "multiple_faces"
        elif not saw_face:
            reason = "no_face"
        else:
            reason = "insufficient_quality_frames"
        return LivenessResult(
            False,
            reason,
            duration_ms=int((time.monotonic() - started) * 1000),
        )

    matrix = np.vstack([item["encoding"] for item in observations])
    center = np.median(matrix, axis=0)
    distances = np.linalg.norm(matrix - center, axis=1)
    inlier_indexes = [index for index, distance in enumerate(distances) if distance <= max_intra_distance]
    if len(inlier_indexes) < minimum_valid:
        return LivenessResult(
            False,
            "inconsistent_face",
            duration_ms=int((time.monotonic() - started) * 1000),
        )

    motion_scores = [
        _frame_motion_score(observations[index - 1]["image"], observations[index]["image"])
        for index in range(1, len(observations))
    ]
    motion_score = max(motion_scores, default=0.0)
    if motion_score < min_motion_score:
        return LivenessResult(
            False,
            "liveness_failed",
            duration_ms=int((time.monotonic() - started) * 1000),
        )

    inlier_matrix = matrix[inlier_indexes]
    consolidated = np.median(inlier_matrix, axis=0)
    best_index = max(inlier_indexes, key=lambda index: observations[index]["quality"])
    best = observations[best_index]
    quality = float(np.mean([observations[index]["quality"] for index in inlier_indexes]))

    return LivenessResult(
        True,
        "passed",
        encoding=consolidated,
        best_frame_jpeg=best["jpeg"],
        duration_ms=int((time.monotonic() - started) * 1000),
        blink_count=0,
        quality_score=round(quality, 3),
    )
