"""Provas do acesso direto público sem enfraquecer os ambientes convencionais."""
import os
import unittest
from unittest.mock import patch
from cryptography.fernet import Fernet
from main import create_app
from app.models import db, Company, User, Employee
from app.onboarding_models import OnboardingDraft
from app.public_demo import install_public_demo


class PublicDemoUnitTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {
            'POTIGUAR_PUBLIC_DEMO': '1',
            'APP_ENV': 'development',
        })
        self.env.start()
        self.app = create_app({
            'TESTING': True,
            'SECRET_KEY': 'isolated-synthetic-demo-test-key',
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'AUTO_CREATE_SCHEMA': True,
            'WTF_CSRF_ENABLED': False,
            'SESSION_COOKIE_SECURE': True,
            'COPILOT_ENABLED': True,
            'COPILOT_ACTIONS_ENABLED': True,
            'ONBOARDING_FERNET_KEY': Fernet.generate_key(),
        })
        install_public_demo(self.app)
        self.client = self.app.test_client()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
        self.env.stop()

    def test_direct_entry_without_login_and_advertises_demo(self):
        self.assertEqual(self.client.get('/admin/login').location, '/admin/copilot')
        home = self.client.get('/')
        self.assertEqual(home.status_code, 302)
        shell = self.client.get('/admin/copilot')
        self.assertEqual(shell.status_code, 200)
        self.assertEqual(shell.headers['X-Potiguar-Demo'], 'synthetic-no-login')
        self.assertIn('noindex', shell.headers['X-Robots-Tag'])
        self.assertIn("frame-src 'self'", shell.headers['Content-Security-Policy'])
        meta = self.client.get('/admin/copilot/meta')
        self.assertTrue(meta.json['public_demo_no_login'])
        self.assertTrue(meta.json['can_create_with_ai'])
        self.assertTrue(meta.json['links']['drafts'])
        self.assertEqual(self.client.get('/admin/dashboard').status_code, 200)
        self.assertEqual(self.client.get('/admin/relatorios').status_code, 200)
        self.assertEqual(self.client.get('/admin/users').status_code, 200)
        with self.app.app_context():
            self.assertEqual(Company.query.count(), 1)
            principal = User.query.one()
            self.assertEqual(principal.access_role, 'manager')
            self.assertTrue(principal.username.startswith('demo.'))

    def test_private_isolation_of_two_independent_visitors(self):
        other = self.app.test_client()
        self.assertEqual(self.client.get('/admin/copilot').status_code, 200)
        self.assertEqual(other.get('/admin/copilot').status_code, 200)
        with self.client.session_transaction() as a:
            first = a['public_demo_user_id']
        with other.session_transaction() as a:
            second = a['public_demo_user_id']
        self.assertNotEqual(first, second)
        with self.app.app_context():
            self.assertNotEqual(db.session.get(User, first).company_id,
                                db.session.get(User, second).company_id)
        with self.app.app_context():
            other_username = db.session.get(User, second).username
            first_username = db.session.get(User, first).username
        page = other.get('/admin/users').text
        self.assertIn(other_username, page)
        self.assertNotIn(first_username, page)
        self.assertEqual(self.client.get('/admin/copilot/meta').status_code, 200)

    def test_draft_allowed_but_real_actions_are_denied(self):
        self.assertEqual(self.client.get('/admin/copilot').status_code, 200)
        draft = self.client.get('/admin/onboarding/new')
        self.assertEqual(draft.status_code, 302)
        self.assertEqual(self.client.get(draft.location).status_code, 200)
        self.assertEqual(self.client.get('/admin/onboarding/drafts').status_code, 200)
        fields = {'relation_type':'CLT intermitente','full_name':'Pessoa de Teste',
                  'country':'Brasil','address_type':'Urbano'}
        row = self.client.post(draft.location + '/save',json={'version':0,'fields':fields})
        self.assertEqual(row.status_code, 200, row.json)
        self.assertEqual(row.json['version'],1)
        self.assertEqual(self.client.post(draft.location + '/complete',json={'version':1}).status_code,403)
        self.assertEqual(self.client.post('/admin/users',data={'username':'bad'}).status_code,403)
        self.assertEqual(self.client.get('/admin/users/1/biometric').status_code,403)
        self.assertEqual(self.client.post('/admin/logout').status_code,403)
        self.assertEqual(self.client.get('/admin/login').status_code,302)
        self.assertEqual(self.client.get('/static/copilot/app.js').status_code,200)
        self.assertEqual(self.client.get('/static/copilot/pcm-worklet.js').status_code,200)
        self.assertEqual(self.client.get('/static/uploads/something.jpg').status_code,403)
        self.assertEqual(self.client.get('/static/biometric_capture.js').status_code,403)
        with self.app.app_context():
            self.assertEqual(Employee.query.count(),0)
            self.assertEqual(OnboardingDraft.query.count(),1)

    def test_sensitive_or_non_synthetic_values_denied_even_with_valid_version(self):
        self.client.get('/admin/copilot')
        draft = self.client.get('/admin/onboarding/new').location
        for fields in (
            {'relation_type':'CLT comum','full_name':'Pessoa Real'},
            {'cpf':'52998224725'},
            {'phone':'81900000000'},
            {'bank':'Banco de Teste'},
            {'pix_key':'123'},
            {'has_system_access':True},
            {'biometric_notice_ack':True},
        ):
            response = self.client.post(draft+'/save',json={'version':0,'fields':fields})
            self.assertEqual(response.status_code,422,fields)
        with self.app.app_context():
            self.assertEqual(OnboardingDraft.query.one().version,0)

    def test_regular_application_keeps_authentication(self):
        ordinary = create_app({
            'TESTING':True,
            'SECRET_KEY':'private-app',
            'SQLALCHEMY_DATABASE_URI':'sqlite:///:memory:',
            'AUTO_CREATE_SCHEMA':True,
            'WTF_CSRF_ENABLED':False,
        })
        auth = ordinary.test_client().get('/admin/copilot')
        self.assertEqual(auth.status_code,302)
        self.assertIn('/admin/login', auth.location)
