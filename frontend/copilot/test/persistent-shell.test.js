import test from 'node:test';
import assert from 'node:assert/strict';
import {isOnboardingFormRoute,isAppFrameRoute,routeReached,isTrustedAppMessage} from '../src/persistent-shell.js';
import {PotiguarLive} from '../src/live.js';

test('o shell permite apenas URLs administrativas internas canônicas',()=>{
  assert.equal(isOnboardingFormRoute('/admin/onboarding/0123456789abcdef0123456789abcdef'),true);
  assert.equal(isOnboardingFormRoute('/admin/onboarding/new'),false);
  for(const path of ['/admin/dashboard','/admin/pontos','/admin/relatorios','/admin/users',
    '/admin/onboarding/drafts','/admin/users/new'])
    assert.equal(isAppFrameRoute(path),true,path);
  for(const path of ['/admin/login','/admin/copilot','/admin/copilot/embed/onboarding',
    'https://outside.invalid/admin/users','//outside.invalid','/admin/users?x=1','/admin/../admin'])
    assert.equal(isAppFrameRoute(path),false,path);
});
test('redirecionamento da criação termina no formulário sem finalizar cadastro',()=>{
  const target='/admin/onboarding/0123456789abcdef0123456789abcdef';
  assert.equal(routeReached('/admin/users/new',target),true);
  assert.equal(routeReached('/admin/onboarding/new',target),true);
  assert.equal(routeReached('/admin/users',target),false);
  assert.equal(routeReached('/admin/users','/admin/users'),true);
  assert.equal(routeReached('/admin/dashboard','https://outside.invalid'),false);
});
test('postMessage de interface exige a origem e a janela do frame',()=>{
  const frame={id:1};
  assert.equal(isTrustedAppMessage({origin:'https://test.invalid',source:frame,data:{type:'ok'}},
    frame,'https://test.invalid'),true);
  for(const event of [
    {origin:'https://evil.invalid',source:frame,data:{type:'ok'}},
    {origin:'https://test.invalid',source:{id:1},data:{type:'ok'}},
    {origin:'https://test.invalid',source:frame,data:null},
    {origin:'https://test.invalid',source:frame,data:['bad']},
  ])assert.equal(isTrustedAppMessage(event,frame,'https://test.invalid'),false);
});
test('navegar entre módulos e formulário reutiliza a mesma sessão de ferramentas',async()=>{
  const receipts=[];
  const live=new PotiguarLive({
    onAppNavigation:async()=>({status:'navigated'}),
    onOnboardingAction:async()=>({status:'saved',step:2}),
  });
  const session={sendToolResponse(x){receipts.push(x)}};
  live.session=session;
  live.allowAppNavigation=true;
  live.allowOnboardingSuggestions=true;
  live.allowEmployeeActions=true;
  await live.handleToolCalls([{id:'a',name:'navigate_potiguar',args:{destination:'employees'}}]);
  assert.equal(live.session,session);
  assert.equal(receipts.at(-1).functionResponses[0].response.status,'navigated');
  await live.handleToolCalls([{id:'b',name:'operate_onboarding',args:{action:'save_draft'}}]);
  assert.equal(receipts.at(-1).functionResponses[0].response.status,'denied');
  live.setOnboardingMode(true);live.setOnboardingStep(2);
  await live.handleToolCalls([{id:'c',name:'operate_onboarding',args:{action:'save_draft'}}]);
  assert.equal(receipts.at(-1).functionResponses[0].response.status,'saved');
  live.setOnboardingMode(false);
  await live.handleToolCalls([{id:'d',name:'navigate_potiguar',args:{destination:'dashboard'}}]);
  assert.equal(live.session,session);
  assert.equal(receipts.at(-1).functionResponses[0].response.status,'navigated');
  assert.equal(receipts.length,4);
});
