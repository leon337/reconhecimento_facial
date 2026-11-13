import test from 'node:test';
import assert from 'node:assert/strict';
import guide from '../../../static/admin-onboarding-controller.js';
import {sanitizeOnboardingNavigation, sanitizeOnboardingSuggestions} from '../src/onboarding-suggestions.js';

function input(name, value='', options=[]) {
  return {name,value,disabled:false,type:'text',tagName:options.length?'SELECT':'INPUT',
    options:options.map(value=>({value}))};
}

test('somente campos previamente autorizados podem ser escritos pela IA',()=>{
  assert.equal(guide.isSafe(0,'relation_type'),true);
  assert.equal(guide.isSafe(1,'full_name'),true);
  for(const field of ['cpf','rg','birth_date','personal_email','street','salary','pix_key','access_role','biometric_timing','sensitive_data_ack'])
    for(let step=0;step<8;step++) assert.equal(guide.isSafe(step,field),false);
});

test('campos condicionais seguem relação, endereço, pagamento, acesso e biometria',()=>{
  const base={relation_type:'CLT comum',address_type:'Urbano',payment_method:'PIX',has_system_access:false,
    third_party_holder:false,biometric_timing:'Depois',has_dependents:'Não'};
  assert.equal(guide.applicable('other_relation',base),false);
  assert.equal(guide.applicable('street',base),true);
  assert.equal(guide.applicable('rural_road',base),false);
  assert.equal(guide.applicable('pix_key',base),true);
  assert.equal(guide.applicable('bank',base),false);
  assert.equal(guide.applicable('access_login',base),false);
  assert.equal(guide.applicable('biometric_notice_ack',base),false);
  assert.equal(guide.applicable('dependent_name',base),false);
  assert.equal(guide.applicable('intermittent_date',{...base,relation_type:'CLT intermitente'}),true);
  assert.equal(guide.applicable('foreign_postal',{...base,address_type:'Exterior'}),true);
  assert.equal(guide.applicable('third_party_reason',{...base,third_party_holder:true}),true);
  assert.equal(guide.applicable('biometric_notice_ack',{...base,biometric_timing:'Agora'}),true);
});

test('uma pergunta por vez; preexistentes e pulados não são perguntados novamente',()=>{
  const fields=[input('full_name','Maria Oliveira'),input('education'),input('social_name')];
  assert.equal(guide.nextField(fields,{},new Set()).name,'education');
  assert.equal(guide.nextField(fields,{},new Set(['education'])).name,'social_name');
  assert.equal(guide.nextField(fields,{},new Set(['education','social_name'])),null);
});

test('valor seguro exige validação de seletor, tamanho e conteúdo',()=>{
  const contract=input('relation_type','',['CLT comum','CLT intermitente']);
  assert.equal(guide.validSafeValue(contract,'CLT comum'),true);
  assert.equal(guide.validSafeValue(contract,'ADMIN'),false);
  assert.equal(guide.validSafeValue(input('full_name'),'Ma'),false);
  assert.equal(guide.validSafeValue(input('full_name'),'Maria Oliveira'),true);
  assert.equal(guide.validSafeValue(input('full_name'),'<script>'),false);
  assert.equal(guide.validSafeValue(input('full_name'),'X'.repeat(121)),false);
});

test('navegação é somente índice/campo sem valores privados',()=>{
  assert.deepEqual(sanitizeOnboardingNavigation({kind:'correct_field',step:3,field:'job_role'}),
    {kind:'correct_field',step:3,field:'job_role'});
  assert.deepEqual(sanitizeOnboardingNavigation({kind:'open_step',step:2}),
    {kind:'open_step',step:2,field:null});
  assert.equal(sanitizeOnboardingNavigation({kind:'correct_field',step:9,field:'job_role'}),null);
  assert.equal(sanitizeOnboardingNavigation({kind:'correct_field',step:1,field:'cpf);alert(1)'}),null);
});

test('bloqueia sugestões financeiras, biométricas e fora da etapa',()=>{
  assert.deepEqual(sanitizeOnboardingSuggestions({step:4,suggestions:[{field:'pix_key',value:'123'}]},4),[]);
  assert.deepEqual(sanitizeOnboardingSuggestions({step:3,suggestions:[{field:'job_role',value:'Analista'}]},2),[]);
});
