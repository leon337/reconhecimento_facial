import { GoogleGenAI, Modality, StartSensitivity, EndSensitivity } from '@google/genai';
import { registrationTool, REGISTRATION_FUNCTION_NAME, sanitizeRegistrationDraft } from './registration.js';
import { AudioPlayer, Microphone } from './audio.js';

const MODEL_IDS = ['gemini-3.8-live', 'gemini-3.8-live-extended-thinking'];
const SYSTEM_INSTRUCTIONS = [
  'Você é o Copiloto Potiguar, assistente de navegação do Sistema de Ponto Potiguar.',
  'Fale sempre em português do Brasil com clareza e acessibilidade.',
  'Este ambiente permite preparar um RASCUNHO de cadastro, mas o cadastro só ocorre após confirmação explícita do humano.',
  'Ajude o usuário a entender onde consultar funcionários, iniciar um cadastro ou buscar informações.',
  'Nunca diga que registrou ponto, aprovou ajuste, cadastrou funcionário, reconheceu rosto ou executou qualquer operação real. O resultado da ferramenta de rascunho não é criação.',
  'Não peça senhas, chaves, documentos oficiais ou imagem facial. Se a pessoa pedir o cadastro, obtenha nome, usuário e dados funcionais mínimos, com consentimento para processamento externo.',
  'Quando necessário, recomende o uso dos controles oficiais da interface e de seus mecanismos de validação.',
  'Se o usuário pedir cadastro de funcionário, use prepare_employee_registration somente para preparar o rascunho na interface. A confirmação e persistência ocorrem exclusivamente fora do modelo.',
].join('\n');

export class PotiguarLive {
  constructor(handlers = {}) {
    this.handlers = handlers;
    this.session = null;
    this.microphone = null;
    this.player = new AudioPlayer();
    this.audioEnabled = false;
    this.allowEmployeeActions = false;
  }

  async connect(model, csrf, { allowEmployeeActions = false } = {}) {
    if (!MODEL_IDS.includes(model)) throw new Error('Modelo não autorizado.');
    if (this.session) return;
    // Extended Thinking não emitiu toolCall no teste real 11/11/2026.
    // Cadastro por voz exige o modelo Live padrão; Extended mantém orientação.
    this.allowEmployeeActions = Boolean(allowEmployeeActions) && model === 'gemini-3.8-live';
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
          systemInstruction: this.allowEmployeeActions
            ? SYSTEM_INSTRUCTIONS
            : SYSTEM_INSTRUCTIONS.replace(
                'use prepare_employee_registration somente para preparar o rascunho na interface.',
                'oriente a abrir o cartão de cadastro assistido, sem afirmar que cadastrou.',
              ),
          realtimeInputConfig: {
            automaticActivityDetection: {
              disabled: false,
              startOfSpeechSensitivity: StartSensitivity.START_SENSITIVITY_LOW,
              endOfSpeechSensitivity: EndSensitivity.END_SENSITIVITY_LOW,
              prefixPaddingMs: 220,
              silenceDurationMs: 750,
            },
          },
          ...(this.allowEmployeeActions ? { tools: [registrationTool] } : {}),
          ...(model.endsWith('extended-thinking') ? { thinkingConfig: { thinkingLevel: 'medium' } } : {}),
        },
        callbacks: {
          onopen: () => this.handlers.onStatus?.('connected'),
          onmessage: (message) => this.handleMessage(message),
          onerror: () => this.handlers.onError?.('A conexão de voz apresentou uma falha.'),
          onclose: () => {
            this.session = null;
            // Nunca manter o microfone aberto após uma queda de rede.
            this.stopMic().catch(() => {});
            this.player.close().catch(() => {});
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
    if (message.toolCall?.functionCalls?.length) this.handleToolCalls(message.toolCall.functionCalls);
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

  handleToolCalls(calls) {
    const functionResponses = [];
    for (const call of calls) {
      if (!call?.id || !call?.name) continue;
      if (call.name !== REGISTRATION_FUNCTION_NAME || !this.allowEmployeeActions) {
        functionResponses.push({
          id: call.id, name: call.name,
          response: { status: 'denied', reason: 'function_not_allowed' },
        });
        continue;
      }
      try {
        const raw = typeof call.args === 'string' ? JSON.parse(call.args) : call.args;
        const draft = sanitizeRegistrationDraft(raw);
        this.handlers.onEmployeeDraft?.(draft);
        functionResponses.push({
          id: call.id, name: call.name,
          response: { status: 'awaiting_human_review', created: false },
        });
      } catch {
        functionResponses.push({
          id: call.id, name: call.name,
          response: { status: 'invalid_draft', created: false },
        });
      }
    }
    if (functionResponses.length) {
      try {
        this.session?.sendToolResponse({ functionResponses });
      } catch {
        this.handlers.onError?.('O Gemini não conseguiu preparar o cadastro assistido.');
      }
    }
  }

  sendText(text) {
    if (!this.session) throw new Error('Conecte-se antes de enviar uma mensagem.');
    this.session.sendClientContent({
      turns: [{ role: 'user', parts: [{ text }] }],
      turnComplete: true,
    });
  }

  async startMic(mode = 'automatic') {
    if (!this.session) throw new Error('Conecte-se antes de ativar o microfone.');
    if (this.microphone) return;
    this.microphone = new Microphone((audio) => {
      try { this.session?.sendRealtimeInput({ audio }); } catch { /* Sessão encerrada. */ }
    }, {
      mode,
      onSpeechState: (state) => this.handlers.onSpeechState?.(state),
      onTurnEnd: () => {
        try { this.session?.sendRealtimeInput({ audioStreamEnd: true }); }
        catch { /* Sessão encerrada. */ }
      },
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
    const shouldEndTurn = mic && (mic.mode === 'manual' || mic.voiceGate.active);
    if (mic) await mic.stop();
    if (shouldEndTurn) {
      try { this.session?.sendRealtimeInput({ audioStreamEnd: true }); } catch { /* Sessão encerrada. */ }
    }
  }

  async disconnect() {
    await this.stopMic();
    this.session?.close();
    this.session = null;
    await this.player.close();
    this.handlers.onStatus?.('disconnected');
  }
}
