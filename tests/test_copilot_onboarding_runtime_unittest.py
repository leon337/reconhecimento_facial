"""Regressão do Copiloto V2: sem rede, sem funcionários reais e sem senhas expostas."""
import unittest
from uuid import uuid4
from cryptography.fernet import Fernet
from main import create_app
from app.models import db,User,Employee,Company,Worksite
from app.onboarding_models import OnboardingDraft
from app.rbac import AccessRole

class CopilotOnboardingTests(unittest.TestCase):
 def setUp(self):
  self.app=create_app({'TESTING':True,'SECRET_KEY':'synthetic-test-only',
   'SQLALCHEMY_DATABASE_URI':'sqlite:///:memory:','AUTO_CREATE_SCHEMA':True,
   'WTF_CSRF_ENABLED':False,'COPILOT_ENABLED':True,'COPILOT_ACTIONS_ENABLED':True,
   'ONBOARDING_FERNET_KEY':Fernet.generate_key()})
  self.client=self.app.test_client()
  with self.app.app_context():
   a=User(username='admin-test',access_role=AccessRole.ADMIN.value);a.set_password('synthetic')
   u=User(username='auditor-test',access_role=AccessRole.AUDITOR.value);u.set_password('synthetic')
   c=Company(name='Empresa de Teste',slug='empresa-de-teste')
   w=Worksite(name='Obra de Teste',company=c)
   m=User(username='gestor-test',access_role=AccessRole.MANAGER.value,company=c,worksite=w);m.set_password('synthetic')
   db.session.add_all([a,u,c,w,m]);db.session.commit()
   self.admin,self.auditor,self.manager=a.id,u.id,m.id
   self.company,self.worksite=c.id,w.id
  self.login(self.admin)
 def login(self,user,company=None,worksite=None):
  with self.client.session_transaction() as s:
   s['admin_user_id']=user;s['admin_company_id']=company;s['admin_worksite_id']=worksite
 def payload(self,**kw):
  d=dict(request_id=str(uuid4()),name='Maria de Teste',username='maria.teste',
   registration='TEST-001',job_title='Analista de Teste',schedule='08:00-17:00')
  d.update(kw);return d
 def test_legacy_write_blocked(self):
  r=self.client.post('/admin/copilot/employee-create',json=self.payload())
  self.assertEqual(r.status_code,410)
  with self.app.app_context():
   self.assertEqual(Employee.query.count(),0)
   self.assertEqual(OnboardingDraft.query.count(),0)
 def test_copilot_prepares_only_encrypted_draft(self):
  r=self.client.post('/admin/copilot/employee-draft',json=self.payload())
  self.assertEqual(r.status_code,201,r.get_json())
  self.assertFalse(r.json['created'])
  self.assertTrue(r.json['draft_created'])
  self.assertNotIn('temporary_password',r.json)
  with self.app.app_context():
   d=OnboardingDraft.query.one()
   self.assertEqual(d.status,'draft')
   self.assertNotIn('Maria de Teste',d.encrypted_payload)
   self.assertNotIn('maria.teste',d.encrypted_payload)
   self.assertEqual(Employee.query.count(),0)
  wizard=self.client.get(r.json['redirect'])
  self.assertEqual(wizard.status_code,200)
  self.assertIn('✦ Abrir Copiloto',wizard.get_data(as_text=True))
 def test_rejects_unapproved_fields_and_auditor(self):
  self.assertEqual(self.client.post('/admin/copilot/employee-draft',json=self.payload(access_role='admin')).status_code,422)
  self.login(self.auditor)
  self.assertEqual(self.client.post('/admin/copilot/employee-draft',json=self.payload()).status_code,403)
  self.assertEqual(self.client.get('/admin/copilot/embed/onboarding').status_code,403)
 def test_scoped_draft_not_employee(self):
  self.login(self.manager,self.company,self.worksite)
  r=self.client.post('/admin/copilot/employee-draft',json=self.payload())
  self.assertEqual(r.status_code,201,r.get_json())
  with self.app.app_context():
   d=OnboardingDraft.query.one()
   self.assertEqual(d.company_id,self.company)
   self.assertEqual(d.worksite_id,self.worksite)
   self.assertEqual(Employee.query.count(),0)
  self.login(self.admin)
  self.assertEqual(self.client.get(r.json['redirect']).status_code,404)
 def test_iframe_security_and_microphone(self):
  r=self.client.get('/admin/copilot/embed/onboarding')
  self.assertEqual(r.status_code,200)
  self.assertEqual(r.headers.get('X-Frame-Options'),'SAMEORIGIN')
  self.assertIn("frame-ancestors 'self'",r.headers.get('Content-Security-Policy',''))
  self.assertEqual(r.headers.get('Referrer-Policy'),'same-origin')
  self.assertIn('microphone=(self)',r.headers.get('Permissions-Policy',''))
  self.assertIn('data-embed="onboarding"',r.get_data(as_text=True))
  new=self.client.get('/admin/onboarding/new')
  page=self.client.get(new.location)
  self.assertEqual(page.status_code,200)
  self.assertIn('microphone=(self)',page.headers.get('Permissions-Policy',''))
  self.assertIn('onboarding-copilot-drawer',page.get_data(as_text=True))
 def test_disabled_and_csrf(self):
  self.app.config['COPILOT_ACTIONS_ENABLED']=False
  self.assertEqual(self.client.post('/admin/copilot/employee-draft',json=self.payload()).status_code,503)
  self.app.config['COPILOT_ACTIONS_ENABLED']=True
  self.app.config['WTF_CSRF_ENABLED']=True
  self.assertEqual(self.client.post('/admin/copilot/employee-draft',json=self.payload()).status_code,400)
if __name__=='__main__':unittest.main(verbosity=2)
