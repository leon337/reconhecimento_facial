<script setup>
import { computed, onMounted, onUnmounted, ref, nextTick } from 'vue';
import { PotiguarLive } from './live.js';

const props = defineProps({ csrf: { type: String, required: true } });
const meta = ref({ enabled: false, configured: false, can_create_user: false, links: {}, models: [] });
const loading = ref(true);
const connected = ref(false);
const busy = ref(false);
const micActive = ref(false);
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
      await live.connect(model.value, props.csrf);
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
      await live.startMic();
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
              <span>Sem registro automático de ponto</span>
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
            <label class="consent">
              <input type="checkbox" v-model="consent" :disabled="connected">
              <span>Entendo que minhas falas e mensagens serão processadas pelo provedor Gemini. Não informarei senhas nem dados sensíveis.</span>
            </label>
            <button class="connect-button" type="button" :disabled="loading || busy || (!connected && (!available || !consent))"
              @click="toggleConnection">
              {{ busy ? 'Conectando…' : connected ? 'Encerrar conversa' : 'Iniciar conversa com IA' }}
            </button>
            <p v-if="!loading && !available" class="config-note">
              A integração está desativada ou sem credencial. Esta é uma prévia visual; o administrador pode habilitá-la em ambiente de teste.
            </p>
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
