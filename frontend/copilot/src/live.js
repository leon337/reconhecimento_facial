import { GoogleGenAI, Modality, StartSensitivity, EndSensitivity } from '@google/genai';
import { registrationTool, REGISTRATION_FUNCTION_NAME, sanitizeRegistrationDraft } from './registration.js';
import { onboardingSuggestionTool, ONBOARDING_FUNCTION_NAME, ONBOARDING_NAVIGATION_NAME, ONBOARDING_OPERATION_NAME, sanitizeOnboardingSuggestions, sanitizeOnboardingNavigation, sanitizeOnboardingOperation } from './onboarding-suggestions.js';
import { appNavigationTool, APP_NAVIGATION_NAME, sanitizeAppNavigation } from './app-navigation.js';
import { AudioPlayer, Microphone } from './audio.js';
import { classifyLiveFailure, liveSessionClosedMessage, safeCloseCode } from './live-connection-diagnostics.js';

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
  constructor(handlers = {}, dependencies = {}) {
    this.handlers = handlers;
    // Factories injectable only for deterministic, credential-free tests.
    this.fetchFn = dependencies.fetchFn || ((...args) => fetch(...args));
    this.createClient = dependencies.createClient || ((token) => new GoogleGenAI({
      apiKey: token,
      // Token efêmero Live exige v1alpha (não alterar sem teste de integração).
      httpOptions: { apiVersion: 'v1alpha' },
    }));
    this.connectionAttempt = null;
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

  async connect(model, csrf, options = {}) {
    if (!MODEL_IDS.includes(model)) throw new Error('Modelo não autorizado.');
    if (this.session) return;
    if (this.connectionAttempt) throw new Error('Já existe uma conexão em andamento [LIVE_CONNECT_BUSY].');
    const attempt = { opened:false, closed:false, errored:false, ready:false, closeCode:null, errorReported:false };
    this.connectionAttempt = attempt;
    try {
      await this.connectAttempt(attempt, model, csrf, options);
    } catch (error) {
      if (this.connectionAttempt === attempt) this.connectionAttempt = null;
      throw error;
    }
  }

  async connectAttempt(attempt, model, csrf, { allowEmployeeActions = false, allowOnboardingSuggestions = false, persistentShell = false } = {}) {
    const isCurrent = () => this.connectionAttempt === attempt;
    // Extended Thinking não emitiu toolCall no teste real 11/11/2026.
    // Cadastro por voz exige o modelo Live padrão; Extended mantém orientação.
    this.onboardingMode = Boolean(allowOnboardingSuggestions) && !persistentShell;
    this.allowOnboardingSuggestions = Boolean(allowOnboardingSuggestions) && model === 'gemini-3.8-live';
    this.allowEmployeeActions = (!this.onboardingMode || persistentShell) && Boolean(allowEmployeeActions) && model === 'gemini-3.8-live';
    this.allowAppNavigation = (!this.onboardingMode || persistentShell) && model === 'gemini-3.8-live';
    // Navegações concorrentes do iframe podem atualizar o cookie da sessão.
    // Emitir um CSRF imediatamente antes do POST evita usar um token antigo do HTML.
    this.handlers.onStatusDetail?.('validando_csrf');
    let csrfResponse;
    try {
      csrfResponse = await this.fetchFn('/admin/copilot/csrf-token', {
        credentials: 'same-origin', cache: 'no-store',
        headers: { Accept: 'application/json' },
      });
    } catch {
      throw new Error('Não foi possível consultar a sessão [LIVE_CSRF_NETWORK].');
    }
    if (!csrfResponse.ok) throw new Error(`Sessão não validada [LIVE_CSRF_HTTP_${csrfResponse.status}].`);
    const freshCsrf = await csrfResponse.json().catch(() => ({}));
    if (!freshCsrf || typeof freshCsrf.csrf_token !== 'string' || !freshCsrf.csrf_token)
      throw new Error('Resposta CSRF inválida [LIVE_CSRF_INVALID].');

    this.handlers.onStatusDetail?.('solicitando_token');
    let response;
    try {
      response = await this.fetchFn('/admin/copilot/session-token', {
        method: 'POST', credentials: 'same-origin', cache: 'no-store',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': freshCsrf.csrf_token },
        body: JSON.stringify({ model }),
      });
    } catch {
      throw new Error('Falha de rede na emissão do token [LIVE_TOKEN_NETWORK].');
    }
    const rawPayload = await response.json().catch(() => ({}));
    const payload = rawPayload && typeof rawPayload === 'object' ? rawPayload : {};
    if (!response.ok) {
      // A API já aplica cooldown/quotas no servidor. Sem tentativas automáticas.
      const hint = response.status === 429
        ? (payload.error === 'Aguarde antes de iniciar outra sessão.'
            ? 'Aguarde 15 segundos antes de tentar novamente.'
            : 'Limite temporário de sessões. Não tente repetidamente.')
        : response.status === 403 || response.status === 400
          ? 'Sessão ou solicitação recusada.' : 'Serviço Live indisponível.';
      throw new Error(`${hint} [LIVE_TOKEN_HTTP_${response.status}].`);
    }
    if (typeof payload.token !== 'string' || !payload.token || payload.model !== model)
      throw new Error('Resposta de token inválida [LIVE_TOKEN_INVALID].');
    if (!isCurrent()) throw new Error('Conexão interrompida [LIVE_CANCELLED].');

    this.handlers.onStatusDetail?.('negociando_websocket');
    let ai;
    try { ai = this.createClient(payload.token); }
    catch { throw new Error('Não foi possível inicializar o cliente Live [LIVE_SDK_INIT].'); }
    try {
      const openedSession = await ai.live.connect({
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
                'Use operate_onboarding para consultar estado, salvar rascunho, mostrar campo, pular opcional ou request_completion quando estiver na etapa 7 e a pessoa solicitar a conclusão. request_completion mostra a revisão e exige que o humano confirme na interface; não cria funcionário. Aguarde recibos.',
                'Apenas valores explicitamente informados podem entrar nos campos seguros. Campos protegidos permanecem locais. Nenhuma ferramenta cria funcionário diretamente: a pessoa confirma na interface após revisar; nunca afirme cadastro concluído antes do resultado verificado do Flask.',
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
          onopen: () => {
            if (!isCurrent()) return;
            attempt.opened = true;
            this.handlers.onStatusDetail?.('websocket_aberto');
          },
          onmessage: (message) => {
            if (!isCurrent()) return;
            if (message?.setupComplete) this.handlers.onStatusDetail?.('setup_live_confirmado');
            this.handleMessage(message);
          },
          onerror: () => {
            if (!isCurrent()) return;
            attempt.errored = true;
            // O evento do SDK pode conter URL/token; nunca registrar ou exibir e.message.
            if (attempt.ready && !attempt.errorReported) {
              attempt.errorReported = true;
              this.handlers.onError?.(classifyLiveFailure(attempt));
            }
          },
          onclose: (event) => {
            if (!isCurrent()) return;
            attempt.closed = true;
            attempt.closeCode = safeCloseCode(event);
            this.session = null;
            this.stopMic().catch(() => {});
            this.player.close().catch(() => {});
            this.handlers.onStatus?.('disconnected');
            if (attempt.ready && !attempt.errorReported) {
              attempt.errorReported = true;
              this.handlers.onError?.(liveSessionClosedMessage(attempt));
            }
            this.connectionAttempt = null;
          },
        },
      });
      // Um onerror/onclose pode chegar antes de o SDK resolver connect().
      // Nunca indicar conectado se a sessão já foi encerrada ou substituída.
      if (!isCurrent() || attempt.closed || attempt.errored) {
        try { openedSession.close(); } catch { /* conexão já encerrada */ }
        throw new Error('Live interrompido durante a negociação.');
      }
      this.session = openedSession;
      attempt.ready = true;
      this.handlers.onStatus?.('connected');
    } catch {
      if (isCurrent()) {
        this.session = null;
        this.handlers.onStatus?.('disconnected');
      }
      throw new Error(classifyLiveFailure(attempt));
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
        'awaiting_human_review','awaiting_human_confirmation','no_eligible_suggestions','denied','execution_failed',
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
    // Invalida callbacks atrasados de sessões anteriores sem desconectar a nova.
    this.connectionAttempt = null;
    await this.stopMic();
    const oldSession = this.session;
    this.session = null;
    oldSession?.close();
    await this.player.close();
    this.handlers.onStatus?.('disconnected');
  }
}
