import { GoogleGenAI, Modality } from '@google/genai';
import { AudioPlayer, Microphone } from './audio.js';

const MODEL_IDS = ['gemini-3.8-live', 'gemini-3.8-live-extended-thinking'];
const SYSTEM_INSTRUCTIONS = [
  'Você é o Copiloto Potiguar, assistente de navegação do Sistema de Ponto Potiguar.',
  'Fale sempre em português do Brasil com clareza e acessibilidade.',
  'Este ambiente é uma prévia somente de orientação. Não possui ferramentas para alterar dados.',
  'Ajude o usuário a entender onde consultar funcionários, iniciar um cadastro ou buscar informações.',
  'Nunca diga que registrou ponto, aprovou ajuste, cadastrou funcionário, reconheceu rosto ou executou qualquer operação real.',
  'Não peça senha, chave, imagem facial, documento sensível nem informações pessoais de funcionários.',
  'Quando necessário, recomende o uso dos controles oficiais da interface e de seus mecanismos de validação.',
  'Se for solicitado a realizar ações, explique que o usuário deve confirmá-las no fluxo oficial.',
].join('\n');

export class PotiguarLive {
  constructor(handlers = {}) {
    this.handlers = handlers;
    this.session = null;
    this.microphone = null;
    this.player = new AudioPlayer();
    this.audioEnabled = false;
  }

  async connect(model, csrf) {
    if (!MODEL_IDS.includes(model)) throw new Error('Modelo não autorizado.');
    if (this.session) return;
    const response = await fetch('/admin/copilot/session-token', {
      method: 'POST',
      credentials: 'same-origin',
      cache: 'no-store',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf },
      body: JSON.stringify({ model }),
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(payload.error || 'Conexão não disponível.');
    const ai = new GoogleGenAI({
      apiKey: payload.token,
      httpOptions: { apiVersion: 'v1beta' },
    });
    try {
      this.session = await ai.live.connect({
        model: payload.model,
        config: {
          responseModalities: [Modality.AUDIO],
          inputAudioTranscription: {},
          outputAudioTranscription: {},
          systemInstruction: SYSTEM_INSTRUCTIONS,
          ...(model.endsWith('extended-thinking') ? { thinkingConfig: { thinkingLevel: 'medium' } } : {}),
        },
        callbacks: {
          onopen: () => this.handlers.onStatus?.('connected'),
          onmessage: (message) => this.handleMessage(message),
          onerror: () => this.handlers.onError?.('A conexão de voz apresentou uma falha.'),
          onclose: () => {
            this.session = null;
            this.handlers.onStatus?.('disconnected');
          },
        },
      });
      this.handlers.onStatus?.('connected');
    } catch {
      this.handlers.onStatus?.('disconnected');
      throw new Error('Não foi possível abrir a conversa com o modelo selecionado.');
    }
  }

  handleMessage(message) {
    const content = message.serverContent || {};
    if (content.interrupted) this.player.interrupt();
    if (content.inputTranscription?.text) {
      this.handlers.onUserSpeech?.(content.inputTranscription.text);
    }
    if (content.outputTranscription?.text) {
      this.handlers.onAssistantText?.(content.outputTranscription.text);
    }
    // A API pode enviar várias partes na mesma mensagem.
    for (const part of content.modelTurn?.parts || []) {
      if (part.inlineData?.data && part.inlineData.mimeType?.startsWith('audio/pcm')) {
        this.player.add(part.inlineData.data, part.inlineData.mimeType).catch(() => {
          this.handlers.onError?.('Não foi possível reproduzir o áudio.');
        });
      }
    }
    if (content.turnComplete) this.handlers.onTurnComplete?.();
    // Extended Thinking pode continuar raciocinando após turnComplete.
    if (message.interactionStatus) this.handlers.onStatusDetail?.(message.interactionStatus);
  }

  sendText(text) {
    if (!this.session) throw new Error('Conecte-se antes de enviar uma mensagem.');
    this.session.sendClientContent({
      turns: [{ role: 'user', parts: [{ text }] }],
      turnComplete: true,
    });
  }

  async startMic() {
    if (!this.session) throw new Error('Conecte-se antes de ativar o microfone.');
    if (this.microphone) return;
    this.microphone = new Microphone((audio) => {
      try { this.session?.sendRealtimeInput({ audio }); } catch { /* Sessão encerrada. */ }
    });
    try {
      await this.microphone.start();
      this.audioEnabled = true;
    } catch (error) {
      this.microphone = null;
      throw error;
    }
  }

  async stopMic() {
    const mic = this.microphone;
    this.microphone = null;
    this.audioEnabled = false;
    if (mic) await mic.stop();
    try { this.session?.sendRealtimeInput({ audioStreamEnd: true }); } catch { /* Sessão encerrada. */ }
  }

  async disconnect() {
    await this.stopMic();
    this.session?.close();
    this.session = null;
    await this.player.close();
    this.handlers.onStatus?.('disconnected');
  }
}
