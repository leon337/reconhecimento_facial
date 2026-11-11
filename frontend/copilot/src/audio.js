/* Conversão de áudio em memória: PCM 16kHz para entrada, 24kHz para saída. */
export function encodePcm16(samples, sourceRate) {
  if (!Number.isFinite(sourceRate) || sourceRate <= 0) throw new Error('Taxa de áudio inválida.');
  const ratio = sourceRate / 16000;
  const count = Math.max(1, Math.round(samples.length / ratio));
  const bytes = new Uint8Array(count * 2);
  const view = new DataView(bytes.buffer);
  for (let index = 0; index < count; index += 1) {
    const position = Math.min(samples.length - 1, Math.floor(index * ratio));
    const input = Math.max(-1, Math.min(1, samples[position] || 0));
    view.setInt16(index * 2, input < 0 ? Math.round(input * 32768) : Math.round(input * 32767), true);
  }
  let raw = '';
  for (let offset = 0; offset < bytes.length; offset += 8192) {
    raw += String.fromCharCode(...bytes.subarray(offset, offset + 8192));
  }
  return btoa(raw);
}

export class Microphone {
  constructor(sendAudio) {
    this.sendAudio = sendAudio;
    this.stream = null;
    this.context = null;
  }

  async start() {
    if (!window.isSecureContext || !navigator.mediaDevices?.getUserMedia) {
      throw new Error('O microfone exige HTTPS ou localhost e permissão do navegador.');
    }
    this.stream = await navigator.mediaDevices.getUserMedia({
      audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true },
    });
    try {
      this.context = new AudioContext({ sampleRate: 16000, latencyHint: 'interactive' });
      await this.context.audioWorklet.addModule('/static/copilot/pcm-worklet.js');
      const source = this.context.createMediaStreamSource(this.stream);
      const processor = new AudioWorkletNode(this.context, 'potiguar-pcm');
      const gain = this.context.createGain();
      gain.gain.value = 0;
      processor.port.onmessage = ({ data }) => {
        if (data?.pcm) this.sendAudio({
          data: encodePcm16(data.pcm, data.sampleRate),
          mimeType: 'audio/pcm;rate=16000',
        });
      };
      source.connect(processor);
      processor.connect(gain);
      gain.connect(this.context.destination);
      await this.context.resume();
    } catch (error) {
      await this.stop();
      throw error;
    }
  }

  async stop() {
    this.stream?.getTracks().forEach((track) => track.stop());
    this.stream = null;
    const context = this.context;
    this.context = null;
    if (context && context.state !== 'closed') await context.close();
  }
}

export class AudioPlayer {
  constructor() {
    this.context = null;
    this.nextTime = 0;
    this.sources = new Set();
  }

  async add(base64, mimeType = 'audio/pcm;rate=24000') {
    if (!mimeType.startsWith('audio/pcm')) return;
    if (!this.context) this.context = new AudioContext({ sampleRate: 24000 });
    if (this.context.state === 'suspended') await this.context.resume();
    const sampleRate = Number(/rate=(\d+)/.exec(mimeType)?.[1] || 24000);
    if (sampleRate < 8000 || sampleRate > 48000) return;
    const raw = atob(base64);
    const sampleCount = Math.floor(raw.length / 2);
    if (!sampleCount) return;
    const buffer = this.context.createBuffer(1, sampleCount, sampleRate);
    const pcm = buffer.getChannelData(0);
    for (let i = 0; i < sampleCount; i += 1) {
      const value = (raw.charCodeAt(i * 2) | (raw.charCodeAt(i * 2 + 1) << 8));
      pcm[i] = (value >= 32768 ? value - 65536 : value) / 32768;
    }
    const source = this.context.createBufferSource();
    source.buffer = buffer;
    source.connect(this.context.destination);
    source.onended = () => this.sources.delete(source);
    const startAt = Math.max(this.context.currentTime, this.nextTime);
    source.start(startAt);
    this.nextTime = startAt + buffer.duration;
    this.sources.add(source);
  }

  interrupt() {
    for (const source of this.sources) {
      try { source.stop(); } catch { /* Já finalizado. */ }
    }
    this.sources.clear();
    this.nextTime = this.context?.currentTime || 0;
  }

  async close() {
    this.interrupt();
    if (this.context && this.context.state !== 'closed') await this.context.close();
    this.context = null;
  }
}
