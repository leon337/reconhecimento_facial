import test from 'node:test';
import assert from 'node:assert/strict';
import { sanitizeRegistrationDraft, validRegistrationDraft, registrationTool } from '../src/registration.js';

test('somente campos permitidos entram no rascunho do modelo', () => {
  const draft = sanitizeRegistrationDraft({
    name:' Maria de Teste ',username:' maria.teste ',registration:'TEST-1',
    access_role:'admin',password:'NEVER_TO_THE_MODEL',company_id:99,
  });
  assert.deepEqual(Object.keys(draft).sort(), ['job_title','name','registration','schedule','username']);
  assert.equal(draft.name,'Maria de Teste');
  assert.equal(Object.hasOwn(draft,'access_role'),false);
  assert.equal(Object.hasOwn(draft,'password'),false);
});

test('não cadastra por rascunho incompleto nem aceita username inválido', () => {
  const missing=sanitizeRegistrationDraft({name:'Maria de Teste'});
  assert.ok(validRegistrationDraft(missing).length);
  const ready=sanitizeRegistrationDraft({name:'Maria de Teste',username:'maria.teste'});
  assert.deepEqual(validRegistrationDraft(ready),[]);
  assert.ok(validRegistrationDraft({...ready,username:'admin root'}).length);
});

test('ferramenta de IA nunca dispõe da execução do cadastro', () => {
  assert.equal(registrationTool.functionDeclarations.length,1);
  assert.equal(registrationTool.functionDeclarations[0].name,'prepare_employee_registration');
  assert.ok(!JSON.stringify(registrationTool).includes('password'));
  assert.ok(!JSON.stringify(registrationTool).includes('employee-create'));
});
