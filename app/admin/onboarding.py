"""Onboarding V2 operacional: rascunhos criptografados, escopo RBAC e conclusão atômica."""
import json
import os
import re
import secrets
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from cryptography.fernet import Fernet, InvalidToken
from flask import abort, current_app, g, jsonify, redirect, render_template, request, session, url_for
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError

from app.admin import bp
from app.admin.auth import permission_required
from app.models import db, Employee, User
from app.observability import audit
from app.onboarding_fields import STEPS, SENSITIVE_FIELDS, normalize
from app.onboarding_models import EmployeeOnboarding, OnboardingDraft
from app.rbac import Permission

MAX_ACTIVE_DRAFTS = 30


def _cipher():
    raw = current_app.config.get('ONBOARDING_FERNET_KEY') or os.environ.get('POTIGUAR_ONBOARDING_FERNET_KEY')
    if not raw:
        file = Path(current_app.root_path) / 'instance' / 'onboarding-fernet.key'
        if file.is_file():
            raw = file.read_bytes().strip()
    if not raw:
        abort(503, description='Cofre de cadastro indisponível')
    try:
        return Fernet(raw if isinstance(raw, bytes) else raw.encode('ascii'))
    except (ValueError, TypeError):
        abort(503, description='Cofre de cadastro inválido')


def _seal(payload):
    return _cipher().encrypt(json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode()).decode('ascii')


def _open(token):
    try:
        return json.loads(_cipher().decrypt(token.encode('ascii')))
    except (InvalidToken, ValueError, TypeError):
        abort(503, description='Rascunho indisponível')


def _draft_or_404(draft_id):
    if not re.fullmatch(r'[a-f0-9]{32}', draft_id):
        abort(404)
    draft = db.session.get(OnboardingDraft, draft_id)
    if not draft or draft.owner_user_id != g.admin_user.id:
        abort(404)
    if draft.company_id != session.get('admin_company_id') or draft.worksite_id != session.get('admin_worksite_id'):
        abort(404)
    return draft


def _validate(payload):
    errors = []
    name = payload['full_name'].strip()
    if len(name) < 3 or len(name) > 120:
        errors.append('Nome completo deve ter de 3 a 120 caracteres.')
    if not payload['relation_type']:
        errors.append('Tipo de relação obrigatório.')
    if not payload['country'] or not payload['address_type']:
        errors.append('País e tipo de endereço são obrigatórios.')
    if not payload['biometric_timing']:
        errors.append('Defina quando cadastrar a biometria.')
    cpf = re.sub(r'\D', '', payload['cpf'])
    if payload['cpf'] and (len(cpf) != 11 or len(set(cpf)) == 1 or any((sum(int(cpf[i]) * (length + 1 - i) for i in range(length)) * 10 % 11 % 10) != int(cpf[length]) for length in (9, 10))):
        errors.append('CPF inválido.')
    for name_key in ('birth_date','admission_date','intermittent_date','relation_start'):
        value = payload[name_key]
        if value:
            try:
                from datetime import date
                date.fromisoformat(value)
            except ValueError:
                errors.append('Data inválida: ' + name_key)
    if payload['personal_email'] and not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', payload['personal_email']):
        errors.append('E-mail pessoal inválido.')
    if payload['third_party_holder'] and (not payload['third_party_name'] or not payload['third_party_reason']):
        errors.append('Titularidade de terceiro exige nome e justificativa.')
    if any(payload.get(k) and payload[k] not in ('Não informado','Prefiro não informar') for k in SENSITIVE_FIELDS) and not payload['sensitive_data_ack']:
        errors.append('Confirme a necessidade e transparência antes de coletar dados sensíveis opcionais.')
    if payload['has_system_access']:
        if not payload['access_role'] or not payload['access_login']:
            errors.append('Para solicitar acesso, informe perfil e login.')
        if not re.fullmatch(r'[A-Za-z0-9_.@+\-]{3,80}', payload['access_login']):
            errors.append('Login solicitado inválido.')
    if payload['biometric_timing'] == 'Agora' and not payload['biometric_notice_ack']:
        errors.append('Apresente o aviso de transparência antes do cadastro facial.')
    return errors


