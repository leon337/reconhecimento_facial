import json
from dataclasses import dataclass

import face_recognition
import numpy as np
from PIL import Image

from app.biometrics import BiometricCryptoError, decrypt_template
from app.models import User

MAX_RECOGNITION_IMAGE_DIMENSION = 640


@dataclass(frozen=True)
class RecognitionResult:
    user: User | None
    reason: str
    distance: float | None = None


def _template_for_user(user: User) -> str | None:
    profile = getattr(user, "biometric_profile", None)
    if profile is not None and profile.active:
        try:
            return decrypt_template(profile.encrypted_template)
        except BiometricCryptoError:
            return None
    return user.face_encoding


def _load_normalized_rgb_image(image_file):
    """Limita imagens reais sem quebrar adaptadores sintéticos dos testes."""
    loaded = face_recognition.load_image_file(image_file)
    if not isinstance(loaded, np.ndarray):
        return loaded

    image = Image.fromarray(loaded).convert("RGB")
    resampling = getattr(Image, "Resampling", Image).LANCZOS
    image.thumbnail(
        (MAX_RECOGNITION_IMAGE_DIMENSION, MAX_RECOGNITION_IMAGE_DIMENSION),
        resampling,
    )
    return np.asarray(image)


def _known_templates(
    *,
    company_id: int | None = None,
    worksite_id: int | None = None,
    exclude_user_id: int | None = None,
):
    query = User.query
    if company_id is not None:
        query = query.filter(User.company_id == company_id)
    if worksite_id is not None:
        query = query.filter(User.worksite_id == worksite_id)
    if exclude_user_id is not None:
        query = query.filter(User.id != exclude_user_id)

    known_users = []
    known_encodings = []
    for user in query.all():
        template_json = _template_for_user(user)
        if not template_json:
            continue
        try:
            encoding = np.asarray(json.loads(template_json), dtype=float)
        except (TypeError, ValueError, json.JSONDecodeError):
            continue
        if encoding.shape != (128,):
            continue
        known_users.append(user)
        known_encodings.append(encoding)
    return known_users, known_encodings


def recognize_encoding(
    encoding,
    tolerance: float = 0.6,
    *,
    company_id: int | None = None,
    worksite_id: int | None = None,
    ambiguity_margin: float = 0.05,
) -> RecognitionResult:
    """Compara um encoding validado e recusa cadastros indistinguíveis."""
    if worksite_id is not None and company_id is None:
        return RecognitionResult(None, "company_scope_required")

    candidate = np.asarray(encoding, dtype=float)
    if candidate.shape != (128,):
        return RecognitionResult(None, "invalid_encoding")

    known_users, known_encodings = _known_templates(
        company_id=company_id,
        worksite_id=worksite_id,
    )
    if not known_encodings:
        return RecognitionResult(None, "no_registered_faces")

    distances = face_recognition.face_distance(known_encodings, candidate)
    order = np.argsort(distances)
    best_index = int(order[0])
    best_distance = float(distances[best_index])
    if best_distance > tolerance:
        return RecognitionResult(None, "unknown_face", best_distance)

    if len(order) > 1:
        second_distance = float(distances[int(order[1])])
        if second_distance <= tolerance and second_distance - best_distance <= ambiguity_margin:
            return RecognitionResult(None, "ambiguous_face", best_distance)

    return RecognitionResult(known_users[best_index], "matched", best_distance)


def find_duplicate_biometric(
    encoding,
    *,
    company_id: int | None,
    exclude_user_id: int,
    tolerance: float = 0.45,
) -> RecognitionResult:
    """Impede que o mesmo rosto seja associado a dois funcionários da empresa."""
    candidate = np.asarray(encoding, dtype=float)
    if candidate.shape != (128,):
        return RecognitionResult(None, "invalid_encoding")

    users, encodings = _known_templates(
        company_id=company_id,
        exclude_user_id=exclude_user_id,
    )
    if not encodings:
        return RecognitionResult(None, "not_duplicate")

    distances = face_recognition.face_distance(encodings, candidate)
    best_index = int(np.argmin(distances))
    best_distance = float(distances[best_index])
    if best_distance <= tolerance:
        return RecognitionResult(users[best_index], "duplicate_face", best_distance)
    return RecognitionResult(None, "not_duplicate", best_distance)


def recognize_registered_user(
    image_file,
    tolerance: float = 0.6,
    *,
    company_id: int | None = None,
    worksite_id: int | None = None,
) -> RecognitionResult:
    """Compatibilidade para integrações antigas sem prova de vida."""
    try:
        image = _load_normalized_rgb_image(image_file)
        encodings = face_recognition.face_encodings(image)
    except (OSError, ValueError, TypeError, AttributeError):
        return RecognitionResult(None, "invalid_image")

    if not encodings:
        return RecognitionResult(None, "no_face")
    if len(encodings) != 1:
        return RecognitionResult(None, "multiple_faces")

    return recognize_encoding(
        encodings[0],
        tolerance=tolerance,
        company_id=company_id,
        worksite_id=worksite_id,
    )
