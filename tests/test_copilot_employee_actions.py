"""Regressão pytest: Copiloto só prepara rascunhos e não contorna onboarding V2."""
from uuid import uuid4
from cryptography.fernet import Fernet
from app.models import Employee, User, db
from app.onboarding_models import OnboardingDraft
from app.rbac import AccessRole


def login(app,client,role):
    app.config['ONBOARDING_FERNET_KEY']=Fernet.generate_key()
    username='copilot-draft-'+role
    with app.app_context():
        user=User(username=username,access_role=role)
        user.set_password('synthetic-test-password')
        db.session.add(user)
        db.session.commit()
    assert client.post('/admin/login',data={
        'username':username,'password':'synthetic-test-password'
    }).status_code==302


def body(**changes):
    data=dict(request_id=str(uuid4()),name='Maria de Teste',username='maria.teste',
              registration='TEST-101',job_title='Analista de Teste',schedule='08:00-17:00')
    data.update(changes)
    return data


def test_disabled_feature_prevents_draft(app,client):
    login(app,client,AccessRole.ADMIN.value)
    assert client.post('/admin/copilot/employee-draft',json=body()).status_code==503
    with app.app_context(): assert OnboardingDraft.query.count()==0


def test_legacy_create_is_retired_without_side_effects(app,client):
    login(app,client,AccessRole.ADMIN.value)
    app.config.update(COPILOT_ENABLED=True,COPILOT_ACTIONS_ENABLED=True)
    res=client.post('/admin/copilot/employee-create',json=body())
    assert res.status_code==410
    assert '/admin/users/new' in res.json['redirect']
    with app.app_context():
        assert Employee.query.count()==0
        assert OnboardingDraft.query.count()==0


def test_auditor_cannot_create_or_embed(app,client):
    login(app,client,AccessRole.AUDITOR.value)
    app.config.update(COPILOT_ENABLED=True,COPILOT_ACTIONS_ENABLED=True)
    assert client.post('/admin/copilot/employee-draft',json=body()).status_code==403
    assert client.get('/admin/copilot/embed/onboarding').status_code==403


def test_confirmed_copilot_action_creates_only_encrypted_v2_draft(app,client):
    login(app,client,AccessRole.ADMIN.value)
    app.config.update(COPILOT_ENABLED=True,COPILOT_ACTIONS_ENABLED=True)
    res=client.post('/admin/copilot/employee-draft',json=body())
    assert res.status_code==201,res.json
    assert res.json['created'] is False
    assert res.json['draft_created'] is True
    assert 'temporary_password' not in res.json
    assert '/admin/onboarding/' in res.json['redirect']
    with app.app_context():
        assert Employee.query.count()==0
        draft=OnboardingDraft.query.one()
        assert draft.status=='draft'
        assert 'Maria de Teste' not in draft.encrypted_payload
        assert User.query.filter_by(username='maria.teste').count()==0
    assert client.get(res.json['redirect']).status_code==200


def test_unapproved_fields_rejected(app,client):
    login(app,client,AccessRole.ADMIN.value)
    app.config.update(COPILOT_ENABLED=True,COPILOT_ACTIONS_ENABLED=True)
    for data in (body(access_role='admin'),body(company_id=999),body(username='Invalid User'),
                 body(name='X'),body(request_id='invalid-uuid')):
        assert client.post('/admin/copilot/employee-draft',json=data).status_code==422
    with app.app_context(): assert Employee.query.count()==0


def test_guests_redirected(client):
    assert client.post('/admin/copilot/employee-draft',json=body()).status_code==302


def test_demo_rejects_real_pii(app,client,monkeypatch):
    login(app,client,AccessRole.ADMIN.value)
    app.config.update(COPILOT_ENABLED=True,COPILOT_ACTIONS_ENABLED=True)
    monkeypatch.setenv('POTIGUAR_COPILOT_DEMO_DAILY_LIMIT','12')
    assert client.post('/admin/copilot/employee-draft',json=body(name='Nome Real',username='nome.real')).status_code==422
    with app.app_context(): assert Employee.query.count()==0


def test_embedded_copilot_same_origin_and_privacy_headers(app,client):
    login(app,client,AccessRole.ADMIN.value)
    app.config.update(COPILOT_ENABLED=True,COPILOT_ACTIONS_ENABLED=True)
    r=client.get('/admin/copilot/embed/onboarding')
    assert r.status_code==200
    assert r.headers['X-Frame-Options']=='SAMEORIGIN'
    assert "frame-ancestors 'self'" in r.headers['Content-Security-Policy']
    assert 'microphone=(self)' in r.headers['Permissions-Policy']
    assert r.headers['Referrer-Policy']=='same-origin'
