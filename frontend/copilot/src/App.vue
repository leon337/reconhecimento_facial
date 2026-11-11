<script setup>
import { computed, onMounted, onUnmounted, ref, nextTick } from 'vue';
import { PotiguarLive } from './live.js';
import { validRegistrationDraft } from './registration.js';

const props = defineProps({ csrf: { type: String, required: true } });
const meta = ref({ enabled: false, configured: false, can_create_user: false, links: {}, models: [] });
const loading = ref(true);
const connected = ref(false);
const busy = ref(false);
const micActive = ref(false);
const micMode = ref('automatic');
const speechState = ref('idle');
const employeeDraft = ref(null);
const registeredEmployee = ref(null);
const registrationBusy = ref(false);
const draftCard = ref(null);
const consent = ref(false);
const model = ref('gemini-3.8-live');
const textInput = ref('');
const error = ref('');
const detail = ref('');
const transcript = ref(null);
const logEnd = ref(null);
const initial = () => [{
  role: 'guide',
  text: 'Olá! Sou o Copiloto Potiguar. Posso orientar você sobre as funções do sistema. Quando a conversa por IA estiver habilitada, também poderei responder por voz.',
}];
const messages = ref(initial());
let assistantIndex = -1;
let voiceIndex = -1;
const available = computed(() => meta.value.enabled && meta.value.configured);
const canRegister = computed(() => Boolean(meta.value.can_create_with_ai));
const registrationErrors = computed(() => employeeDraft.value ? validRegistrationDraft(employeeDraft.value) : []);

const statusLabel = computed(() => connected.value ? (micActive.value ? 'Ouvindo o microfone' : 'Conversa conectada')
  : available.value ? 'Pronto para conectar' : 'Prévia — IA desativada');

function scrollToLatest() {
  nextTick(() => logEnd.value?.scrollIntoView({ block: 'end', behavior: 'smooth' }));
}
function pushMessage(role, text) {
  messages.value.push({ role, text });
  scrollToLatest();
}
const live = new PotiguarLive({
  onStatus(status) {
    connected.value = status === 'connected';
    if (status !== 'connected') micActive.value = false;
  },
  onStatusDetail(status) { detail.value = String(status).replaceAll('_', ' ').toLowerCase(); },
  onAssistantText(text) {
    voiceIndex = -1;
    if (assistantIndex === -1) {
      pushMessage('assistant', text);
      assistantIndex = messages.value.length - 1;
    } else {
      messages.value[assistantIndex].text += text;
    }
    scrollToLatest();
  },
  onUserSpeech(text) {
    assistantIndex = -1;
    if (voiceIndex === -1) {
      pushMessage('user', text);
      voiceIndex = messages.value.length - 1;
    } else {
      messages.value[voiceIndex].text += text;
    }
    scrollToLatest();
  },
  onTurnComplete() {
    assistantIndex = -1;
    voiceIndex = -1;
  },
  onEmployeeDraft(draft) {
    if (!canRegister.value) return;
    registeredEmployee.value = null;
    employeeDraft.value = { ...draft, request_id: crypto.randomUUID() };
    pushMessage('guide', 'Preparei um rascunho. Revise os campos no cartão e clique em Confirmar e cadastrar quando estiver correto.');
    nextTick(() => draftCard.value?.scrollIntoView({ block: 'center', behavior: 'smooth' }));
  },
  onSpeechState(state) { speechState.value = state; },
  onError(message) { error.value = message; },
});

async function loadMeta() {
  try {
    const response = await fetch('/admin/copilot/meta', {
      credentials: 'same-origin', cache: 'no-store', headers: { Accept: 'application/json' },
    });
    if (!response.ok) throw new Error('Não foi possível verificar suas permissões.');
    meta.value = await response.json();
  } catch (e) {
    error.value = e.message;
  } finally {
    loading.value = false;
  }
}

function startEmployeeDraft() {
  if (!canRegister.value || registrationBusy.value) return;
  registeredEmployee.value = null;
  employeeDraft.value = {
    request_id: crypto.randomUUID(), name: '', username: '',
    registration: '', job_title: '', schedule: '',
  };
  nextTick(() => draftCard.value?.scrollIntoView({ block: 'center', behavior: 'smooth' }));
}

