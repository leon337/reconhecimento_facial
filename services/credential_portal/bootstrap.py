"""Prepara acesso de uso único ao portal de provisionamento.

O código de acesso é apresentado APENAS na saída deste comando.
Nenhuma API key passa pela linha de comando, por Git ou por logs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import secrets
import time
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from services.credential_portal.vault import _private_file, _private_root


def setup(directory: str | Path, ttl_seconds: int = 7200):
    root = _private_root(directory)
    path = root / "setup-access.json"
    if path.exists():
        data = json.loads(path.read_text())
        if not data.get("used") and time.time() < data.get("expires_at", 0):
            raise RuntimeError("já existe um acesso ativo; não recriar enquanto válido")
    _private_file(root, "portal-session.key", lambda: secrets.token_bytes(48))
    def make_private_key():
        key = rsa.generate_private_key(public_exponent=65537, key_size=3072)
        return key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
    _private_file(root, "transport-private.pem", make_private_key)
    code = secrets.token_urlsafe(18)
    salt = secrets.token_bytes(16)
    digest = hashlib.sha256(salt + code.encode("ascii")).hexdigest()
    new_state = {
        "salt": salt.hex(),
        "code_hash": digest,
        "expires_at": int(time.time()) + ttl_seconds,
        "used": False,
        "failures": 0,
    }
    temporary = root / "setup-access.tmp"
    with open(temporary, "w", encoding="utf-8") as f:
        os.chmod(temporary, 0o600)
        json.dump(new_state, f)
        f.flush()
        os.fsync(f.fileno())
    os.replace(temporary, path)
    os.chmod(path, 0o600)
    return code, new_state["expires_at"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--private-dir", required=True)
    parser.add_argument("--ttl-seconds", type=int, default=7200)
    args = parser.parse_args()
    code, expiry = setup(args.private_dir, args.ttl_seconds)
    print("PORTAL_ACCESS_CODE=" + code)
    print("EXPIRES_UNIX=" + str(expiry))
