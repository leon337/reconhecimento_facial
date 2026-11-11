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
    explicit = current_app.config.get("COPILOT_GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if explicit:
        return str(explicit)
    vault_dir = os.environ.get("POTIGUAR_COPILOT_VAULT_DIR")
    if not vault_dir:
        return ""
    # O cofre é local; a chave é aberta apenas no servidor e nunca integra o HTML.
    from services.credential_portal.vault import CredentialVaultError, load_gemini_api_key
    try:
        return load_gemini_api_key(vault_dir) or ""
    except CredentialVaultError:
        current_app.logger.warning("copilot.vault.unavailable")
        return ""


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
    # Flask-WTF exige Referer de mesma origem em HTTPS para aceitar CSRF.
    # no-referrer bloquearia o POST do cliente Vue antes da chamada Gemini.
    # same-origin preserva o referenciador só dentro do nosso domínio.
    response = _no_cache(response)
    response.headers["Referrer-Policy"] = "same-origin"
    return response


@bp.get("/meta")
@permission_required(Permission.USERS_VIEW)
def metadata():
    user = g.admin_user
    return _no_cache(jsonify({
        "enabled": _available(),
        "configured": bool(_api_key()),
        "models": sorted(ALLOWED_MODELS),
        "can_create_user": user.can(Permission.USERS_CREATE),
        "can_create_with_ai": bool(
            _available()
            and current_app.config.get("COPILOT_ACTIONS_ENABLED", False)
            and user.can(Permission.USERS_CREATE)
        ),
        "demo_synthetic_only": bool(os.environ.get("POTIGUAR_COPILOT_DEMO_DAILY_LIMIT")),
        "links": {
            "users": url_for("admin.list_users"),
            "new_user": url_for("admin.new_user") if user.can(Permission.USERS_CREATE) else None,
        },
        "mode": "guidance_only",
    }))


@bp.post("/employee-create")
@permission_required(Permission.USERS_CREATE)
def employee_create():
    """Somente confirmação humana autenticada, nunca chamada direta do modelo."""
    if not _available() or not current_app.config.get("COPILOT_ACTIONS_ENABLED"):
        return _no_cache(jsonify(error="Cadastro assistido não habilitado.")), 503
    if not request.is_json:
        return _no_cache(jsonify(error="Envie JSON.")), 415
    if request.content_length is not None and request.content_length > 4096:
        return _no_cache(jsonify(error="Cadastro excede o tamanho permitido.")), 413
    from app.copilot.actions import (
        InvalidDraft, DuplicateEmployee, create_employee, validate_draft,
    )
    try:
        draft = validate_draft(request.get_json(silent=True))
    except InvalidDraft as exc:
        return _no_cache(jsonify(error=str(exc))), 400

    # HML exposta por túnel tem credenciais de teste compartilhadas:
    # exigir identificadores sintéticos para evitar dados reais no SQLite.
    if os.environ.get("POTIGUAR_COPILOT_DEMO_DAILY_LIMIT"):
        if not (
            (draft.name.lower().endswith(" de teste") or draft.name.lower().startswith("teste "))
            and (draft.username.endswith(".teste") or draft.username.startswith("teste."))
            and (draft.registration or "").upper().startswith("TEST-")
        ):
            return _no_cache(jsonify(
                error="Nesta homologação, use somente dados fictícios: nome terminando em 'de Teste', usuário terminado em '.teste' e matrícula 'TEST-...'."
            )), 400
        from app.copilot.demo_quota import (
            DemoQuotaReached, DemoQuotaUnavailable, reserve_session,
        )
        try:
            reserve_session(current_app.instance_path, 5, category="employee")
        except DemoQuotaReached:
            return _no_cache(jsonify(error="Limite diário de cadastros de teste atingido.")), 429
        except DemoQuotaUnavailable:
            return _no_cache(jsonify(error="Controle de cadastros indisponível.")), 503

    try:
        user, temporary_password = create_employee(
            draft, actor=g.admin_user,
            company_id=session.get("admin_company_id"),
            worksite_id=session.get("admin_worksite_id"),
        )
    except DuplicateEmployee as exc:
        return _no_cache(jsonify(error=str(exc))), 409
    return _no_cache(jsonify({
        "id": user.id,
        "username": user.username,
        "name": user.name,
        "temporary_password": temporary_password,
        "requires_biometric_enrollment": True,
        "message": "Cadastro criado após sua confirmação. A biometria permanece pendente.",
    })), 201


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

    # HML pública tem orçamento limitado de sessões por dia, atômico mesmo
    # com várias sessões/abas e persistente após reinício do processo.
    quota_setting = os.environ.get("POTIGUAR_COPILOT_DEMO_DAILY_LIMIT")
    if quota_setting:
        from app.copilot.demo_quota import (
            DemoQuotaReached, DemoQuotaUnavailable, reserve_session,
        )
        try:
            limit = int(quota_setting)
            if not 1 <= limit <= 100:
                raise ValueError("limite inválido")
            reserve_session(current_app.instance_path, limit)
        except DemoQuotaReached:
            return _no_cache(jsonify(error="Limite de conversas da demonstração atingido hoje.")), 429
        except (ValueError, DemoQuotaUnavailable):
            current_app.logger.warning("copilot.demo_quota.unavailable")
            return _no_cache(jsonify(error="Controle de uso da demonstração indisponível.")), 503

    try:
        token = provision_live_token(key, body["model"])
    except LiveProvisioningError:
        current_app.logger.warning("copilot.live.provision_failed")
        return _no_cache(jsonify(error="Não foi possível conectar ao serviço de voz.")), 502

    return _no_cache(jsonify(token=token, model=body["model"]))