async function confirmEmployee() {
  if (!canRegister.value || !employeeDraft.value || registrationErrors.value.length || registrationBusy.value) return;
  error.value = '';
  registrationBusy.value = true;
  try {
    const response = await fetch('/admin/copilot/employee-create', {
      method: 'POST', credentials: 'same-origin', cache: 'no-store',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': props.csrf },
      body: JSON.stringify(employeeDraft.value),
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.error || 'Cadastro não autorizado.');
    registeredEmployee.value = data;
    employeeDraft.value = null;
    pushMessage('guide', 'O servidor confirmou o cadastro. A senha inicial está no cartão seguro; a biometria ainda precisa do fluxo oficial.');
  } catch (e) {
    error.value = e.message;
  } finally {
    registrationBusy.value = false;
  }
}

function cancelEmployeeDraft() {
  employeeDraft.value = null;
}

async function toggleConnection() {
  error.value = '';
  if (busy.value) return;
  busy.value = true;
  try {
    if (connected.value) {
      await live.disconnect();
      transcript.value = null;
    } else {
      if (!consent.value) throw new Error('Confirme o aviso de privacidade para iniciar.');
      if (!available.value) throw new Error('O administrador ainda não habilitou a integração por IA.');
      await live.connect(model.value, props.csrf, { allowEmployeeActions: canRegister.value });
      pushMessage('guide', 'Conexão ativa. Você pode digitar ou ativar o microfone. Para registrar dados reais, utilize as telas oficiais.');
    }
  } catch (e) {
    error.value = e.message;
  } finally {
    busy.value = false;
  }
}

function send() {
  const message = textInput.value.trim();
  if (!message || !connected.value || message.length > 1200) return;
  error.value = '';
  try {
    live.sendText(message);
    voiceIndex = -1;
    assistantIndex = -1;
    pushMessage('user', message);
    textInput.value = '';
  } catch (e) {
    error.value = e.message;
  }
}

async function toggleMic() {
  error.value = '';
  try {
    if (micActive.value) {
      await live.stopMic();
      micActive.value = false;
    } else {
      await live.startMic(micMode.value);
      micActive.value = true;
    }
  } catch (e) {
    micActive.value = false;
    error.value = e.message;
  }
}

function ask(prompt) {
  if (connected.value) {
    textInput.value = prompt;
    send();
    return;
  }
  const localGuidance = {
    'Como cadastro um novo funcionário?': 'Na barra lateral, acesse Funcionários e selecione Novo funcionário. O cadastro e a biometria são concluídos no fluxo oficial, com permissões e validação.',
    'Onde encontro a lista de funcionários?': 'Use Funcionários na barra lateral para consultar a lista disponível à sua conta. O acesso e os resultados são controlados pelo sistema.',
    'Como funciona a validação do ponto eletrônico?': 'O registro oficial exige os controles de identidade, horário e jornada definidos pelo sistema. A conversa com IA não registra ponto por conta própria.',
  };
  pushMessage('user', prompt);
  pushMessage('guide', localGuidance[prompt] || 'Utilize os links oficiais da barra lateral. Para outras perguntas, peça ao administrador que habilite a IA.');
}

function resetConversation() {
  messages.value = initial();
  assistantIndex = -1;
  voiceIndex = -1;
  // Se há confirmação pendente, mantê-la visível até decisão humana.
}

onMounted(loadMeta);
onUnmounted(() => { live.disconnect(); });
</script>

<template>
  <div class="shell">
    <aside class="sidebar" aria-label="Navegação do copiloto">
      <div class="brand">
        <span class="brand-mark" aria-hidden="true">P</span>
        <div><strong>POTIGUAR</strong><span>Gestão de ponto</span></div>
      </div>

      <div class="sidebar-label">ESPAÇO DE TRABALHO</div>
      <div class="side-item active"><span aria-hidden="true">✦</span> Copiloto de IA</div>
      <a class="side-item" :href="meta.links.users || '/admin/users'">
        <span aria-hidden="true">▤</span> Funcionários <span aria-hidden="true" class="side-arrow">↗</span>
      </a>
      <a v-if="meta.can_create_user && meta.links.new_user" class="side-item" :href="meta.links.new_user">
        <span aria-hidden="true">＋</span> Novo funcionário <span aria-hidden="true" class="side-arrow">↗</span>
      </a>
      <div class="sidebar-spacer"></div>
      <div class="notice">
        <strong>Ambiente de avaliação</strong>
        <p>O copiloto apenas orienta. Não altera ponto, funcionários ou biometria.</p>
      </div>
      <a class="return-link" :href="meta.links.users || '/admin/users'">← Voltar ao sistema</a>
    </aside>

    <main class="workspace">
      <header class="topbar">
        <div>
          <div class="eyebrow">INTELIGÊNCIA ASSISTIVA <span class="dot" aria-hidden="true"></span> MVP</div>
          <h1>Copiloto Potiguar</h1>
          <p class="subtitle">Seu assistente de navegação e orientação por voz.</p>
        </div>
        <span class="status" :class="{ online: connected }" role="status" aria-live="polite">
          <span class="status-dot" aria-hidden="true"></span> {{ statusLabel }}
        </span>
      </header>

      <div class="content-grid">
        <section class="conversation" aria-label="Conversa com o copiloto">
          <div class="conversation-top">
            <div><span class="small-caps">CONVERSA</span><p>O histórico não é salvo aqui. Quando conectado, suas mensagens são processadas pelo Gemini.</p></div>
            <button class="clear-button" type="button" @click="resetConversation" aria-label="Limpar mensagens desta sessão">Limpar</button>
          </div>

          <div class="chat-log" role="log" aria-live="polite" aria-relevant="additions text">
            <div v-for="(message, index) in messages" :key="index" class="bubble-row" :class="message.role">
              <span class="avatar" aria-hidden="true">{{ message.role === 'user' ? 'V' : '✦' }}</span>
              <div class="bubble">
                <strong>{{ message.role === 'user' ? 'Você' : message.role === 'guide' ? 'Guia Potiguar' : 'Copiloto IA' }}</strong>
                <p>{{ message.text }}</p>
              </div>
            </div>
            <div ref="logEnd"></div>
          </div>

          <div class="composer">
            <p v-if="error" class="error" role="alert">{{ error }}</p>
            <p v-if="detail && connected" class="thinking" aria-live="polite">Estado da IA: {{ detail }}</p>
            <form @submit.prevent="send" class="prompt-form">
              <label for="question" class="sr-only">Mensagem para o copiloto</label>
              <input id="question" v-model="textInput" maxlength="1200" :disabled="!connected"
                :placeholder="connected ? 'Pergunte ou peça uma orientação…' : 'Conecte-se para conversar com a IA'" autocomplete="off">
              <button class="send-button" type="submit" :disabled="!connected || !textInput.trim()" aria-label="Enviar mensagem">↑</button>
            </form>
            <div class="composer-bottom">
              <button type="button" class="microphone" :class="{ recording: micActive }" @click="toggleMic"
                :disabled="!connected" :aria-pressed="micActive">
                <span aria-hidden="true">{{ micActive ? '◼' : '🎙' }}</span>
                {{ micActive ? 'Parar microfone' : 'Conversar por voz' }}
              </button>
              <span v-if="micActive && micMode === 'automatic'" aria-live="polite">{{ speechState === 'speaking' ? 'Fala detectada' : 'Aguardando fala — ruídos filtrados' }}</span>
              <span v-else>Sem registro automático de ponto</span>
            </div>
          </div>
        </section>

        <aside class="assist-panel" aria-label="Configuração e sugestões">
          <div class="panel-card accent-card">
            <div class="panel-icon" aria-hidden="true">✧</div>
            <span class="small-caps">ASSISTÊNCIA EM TEMPO REAL</span>
            <h2>Converse com o sistema.</h2>
            <p>Utilize sua voz ou escreva. A IA explica os caminhos e você continua no controle.</p>
          </div>

          <div class="panel-card control-card">
            <h2>Configurar conversa</h2>
            <label for="model">Modelo de IA</label>
            <select id="model" v-model="model" :disabled="connected || busy || loading">
              <option value="gemini-3.8-live">Gemini 3.8 Live · rápido</option>
              <option value="gemini-3.8-live-extended-thinking">Gemini 3.8 Live · raciocínio avançado</option>
            </select>
            <p v-if="canRegister && model.endsWith('extended-thinking')" class="config-note">
              Para preparar cadastros automaticamente pela conversa, selecione Gemini 3.8 Live · rápido. O Extended Thinking não passou no teste de ferramentas.
            </p>
            <label for="mic-mode">Modo do microfone</label>
            <select id="mic-mode" v-model="micMode" :disabled="micActive">
              <option value="automatic">Automático — filtrar ruídos (VAD)</option>
              <option value="manual">Manual — tocar para iniciar/parar</option>
            </select>
            <p class="config-note">Em ambientes barulhentos, prefira o modo manual. O VAD automático pode não distinguir toda música ou fala distante.</p>
            <label class="consent">
              <input type="checkbox" v-model="consent" :disabled="connected">
              <span>Consinto no processamento das minhas falas e, se eu ditar um cadastro, do nome e dos dados funcionais informados pelo Gemini. Não direi senhas, documentos ou informações biométricas.</span>
            </label>
            <button class="connect-button" type="button" :disabled="loading || busy || (!connected && (!available || !consent))"
              @click="toggleConnection">
              {{ busy ? 'Conectando…' : connected ? 'Encerrar conversa' : 'Iniciar conversa com IA' }}
            </button>
            <p v-if="!loading && !available" class="config-note">
              A integração está desativada ou sem credencial. Esta é uma prévia visual; o administrador pode habilitá-la em ambiente de teste.
            </p>
          </div>

          <div v-if="canRegister" class="panel-card registration-panel" ref="draftCard">
            <h2>Cadastro assistido</h2>
            <p class="registration-note">Diga ao Gemini: “Cadastre uma funcionária chamada Maria de Teste, usuário maria.teste”. Ele prepara os campos; só você confirma a gravação.</p>
            <button v-if="!employeeDraft && !registeredEmployee" class="connect-button" type="button" @click="startEmployeeDraft">
              Iniciar cadastro assistido
            </button>
            <form v-if="employeeDraft" class="registration-form" @submit.prevent="confirmEmployee" aria-label="Revisar cadastro proposto pela IA">
              <label for="emp-name">Nome completo *</label>
              <input id="emp-name" v-model="employeeDraft.name" maxlength="120" required autocomplete="off">
              <label for="emp-username">Usuário de acesso *</label>
              <input id="emp-username" v-model="employeeDraft.username" maxlength="64" required autocapitalize="off" autocomplete="off">
              <label for="emp-registration">Matrícula</label>
              <input id="emp-registration" v-model="employeeDraft.registration" maxlength="50" autocomplete="off">
              <label for="emp-role">Função</label>
              <input id="emp-role" v-model="employeeDraft.job_title" maxlength="80">
              <label for="emp-schedule">Horário</label>
              <input id="emp-schedule" v-model="employeeDraft.schedule" maxlength="120">
              <p v-if="registrationErrors.length" class="error" role="status">{{ registrationErrors[0] }}</p>
              <p class="registration-note">A senha inicial será gerada somente após confirmar. Nenhuma biometria ou marcação de ponto será criada.</p>
              <div class="registration-actions">
                <button type="button" @click="cancelEmployeeDraft" :disabled="registrationBusy">Cancelar</button>
                <button type="submit" class="connect-button" :disabled="registrationBusy || registrationErrors.length > 0">
                  {{ registrationBusy ? 'Salvando…' : 'Confirmar e cadastrar' }}
                </button>
              </div>
            </form>
            <div v-if="registeredEmployee" class="registration-result" role="status">
              <strong>Funcionário cadastrado após confirmação</strong>
              <p>{{ registeredEmployee.name }} ({{ registeredEmployee.username }})</p>
              <label for="initial-password">Senha inicial (mostrar somente ao administrador)</label>
              <input id="initial-password" :value="registeredEmployee.temporary_password" readonly autocomplete="off">
              <p class="registration-note">Entregue a senha por canal seguro. Ela não será enviada ao Gemini e desaparecerá ao sair da página. A biometria continua pendente.</p>
              <button class="connect-button" type="button" @click="registeredEmployee = null; startEmployeeDraft()">Novo cadastro</button>
            </div>
          </div>

          <div class="panel-card suggestions">
            <h2>Experimente perguntar</h2>
            <button type="button" @click="ask('Como cadastro um novo funcionário?')">Como cadastro um funcionário? <span aria-hidden="true">↗</span></button>
            <button type="button" @click="ask('Onde encontro a lista de funcionários?')">Onde consulto os funcionários? <span aria-hidden="true">↗</span></button>
            <button type="button" @click="ask('Como funciona a validação do ponto eletrônico?')">Como funciona o registro de ponto? <span aria-hidden="true">↗</span></button>
          </div>
        </aside>
      </div>
    </main>
  </div>
</template>
