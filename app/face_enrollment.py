from __future__ import annotations

import time
from dataclasses import dataclass
from io import BytesIO

import face_recognition
import numpy as np
from flask import current_app
from PIL import Image, ImageOps, UnidentifiedImageError


@dataclass(frozen=True)
class FaceEnrollmentResult:
    passed: bool
    reason: str
    encoding: np.ndarray | None = None
    best_frame_jpeg: bytes | None = None
    duration_ms: int = 0
    valid_frames: int = 0
    quality_score: float = 0.0
    max_intra_distance: float = 0.0


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


def _quality_score(brightness: float, sharpness: float, face_ratio: float) -> float:
    return min(
        1.0,
        max(0.0, min(1.0, face_ratio / 0.20)) * 0.40
        + max(0.0, min(1.0, sharpness / 40.0)) * 0.30
        + max(0.0, 1.0 - abs(brightness - 130.0) / 130.0) * 0.30,
    )


def analyze_face_enrollment(frame_files) -> FaceEnrollmentResult:
    """Gera um perfil facial consolidado a partir de várias leituras ao vivo.

    O cadastro não depende de piscada. Quadros ruins são descartados, os vetores
    válidos precisam representar o mesmo rosto e o perfil final é a mediana dos
    vetores consistentes.
    """

    started = time.monotonic()
    frames = list(frame_files)
    expected = int(current_app.config.get("ENROLLMENT_FRAME_COUNT", 8))
    minimum_valid = int(current_app.config.get("ENROLLMENT_MIN_VALID_FRAMES", 5))
    if len(frames) != expected:
        return FaceEnrollmentResult(False, "invalid_frame_count")

    max_dimension = int(current_app.config.get("ENROLLMENT_MAX_FRAME_DIMENSION", 360))
    min_brightness = float(current_app.config.get("ENROLLMENT_MIN_BRIGHTNESS", 30))
    max_brightness = float(current_app.config.get("ENROLLMENT_MAX_BRIGHTNESS", 230))
    min_sharpness = float(current_app.config.get("ENROLLMENT_MIN_SHARPNESS", 5))
    min_face_ratio = float(current_app.config.get("ENROLLMENT_MIN_FACE_RATIO", 0.045))
    max_intra_distance = float(current_app.config.get("ENROLLMENT_MAX_INTRA_DISTANCE", 0.34))

    observations: list[dict] = []
    saw_multiple_faces = False
    saw_face = False

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
                    "encoding": np.asarray(encodings[0], dtype=float),
                    "jpeg": jpeg,
                    "quality": _quality_score(brightness, sharpness, face_ratio),
                }
            )
    except (ValueError, OSError, TypeError):
        return FaceEnrollmentResult(False, "invalid_frame")

    if len(observations) < minimum_valid:
        if saw_multiple_faces:
            reason = "multiple_faces"
        elif not saw_face:
            reason = "no_face"
        else:
            reason = "insufficient_quality_frames"
        return FaceEnrollmentResult(
            False,
            reason,
            duration_ms=int((time.monotonic() - started) * 1000),
            valid_frames=len(observations),
        )

    matrix = np.vstack([item["encoding"] for item in observations])
    center = np.median(matrix, axis=0)
    distances = np.linalg.norm(matrix - center, axis=1)
    inlier_indexes = [index for index, distance in enumerate(distances) if distance <= max_intra_distance]

    if len(inlier_indexes) < minimum_valid:
        return FaceEnrollmentResult(
            False,
            "inconsistent_face",
            duration_ms=int((time.monotonic() - started) * 1000),
            valid_frames=len(inlier_indexes),
            max_intra_distance=float(distances.max()),
        )

    inlier_matrix = matrix[inlier_indexes]
    consolidated = np.median(inlier_matrix, axis=0)
    best_index = max(inlier_indexes, key=lambda index: observations[index]["quality"])
    best = observations[best_index]
    duration_ms = int((time.monotonic() - started) * 1000)

    return FaceEnrollmentResult(
        True,
        "passed",
        encoding=consolidated,
        best_frame_jpeg=best["jpeg"],
        duration_ms=duration_ms,
        valid_frames=len(inlier_indexes),
        quality_score=round(float(np.mean([observations[index]["quality"] for index in inlier_indexes])), 3),
        max_intra_distance=round(float(max(distances[index] for index in inlier_indexes)), 4),
    )
