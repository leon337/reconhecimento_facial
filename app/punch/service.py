import json
from dataclasses import dataclass

import face_recognition
import numpy as np

from app.models import User


@dataclass(frozen=True)
class RecognitionResult:
    user: User | None
    reason: str


def recognize_registered_user(image_file, tolerance: float = 0.6) -> RecognitionResult:
    """Identifica exatamente um rosto entre usuários com biometria cadastrada."""
    try:
        image = face_recognition.load_image_file(image_file)
        encodings = face_recognition.face_encodings(image)
    except (OSError, ValueError, TypeError):
        return RecognitionResult(None, "invalid_image")

    if not encodings:
        return RecognitionResult(None, "no_face")
    if len(encodings) != 1:
        return RecognitionResult(None, "multiple_faces")

    users = User.query.filter(User.face_encoding.isnot(None)).all()
    known_users = []
    known_encodings = []

    for user in users:
        try:
            encoding = np.asarray(json.loads(user.face_encoding), dtype=float)
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
