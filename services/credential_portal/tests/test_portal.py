"""Testes do cofre e do login sem cookies, com credenciais 100% fictícias."""
import base64
import json
import re
from pathlib import Path

import pytest
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

from services.credential_portal.bootstrap import setup
from services.credential_portal.portal import create_app
from services.credential_portal.vault import load_gemini_api_key


@pytest.fixture
def enrollment(tmp_path):
    directory = tmp_path / "private"
    code, _ = setup(directory, ttl_seconds=1800)
    # Simula um navegador que não salva nenhum cookie, como alguns WebViews/VPNs.
    client = create_app(str(directory), testing=True).test_client(use_cookies=False)
    return directory, code, client


def hidden_csrf(client):
    page = client.get("/")
    assert page.status_code == 200
    match = re.search(r'name="csrf_token" value="([^"]+)"', page.get_data(as_text=True))
    assert match, "faltou o token de formulário assinado"
    return match.group(1)


def login(client, code, **headers):
    csrf = hidden_csrf(client)
    return client.post(
        "/unlock", data={"code": code, "csrf_token": csrf},
        headers=headers,
        follow_redirects=False,
    )


def credentials_from_setup(response):
    html = response.get_data(as_text=True)
    assert "Adicionar chave do Gemini" in html
    ticket = re.search(r'data-access-ticket="([^"]+)"', html)
    csrf = re.search(r'data-csrf="([^"]+)"', html)
    assert ticket and csrf, "credenciais de sessão curta não encontradas no HTML"
    return ticket.group(1), csrf.group(1)


def encrypt_with_public_key(public_pem, plain):
    public_key = serialization.load_pem_public_key(public_pem.encode("ascii"))
    cipher = public_key.encrypt(
        plain.encode("utf-8"),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    return base64.b64encode(cipher).decode("ascii")


def test_initial_form_and_private_directory(enrollment):
    directory, code, client = enrollment
    csrf = hidden_csrf(client)
    assert csrf and code not in client.get("/").get_data(as_text=True)
    assert directory.stat().st_mode & 0o077 == 0
    assert (directory / "setup-access.json").stat().st_mode & 0o077 == 0
    assert client.get("/public-key").status_code == 403
    assert client.get("/setup").status_code == 403
    assert client.get("/health").json["status"] == "ready"
    assert "no-store" in client.get("/").headers["Cache-Control"]


def test_correct_code_unlocks_without_cookies_or_redirect(enrollment):
    directory, code, client = enrollment
    response = login(client, code)
    assert response.status_code == 200
    assert response.headers.get("Location") is None
    ticket, csrf = credentials_from_setup(response)
    assert ticket and csrf
    assert client.get("/public-key", headers={"X-Portal-Ticket": ticket}).status_code == 200
    assert not (directory / "credentials.sqlite3").exists()
    assert client.get("/health").json["status"] == "ready"


def test_wrong_code_and_failure_limit(enrollment):
    directory, code, client = enrollment
    for attempt in range(8):
        response = login(client, "senha-invalida")
        assert response.status_code == 403
        assert "Código incorreto" in response.get_data(as_text=True)
    response = login(client, code)
    assert response.status_code == 429


def test_unguarded_posts_denied(enrollment):
    _, code, client = enrollment
    assert client.post("/unlock", data={"code": code}).status_code == 403
    assert client.post("/submit", json={"encrypted": "aa"}).status_code == 403
    assert client.get("/public-key").status_code == 403
    assert client.get("/complete").status_code == 403


def test_invalid_csrf_rejected_before_code_check(enrollment):
    directory, code, client = enrollment
    response = client.post("/unlock", data={"code": code, "csrf_token": "invalid"})
    assert response.status_code == 403
    assert json.loads((directory / "setup-access.json").read_text())["failures"] == 0


def test_cross_site_origin_or_referer_denied(enrollment):
    _, code, client = enrollment
    csrf = hidden_csrf(client)
    for headers in (
        {"Origin": "https://attacker.example"},
        {"Referer": "https://attacker.example/path"},
    ):
        response = client.post(
            "/unlock", data={"code": code, "csrf_token": csrf}, headers=headers
        )
        assert response.status_code == 403
    assert login(client, code, Origin="http://localhost").status_code == 200


def test_encrypted_submission_one_use_without_cookies(enrollment):
    directory, code, client = enrollment
    response = login(client, code)
    ticket, csrf = credentials_from_setup(response)
    pub_response = client.get("/public-key", headers={"X-Portal-Ticket": ticket})
    assert pub_response.status_code == 200
    fake_key = "AIza" + "s" * 39
    cipher = encrypt_with_public_key(pub_response.json["publicKey"], fake_key)
    assert fake_key not in cipher
    bad_post = client.post(
        "/submit", json={"encrypted": cipher},
        headers={"X-Portal-Ticket": ticket, "X-CSRFToken": "incorrect"},
    )
    assert bad_post.status_code == 403
    result = client.post(
        "/submit", json={"encrypted": cipher},
        headers={"X-Portal-Ticket": ticket, "X-CSRFToken": csrf},
    )
    assert result.status_code == 201
    assert result.json["saved"] is True
    assert fake_key not in result.get_data(as_text=True)
    assert fake_key.encode("ascii") not in (directory / "credentials.sqlite3").read_bytes()
    assert fake_key.encode("ascii") not in (directory / "setup-access.json").read_bytes()
    assert load_gemini_api_key(directory) == fake_key
    assert (directory / "credentials.sqlite3").stat().st_mode & 0o077 == 0
    assert (directory / "vault-fernet.key").stat().st_mode & 0o077 == 0
    assert client.post(
        "/submit", json={"encrypted": cipher},
        headers={"X-Portal-Ticket": ticket, "X-CSRFToken": csrf},
    ).status_code == 403
    assert client.get("/health").json["status"] == "closed"
    assert client.get("/complete").status_code == 200
    assert client.get("/").status_code == 410


def test_expired_access_denied(enrollment):
    directory, code, client = enrollment
    state_file = directory / "setup-access.json"
    state = json.loads(state_file.read_text())
    state["expires_at"] = 0
    state_file.write_text(json.dumps(state))
    assert client.get("/").status_code == 410
    assert client.get("/health").json["status"] == "closed"


def test_invalid_cipher_does_not_revoke_access(enrollment):
    _, code, client = enrollment
    ticket, csrf = credentials_from_setup(login(client, code))
    response = client.post(
        "/submit", json={"encrypted": base64.b64encode(b"broken").decode()},
        headers={"X-Portal-Ticket": ticket, "X-CSRFToken": csrf},
    )
    assert response.status_code == 400
    assert client.get("/health").json["status"] == "ready"


def test_ticket_and_csrf_are_bound_together(enrollment):
    _, code, client = enrollment
    ticket1, csrf1 = credentials_from_setup(login(client, code))
    ticket2, csrf2 = credentials_from_setup(login(client, code))
    assert ticket1 != ticket2
    assert csrf1 != csrf2
    fake = base64.b64encode(b"invalid-payload").decode()
    response = client.post(
        "/submit", json={"encrypted": fake},
        headers={"X-Portal-Ticket": ticket1, "X-CSRFToken": csrf2},
    )
    assert response.status_code == 403
    assert client.get("/health").json["status"] == "ready"


def test_retry_screen_is_explanatory(enrollment):
    _, _, client = enrollment
    response = client.get("/setup")
    assert response.status_code == 403
    assert "Não foi possível confirmar sua sessão" in response.get_data(as_text=True)
    assert "Voltar ao início" in response.get_data(as_text=True)