def _http_response(payload, code=200):
    res = jsonify(payload)
    res.status_code = code
    res.headers['Cache-Control'] = 'private, no-store'
    return res


@bp.get('/onboarding/drafts')
@permission_required(Permission.USERS_CREATE)
def onboarding_drafts():
    drafts = OnboardingDraft.query.filter_by(
        owner_user_id=g.admin_user.id,
        company_id=session.get('admin_company_id'),
        worksite_id=session.get('admin_worksite_id'),
        status='draft',
    ).order_by(OnboardingDraft.updated_at.desc()).limit(30).all()
    from flask import make_response
    response = make_response(render_template('admin/onboarding_drafts.html', drafts=drafts))
    response.headers['Cache-Control'] = 'private, no-store'
    return response


@bp.get('/onboarding/new')
@permission_required(Permission.USERS_CREATE)
def onboarding_new():
    active = OnboardingDraft.query.filter_by(owner_user_id=g.admin_user.id, status='draft').count()
    if active >= MAX_ACTIVE_DRAFTS:
        abort(429, 'Limite de rascunhos atingido; conclua ou descarte um existente.')
    draft = OnboardingDraft(
        id=uuid4().hex, owner_user_id=g.admin_user.id,
        company_id=session.get('admin_company_id'),
        worksite_id=session.get('admin_worksite_id'),
        encrypted_payload=_seal({}), version=0, status='draft',
    )
    db.session.add(draft)
    audit('admin.onboarding.draft_created', 'success', actor=g.admin_user, target_type='onboarding_draft', target_id=draft.id)
    db.session.commit()
    return redirect(url_for('admin.onboarding_form', draft_id=draft.id))


@bp.get('/onboarding/<draft_id>')
@permission_required(Permission.USERS_CREATE)
def onboarding_form(draft_id):
    draft = _draft_or_404(draft_id)
    if draft.status == 'submitted':
        return redirect(url_for('admin.list_users'))
    if draft.status != 'draft':
        abort(409)
    response = render_template('admin/users_new_v2.html', draft=draft, steps=STEPS, saved=_open(draft.encrypted_payload))
    from flask import make_response
    response = make_response(response)
    response.headers['Cache-Control'] = 'no-store, private'
    response.headers['Permissions-Policy'] = 'microphone=(self), camera=()'
    return response


@bp.post('/onboarding/<draft_id>/save')
@permission_required(Permission.USERS_CREATE)
def onboarding_save(draft_id):
    draft = _draft_or_404(draft_id)
    body = request.get_json(silent=True)
    if not isinstance(body, dict) or type(body.get('version')) is not int or not isinstance(body.get('fields'), dict):
        return _http_response({'error': 'dados_invalidos'}, 400)
    try:
        cleaned = normalize(body['fields'])
    except ValueError as e:
        return _http_response({'error': str(e)}, 422)
    version = body['version']
    if version < 0 or version > 100000:
        return _http_response({'error': 'versao_invalida'}, 400)
    rows = db.session.execute(
        update(OnboardingDraft).where(
            OnboardingDraft.id == draft.id,
            OnboardingDraft.version == version,
            OnboardingDraft.status == 'draft',
        ).values(encrypted_payload=_seal(cleaned), version=version + 1, updated_at=datetime.utcnow())
    ).rowcount
    if rows != 1:
        db.session.rollback()
        return _http_response({'error': 'conflito_de_versao'}, 409)
    db.session.commit()
    return _http_response({'saved': True, 'version': version + 1})


