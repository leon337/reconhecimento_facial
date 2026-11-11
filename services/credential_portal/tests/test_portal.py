"""Testes com chaves e códigos SINTÉTICOS; navegação sem cookies."""
from __future__ import annotations

import base64
import json
import re

import pytest
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

from services.credential_portal.bootstrap import setup
from services.credential_portal.portal import create_app
from services.credential_portal.vault import load_gemini_api_key


@pytest.fixture
def app_data(tmp_path):
    directory = tmp_path / "cofre"
    code, _ = setup(directory, ttl_seconds=1800)
    client = create_app(str(directory), testing=True).test_client(use_cookies=False)
    return directory, code, client


def challenge(client):
    res = client.get("/")
    assert res.status_code == 200
    html = res.get_data(as_text=True)
    assert "Código temporário do MESTRE" in html
    assert "Chave API do Google AI Studio" in html
    assert "data-challenge" in html
    match = re.search(r'data-challenge="([^"]+)"', html)
    assert match
    return match.group(1)


def encrypted_value(client, text):
    res = client.get("/public-key")
    assert res.status_code == 200
    key = serialization.load_pem_public_key(res.json["publicKey"].encode())
    binary = key.encrypt(
        text.encode(), padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(), label=None,
        ),
    )
    return base64.b64encode(binary).decode()


def submit(client, code, ch=None, encrypted=None, headers=None):
    fake_key = "AIza" + "p" * 39
    return client.post("/submit-once", json={
        "challenge": ch if ch is not None else challenge(client),
        "code": code,
        "encrypted": encrypted if encrypted is not None else encrypted_value(client, fake_key),
    }, headers=headers or {})


def test_form_no_cookie_or_redirect(app_data):
    directory, code, client = app_data
    ch = challenge(client)
    assert ch and code not in client.get("/").get_data(as_text=True)
    assert client.get("/health").json["status"] == "ready"
    assert client.get("/").headers["Cache-Control"].startswith("no-store")
    assert directory.stat().st_mode & 0o077 == 0
    assert client.get("/complete").status_code == 403


def test_synthetic_key_full_submission_no_cookie(app_data):
    directory, code, client = app_data
    fake_key = "AIza" + "X" * 39
    ch = challenge(client)
    cipher = encrypted_value(client, fake_key)
    res = submit(client, code, ch=ch, encrypted=cipher)
    assert res.status_code == 201
    assert res.json["saved"] is True
    assert fake_key not in res.get_data(as_text=True)
    assert load_gemini_api_key(directory) == fake_key
    assert fake_key.encode() not in (directory / "credentials.sqlite3").read_bytes()
    assert fake_key.encode() not in (directory / "setup-access.json").read_bytes()
    assert (directory / "credentials.sqlite3").stat().st_mode & 0o077 == 0
    assert (directory / "vault-fernet.key").stat().st_mode & 0o077 == 0
    assert client.get("/health").json["status"] == "closed"
    assert client.get("/").status_code == 410
    assert client.get("/complete").status_code == 200
    assert submit(client, code, ch=ch, encrypted=cipher).status_code == 410


def test_wrong_code_reports_error_instead_of_session_failure(app_data):
    directory, code, client = app_data
    res = submit(client, "invalid", ch=challenge(client))
    assert res.status_code == 403
    assert res.json["error"] == "Código temporário incorreto."
    assert json.loads((directory / "setup-access.json").read_text())["failures"] == 1
    assert client.get("/health").json["status"] == "ready"


def test_max_bad_code_attempts(app_data):
    directory, code, client = app_data
    ch = challenge(client)
    cipher = encrypted_value(client, "AIza" + "x"*39)
    for _ in range(8):
        assert submit(client, "wrong", ch=ch, encrypted=cipher).status_code == 403
    assert submit(client, code, ch=ch, encrypted=cipher).status_code == 429


def test_bad_form_signature_not_counted_as_password_attempt(app_data):
    directory, code, client = app_data
    assert submit(client, code, ch="bad-token").status_code == 403
    assert json.loads((directory/"setup-access.json").read_text())["failures"] == 0


def test_cross_site_post_blocked(app_data):
    directory, code, client = app_data
    res = submit(client, code, headers={"Origin": "https://attacker.example"})
    assert res.status_code == 403
    assert submit(client, code, headers={"Referer": "https://attacker.example/form"}).status_code == 403
    assert json.loads((directory/"setup-access.json").read_text())["failures"] == 0


def test_origin_matching_host_and_https_testing_is_valid(app_data):
    directory, code, client = app_data
    res = submit(client, code, headers={"Origin": "http://localhost"})
    assert res.status_code == 201


def test_invalid_cipher_does_not_consume_ticket(app_data):
    directory, code, client = app_data
    ch=challenge(client)
    assert submit(client, code, ch=ch, encrypted="invalid===invalid").status_code == 400
    assert client.get("/health").json["status"] == "ready"


def test_expiration_enforced(app_data):
    directory, code, client=app_data
    ch=challenge(client)
    cipher=encrypted_value(client, "AIza" + "z"*39)
    state_file=directory/"setup-access.json"
    state=json.loads(state_file.read_text())
    state["expires_at"]=0
    state_file.write_text(json.dumps(state))
    assert client.get("/").status_code == 410
    assert submit(client, code, ch=ch, encrypted=cipher).status_code == 410


def test_old_two_step_pages_cannot_be_used(app_data):
    directory, code, client=app_data
    assert client.post("/unlock", data={"code":code}).status_code == 409
    assert client.post("/submit",json={"encrypted":"fake"}).status_code == 409
    assert client.get("/setup").status_code == 404


def test_api_key_not_exposed_on_get_or_public_key(app_data):
    directory, code, client=app_data
    for path in ("/","/public-key"):
        r=client.get(path)
        assert r.status_code==200
        assert code not in r.get_data(as_text=True)
        assert "Private" not in r.get_data(as_text=True)
        assert "no-store" in r.headers["Cache-Control"]
