/** VAD modular e privado (sem gravação/servidor de terceiros).
 *
 * Não confundir detecção acústica com identificação de quem está falando:
 * ruídos com cadência de voz e falantes distantes ainda podem ativar a VAD.
 * A revisão humana continua obrigatória para qualquer ação.
 */
export const VAD_DEFAULTS = Object.freeze({
  minimumRms: 0.012,
  relativeNoiseMultiplier: 3.0,
  minimumPitchCorrelation: 0.42,
  minimumZeroCrossing: 0.012,
  maximumZeroCrossing: 0.27,
  startFrames: 2,
  endFrames: 4,
  prerollFrames: 4,
});

export function analyzeSpeechFrame(samples, sampleRate = 16000) {
  const count = samples?.length || 0;
  if (count < 64 || sampleRate <= 0) {
    return { rms: 0, zeroCrossing: 0, pitchCorrelation: 0, peak: 0 };
  }
  let sum = 0;
  let peak = 0;
  let crossings = 0;
  let last = samples[0] || 0;
  for (let i = 0; i < count; i += 1) {
    const value = Number.isFinite(samples[i]) ? samples[i] : 0;
    sum += value * value;
    peak = Math.max(peak, Math.abs(value));
    if ((last < 0 && value >= 0) || (last > 0 && value <= 0)) crossings += 1;
    last = value;
  }
  const rms = Math.sqrt(sum / count);
  const zeroCrossing = crossings / count;
  // Autocorrelação normalizada em lags de F0 80–330 Hz.
  // Não envia áudio e é suficientemente barata para blocos ~128ms.
  let pitchCorrelation = 0;
  const shortest = Math.max(3, Math.floor(sampleRate / 330));
  const longest = Math.min(count - 2, Math.ceil(sampleRate / 80));
  for (let lag = shortest; lag <= longest; lag += 3) {
    let overlap = 0;
    let aEnergy = 0;
    let bEnergy = 0;
    // Em vez de 2048 multiplicações por lag, amostra 1 de 2.
    for (let i = lag; i < count; i += 2) {
      const a = samples[i] || 0;
      const b = samples[i - lag] || 0;
      overlap += a * b;
      aEnergy += a * a;
      bEnergy += b * b;
    }
    const corr = overlap / Math.max(1e-10, Math.sqrt(aEnergy * bEnergy));
    if (corr > pitchCorrelation) pitchCorrelation = corr;
  }
  return { rms, zeroCrossing, pitchCorrelation, peak };
}

export class VoiceActivityGate {
  constructor(options = {}) {
    this.options = { ...VAD_DEFAULTS, ...options };
    this.noiseRms = 0.002;
    this.preroll = [];
    this.voiced = 0;
    this.silent = 0;
    this.active = false;
  }

  process(samples, sampleRate = 16000) {
    if (!(samples instanceof Float32Array) || samples.length < 64) {
      return { frames: [], started: false, ended: false, active: this.active };
    }
    const values = analyzeSpeechFrame(samples, sampleRate);
    const threshold = Math.max(
      this.options.minimumRms,
      this.noiseRms * this.options.relativeNoiseMultiplier,
    );
    const voiceLike = values.rms >= threshold
      && values.peak >= threshold * 1.6
      && values.zeroCrossing >= this.options.minimumZeroCrossing
      && values.zeroCrossing <= this.options.maximumZeroCrossing
      && values.pitchCorrelation >= this.options.minimumPitchCorrelation;

    // Nunca estimar ruído-base com fala detectada.
    if (!voiceLike && !this.active && values.rms < Math.max(0.025, this.noiseRms * 1.8)) {
      this.noiseRms = this.noiseRms * 0.94 + values.rms * 0.06;
    }

    if (!this.active) {
      this.preroll.push(samples);
      if (this.preroll.length > this.options.prerollFrames) this.preroll.shift();
      this.voiced = voiceLike ? this.voiced + 1 : 0;
      if (this.voiced >= this.options.startFrames) {
        this.active = true;
        this.silent = 0;
        const frames = this.preroll.splice(0);
        return { frames, started: true, ended: false, active: true };
      }
      return { frames: [], started: false, ended: false, active: false };
    }

    this.silent = voiceLike ? 0 : this.silent + 1;
    if (this.silent >= this.options.endFrames) {
      this.reset();
      return { frames: [], started: false, ended: true, active: false };
    }
    return { frames: [samples], started: false, ended: false, active: true };
  }

  finish() {
    const ended = this.active;
    this.reset();
    return ended;
  }

  reset() {
    this.preroll.length = 0;
    this.voiced = 0;
    this.silent = 0;
    this.active = false;
  }
}
