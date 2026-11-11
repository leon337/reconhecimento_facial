/* Captura somente áudio do microfone, sem armazenar no disco ou no navegador. */
class PotiguarPcmProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    this.frame = new Float32Array(2048);
    this.offset = 0;
  }

  process(inputs) {
    const input = inputs[0] && inputs[0][0];
    if (!input) return true;
    for (let i = 0; i < input.length; i += 1) {
      this.frame[this.offset++] = input[i];
      if (this.offset === this.frame.length) {
        this.port.postMessage({ pcm: this.frame, sampleRate }, [this.frame.buffer]);
        this.frame = new Float32Array(2048);
        this.offset = 0;
      }
    }
    return true;
  }
}

registerProcessor('potiguar-pcm', PotiguarPcmProcessor);
