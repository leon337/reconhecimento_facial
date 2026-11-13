import test from 'node:test';
import assert from 'node:assert/strict';
import {ALLOWED_ONBOARDING_FIELDS, sanitizeOnboardingSuggestions} from '../src/onboarding-suggestions.js';

test('sugestão segura somente na etapa correta',()=>{
 const raw={step:3,suggestions:[{field:'job_role',value:'Analista de Teste'}]};
 assert.deepEqual(sanitizeOnboardingSuggestions(raw,3),[{field:'job_role',value:'Analista de Teste'}]);
 assert.deepEqual(sanitizeOnboardingSuggestions(raw,1),[]);
});
test('documentos, saúde, dados bancários e permissões não são sugeridos',()=>{
 for(const step of [0,1,2,3,4,5,6,7]){
  for(const field of ['cpf','rg','race','pcd_type','pix_key','account','access_role','has_system_access','biometric_notice_ack','password']){
   assert.deepEqual(sanitizeOnboardingSuggestions({step,suggestions:[{field,value:'secret'}]},step),[]);
  }
 }
 for(const step of [4,5,6,7])assert.deepEqual(ALLOWED_ONBOARDING_FIELDS[step],[]);
});
test('impede HTML, campos duplicados e excesso de sugestões',()=>{
 assert.deepEqual(sanitizeOnboardingSuggestions({step:1,suggestions:[{field:'full_name',value:'<script>'}]},1),[]);
 assert.deepEqual(sanitizeOnboardingSuggestions({step:1,suggestions:[{field:'full_name',value:'Maria de Teste'},{field:'full_name',value:'Outro Nome'}]},1),[{field:'full_name',value:'Maria de Teste'}]);
 assert.deepEqual(sanitizeOnboardingSuggestions({step:1,suggestions:[{field:'full_name',value:'Valor\nRuim'}]},1),[]);
 assert.deepEqual(sanitizeOnboardingSuggestions({step:1,suggestions:Array(6).fill({field:'full_name',value:'Teste'})},1),[]);
});
