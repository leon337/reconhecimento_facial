from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from cryptography.fernet import Fernet, InvalidToken
from flask import current_app


class BiometricCryptoError(RuntimeError):
    pass


def _fernet() -> Fernet:
    key = current_app.config.get("BIOMETRIC_ENCRYPTION_KEY")
    if not key:
        raise BiometricCryptoError("biometric_encryption_key_missing")
    try:
        return Fernet(key.encode() if isinstance(key, str) else key)
    except (TypeError, ValueError) as exc:
        raise BiometricCryptoError("biometric_encryption_key_invalid") from exc


def encrypt_template(template_json: str) -> str:
    return _fernet().encrypt(template_json.encode("utf-8")).decode("ascii")


def decrypt_template(ciphertext: str) -> str:
    try:
        return _fernet().decrypt(ciphertext.encode("ascii")).decode("utf-8")
    except (InvalidToken, UnicodeDecodeError, ValueError) as exc:
        raise BiometricCryptoError("biometric_template_decryption_failed") from exc


def private_storage_root() -> Path:
    root = Path(current_app.config["BIOMETRIC_STORAGE_FOLDER"])
    root.mkdir(parents=True, exist_ok=True)
    return root


def save_private_image(file_storage, extension: str) -> tuple[str, Path]:
    object_key = f"{uuid4().hex}{extension}"
    path = private_storage_root() / object_key
    file_storage.save(path)
    return object_key, path


def save_private_image_bytes(data: bytes, extension: str = ".jpg") -> tuple[str, Path]:
    """Persiste apenas quadros produzidos pela câmera e aprovados pela prova de vida."""
    if not data:
        raise ValueError("empty_private_image")
    object_key = f"{uuid4().hex}{extension}"
    path = private_storage_root() / object_key
    path.write_bytes(data)
    return object_key, path


def delete_private_image(object_key: str | None) -> None:
    if not object_key:
        return
    (private_storage_root() / object_key).unlink(missing_ok=True)
