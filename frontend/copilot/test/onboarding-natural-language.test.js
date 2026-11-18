import test from 'node:test';
import assert from 'node:assert/strict';
import {resolveNaturalSelect,resolveOnboardingAnswer,canonicalizeOnboardingValue,fold} from '../src/onboarding-natural-language.js';
import {sanitizeOnboardingSuggestions} from '../src/onboarding-suggestions.js';

const REL=['CLT comum','CLT intermitente','Sem vínculo empregatício'];
function check(text,field,expected,options=REL){
  assert.equal(resolveNaturalSelect(field,text,options),expected,
    JSON.stringify({text,field,expected}));
}
test('entende manifestações afirmativas e variações de vínculo',()=>{
  for(const text of ['sou CLT comum','pode colocar CLT comum','o regime é CLT normal',
      'me contrata como CLT tradicional','CLT padrão','É CLT COMUM.'])
    check(text,'relation_type','CLT comum');
  for(const text of ['sou intermitente','o contrato é por convocação',
      'é CLT intermitente','coloca intermitente','regime intermitente',
      'trabalho por convocação','CLT-INTERMITENTE'])
    check(text,'relation_type','CLT intermitente');
  for(const text of ['é sem vínculo','sem vínculo empregatício','prestador autônomo',
     'trabalhador autônomo','prestação de serviços sem vínculo'])
    check(text,'relation_type','Sem vínculo empregatício');
});
test('nunca infere em perguntas, contradições e ambiguidades',()=>{
  for(const text of ['qual a diferença entre CLT comum e intermitente?',
    'é CLT comum ou intermitente?', 'não é intermitente', 'nunca foi CLT comum',
    'não, não quero CLT comum','e se fosse CLT intermitente?',
    'explique contrato intermitente','qual a diferença como CLT comum',
    'tenho duas opções, CLT comum e intermitente',
    'qual seria o tipo de vínculo?', 'terceirizado'])
    check(text,'relation_type',null);
});
test('só opera enum seguro e opção exposta, sem inferir campos confidenciais',()=>{
  check('rural','address_type','Rural',['Urbano','Rural','Exterior']);
  check('no exterior','address_type','Exterior',['Urbano','Rural','Exterior']);
  check('no centro urbano','address_type','Urbano',['Urbano','Rural','Exterior']);
  check('não preciso de vale transporte','transport_benefit','Não',['Não','Sim']);
  check('sim','transport_benefit','Sim',['Não','Sim']);
  check('não','transport_benefit','Não',['Não','Sim']);
  check('sou intermitente','relation_type',null,['CLT comum']);
  check('sou intermitente','full_name',null,['CLT intermitente']);
  check('sou intermitente','cpf',null,['CLT intermitente']);
  assert.equal(fold('C L T.  INTERMITENTE'), 'c l t intermitente');
});
test('model tool alias é normalizado sem expandir whitelist',()=>{
  for(const value of ['intermitente','CLT intermitente','contrato por convocação']){
    assert.equal(canonicalizeOnboardingValue('relation_type',value),'CLT intermitente');
    assert.deepEqual(sanitizeOnboardingSuggestions({
      step:0,suggestions:[{field:'relation_type',value}]
    },0),[{field:'relation_type',value:'CLT intermitente'}]);
  }
  assert.deepEqual(sanitizeOnboardingSuggestions({
    step:0,suggestions:[{field:'cpf',value:'12345678901'}]
  },0),[]);
  assert.equal(canonicalizeOnboardingValue('relation_type','não é intermitente'),null);
});

test('texto livre seguro é aplicado somente como resposta inequívoca do campo ativo',()=>{
 assert.equal(resolveOnboardingAnswer('full_name','Teste Funcionário de Teste',[]),'Teste Funcionário de Teste');
 assert.equal(resolveOnboardingAnswer('full_name','Meu nome é Teste de QA',[]),'Teste de QA');
 assert.equal(resolveOnboardingAnswer('full_name','Qual meu nome?',[]),null);
 assert.equal(resolveOnboardingAnswer('full_name','foo@example.com',[]),null);
 assert.equal(resolveOnboardingAnswer('cpf','12345678900',[]),null);
 assert.equal(resolveOnboardingAnswer('payment_method','PIX',[]),null);
 assert.equal(resolveOnboardingAnswer('relation_type','CLT comum',['CLT comum','CLT intermitente']),'CLT comum');
 assert.equal(resolveOnboardingAnswer('relation_type','O que é CLT comum?',['CLT comum','CLT intermitente']),null);
});
