import test from 'node:test';
import assert from 'node:assert/strict';
import { encodePcm16 } from '../src/audio.js';

test('PCM captura 16 kHz em little-endian e respeita limites', () => {
  const raw = atob(encodePcm16(new Float32Array([1, -1, 0, 0.5]), 16000));
  assert.equal(raw.length, 8);
  const view = new DataView(Uint8Array.from(raw, (ch) => ch.charCodeAt(0)).buffer);
  assert.equal(view.getInt16(0, true), 32767);
  assert.equal(view.getInt16(2, true), -32768);
  assert.equal(view.getInt16(4, true), 0);
  assert.ok(view.getInt16(6, true) > 16000);
});

test('PCM converte taxa de 48 kHz em 16 kHz', () => {
  const raw = atob(encodePcm16(new Float32Array(4800).fill(0.25), 48000));
  assert.equal(raw.length, 1600 * 2);
});

test('PCM rejeita amostragem incorreta', () => {
  assert.throws(() => encodePcm16(new Float32Array([0]), 0), /Taxa de áudio inválida/);
});
