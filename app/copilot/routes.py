"""Apenas guia conversacional — sem ferramentas de escrita de ponto ou biometria."""

import os
import time

from flask import current_app, g, jsonify, make_response, render_template, request, session, url_for
from flask_wtf.csrf import generate_csrf

from app.admin.auth import permission_required
from app.copilot import bp
from app.copilot.live import ALLOWED_MODELS, LiveProvisioningError, provision_live_token
from app.rbac import Permission


def _available() -> bool:
    return bool(current_app.config.get("COPILOT_ENABLED", False))


def _api_key() -> str:
    return str(current_app.config.get("COPILOT_GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY") or "")


def _no_cache(response):
    response.headers["Cache-Control"] = "no-store, private"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@bp.get("")
@permission_required(Permission.USERS_VIEW)
def workspace():
    response = make_response(render_template("admin/copilot.html", csrf_value=generate_csrf()))
    response.headers["Permissions-Policy"] = "microphone=(self), camera=()"
    # Restrito ao shell; áudio e tokens permanecem em memória do navegador.
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self'; style-src 'self'; "
        "connect-src 'self' https://generativelanguage.googleapis.com "
        "wss://generativelanguage.googleapis.com; "
        "img-src 'self' data:; media-src 'self' blob:; worker-src 'self'; "
        "object-src 'none'; base-uri 'self'; frame-ancestors 'none'"
    )
    return _no_cache(response)


@bp.get("/meta")
@permission_required(Permission.USERS_VIEW)
def metadata():
    user = g.admin_user
    return _no_cache(jsonify({
        "enabled": _available(),
        "configured": bool(_api_key()),
        "models": sorted(ALLOWED_MODELS),
        "can_create_user": user.can(Permission.USERS_CREATE),
        "links": {
            "users": url_for("admin.list_users"),
            "new_user": url_for("admin.new_user") if user.can(Permission.USERS_CREATE) else None,
        },
        "mode": "guidance_only",
    }))


@bp.post("/session-token")
@permission_required(Permission.USERS_VIEW)
def session_token():
    """Autenticado, sujeito ao CSRF global; sem acesso a usuários ou ponto."""
    if not _available():
        return _no_cache(jsonify(error="Copiloto não habilitado.")), 503
    key = _api_key()
    if not key:
        return _no_cache(jsonify(error="Serviço de IA não configurado.")), 503
    if not request.is_json:
        return _no_cache(jsonify(error="Envie JSON.")), 415
    body = request.get_json(silent=True)
    if not isinstance(body, dict) or body.get("model") not in ALLOWED_MODELS:
        return _no_cache(jsonify(error="Modelo indisponível.")), 400

    now = time.time()
    if now - float(session.get("copilot_last_token_at", 0)) < 15:
        return _no_cache(jsonify(error="Aguarde antes de iniciar outra sessão.")), 429
    # Reserva o intervalo antes da operação externa para evitar tentativas em rajada.
    session["copilot_last_token_at"] = now
    try:
        token = provision_live_token(key, body["model"])
    except LiveProvisioningError:
        current_app.logger.warning("copilot.live.provision_failed")
        return _no_cache(jsonify(error="Não foi possível conectar ao serviço de voz.")), 502

    return _no_cache(jsonify(token=token, model=body["model"]))
