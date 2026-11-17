import test from 'node:test';
import assert from 'node:assert/strict';
import {PotiguarLive} from '../src/live.js';

function harness(handlers={}){
  const packets=[];
  const live=new PotiguarLive(handlers);
  live.session={sendToolResponse(data){packets.push(data);}};
  return {live,packets};
}

test('recibo só volta ao Gemini após execução assíncrona no formulário',async()=>{
  let release;
  const waiting=new Promise(resolve=>{release=resolve});
  const {live,packets}=harness({onOnboardingAction:()=>waiting});
  live.allowOnboardingSuggestions=true;
  live.setOnboardingMode(true);
  const pending=live.handleToolCalls([{id:'abc',name:'operate_onboarding',args:{action:'save_draft'}}]);
  assert.equal(packets.length,0,'model must not receive optimistic success');
  release({status:'saved',step:2,cpf:'52998224725',created:true});
  await pending;
  assert.deepEqual(packets[0].functionResponses[0].response,{status:'saved',step:2,created:false});
  assert(!JSON.stringify(packets).includes('52998224725'));
});

test('navegação não autoriza rotas arbitrárias nem cadastro sem permissão',async()=>{
  let called=0;
  const {live,packets}=harness({onAppNavigation:()=>{called++;return {status:'navigation_started'}}});
  live.allowAppNavigation=true;
  await live.handleToolCalls([
    {id:'one',name:'navigate_potiguar',args:{destination:'employees'}},
    {id:'two',name:'navigate_potiguar',args:{destination:'new_employee'}},
    {id:'three',name:'navigate_potiguar',args:{destination:'https://untrusted.invalid'}},
  ]);
  assert.equal(called,1);
  assert.deepEqual(packets[0].functionResponses.map(x=>x.response.status),
    ['navigation_started','denied','denied']);
});

test('valores confidenciais e ações destrutivas são negados e não entram nos recibos',async()=>{
  let called=false;
  const {live,packets}=harness({
    onOnboardingSuggestions:()=>{called=true;return {status:'saved'}},
  });
  live.allowOnboardingSuggestions=true;
  live.setOnboardingMode(true);
  live.onboardingStep=1;
  live.onboardingField='full_name';
  await live.handleToolCalls([
    {id:'cpf',name:'suggest_onboarding_fields',args:{step:1,suggestions:[{field:'cpf',value:'52998224725'}]}},
    {id:'finish',name:'operate_onboarding',args:{action:'complete'}},
    {id:'unknown',name:'run_terminal',args:{command:'erase-all'}},
  ]);
  assert.equal(called,false);
  assert.deepEqual(packets[0].functionResponses.map(x=>x.response.status),
    ['no_eligible_suggestions','denied','denied']);
  assert(!JSON.stringify(packets).includes('52998224725'));
});

test('agente solicita revisão final sem criar funcionário nem revelar dados',async()=>{
 const called=[];
 const {live,packets}=harness({
   onOnboardingAction:async({action})=>{
      called.push(action);
      return {status:'awaiting_human_confirmation',step:7,created:true,cpf:'00000000191'};
   },
 });
 live.allowOnboardingSuggestions=true;
 live.setOnboardingMode(true);live.setOnboardingStep(7);
 await live.handleToolCalls([{
   id:'complete-request',name:'operate_onboarding',args:{action:'request_completion'}
 }]);
 assert.deepEqual(called,['request_completion']);
 assert.deepEqual(packets[0].functionResponses[0].response,
     {status:'awaiting_human_confirmation',created:false,step:7});
 assert(!JSON.stringify(packets).includes('00000000191'));
});