@bp.post('/onboarding/<draft_id>/complete')
@permission_required(Permission.USERS_CREATE)
def onboarding_complete(draft_id):
    draft = _draft_or_404(draft_id)
    if draft.status == 'submitted' and draft.employee_id:
        return _http_response({'created': True, 'employee_id': draft.employee_id, 'redirect': url_for('admin.list_users')})
    body = request.get_json(silent=True)
    if not isinstance(body, dict) or type(body.get('version')) is not int:
        return _http_response({'error': 'versao_obrigatoria'}, 400)
    if body['version'] != draft.version or draft.status != 'draft':
        return _http_response({'error': 'conflito_de_versao'}, 409)
    try:
        payload = normalize(_open(draft.encrypted_payload))
    except ValueError:
        return _http_response({'error': 'rascunho_invalido'}, 422)
    errors = _validate(payload)
    if errors:
        return _http_response({'error': 'validacao', 'messages': errors}, 422)
    if payload['has_system_access'] and User.query.filter_by(username=payload['access_login']).first():
        return _http_response({'error': 'login_em_uso'}, 409)
    reserved = db.session.execute(
        update(OnboardingDraft).where(
            OnboardingDraft.id == draft.id,
            OnboardingDraft.status == 'draft', OnboardingDraft.version == body['version'],
        ).values(status='processing', updated_at=datetime.utcnow())
    ).rowcount
    if reserved != 1:
        db.session.rollback()
        return _http_response({'error': 'conflito_de_submissao'}, 409)
    employee = Employee(
        company_id=draft.company_id, worksite_id=draft.worksite_id,
        name=payload['full_name'],
        job_title=payload['job_role'][:80],
        schedule=payload['schedule'][:120],
        address=payload['street'][:200] or payload['rural_locality'][:200] or payload['foreign_street'][:200],
        pass_type=payload['relation_type'][:50], active=True,
    )
    try:
        db.session.add(employee)
        db.session.flush()
        employee.registration = f'PF-{employee.id:08d}'
        login = payload['access_login'] if payload['has_system_access'] else f'funcionario.{uuid4().hex[:20]}'
        user = User(
            username=login, name=employee.name, registration=employee.registration,
            employee=employee, role=None, schedule=employee.schedule,
            address=employee.address, pass_type=employee.pass_type,
            company_id=draft.company_id, worksite_id=draft.worksite_id,
            access_role=None,  # Nenhuma conta administrativa ativa sem convite/credencial.
        )
        user.set_password(secrets.token_urlsafe(48))
        db.session.add(user)
        db.session.add(EmployeeOnboarding(
            employee_id=employee.id, company_id=draft.company_id,
            worksite_id=draft.worksite_id, encrypted_payload=_seal(payload),
            created_by=g.admin_user.id,
        ))
        db.session.execute(update(OnboardingDraft).where(OnboardingDraft.id == draft.id).values(
            employee_id=employee.id, status='submitted', updated_at=datetime.utcnow(),
        ))
        audit('admin.onboarding.completed', 'success', actor=g.admin_user,
              target_type='employee', target_id=employee.id,
              metadata={'access_requested': payload['has_system_access'],
                        'biometric_pending': True})
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return _http_response({'error': 'conflito_de_identidade'}, 409)
    redirect_to = (url_for('admin.biometric_form', user_id=user.id)
                   if payload['biometric_timing'] == 'Agora' and g.admin_user.can(Permission.BIOMETRICS_MANAGE)
                   else url_for('admin.list_users'))
    return _http_response({'created': True, 'employee_id': employee.id, 'redirect': redirect_to})


@bp.post('/onboarding/<draft_id>/discard')
@permission_required(Permission.USERS_CREATE)
def onboarding_discard(draft_id):
    draft = _draft_or_404(draft_id)
    if draft.status != 'draft':
        return _http_response({'error': 'rascunho_nao_editavel'}, 409)
    db.session.delete(draft)
    audit('admin.onboarding.draft_discarded','success', actor=g.admin_user,
          target_type='onboarding_draft', target_id=draft.id)
    db.session.commit()
    return _http_response({'discarded': True, 'redirect': url_for('admin.list_users')})
