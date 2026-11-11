"""Portal temporário para receber uma API key Gemini fora de chats e do Git.

Executar somente em 127.0.0.1, atrás de HTTPS, com senha de uso único.
O navegador cifra a chave usando RSA-OAEP; o servidor a guarda em SQLite
com Fernet e chave mestra em arquivo separado, ambos privados.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import threading
import time
from pathlib import Path
from urllib.parse import urlparse

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from flask import Flask, abort, jsonify, redirect, render_template, request, session, url_for

from services.credential_portal.vault import (
    CredentialVaultError,
    _private_root,
    store_gemini_api_key,
)

ACCESS_FILE = "setup-access.json"
PRIVATE_KEY_FILE = "transport-private.pem"
MAX_FAILED_ATTEMPTS = 8


def create_app(private_directory: str, *, testing: bool = False) -> Flask:
    root = _private_root(private_directory)
    secret_file = root / "portal-session.key"
    if not secret_file.is_file():
        raise RuntimeError("é necessário preparar o acesso antes de abrir o portal")
    app = Flask(__name__, template_folder="templates", static_folder="static", static_url_path="/assets")
    app.config.update(
        SECRET_KEY=secret_file.read_bytes(),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Strict",
        SESSION_COOKIE_SECURE=not testing,
        MAX_CONTENT_LENGTH=8192,
        TESTING=testing,
    )
    state_lock = threading.Lock()

    def get_state() -> dict:
        file = root / ACCESS_FILE
        if not file.exists() or file.stat().st_mode & 0o077:
            raise RuntimeError("estado privado do portal indisponível")
        return json.loads(file.read_text(encoding="utf-8"))

    def save_state(data: dict) -> None:
        temporary = root / "setup-access-tmp.json"
        fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as output:
            json.dump(data, output)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, root / ACCESS_FILE)

    def active() -> bool:
        try:
            state = get_state()
            return not state["used"] and time.time() < state["expires_at"]
        except (OSError, ValueError, KeyError, RuntimeError):
            return False

    def authenticated() -> bool:
        return bool(session.get("portal_authenticated") is True and active())

    def verify_csrf(name: str, received: str | None) -> None:
        stored = session.get(name, "")
        if not stored or not received or not hmac.compare_digest(stored, received):
            abort(403)

    def check_origin() -> None:
        # Navegadores móveis / VPNs podem retirar o cabeçalho Origin de
        # formulários HTML. Ainda assim exigimos o CSRF aleatório da
        # sessão (verificado pelo chamador) e SameSite=Strict.
        # Se Origin ou Referer vierem presentes, devem corresponder ao host.
        # Cabeçalhos explicitamente divergentes nunca são aceitos.
        origin = request.headers.get("Origin") or request.headers.get("Referer")
        if not origin:
            return
        parsed = urlparse(origin)
        if parsed.netloc != request.host or (
            parsed.scheme != "https" and not testing
        ):
            abort(403)

    @app.after_request
    def security_headers(response):
        response.headers["Cache-Control"] = "no-store, private"
        response.headers["Pragma"] = "no-cache"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Content-Security-Policy"] = (
            "default-src 'none'; script-src 'self'; style-src 'self'; "
            "connect-src 'self'; img-src 'self' data:; "
            "base-uri 'none'; form-action 'self'; frame-ancestors 'none'"
        )
        return response

    @app.get("/health")
    def health():
        return jsonify(status="ready" if active() else "closed")

    @app.get("/")
    def index():
        if not active():
            return render_template("closed.html"), 410
        challenge = session.get("login_csrf") or secrets.token_urlsafe(25)
        session["login_csrf"] = challenge
        return render_template("unlock.html", csrf_token=challenge)

    @app.post("/unlock")
    def unlock():
        check_origin()
        verify_csrf("login_csrf", request.form.get("csrf_token"))
        code = request.form.get("code", "")
        if len(code) > 256:
            abort(403)
        with state_lock:
            state = get_state()
            if state["used"] or time.time() >= state["expires_at"]:
                return render_template("closed.html"), 410
            if state["failures"] >= MAX_FAILED_ATTEMPTS:
                return render_template("closed.html"), 429
            try:
                incoming_hash = hashlib.sha256(
                    bytes.fromhex(state["salt"]) + code.encode("utf-8")
                ).hexdigest()
                match = hmac.compare_digest(incoming_hash, state["code_hash"])
            except (ValueError, TypeError):
                match = False
            if not match:
                state["failures"] += 1
                save_state(state)
                return render_template("unlock.html", csrf_token=session["login_csrf"], error=True), 403
        session.clear()
        session["portal_authenticated"] = True
        session["post_csrf"] = secrets.token_urlsafe(25)
        return redirect(url_for("setup_page"), code=303)

    @app.get("/setup")
    def setup_page():
        if not authenticated():
            abort(403)
        return render_template("setup.html", csrf_token=session["post_csrf"])

    @app.get("/public-key")
    def public_key():
        if not authenticated():
            abort(403)
        private = serialization.load_pem_private_key(
            (root / PRIVATE_KEY_FILE).read_bytes(), password=None
        )
        pem = private.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode("ascii")
        return jsonify(publicKey=pem)

    @app.post("/submit")
    def submit():
        if not authenticated():
            abort(403)
        check_origin()
        verify_csrf("post_csrf", request.headers.get("X-CSRFToken"))
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict) or not isinstance(payload.get("encrypted"), str):
            return jsonify(error="Dados inválidos."), 400
        try:
            encrypted = base64.b64decode(payload["encrypted"], validate=True)
            private = serialization.load_pem_private_key(
                (root / PRIVATE_KEY_FILE).read_bytes(), password=None
            )
            plaintext = private.decrypt(
                encrypted,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None,
                ),
            ).decode("utf-8")
            if not 20 <= len(plaintext) <= 512 or any(c.isspace() for c in plaintext):
                raise ValueError("invalid input")
        except (ValueError, TypeError):
            return jsonify(error="A chave informada não pôde ser processada."), 400
        # A chave não é incluída em logs, respostas HTTP nem mensagens do chat.
        with state_lock:
            state = get_state()
            if state["used"] or time.time() >= state["expires_at"]:
                return jsonify(error="Acesso expirado."), 410
            try:
                store_gemini_api_key(root, plaintext)
            except CredentialVaultError:
                return jsonify(error="Cofre local indisponível."), 503
            state["used"] = True
            save_state(state)
        session.clear()
        session["completed"] = True
        return jsonify(saved=True, message="Chave recebida e armazenada com criptografia."), 201

    @app.get("/complete")
    def complete():
        if session.get("completed") is not True:
            abort(403)
        return render_template("complete.html")

    @app.errorhandler(403)
    def retry_access(exc):
        # Um pedido sem sessão válida não significa que o código expirou.
        return render_template("retry.html"), 403

    @app.errorhandler(404)
    @app.errorhandler(413)
    def generic_error(exc):
        return render_template("closed.html"), getattr(exc, "code", 403)

    return app


def create_from_env() -> Flask:
    path = os.environ.get("POTIGUAR_COPILOT_VAULT_DIR")
    if not path:
        raise RuntimeError("POTIGUAR_COPILOT_VAULT_DIR não configurado")
    return create_app(path)


app = create_from_env() if os.environ.get("POTIGUAR_PORTAL_BOOT") == "1" else None
