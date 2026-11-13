import test from 'node:test';
import assert from 'node:assert/strict';
import { isProtectedInput } from '../src/protected-input.js';

test('bloqueia documentos, contatos, finanças e endereços explícitos no chat seguro',()=>{
  for(const text of ['529.982.247-25','11.222.333/0001-99','+55 (81) 99999-1111','email@teste.com','minha senha é 123','PIX 77','R$ 1000','Rua dos testes, 123','CEP 12345-678']){
    assert.equal(isProtectedInput(text),true,text);
  }
});
test('mantém respostas funcionais e admite textos sem dado protegido óbvio',()=>{
  for(const text of ['CLT intermitente','Analista de suporte','São Paulo','Jornada parcial','Joana de Teste']){
    assert.equal(isProtectedInput(text),false,text);
  }
});
test('rejeita não-strings por padrão sem vazamento',()=>{
  assert.equal(isProtectedInput(null),false);
  assert.equal(isProtectedInput({token:'123456789'}),false);
});
