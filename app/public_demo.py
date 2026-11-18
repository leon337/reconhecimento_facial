"""Acesso direto somente na demonstração descartável e segregada da Potiguar.

Este módulo NÃO é instalado pelo aplicativo padrão (main:app). O entrypoint
isolado demo_entry:app precisa chamar install_public_demo explicitamente.
Nenhuma credencial administrativa real é consultada.
"""
import os
import secrets
from uuid import uuid4

from flask import abort, jsonify, redirect, request, session, url_for


from app.models import Company, User, Worksite, db
from app.rbac import AccessRole

GET_ENDPOINTS = frozenset({
    'home', 'admin.login',
    'admin.dashboard', 'admin.history', 'admin.reports',
    'admin.list_users', 'admin.new_user',
    'admin.onboarding_new', 'admin.onboarding_drafts', 'admin.onboarding_form',
    'copilot.workspace', 'copilot.metadata', 'copilot.session_csrf_token',
    'copilot.onboarding_embed',
})
STATIC_ALLOWLIST = frozenset({
    '/static/copilot/app.js', '/static/copilot/style.css',
    '/static/copilot/pcm-worklet.js',
    '/static/admin-mobile.css', '/static/admin-dashboard.css',
    '/static/admin-onboarding-v2.css', '/static/admin-onboarding-v2.js',
    '/static/admin-onboarding-controller.js',
})
POST_ENDPOINTS = frozenset({
    'copilot.session_token', 'copilot.employee_draft', 'copilot.text_turn',
    'admin.onboarding_save', 'admin.onboarding_discard',
})
# Valores opcionais fora desta lista ficam em branco na demo; nunca são
# persistidos CPF, telefone, endereço detalhado, dados financeiros ou biometria.
SYNTHETIC_FIELDS = frozenset({
    'relation_type', 'other_relation', 'full_name', 'social_name',
    'nationality', 'education', 'country', 'address_type',
    'city', 'state', 'department', 'job_role', 'manager',
    'schedule', 'contract_type', 'transport_benefit',
    'benefit_policy', 'biometric_timing',
})


def _synthetic_name(text):
    normalized = str(text).strip().casefold()
    return bool(normalized and (
        normalized.startswith('teste ') or
        normalized.endswith(' de teste') or
        normalized.endswith(' sintético') or
        normalized.endswith(' sintetico')
    ))


def install_public_demo(app):
    """Instala o modo sem login exclusivamente em instância sintética dedicada."""
    if os.environ.get('POTIGUAR_PUBLIC_DEMO') != '1':
        raise RuntimeError('Public demo flag not explicitly enabled')
    if os.environ.get('APP_ENV', '').lower() != 'development':
        raise RuntimeError('Public demo cannot run in production or pilot')
    if not app.config.get('COPILOT_ENABLED') or not app.config.get('COPILOT_ACTIONS_ENABLED'):
        raise RuntimeError('Public demo requires explicitly configured copilot')
    if not app.config.get('SESSION_COOKIE_SECURE'):
        raise RuntimeError('Public demo requires secure session cookies')
    uri = str(app.config.get('SQLALCHEMY_DATABASE_URI', ''))
    if not app.config.get('TESTING') and uri != 'sqlite:////app/instance/ponto.db':
        raise RuntimeError('Public demo must use the isolated SQLite database')
    app.config['PUBLIC_DEMO_MODE'] = True

    @app.before_request
    def demo_session_and_policy():
        if request.endpoint == 'static':
            if request.path not in STATIC_ALLOWLIST:
                abort(403)  # nunca servir uploads, biometria ou outros arquivos do disco
            return None
        if request.method == 'GET':
            if request.endpoint not in GET_ENDPOINTS:
                abort(403)
        elif request.method == 'POST':
            if request.endpoint not in POST_ENDPOINTS:
                abort(403)
        else:
            abort(405)

        # URL legado de login é apenas um atalho para o Copiloto;
        # não há formulário de credenciais nesta implantação.
        if request.endpoint in ('home', 'admin.login'):
            return redirect(url_for('copilot.workspace'), code=302)

        # A identidade sintética é segregada por cookie/sessão, empresa e obra.
        # Não existe senha pública, nem conta com role admin/super_admin.
        existing_id = session.get('public_demo_user_id')
        if existing_id:
            existing = db.session.get(User, existing_id)
            if existing and existing.access_role == AccessRole.MANAGER.value \
                    and existing.username.startswith('demo.'):
                if session.get('admin_user_id') != existing.id:
                    session['admin_user_id'] = existing.id
                return _validate_demo_save()

        # Não se aceita um admin_user_id trazido de outra instalação.
        session.clear()
        if Company.query.filter(Company.slug.like('demo-%')).count() >= 180:
            return jsonify(error='Limite de sessões de demonstração atingido.'), 429

        uid = uuid4().hex[:16]
        company = Company(name='Potiguar — Ambiente Sintético', slug='demo-' + uid)
        worksite = Worksite(company=company, name='Ambiente de Teste', code='DEMO')
        user = User(
            username='demo.' + uid,
            name='Operador Sintético de Teste',
            access_role=AccessRole.MANAGER.value,
            company=company, worksite=worksite,
        )
        user.set_password(secrets.token_urlsafe(48))  # senha inacessível e não utilizada
        db.session.add_all((company, worksite, user))
        db.session.commit()

        session.permanent = True
        session['public_demo_user_id'] = user.id
        session['admin_user_id'] = user.id
        session['admin_company_id'] = company.id
        session['admin_worksite_id'] = worksite.id
        return _validate_demo_save()

    @app.after_request
    def demo_security_headers(response):
        # Identifica respostas da demo para auditoria sem vazar identificadores.
        response.headers['X-Potiguar-Demo'] = 'synthetic-no-login'
        response.headers['X-Robots-Tag'] = 'noindex, nofollow, noarchive'
        response.headers.setdefault('Referrer-Policy', 'same-origin')
        if response.mimetype == 'text/html':
            response.headers['Cache-Control'] = 'no-store'
        return response


def _validate_demo_save():
    if request.endpoint != 'admin.onboarding_save':
        return None
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict) or not isinstance(payload.get('fields'), dict):
        return jsonify(error='dados_invalidos'), 400
    fields = payload['fields']
    if any(name not in SYNTHETIC_FIELDS and value not in ('', None, False)
           for name, value in fields.items()):
        return jsonify(error='Dados pessoais, bancários e biométricos são bloqueados na demo pública.'), 422
    for name in ('full_name', 'social_name'):
        if fields.get(name) and not _synthetic_name(fields[name]):
            return jsonify(error='Use nomes fictícios começando por Teste ou terminando em de Teste.'), 422
    return None
