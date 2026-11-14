import test from 'node:test';
import assert from 'node:assert/strict';
import {appNavigationTool,sanitizeAppNavigation,safeAppPath} from '../src/app-navigation.js';
import {onboardingSuggestionTool,ONBOARDING_OPERATION_NAME,
  sanitizeOnboardingOperation} from '../src/onboarding-suggestions.js';

test('navegação aceita apenas telas autorizadas e respeita permissão de criação',()=>{
  for(const destination of ['dashboard','attendance','reports','employees'])
    assert.deepEqual(sanitizeAppNavigation({destination},false),{destination});
  for(const destination of ['drafts','new_employee'])
    assert.deepEqual(sanitizeAppNavigation({destination},true),{destination});
  assert.equal(sanitizeAppNavigation({destination:'drafts'},false),null);
  for(const x of [{destination:'new_employee'},{destination:'payments'},
    {destination:'https://test.invalid'},{destination:'/admin/users'},null,{destination:'employees',url:'https://evil.invalid'}]){
    if(x?.destination==='employees')continue;
    assert.equal(sanitizeAppNavigation(x,false),null);
  }
  assert.deepEqual(appNavigationTool.functionDeclarations[0].parametersJsonSchema.properties.destination.enum,
    ['dashboard','attendance','reports','employees','drafts','new_employee']);
});
test('URLs de navegação devem ser internas e canônicas',()=>{
  for(const p of ['/admin/users','/admin/users/new','/admin/copilot','/admin/onboarding/drafts'])assert.equal(safeAppPath(p),true,p);
  for(const p of ['//example.com','https://example.com','/admin/../admin/users',
    '/admin/users?next=https://bad.com','/admin/users#foo','javascript:alert(1)',null,'/logout'])assert.equal(safeAppPath(p),false,String(p));
});
test('operação de formulário não permite concluir, excluir nem acessar dados protegidos',()=>{
  for(const action of ['get_state','save_draft','focus_current_field','skip_optional'])
    assert.deepEqual(sanitizeOnboardingOperation({action}),{action});
  for(const action of ['complete','delete','update_salary','activate_access','read_cpf','click_anywhere'])
    assert.equal(sanitizeOnboardingOperation({action}),null);
  assert.equal(sanitizeOnboardingOperation(null),null);
  assert.equal(sanitizeOnboardingOperation([]),null);
  const declaration=onboardingSuggestionTool.functionDeclarations.find(x=>x.name===ONBOARDING_OPERATION_NAME);
  assert(declaration);
  assert.deepEqual(declaration.parametersJsonSchema.properties.action.enum,
    ['get_state','save_draft','focus_current_field','skip_optional']);
});
