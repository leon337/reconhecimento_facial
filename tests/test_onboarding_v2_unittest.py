"""Regressão do onboarding V2 com banco em memória e dados totalmente fictícios."""
import json
import unittest
from cryptography.fernet import Fernet
from main import create_app
from app.models import db, User, Employee, Company, Worksite
from app.onboarding_models import EmployeeOnboarding, OnboardingDraft
from app.rbac import AccessRole, Permission
from app.onboarding_fields import FIELD_MAP


class OnboardingV2Tests(unittest.TestCase):
    def setUp(self):
        self.app = create_app({
            'TESTING': True, 'SECRET_KEY':'fake-synthetic-test-only',
            'SQLALCHEMY_DATABASE_URI':'sqlite:///:memory:',
            'WTF_CSRF_ENABLED':False, 'AUTO_CREATE_SCHEMA':True,
            'ONBOARDING_FERNET_KEY':Fernet.generate_key(),
        })
        self.client = self.app.test_client()
        with self.app.app_context():
            admin=User(username='admin-test',name='Administrador de Testes',access_role=AccessRole.ADMIN.value)
            admin.set_password('synthetic-test-password')
            other=Company(name='Empresa B',slug='empresa-b')
            other_manager=User(username='manager-b',name='Gestor B',access_role=AccessRole.MANAGER.value,company=other)
            other_manager.set_password('synthetic-test-password')
            auditor=User(username='audit-test',name='Auditor',access_role=AccessRole.AUDITOR.value)
            auditor.set_password('synthetic-test-password')
            db.session.add_all([admin,other_manager,auditor]); db.session.commit()
            self.admin_id=admin.id
            self.manager_id=other_manager.id
            self.auditor_id=auditor.id
            self.manager_company_id=other.id

    def login(self,user_id=None,company_id=None):
        with self.client.session_transaction() as s:
            s['admin_user_id']=user_id or self.admin_id
            s['admin_company_id']=company_id
            s['admin_worksite_id']=None

    def draft(self):
        r=self.client.get('/admin/users/new')
        self.assertEqual(r.status_code,302)
        self.assertIn('/admin/onboarding/new',r.location)
        created=self.client.get(r.location)
        self.assertEqual(created.status_code,302)
        path=created.location
        self.assertRegex(path,r'/admin/onboarding/[a-f0-9]{32}')
        return path

    def valid_payload(self):
        payload={name:False if f.kind=='checkbox' else '' for name,f in FIELD_MAP.items()}
        payload.update(relation_type='CLT comum',full_name='Funcionário Sintético de Teste',
                       country='Brasil',address_type='Urbano',biometric_timing='Depois',
                       cpf='',job_role='Analista',street='Rua Fictícia 123',
                       payment_method='PIX',pix_key='fake-nonexistent-key')
        return payload

    def save(self,path,payload,version=0):
        return self.client.post(path+'/save',json={'version':version,'fields':payload})

    def test_no_auth_no_creating_draft(self):
        self.assertEqual(self.client.get('/admin/users/new').status_code,302)
        self.assertEqual(self.client.get('/admin/onboarding/new').status_code,302)
        self.login(self.auditor_id)
        self.assertEqual(self.client.get('/admin/users/new').status_code,403)
        self.assertEqual(self.client.get('/admin/onboarding/new').status_code,403)

    def test_eight_step_form_and_secret_draft(self):
        self.login();path=self.draft();page=self.client.get(path)
        self.assertEqual(page.status_code,200)
        body=page.get_data(as_text=True)
        self.assertIn('ETAPA 8 DE 8',body)
        self.assertIn('Dados pessoais',body)
        self.assertIn('Pagamento',body)
        self.assertIn('Biometria',body)
        self.assertIn('Revisão',body)
        self.assertIn('no-store',page.headers['Cache-Control'])
        with self.app.app_context():
            row=OnboardingDraft.query.one()
            self.assertNotIn('full_name',row.encrypted_payload)
            self.assertEqual(row.status,'draft')
            self.assertEqual(Employee.query.count(),0)

    def test_save_encrypted_and_reload(self):
        self.login();path=self.draft()
        data=self.valid_payload()
        result=self.save(path,data)
        self.assertEqual(result.status_code,200,result.get_json())
        self.assertEqual(result.json['version'],1)
        with self.app.app_context():
            row=OnboardingDraft.query.one()
            self.assertNotIn(data['full_name'],row.encrypted_payload)
            self.assertNotIn('fake-nonexistent-key',row.encrypted_payload)
            self.assertEqual(Employee.query.count(),0)
        self.assertIn('Funcionário Sintético de Teste',self.client.get(path).get_data(as_text=True))
        self.assertEqual(self.save(path,data,version=0).status_code,409)
        self.assertEqual(self.save(path,{**data,'not_allowed':'hack'},version=1).status_code,422)
        self.assertEqual(self.save(path,{**data,'access_role':'super_admin'},version=1).status_code,422)

    def test_finish_is_atomic_and_idempotent(self):
        self.login();path=self.draft()
        data=self.valid_payload()
        self.assertEqual(self.save(path,data).status_code,200)
        saved=self.client.post(path+'/complete',json={'version':1})
        self.assertEqual(saved.status_code,200,saved.get_json())
        self.assertIn('/admin/users',saved.json['redirect'])
        self.assertTrue(saved.json['created'])
        self.assertEqual(self.client.post(path+'/complete',json={'version':1}).status_code,200)
        with self.app.app_context():
            self.assertEqual(Employee.query.count(),1)
            self.assertEqual(EmployeeOnboarding.query.count(),1)
            u=User.query.filter(User.employee_id.isnot(None)).one()
            self.assertIsNone(u.access_role)
            self.assertFalse(u.can(Permission.USERS_VIEW))
            self.assertEqual(u.name,'Funcionário Sintético de Teste')
            record=EmployeeOnboarding.query.one()
            self.assertNotIn('fake-nonexistent-key',record.encrypted_payload)
            draft=OnboardingDraft.query.one()
            self.assertEqual(draft.status,'submitted')
            self.assertEqual(draft.employee_id,record.employee_id)

    def test_invalid_records_preserve_draft_no_employee(self):
        self.login();path=self.draft();data=self.valid_payload()
        data['cpf']='12345678900'
        self.assertEqual(self.save(path,data).status_code,200)
        result=self.client.post(path+'/complete',json={'version':1})
        self.assertEqual(result.status_code,422,result.get_json())
        with self.app.app_context():
            self.assertEqual(Employee.query.count(),0)
            self.assertEqual(OnboardingDraft.query.one().status,'draft')

    def test_sensitive_and_financial_guards(self):
        self.login();path=self.draft();data=self.valid_payload()
        data.update(pcd_type='dados-sensiveis-de-teste',third_party_holder=True,third_party_name='Teste Terceiro')
        self.assertEqual(self.save(path,data).status_code,200)
        self.assertEqual(self.client.post(path+'/complete',json={'version':1}).status_code,422)
        data['sensitive_data_ack']=True
        data['third_party_reason']='Motivo fictício para homologação'
        self.assertEqual(self.save(path,data,1).status_code,200)
        self.assertEqual(self.client.post(path+'/complete',json={'version':2}).status_code,200)

    def test_no_foreign_draft_access(self):
        self.login();path=self.draft()
        self.login(self.manager_id,self.manager_company_id)
        self.assertEqual(self.client.get(path).status_code,404)
        self.assertEqual(self.save(path,self.valid_payload()).status_code,404)
        self.assertEqual(self.client.post(path+'/complete',json={'version':0}).status_code,404)
        own=self.draft()
        self.assertEqual(self.client.get(own).status_code,200)

    def test_requested_login_is_not_activated(self):
        self.login();path=self.draft();data=self.valid_payload()
        data.update(has_system_access=True,access_login='pending.employee',access_role='admin',access_scope='Empresa atual')
        self.assertEqual(self.save(path,data).status_code,200)
        self.assertEqual(self.client.post(path+'/complete',json={'version':1}).status_code,200)
        with self.app.app_context():
            new_user=User.query.filter_by(username='pending.employee').one()
            self.assertIsNone(new_user.access_role)
            self.assertFalse(new_user.can(Permission.USERS_VIEW))

    def test_drafts_are_resumeable_in_scoped_list(self):
        self.login();path=self.draft()
        page=self.client.get('/admin/onboarding/drafts')
        self.assertEqual(page.status_code,200)
        self.assertIn(path,page.get_data(as_text=True))
        self.assertIn('no-store',page.headers['Cache-Control'])
        self.login(self.manager_id,self.manager_company_id)
        other=self.client.get('/admin/onboarding/drafts')
        self.assertEqual(other.status_code,200)
        self.assertNotIn(path,other.get_data(as_text=True))

    def test_csrf_blocks_unsolicited_json_posts(self):
        self.app.config['WTF_CSRF_ENABLED']=True
        self.login();r=self.client.get('/admin/onboarding/new')
        self.assertEqual(r.status_code,302)
        path=r.location
        page=self.client.get(path)
        self.assertEqual(page.status_code,200)
        result=self.client.post(path+'/save',json={'version':0,'fields':self.valid_payload()})
        self.assertEqual(result.status_code,400)
        import re
        token=re.search(r'name="csrf_token"[^>]*value="([^"]+)"',page.get_data(as_text=True)).group(1)
        response=self.client.post(path+'/save',json={'version':0,'fields':self.valid_payload()},headers={'X-CSRFToken':token})
        self.assertEqual(response.status_code,200,response.get_json())

    def test_job_title_admin_never_grants_access(self):
        self.login();path=self.draft();data=self.valid_payload()
        data['job_role']='admin'
        self.assertEqual(self.save(path,data).status_code,200)
        self.assertEqual(self.client.post(path+'/complete',json={'version':1}).status_code,200)
        with self.app.app_context():
            employee_user=User.query.filter(User.employee_id.isnot(None)).one()
            self.assertIsNone(employee_user.role)
            self.assertIsNone(employee_user.access_role)
            self.assertFalse(employee_user.can(Permission.USERS_VIEW))
            self.assertEqual(employee_user.employee.job_title,'admin')

    def test_draft_discard(self):
        self.login();path=self.draft()
        self.assertEqual(self.client.post(path+'/discard').status_code,200)
        self.assertEqual(self.client.get(path).status_code,404)
        with self.app.app_context():self.assertEqual(Employee.query.count(),0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
