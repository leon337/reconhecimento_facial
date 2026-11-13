import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

// Contrato de integração: a emissão de tokens temporários do SDK foi comprovada em v1alpha.
test('conexão Gemini Live com token efêmero solicita API v1alpha',()=>{
  const src=readFileSync(new URL('../src/live.js',import.meta.url),'utf8');
  assert.match(src,/httpOptions:\s*\{\s*apiVersion:\s*'v1alpha'\s*\}/);
  assert.doesNotMatch(src,/httpOptions:\s*\{\s*apiVersion:\s*'v1beta'\s*\}/);
});
