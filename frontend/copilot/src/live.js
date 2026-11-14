import { GoogleGenAI, Modality, StartSensitivity, EndSensitivity } from '@google/genai';
import { registrationTool, REGISTRATION_FUNCTION_NAME, sanitizeRegistrationDraft } from './registration.js';
import { onboardingSuggestionTool, ONBOARDING_FUNCTION_NAME, ONBOARDING_NAVIGATION_NAME, ONBOARDING_OPERATION_NAME, sanitizeOnboardingSuggestions, sanitizeOnboardingNavigation, sanitizeOnboardingOperation } from './onboarding-suggestions.js';
import { appNavigationTool, APP_NAVIGATION_NAME, sanitizeAppNavigation } from './app-navigation.js';
import { AudioPlayer, Microphone } from './audio.js';

const MODEL_IDS = ['gemini-3.8-live', 'gemini-3.8-live-extended-thinking'];
const SYSTEM_INSTRUCTIONS = [
  'Você é o Copiloto Potiguar, assistente de navegação do Sistema de Ponto Potiguar.',
  'Fale sempre em português do Brasil com clareza e acessibilidade.',
  'Este ambiente permite preparar um RASCUNHO de cadastro, mas o cadastro só ocorre após confirmação explícita do humano.',
  'Ajude o usuário a entender onde consultar funcionários, iniciar um cadastro ou buscar informações.',
  'Nunca diga que registrou ponto, aprovou ajuste, cadastrou funcionário, reconheceu rosto ou executou qualquer operação real. O resultado da ferramenta de rascunho não é criação.',
  'Não peça senhas, chaves, documentos oficiais ou imagem facial. Se a pessoa pedir o cadastro, obtenha nome, usuário e dados funcionais mínimos, com consentimento para processamento externo.',
  'Use navigate_potiguar para abrir telas permitidas. No shell persistente, a navegação não encerra a sessão Live; continue acompanhando o usuário após a nova tela carregar.',
  'Nunca afirme que uma ferramenta funcionou antes de receber o recibo da interface.',
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
    this.allowAppNavigation = false;
    this.onboardingMode = false;
    this.allowOnboardingSuggestions = false;
    this.onboardingStep = 0;
    this.onboardingField = null;
  }

  async connect(model, csrf, { allowEmployeeActions = false, allowOnboardingSuggestions = false, persistentShell = false } = {}) {
    if (!MODEL_IDS.includes(model)) throw new Error('Modelo não autorizado.');
    if (this.session) return;
    // Extended Thinking não emitiu toolCall no teste real 11/11/2026.
    // Cadastro por voz exige o modelo Live padrão; Extended mantém orientação.
    this.onboardingMode = Boolean(allowOnboardingSuggestions) && !persistentShell;
    this.allowOnboardingSuggestions = Boolean(allowOnboardingSuggestions) && model === 'gemini-3.8-live';
    this.allowEmployeeActions = (!this.onboardingMode || persistentShell) && Boolean(allowEmployeeActions) && model === 'gemini-3.8-live';
    this.allowAppNavigation = (!this.onboardingMode || persistentShell) && model === 'gemini-3.8-live';
    // Navegações concorrentes do iframe podem atualizar o cookie da sessão.
    // Emitir um CSRF imediatamente antes do POST evita usar um token antigo do HTML.
    const csrfResponse = await fetch('/admin/copilot/csrf-token', {
      credentials: 'same-origin', cache: 'no-store',
      headers: { Accept: 'application/json' },
    });
    if (!csrfResponse.ok) throw new Error('Sessão expirada. Faça login novamente.');
    const freshCsrf = await csrfResponse.json().catch(() => ({}));
    if (!freshCsrf.csrf_token) throw new Error('Não foi possível validar a sessão.');
    const response = await fetch('/admin/copilot/session-token', {
      method: 'POST',
      credentials: 'same-origin',
      cache: 'no-store',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': freshCsrf.csrf_token },
      body: JSON.stringify({ model }),
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(payload.error || 'Conexão não disponível.');
    const ai = new GoogleGenAI({
      apiKey: payload.token,
      // A emissão de tokens efêmeros da Live API utiliza v1alpha (testado em 13/11/2026).
      httpOptions: { apiVersion: 'v1alpha' },
    });
    try {
      this.session = await ai.live.connect({
        model: payload.model,
        config: {
          responseModalities: [Modality.AUDIO],
          inputAudioTranscription: {},
          outputAudioTranscription: {},
          systemInstruction: (this.onboardingMode || persistentShell)
            ? [
                'Você é o Copiloto persistente da Potiguar, presente em todas as telas administrativas autorizadas. Use navigate_potiguar para abrir páginas sem encerrar a sessão Live.',
                'No cadastro V2 atue como guia das oito etapas, somente após receber contexto do formulário.',
                'Responda exclusivamente em português brasileiro. Não invente dados nem preencha sem pedido explícito.',
                'Os valores já digitados no formulário não são enviados à IA.',
                'Não peça CPF, RG, documentos, dados financeiros, senhas, raça/cor, saúde, PCD ou biometria.',
                'Aguarde o controlador informar o campo atual. Faça uma pergunta por vez. Para resposta sobre campo seguro, invoque suggest_onboarding_fields SOMENTE com o campo atual e o valor que o usuário informou. Nunca invente ou infira valores.',
                'Se o usuário disser corrige, altere ou volte a uma etapa, use navigate_onboarding sem enviar qualquer dado existente.',
                'Use operate_onboarding para consultar estado, salvar o rascunho, mostrar o campo no formulário ou pular um campo opcional. Espere o resultado da ferramenta antes de dizer se funcionou.',
                'Apenas valores explicitamente informados podem entrar nos campos seguros. Campos protegidos permanecem locais. Nenhuma ferramenta pode criar o funcionário, ativar credenciais ou finalizar cadastros.',
                'Etapas: 0 Relação, 1 Dados pessoais, 2 Endereço, 3 Vínculo, 4 Pagamento, 5 Acesso, 6 Biometria, 7 Revisão.',
                'Etapas 4 a 7: só oriente; não sugira preenchimento.',
                'Fora do cadastro V2, não use ferramentas do formulário. Não afirme ter executado operações antes de receber o recibo verificado.',
              ].join('\n')
            : this.allowEmployeeActions
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
          ...((this.allowOnboardingSuggestions || this.allowAppNavigation || this.allowEmployeeActions) ? {
            tools: [{functionDeclarations:[
              ...(this.allowAppNavigation ? appNavigationTool.functionDeclarations : []),
              ...(this.allowOnboardingSuggestions ? onboardingSuggestionTool.functionDeclarations : []),
              ...(this.allowEmployeeActions ? registrationTool.functionDeclarations : []),
            ]}],
          } : {}),
          ...(model.endsWith('extended-thinking') ? { thinkingConfig: { thinkingLevel: 'medium' } } : {}),
        },
        callbacks: {
          // WebSocket aberto não significa que o SDK já entregou uma sessão utilizável.
          // Sinalize conectado apenas após await ai.live.connect() concluir.
          onopen: () => this.handlers.onStatusDetail?.('negociando_sessao_live'),
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
    if (message.toolCall?.functionCalls?.length) this.handleToolCalls(message.toolCall.functionCalls)
      .catch(() => this.handlers.onError?.('Falha no processamento das ferramentas do Copiloto.'));
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

  async handleToolCalls(calls) {
    // A resposta ao Gemini é emitida só após a interface executar a ação e devolver o recibo.
    // Não devolver "sucesso" enquanto o controlador estiver aguardando validação/salvamento.
    const session = this.session;
    const functionResponses = [];
    for (const call of calls) {
      if (!call?.id || !call?.name) continue;
      let receipt = {status:'denied',created:false};
      try {
        const raw = typeof call.args === 'string' ? JSON.parse(call.args) : call.args;
        if (call.name === ONBOARDING_NAVIGATION_NAME && this.allowOnboardingSuggestions && this.onboardingMode) {
          const navigation = sanitizeOnboardingNavigation(raw);
          receipt = navigation && this.handlers.onOnboardingNavigation
            ? await this.handlers.onOnboardingNavigation(navigation) : receipt;
        } else if (call.name === ONBOARDING_OPERATION_NAME && this.allowOnboardingSuggestions && this.onboardingMode) {
          const operation = sanitizeOnboardingOperation(raw);
          receipt = operation && this.handlers.onOnboardingAction
            ? await this.handlers.onOnboardingAction(operation) : receipt;
        } else if (call.name === ONBOARDING_FUNCTION_NAME && this.allowOnboardingSuggestions && this.onboardingMode) {
          const suggestions = sanitizeOnboardingSuggestions(raw,this.onboardingStep)
            .filter(item => item.field === this.onboardingField);
          receipt = suggestions.length && this.handlers.onOnboardingSuggestions
            ? await this.handlers.onOnboardingSuggestions(this.onboardingStep,suggestions)
            : {status:'no_eligible_suggestions',created:false};
        } else if (call.name === APP_NAVIGATION_NAME && this.allowAppNavigation) {
          const navigation = sanitizeAppNavigation(raw,this.allowEmployeeActions);
          receipt = navigation && this.handlers.onAppNavigation
            ? await this.handlers.onAppNavigation(navigation) : receipt;
        } else if (call.name === REGISTRATION_FUNCTION_NAME && this.allowEmployeeActions && !this.onboardingMode) {
          const draft = sanitizeRegistrationDraft(raw);
          if (this.handlers.onEmployeeDraft) {
            this.handlers.onEmployeeDraft(draft);
            receipt = {status:'awaiting_human_review',created:false};
          }
        }
      } catch {
        receipt = {status:'execution_failed',created:false};
      }
      // Somente status e metadados não sensíveis atravessam a fronteira da ferramenta.
      const allowed = ['saved','navigated','focused','skipped','state','navigation_started',
        'awaiting_human_review','no_eligible_suggestions','denied','execution_failed',
        'not_available','timeout','invalid_state','validation_failed','conflict'];
      const status = receipt && allowed.includes(receipt.status) ? receipt.status : 'execution_failed';
      const safeResponse = {status,created:false};
      if (Number.isInteger(receipt?.step) && receipt.step>=0 && receipt.step<8) safeResponse.step=receipt.step;
      if (status==='state' && typeof receipt?.field==='string' && /^[a-z_]{2,40}$/.test(receipt.field)) {
        safeResponse.field=receipt.field;
      }
      functionResponses.push({id:call.id,name:call.name,response:safeResponse});
    }
    if (functionResponses.length && session && this.session===session) {
      try { session.sendToolResponse({functionResponses}); }
      catch { this.handlers.onError?.('Não foi possível devolver o resultado da ação ao Gemini.'); }
    }
  }

  setOnboardingMode(enabled) {
    this.onboardingMode = Boolean(enabled) && this.allowOnboardingSuggestions;
    if (!this.onboardingMode) this.onboardingField = null;
  }
  setOnboardingStep(step) { if (Number.isInteger(step) && step>=0 && step<=7) this.onboardingStep=step; }
  setOnboardingField(field) { this.onboardingField=typeof field==='string' && /^[a-z_]{2,40}$/.test(field) ? field : null; }

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
