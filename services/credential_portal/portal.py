"""Portal de uso único sem cookies: formulário simples e chave cifrada no navegador.

Abre somente em 127.0.0.1 atrás de túnel HTTPS. Nenhuma chave é registrada
em logs, em texto simples no SQLite, na URL ou no repositório Git.
"""
from __future__ import annotations

import base64
import binascii
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
from flask import Flask, abort, jsonify, render_template, request
from itsdangerous import URLSafeTimedSerializer, BadSignature

from services.credential_portal.vault import (
    CredentialVaultError,
    _private_root,
    store_gemini_api_key,
)

MAX_FAILED_ATTEMPTS = 8


def create_app(private_directory: str, *, testing: bool = False) -> Flask:
    root = _private_root(private_directory)
    secret_file = root / "portal-session.key"
    if not secret_file.is_file():
        raise RuntimeError("portal não foi inicializado")

    app = Flask(__name__, template_folder="templates", static_folder="static",
                static_url_path="/assets")
    app.config.update(TESTING=testing, MAX_CONTENT_LENGTH=8192)
    state_lock = threading.Lock()
    form_signer = URLSafeTimedSerializer(
        secret_file.read_bytes(), salt="potiguar-single-page-form-v1"
    )

    def get_state() -> dict:
        path = root / "setup-access.json"
        if not path.is_file() or path.stat().st_mode & 0o077:
            raise RuntimeError("estado de acesso indisponível")
        return json.loads(path.read_text(encoding="utf-8"))

    def save_state(state: dict) -> None:
        path = root / "setup-access-tmp.json"
        fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(state, handle)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(path, root / "setup-access.json")

    def active() -> bool:
        try:
            state = get_state()
            return not state["used"] and time.time() < state["expires_at"]
        except (OSError, ValueError, KeyError, RuntimeError):
            return False

    def verify_origin() -> bool:
        for source in ("Origin", "Referer"):
            value = request.headers.get(source)
            if not value:
                continue
            parsed = urlparse(value)
            if parsed.netloc != request.host:
                return False
            if parsed.scheme != "https" and not testing:
                return False
        return True

    def verify_form(raw: str | None) -> bool:
        if not isinstance(raw, str) or len(raw) > 512:
            return False
        try:
            value = form_signer.loads(raw, max_age=600)
            return isinstance(value.get("nonce"), str)
        except (BadSignature, ValueError, TypeError, AttributeError):
            return False

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
            "form-action 'self'; base-uri 'none'; frame-ancestors 'none'"
        )
        return response

    @app.get("/health")
    def health():
        return jsonify(status="ready" if active() else "closed")

    @app.get("/")
    def index():
        if not active():
            return render_template("closed.html"), 410
        return render_template("unlock.html", csrf_token=form_signer.dumps({
            "nonce": secrets.token_urlsafe(22)
        }))

    @app.get("/public-key")
    def public_key():
        if not active():
            return jsonify(error="Este acesso não está disponível."), 410
        private = serialization.load_pem_private_key(
            (root / "transport-private.pem").read_bytes(), password=None
        )
        public = private.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        # A chave RSA aqui é PUBLICA: sozinha não dá acesso ao cofre.
        return jsonify(publicKey=public.decode("ascii"))

    @app.post("/submit-once")
    def submit_once():
        if not request.is_json:
            return jsonify(error="Reabra o formulário atualizado."), 415
        body = request.get_json(silent=True)
        if not isinstance(body, dict):
            return jsonify(error="Formulário inválido."), 400
        if not verify_origin() or not verify_form(body.get("challenge")):
            return jsonify(error="Sessão expirada. Reabra o portal."), 403

        code = body.get("code")
        cipher_text = body.get("encrypted")
        if not isinstance(code, str) or len(code) > 256:
            return jsonify(error="Código de acesso inválido."), 400
        if not isinstance(cipher_text, str) or len(cipher_text) > 4096:
            return jsonify(error="Chave API inválida."), 400

        with state_lock:
            state = get_state()
            if state["used"] or time.time() >= state["expires_at"]:
                return jsonify(error="Este acesso já foi usado ou expirou."), 410
            if state["failures"] >= MAX_FAILED_ATTEMPTS:
                return jsonify(error="Limite de tentativas atingido."), 429
            salt = bytes.fromhex(state["salt"])
            attempt = hashlib.sha256(salt + code.encode("utf-8")).hexdigest()
            if not hmac.compare_digest(attempt, state["code_hash"]):
                state["failures"] += 1
                save_state(state)
                return jsonify(error="Código temporário incorreto."), 403

            try:
                encrypted = base64.b64decode(cipher_text, validate=True)
                private = serialization.load_pem_private_key(
                    (root / "transport-private.pem").read_bytes(), password=None
                )
                key = private.decrypt(
                    encrypted,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None,
                    ),
                ).decode("utf-8")
                if not 20 <= len(key) <= 512 or any(c.isspace() for c in key):
                    raise ValueError("invalid key")
            except (ValueError, TypeError, binascii.Error):
                return jsonify(error="Chave API inválida. Confira e tente novamente."), 400
            try:
                store_gemini_api_key(root, key)
            except CredentialVaultError:
                return jsonify(error="Cofre indisponível. Tente novamente."), 503
            state["used"] = True
            save_state(state)
        return jsonify(saved=True, message="Chave recebida com segurança."), 201

    @app.post("/unlock")
    @app.post("/submit")
    def old_form():
        return jsonify(error="Formulário anterior desatualizado. Reabra o endereço do portal."), 409

    @app.get("/complete")
    def complete():
        if not get_state().get("used"):
            return render_template("closed.html"), 403
        return render_template("complete.html")

    @app.errorhandler(413)
    def too_large(_):
        return jsonify(error="Envio muito grande. Confira a chave."), 413

    return app


def create_from_env() -> Flask:
    path = os.environ.get("POTIGUAR_COPILOT_VAULT_DIR")
    if not path:
        raise RuntimeError("POTIGUAR_COPILOT_VAULT_DIR não configurado")
    return create_app(path)


app = create_from_env() if os.environ.get("POTIGUAR_PORTAL_BOOT") == "1" else None
