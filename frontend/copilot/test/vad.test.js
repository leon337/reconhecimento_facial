import test from 'node:test';
import assert from 'node:assert/strict';
import { analyzeSpeechFrame, VoiceActivityGate } from '../src/vad.js';

function sine(amp = 0.15, freq = 180, count = 2048) {
  return Float32Array.from({length: count}, (_, i) => Math.sin(2 * Math.PI * freq * i / 16000) * amp);
}
function noise(amp = 0.003, count = 2048, seed = 17) {
  let state = seed;
  return Float32Array.from({length: count}, () => {
    state = (1664525 * state + 1013904223) >>> 0;
    return ((state / 4294967295) * 2 - 1) * amp;
  });
}

test('RMS e periodicidade identificam voz sintética sem gravar áudio', () => {
  const v = analyzeSpeechFrame(sine());
  assert.ok(v.rms > 0.05);
  assert.ok(v.pitchCorrelation > 0.8);
});

test('silêncio e ruído baixo não são enviados ao Gemini', () => {
  const gate = new VoiceActivityGate();
  let sent = 0;
  for (let i = 0; i < 80; i++) sent += gate.process(noise(0.006, 2048, i)).frames.length;
  assert.equal(sent, 0);
  assert.equal(gate.active, false);
});

test('ruído branco alto não deve ser classificado como fala', () => {
  const gate = new VoiceActivityGate();
  let sent = 0;
  for (let i = 0; i < 15; i++) sent += gate.process(noise(0.12, 2048, i)).frames.length;
  assert.equal(sent, 0);
});

test('fala sustentada é transmitida e termina após silêncio', () => {
  const gate = new VoiceActivityGate();
  let started = 0;
  let ended = 0;
  let sent = 0;
  for (let i = 0; i < 9; i++) {
    const r = gate.process(sine());
    started += +r.started;
    sent += r.frames.length;
  }
  for (let i = 0; i < 6; i++) {
    const r = gate.process(new Float32Array(2048));
    ended += +r.ended;
    sent += r.frames.length;
  }
  assert.equal(started, 1);
  assert.equal(ended, 1);
  assert.ok(sent >= 8);
  assert.equal(gate.active, false);
});

test('pulsos de ruído curtos não abrem uma fala', () => {
  const gate = new VoiceActivityGate();
  const tone = sine();
  for (let i = 0; i < 20; i++) {
    assert.equal(gate.process(tone).started, false);
    gate.process(new Float32Array(2048));
  }
  assert.equal(gate.active, false);
});

test('finalização limpa o estado e protege nova sessão', () => {
  const gate = new VoiceActivityGate();
  gate.process(sine());
  gate.process(sine());
  assert.ok(gate.finish());
  assert.equal(gate.finish(), false);
  assert.equal(gate.process(noise()).frames.length, 0);
});
