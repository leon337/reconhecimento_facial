import json
from dataclasses import dataclass

import face_recognition
import numpy as np

from app.biometrics import BiometricCryptoError, decrypt_template
from app.models import User


@dataclass(frozen=True)
class RecognitionResult:
    user: User | None
    reason: str


def _template_for_user(user: User) -> str | None:
    profile = getattr(user, "biometric_profile", None)
    if profile is not None and profile.active:
        try:
            return decrypt_template(profile.encrypted_template)
        except BiometricCryptoError:
            return None
    return user.face_encoding


def recognize_registered_user(
    image_file,
    tolerance: float = 0.6,
    *,
    company_id: int | None = None,
    worksite_id: int | None = None,
) -> RecognitionResult:
    """Identifica um rosto respeitando escopo e perfis biométricos protegidos."""
    try:
        image = face_recognition.load_image_file(image_file)
        encodings = face_recognition.face_encodings(image)
    except (OSError, ValueError, TypeError):
        return RecognitionResult(None, "invalid_image")

    if not encodings:
        return RecognitionResult(None, "no_face")
    if len(encodings) != 1:
        return RecognitionResult(None, "multiple_faces")

    if worksite_id is not None and company_id is None:
        return RecognitionResult(None, "company_scope_required")

    query = User.query
    if company_id is not None:
        query = query.filter(User.company_id == company_id)
    if worksite_id is not None:
        query = query.filter(User.worksite_id == worksite_id)

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

    if not known_encodings:
        return RecognitionResult(None, "no_registered_faces")

    distances = face_recognition.face_distance(known_encodings, encodings[0])
    best_index = int(np.argmin(distances))
    if float(distances[best_index]) > tolerance:
        return RecognitionResult(None, "unknown_face")
    return RecognitionResult(known_users[best_index], "matched")
