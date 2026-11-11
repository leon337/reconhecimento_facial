"""Testes de segurança do portal — somente dados sintéticos."""
import base64
import json
import os
from pathlib import Path

import pytest
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

from services.credential_portal.vault import load_gemini_api_key
from services.credential_portal.bootstrap import setup
from services.credential_portal.portal import create_app


@pytest.fixture
def enrollment(tmp_path):
    folder = tmp_path / "private"
    code, _ = setup(folder, ttl_seconds=1800)
    app = create_app(str(folder), testing=True)
    return folder, code, app.test_client()


def _login(client, code):
    page = client.get("/")
    assert page.status_code == 200
    with client.session_transaction() as s:
        csrf = s["login_csrf"]
    response = client.post(
        "/unlock",
        data={"code": code, "csrf_token": csrf},
        headers={"Origin": "http://localhost"},
    )
    return response


def _encrypt(public_pem, plaintext):
    pub = serialization.load_pem_public_key(public_pem.encode("ascii"))
    encrypted = pub.encrypt(
        plaintext.encode("utf-8"),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    return base64.b64encode(encrypted).decode("ascii")


def test_private_directory_and_token_are_not_public(enrollment):
    folder, code, client = enrollment
    assert folder.stat().st_mode & 0o077 == 0
    assert (folder / "setup-access.json").stat().st_mode & 0o077 == 0
    html = client.get("/").get_data(as_text=True)
    assert code not in html
    assert client.get("/public-key").status_code == 403
    assert client.get("/setup").status_code == 403
    assert client.get("/health").json["status"] == "ready"
    assert "no-store" in client.get("/").headers["Cache-Control"]


def test_wrong_access_code_and_attempt_limit(enrollment):
    _, code, client = enrollment
    client.get("/")
    with client.session_transaction() as s:
        token = s["login_csrf"]
    for _ in range(8):
        r = client.post(
            "/unlock", data={"code": "incorreto", "csrf_token": token},
            headers={"Origin": "http://localhost"},
        )
        assert r.status_code == 403
    assert client.post(
        "/unlock", data={"code": code, "csrf_token": token},
        headers={"Origin": "http://localhost"},
    ).status_code == 429


def test_public_key_submission_encrypts_and_revokes_single_use(enrollment):
    folder, code, client = enrollment
    assert _login(client, code).status_code == 303
    page = client.get("/setup")
    assert page.status_code == 200
    assert "nenhum dado" not in page.get_data(as_text=True).lower()
    with client.session_transaction() as s:
        token = s["post_csrf"]
    public_pem = client.get("/public-key").json["publicKey"]
    fake_key = "AIza" + "m" * 39
    cipher = _encrypt(public_pem, fake_key)
    assert fake_key not in cipher
    assert client.post(
        "/submit", json={"encrypted": cipher},
        headers={"Origin": "http://localhost", "X-CSRFToken": "wrong"},
    ).status_code == 403
    response = client.post(
        "/submit", json={"encrypted": cipher},
        headers={"Origin": "http://localhost", "X-CSRFToken": token},
    )
    assert response.status_code == 201
    assert response.json["saved"] is True
    assert fake_key not in response.get_data(as_text=True)
    assert load_gemini_api_key(folder) == fake_key
    assert fake_key.encode() not in (folder / "credentials.sqlite3").read_bytes()
    assert fake_key.encode() not in (folder / "setup-access.json").read_bytes()
    assert (folder / "vault-fernet.key").stat().st_mode & 0o077 == 0
    assert (folder / "credentials.sqlite3").stat().st_mode & 0o077 == 0
    assert client.post(
        "/submit", json={"encrypted": cipher},
        headers={"Origin": "http://localhost", "X-CSRFToken": token},
    ).status_code == 403
    assert client.get("/").status_code == 410
    assert client.get("/health").json["status"] == "closed"
    assert client.get("/complete").status_code == 200


def test_expired_access_is_rejected(enrollment):
    folder, code, client = enrollment
    state_path = folder / "setup-access.json"
    state = json.loads(state_path.read_text())
    state["expires_at"] = 0
    state_path.write_text(json.dumps(state))
    assert client.get("/").status_code == 410
    assert client.get("/health").json["status"] == "closed"


def test_cross_origin_and_bad_cipher_rejected(enrollment):
    _, code, client = enrollment
    client.get("/")
    with client.session_transaction() as s:
        token = s["login_csrf"]
    assert client.post(
        "/unlock", data={"code": code, "csrf_token": token},
        headers={"Origin": "https://evil.example"},
    ).status_code == 403
    assert _login(client, code).status_code == 303
    with client.session_transaction() as s:
        post_csrf = s["post_csrf"]
    r = client.post(
        "/submit", json={"encrypted": base64.b64encode(b"garbage").decode()},
        headers={"Origin": "http://localhost", "X-CSRFToken": post_csrf},
    )
    assert r.status_code == 400
