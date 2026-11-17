<script setup>
import { computed, onMounted, onUnmounted, ref, nextTick } from 'vue';
import { PotiguarLive } from './live.js';
import { validRegistrationDraft } from './registration.js';
import { safeAppPath } from './app-navigation.js';
import { isProtectedInput } from './protected-input.js';
import {resolveNaturalSelect} from './onboarding-natural-language.js';
import { isOnboardingFormRoute,isAppFrameRoute,routeReached,isTrustedAppMessage } from './persistent-shell.js';

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
const configCard = ref(null);
const initial = () => [{
  role: 'guide',
  text: 'Olá! Sou o Copiloto Potiguar. Posso orientar você sobre as funções do sistema. Quando a conversa por IA estiver habilitada, também poderei responder por voz.',
}];
const messages = ref(initial());
let assistantIndex = -1;
let voiceIndex = -1;
const available = computed(() => meta.value.enabled && meta.value.configured);
const canRegister = computed(() => Boolean(meta.value.can_create_with_ai));
const registrationErrors = computed(() => {
  if (!employeeDraft.value) return [];
  const errors = validRegistrationDraft(employeeDraft.value);
  if (meta.value.demo_synthetic_only) {
    const d = employeeDraft.value;
    if (!((d.name || '').toLowerCase().endsWith(' de teste') || (d.name || '').toLowerCase().startsWith('teste '))
        || !((d.username || '').endsWith('.teste') || (d.username || '').startsWith('teste.'))
        || !(d.registration || '').toUpperCase().startsWith('TEST-')) {
      errors.push('Homologação: utilize somente nomes de Teste, usuário .teste e matrícula TEST-.');
    }
  }
  return errors;
});

const statusLabel = computed(() => connected.value ? (micActive.value ? 'Ouvindo o microfone' : 'Conversa conectada')
  : available.value ? 'Pronto para conectar' : 'Prévia — IA desativada');

function scrollToLatest() {
  nextTick(() => logEnd.value?.scrollIntoView({ block: 'end', behavior: 'smooth' }));
}
function pushMessage(role, text) {
  messages.value.push({ role, text });
  scrollToLatest();
}
// O iframe pode trocar de documento; este componente, o microfone e o WebSocket não.
const appFrame = ref(null);
const frameSrc = ref('');
const frameRoute = ref('');
const copilotVisible = ref(true);
const settingsVisible = ref(false);
const onboardingQuestion = ref(null);
const onboardingReview = ref(false);
// Só pula opcionais protegidos quando o operador optar explicitamente.
const autoSkipProtected = ref(false);
const skipProtectedBusy = ref(false);
const skippedProtectedCount = ref(0);
let micPausedForProtected = false;
let micPausePromise = Promise.resolve();
const formActive = computed(() => isOnboardingFormRoute(frameRoute.value));
const stageLabel = computed(() => {
  const pairs = [
    ['dashboard','Painel'], ['attendance','Histórico de ponto'],
    ['reports','Relatórios'], ['users','Funcionários'],
    ['drafts','Rascunhos'], ['new_user','Novo funcionário'],
  ];
  if (formActive.value) return 'Cadastro V2 — oito etapas';
  return pairs.find(([key]) => meta.value.links?.[key] === frameRoute.value)?.[1] || 'Aplicação Potiguar';
});
let navigationWaiter = null;
let guideTimer = null;
const pendingActions = new Map();

function resolveNavigation(status) {
  if (!navigationWaiter) return;
  const waiter = navigationWaiter;
  navigationWaiter = null;
  clearTimeout(waiter.timeout);
  waiter.resolve({status,created:false});
}
function cancelPendingActions() {
  for (const pending of pendingActions.values()) {
    clearTimeout(pending.timeout);
    pending.resolve({status:'not_available',created:false});
  }
  pendingActions.clear();
  clearTimeout(guideTimer);
}
function navigateTo(route) {
  if (!isAppFrameRoute(route)) return Promise.resolve({status:'denied',created:false});
  const target = appFrame.value?.contentWindow;
  if (!target) return Promise.resolve({status:'not_available',created:false});
  if (frameRoute.value === route)
    return Promise.resolve({status:'navigated',created:false});
  resolveNavigation('not_available');
  return new Promise(resolve => {
    navigationWaiter = {expected:route,resolve,timeout:setTimeout(() => resolveNavigation('timeout'),12000)};
    try { target.location.assign(route); }
    catch { resolveNavigation('execution_failed'); }
  });
}
function postToForm(type, data = {}) {
  if (!connected.value || !formActive.value || !live.onboardingMode ||
      !appFrame.value?.contentWindow) return Promise.resolve({status:'denied'});
  const requestId = crypto.randomUUID();
  return new Promise(resolve => {
    const timeout=setTimeout(() => {
      pendingActions.delete(requestId);resolve({status:'timeout'});
    },10000);
    pendingActions.set(requestId,{resolve,timeout});
    appFrame.value.contentWindow.postMessage({type,requestId,...data},window.location.origin);
  });
}
function beginGuidedForm() {
  if (!connected.value || !formActive.value || !live.allowOnboardingSuggestions ||
      !appFrame.value?.contentWindow) return;
  live.setOnboardingMode(true);
  appFrame.value.contentWindow.postMessage({type:'potiguar:onboarding:begin'},window.location.origin);
}
// Comandos locais: não enviam valores protegidos para o Gemini.
async function skipCurrentProtectedOptional() {
  const q=onboardingQuestion.value;
  if (!connected.value || !formActive.value || !q || q.safe || q.required || skipProtectedBusy.value) return;
  const originalKey=String(q.step)+':'+q.field;
  skipProtectedBusy.value=true;
  try {
    const receipt=await postToForm('potiguar:onboarding:execute',{action:'skip_optional'});
    if(receipt.status!=='skipped') throw Error('Não foi possível avançar. Confira o formulário.');
    skippedProtectedCount.value++;
  } catch(failure) {
    autoSkipProtected.value=false;
    error.value=failure.message || 'Falha ao avançar no cadastro.';
  } finally {
    skipProtectedBusy.value=false;
    // A pergunta seguinte pode chegar antes do recibo anterior.
    const next=onboardingQuestion.value;
    if(autoSkipProtected.value && next && !next.safe && !next.required &&
       String(next.step)+':'+next.field!==originalKey) {
      queueMicrotask(()=>skipCurrentProtectedOptional());
    }
  }
}
function skipProtectedOptionalsByChoice() {
  autoSkipProtected.value=true;
  pushMessage('guide','Você optou por adiar os campos opcionais protegidos. Eles ficam em branco; confira CPF, contatos, pagamento e demais dados necessários no formulário antes de concluir.');
  void skipCurrentProtectedOptional();
}
function openCurrentProtectedField() {
  const q=onboardingQuestion.value;
  if(!q || q.safe) return;
  void postToForm('potiguar:onboarding:execute',{action:'focus_current_field'})
    .then(receipt=>{
      if(receipt.status!=='focused') error.value='Não foi possível abrir o campo.';
      else copilotVisible.value=false;
    });
}
function scheduleGuide(data) {
  clearTimeout(guideTimer);
  const text = `CONTROLE DO FORMULÁRIO: etapa ${data.step+1}; campo ${data.field} (${data.label});
${data.required?'obrigatório':'opcional'}; opções: ${Array.isArray(data.options)?data.options.join(', '):'texto livre'}.
Pergunte somente esse campo em português brasileiro. Para resposta explícita, use
suggest_onboarding_fields APENAS para ${data.field}. Nunca infira, nunca confirme gravação antes do recibo.
Comandos de navegação usam navigate_onboarding ou operate_onboarding.`;
  const attempt=() => {
    if (!connected.value || !formActive.value || !onboardingQuestion.value?.safe ||
        onboardingQuestion.value.field!==data.field || onboardingQuestion.value.step!==data.step)return;
    if(pendingActions.size){guideTimer=setTimeout(attempt,500);return;}
    try { live.sendText(text); }
    catch {error.value='Não foi possível continuar as perguntas do formulário.';}
  };
  guideTimer=setTimeout(attempt,750);
}
function onAppFrameMessage(event) {
  if (!isTrustedAppMessage(event,appFrame.value?.contentWindow,window.location.origin))return;
  const data=event.data;
  if(data.type==='potiguar:onboarding:result' && typeof data.requestId==='string') {
    const pending=pendingActions.get(data.requestId);
    if(pending) {
      pendingActions.delete(data.requestId);
      clearTimeout(pending.timeout);
      pending.resolve({status:typeof data.status==='string'?data.status:'execution_failed',
        step:data.step,field:data.field});
    }
    return;
  }
  if(!formActive.value && data.type!=='potiguar:shell:onboarding-ready')return;
  if(data.type==='potiguar:shell:onboarding-ready' && Number.isInteger(data.step)){
    live.setOnboardingStep(data.step);
    return;
  }
  if(data.type==='potiguar:shell:show-form'){
    copilotVisible.value=false;return;
  }
  if(data.type==='potiguar:onboarding:context' && Number.isInteger(data.step) &&
      data.step>=0 && data.step<8) {
    live.setOnboardingStep(data.step);return;
  }
  if(data.type==='potiguar:onboarding:question' && Number.isInteger(data.step) &&
      data.step>=0 && data.step<8 && typeof data.field==='string' &&
      /^[a-z_]{2,40}$/.test(data.field) && typeof data.label==='string') {
    live.setOnboardingStep(data.step);
    live.setOnboardingField(data.safe?data.field:null);
    onboardingReview.value=false;
    onboardingQuestion.value={step:data.step,field:data.field,label:data.label,
      safe:!!data.safe,required:!!data.required,
      options:Array.isArray(data.options)?data.options.filter(option=>typeof option==='string'&&option.length<90):[]};
    if(!data.safe) {
      clearTimeout(guideTimer);
      if(micActive.value) micPausedForProtected=true;
      micPausePromise=live.stopMic().catch(()=>{});
      micActive.value=false;
      if(!data.required && autoSkipProtected.value) void skipCurrentProtectedOptional();
      if(!autoSkipProtected.value || data.required)
        pushMessage('guide','Campo protegido: '+data.label+'. '+
          (data.required
            ? 'Obrigatório: preencha no formulário, sem ditar.'
            : 'Preencha no formulário ou pule o campo opcional. Nunca dite esse valor.'));
    } else {
      pushMessage('guide',`Etapa ${data.step+1}: ${data.label}. Informe um campo por vez.`);
      if(connected.value) scheduleGuide(data);
      if(connected.value && micPausedForProtected) {
        micPausedForProtected=false;
        void micPausePromise.then(async()=>{
          if(!connected.value || !formActive.value || onboardingQuestion.value?.field!==data.field)return;
          await live.startMic(micMode.value);
          micActive.value=true;
        }).catch(()=>{error.value='Para retomar a voz, clique em Conversar por voz.';});
      }
    }
    return;
  }
  if(data.type==='potiguar:onboarding:filled') {
    pushMessage('guide','Campo validado e salvo no rascunho.');
    return;
  }
  if(data.type==='potiguar:onboarding:review') {
    live.setOnboardingField(null);
    onboardingQuestion.value=null;onboardingReview.value=true;
    pushMessage('guide','Revisão final: confira todos os dados. '+
      (skippedProtectedCount.value
        ? 'Atenção: '+skippedProtectedCount.value+' campos opcionais protegidos foram adiados; preencha os necessários no formulário antes da confirmação. '
        : '')+
      'Em ambiente protegido, peça para mostrar a conclusão e confirme diretamente no formulário.');
    return;
  }
  if(data.type==='potiguar:onboarding:completed') {
    pushMessage('guide','Cadastro confirmado pelo servidor após sua aprovação. Consulte a lista de funcionários.');
    onboardingReview.value=false;
    return;
  }
  if(data.type==='potiguar:onboarding:error') {
    pushMessage('guide','O formulário não validou ou salvou o campo. Corrija-o na tela.');
  }
}
async function onAppFrameLoad() {
  const frame=appFrame.value;
  if(!frame)return;
  let route='';
  try {
    if(frame.contentWindow.location.origin!==window.location.origin)throw Error('origin');
    route=frame.contentWindow.location.pathname;
  } catch {
    error.value='A navegação saiu da origem autorizada. A sessão de voz foi encerrada por segurança.';
    resolveNavigation('denied');cancelPendingActions();
    await live.disconnect();return;
  }
  if(route==='/admin/login'){
    resolveNavigation('denied');cancelPendingActions();
    await live.disconnect();window.location.assign('/admin/login');return;
  }
  if(!isAppFrameRoute(route)) {
    resolveNavigation('denied');
    error.value='Esta tela não está autorizada dentro do shell.';
    return;
  }
  const wasForm=formActive.value;
  const changed=frameRoute.value!==route;
  frameRoute.value=route;
  try {
    window.history.replaceState(null,'',`/admin/copilot?view=${encodeURIComponent(route)}`);
  }catch{}
  if(formActive.value) {
    if(changed){
      autoSkipProtected.value=false;skippedProtectedCount.value=0;micPausedForProtected=false;
      cancelPendingActions();onboardingQuestion.value=null;onboardingReview.value=false;
      live.setOnboardingField(null);
    }
    live.setOnboardingMode(connected.value && live.allowOnboardingSuggestions);
    if(changed && micActive.value){
      micPausedForProtected=true;
      micPausePromise=live.stopMic().catch(()=>{});
      await micPausePromise;
      micActive.value=false;
    }
    if(connected.value && live.allowOnboardingSuggestions)beginGuidedForm();
  } else {
    if(wasForm){
      autoSkipProtected.value=false;skippedProtectedCount.value=0;micPausedForProtected=false;
      cancelPendingActions();onboardingQuestion.value=null;onboardingReview.value=false;
    }
    live.setOnboardingMode(false);
  }
  if(navigationWaiter)resolveNavigation(routeReached(navigationWaiter.expected,route)?'navigated':'denied');
}

const live = new PotiguarLive({
  onStatus(status) {
    connected.value = status === 'connected';
    if (status !== 'connected') {
      micActive.value = false;
      cancelPendingActions();
    }
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
    pushMessage('guide', 'Preparei um rascunho. Revise os campos no cartão e clique em Continuar no cadastro V2 quando estiver correto.');
    nextTick(() => draftCard.value?.scrollIntoView({ block: 'center', behavior: 'smooth' }));
  },
  async onAppNavigation({destination}) {
    // Toda navegação ocorre no frame. A sessão Live permanece no componente pai.
    const canCreate = meta.value.can_create_user && meta.value.can_create_with_ai;
    const targets={dashboard:meta.value.links?.dashboard,attendance:meta.value.links?.attendance,
      reports:meta.value.links?.reports,employees:meta.value.links?.users,
      drafts:canCreate?meta.value.links?.drafts:null,
      new_employee:canCreate?meta.value.links?.new_user:null};
    const route=Object.hasOwn(targets,destination)?targets[destination]:null;
    if (!safeAppPath(route)) return {status:'denied',created:false};
    const result=await navigateTo(route);
    if(result.status==='navigated')pushMessage('guide','Tela aberta. A mesma conversa Live continua conectada.');
    return result;
  },
  onOnboardingNavigation(data) {
    return postToForm('potiguar:onboarding:navigate',data);
  },
  onOnboardingSuggestions(step,suggestions) {
    return postToForm('potiguar:onboarding:proposal',{step,suggestions});
  },
  onOnboardingAction(action) {
    return postToForm('potiguar:onboarding:execute',action);
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
    const requested=new URLSearchParams(window.location.search).get('view');
    const allowed=Object.values(meta.value.links||{});
    frameSrc.value=isAppFrameRoute(requested) &&
      (allowed.includes(requested) || (meta.value.can_create_user && isOnboardingFormRoute(requested)))
        ? requested : meta.value.links?.dashboard || meta.value.links?.users || '/admin/users';
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
    const response = await fetch('/admin/copilot/employee-draft', {
      method: 'POST', credentials: 'same-origin', cache: 'no-store',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': props.csrf },
      body: JSON.stringify(employeeDraft.value),
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.error || 'Cadastro não autorizado.');
    employeeDraft.value = null;
    pushMessage('guide', 'Rascunho protegido criado. Continue nas oito etapas para revisão e confirmação humana.');
    const navigated=await navigateTo(data.redirect);
    if(navigated.status!=='navigated')throw Error('O rascunho foi preparado, mas a nova tela não abriu. Consulte a lista de rascunhos.');
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
      await live.connect(model.value, props.csrf, {
        allowEmployeeActions: canRegister.value,
        allowOnboardingSuggestions: canRegister.value,
        persistentShell: true,
      });
      if(formActive.value)beginGuidedForm();
      settingsVisible.value=false;
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
  // Seletores seguros de vocabulário fechado podem ser resolvidos localmente.
  // Isso reduz latência e falhas de interpretação sem revelar dados ao provedor.
  const question=onboardingQuestion.value;
  if(formActive.value && question?.safe && !isProtectedInput(message)) {
    const selected=resolveNaturalSelect(question.field,message,question.options);
    if(selected){
      clearTimeout(guideTimer);
      textInput.value='';pushMessage('user',message);
      postToForm('potiguar:onboarding:proposal',{
        step:question.step,suggestions:[{field:question.field,value:selected}],
      }).then(receipt=>{
        if(receipt.status!=='saved')error.value='O valor não foi gravado. Revise a opção no formulário.';
      }).catch(()=>{error.value='Falha ao preencher o campo no formulário.';});
      return;
    }
  }
  // Texto "pular campo" é executado localmente e não enviado ao provedor.
  if(formActive.value && question && !question.safe && !question.required &&
     /^(?:pular|pule|próximo|proximo|seguir|avançar|avancar|não informar|nao informar|deixar em branco)(?: (?:este |esse |o |a )?(?:campo|cpf))?[.!]?$/i.test(message)) {
    textInput.value='';pushMessage('user',message);
    void skipCurrentProtectedOptional();return;
  }
  if(formActive.value && isProtectedInput(message)) {
    error.value='Dado possivelmente protegido: preencha diretamente no formulário.';return;
  }
  if(formActive.value && onboardingQuestion.value && !onboardingQuestion.value.safe &&
      !/^(abra|abrir|ir para|voltar|mostre|mostrar|salve|salvar|pular|pule) (?:o |a |para |este )?(?:dashboard|painel|histórico|relatórios|funcionários|rascunho|rascunhos|formulário|campo)[.!]?$/i.test(message)) {
    error.value='Este campo é protegido. Preencha-o no formulário, não na conversa.';return;
  }
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
      if(formActive.value && onboardingQuestion.value && !onboardingQuestion.value.safe)
        throw Error('Microfone bloqueado durante o preenchimento de campos protegidos.');
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

function showConfig() {
  copilotVisible.value=true;settingsVisible.value=true;
  nextTick(()=>configCard.value?.scrollIntoView({block:'nearest',behavior:'smooth'}));
}
function pageExit(){live.disconnect().catch(()=>{});}
onMounted(()=>{
  window.addEventListener('message',onAppFrameMessage);
  window.addEventListener('pagehide',pageExit);
  loadMeta();
});
onUnmounted(()=>{
  window.removeEventListener('message',onAppFrameMessage);
  window.removeEventListener('pagehide',pageExit);
  cancelPendingActions();resolveNavigation('not_available');
  live.disconnect();
});
</script>

<template>
  <div class="shell persistent-shell">
    <aside class="sidebar" aria-label="Navegação do copiloto">
      <div class="brand">
        <span class="brand-mark" aria-hidden="true">P</span>
        <div><strong>POTIGUAR</strong><span>Gestão de ponto</span></div>
      </div>

      <div class="sidebar-label">ESPAÇO DE TRABALHO</div>
      <button type="button" class="side-item active" @click="copilotVisible=!copilotVisible" :aria-pressed="copilotVisible"><span aria-hidden="true">✦</span> Copiloto de IA</button>
      <a v-if="meta.links.dashboard" class="side-item" target="potiguar-application" :href="meta.links.dashboard"><span aria-hidden="true">▣</span> Painel</a>
      <a v-if="meta.links.attendance" class="side-item" target="potiguar-application" :href="meta.links.attendance"><span aria-hidden="true">◷</span> Histórico de ponto</a>
      <a v-if="meta.links.reports" class="side-item" target="potiguar-application" :href="meta.links.reports"><span aria-hidden="true">▥</span> Relatórios</a>
      <a class="side-item" target="potiguar-application" :href="meta.links.users || '/admin/users'">
        <span aria-hidden="true">▤</span> Funcionários <span aria-hidden="true" class="side-arrow">↗</span>
      </a>
      <a v-if="meta.can_create_user && meta.links.drafts" class="side-item" target="potiguar-application" :href="meta.links.drafts"><span aria-hidden="true">▤</span> Rascunhos</a>
      <a v-if="meta.can_create_user && meta.links.new_user" class="side-item" target="potiguar-application" :href="meta.links.new_user">
        <span aria-hidden="true">＋</span> Novo funcionário <span aria-hidden="true" class="side-arrow">↗</span>
      </a>
      <div class="sidebar-spacer"></div>
      <div class="notice">
        <strong>Ambiente de avaliação</strong>
        <p>O copiloto pode abrir telas autorizadas e preparar rascunhos. Cadastro final, ponto e biometria exigem os fluxos oficiais.</p>
      </div>
      <a class="return-link" :href="meta.links.users || '/admin/users'">← Sair do modo Copiloto</a>
    </aside>

    <main class="workspace persistent-workspace">
      <div v-if="meta.public_demo_no_login" class="public-demo-banner" role="note">
        <strong>DEMONSTRAÇÃO SEM LOGIN</strong> · Use somente dados fictícios. Navegação e rascunhos V2 estão habilitados; operações reais e conclusão de cadastros estão bloqueadas.
      </div>
      <header class="topbar">
        <div>
          <div class="eyebrow">INTELIGÊNCIA ASSISTIVA <span class="dot" aria-hidden="true"></span> MVP</div>
          <h1>Copiloto Potiguar</h1>
          <p class="subtitle">Navegue pelos módulos sem interromper o Gemini Live.</p>
        </div>
        <span class="status" :class="{ online: connected }" role="status" aria-live="polite">
          <span class="status-dot" aria-hidden="true"></span> {{ statusLabel }}
        </span>
      </header>

      <div class="persistent-columns">
        <section class="app-stage" aria-label="Aplicação Potiguar">
          <div class="app-stage-toolbar">
            <div><strong>Aplicação Potiguar</strong><span>{{ stageLabel }}</span></div>
            <div class="app-stage-controls">
              <button type="button" @click="copilotVisible=!copilotVisible"
                :aria-pressed="copilotVisible" aria-label="Mostrar ou ocultar conversa">
                {{ copilotVisible?'Ocultar conversa':'✦ Conversar' }}
              </button>
              <button type="button" @click="showConfig">⚙ Configurar IA</button>
            </div>
          </div>
          <iframe v-if="frameSrc" ref="appFrame" name="potiguar-application"
            :src="frameSrc" title="Telas administrativas da Potiguar"
            class="app-frame" allow="camera 'self'; microphone 'self'"
            @load="onAppFrameLoad"></iframe>
          <p v-else class="frame-loading">Carregando o ambiente autorizado…</p>
        </section>
        <div class="content-grid persistent-copilot-grid" v-show="copilotVisible">
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
            <p v-if="formActive && skippedProtectedCount>0" class="protected-review-alert" role="note">
              {{ skippedProtectedCount }} campos opcionais protegidos adiados. Revise-os no formulário antes de concluir.
            </p>
            <div v-if="connected && formActive && onboardingQuestion && !onboardingQuestion.safe"
                 class="protected-step-actions" role="group" aria-label="Avançar no campo protegido">
              <strong>Campo protegido: {{ onboardingQuestion.label }}</strong>
              <p v-if="onboardingQuestion.required">Obrigatório: preencha diretamente no formulário, sem ditar para a IA.</p>
              <p v-else>Opcional: preencha no formulário ou deixe para a revisão final.</p>
              <div class="protected-step-buttons">
                <button type="button" @click="openCurrentProtectedField">Preencher no formulário</button>
                <button v-if="!onboardingQuestion.required && !autoSkipProtected" type="button"
                    :disabled="skipProtectedBusy" @click="skipCurrentProtectedOptional">Pular este campo</button>
                <button v-if="!onboardingQuestion.required && !autoSkipProtected" type="button"
                    :disabled="skipProtectedBusy" @click="skipProtectedOptionalsByChoice">Seguir sem opcionais protegidos</button>
                <button v-if="autoSkipProtected" type="button" @click="autoSkipProtected=false">Parar de pular automaticamente</button>
              </div>
              <p v-if="autoSkipProtected" class="protected-step-note">Opcionais protegidos adiados: {{ skippedProtectedCount }}. Revise os dados necessários antes de concluir.</p>
            </div>
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

        <aside class="assist-panel" v-show="settingsVisible" aria-label="Configuração e sugestões">
          <div class="panel-card accent-card">
            <div class="panel-icon" aria-hidden="true">✧</div>
            <span class="small-caps">ASSISTÊNCIA EM TEMPO REAL</span>
            <h2>Converse com o sistema.</h2>
            <p>Utilize sua voz ou escreva. A IA explica os caminhos e você continua no controle.</p>
          </div>

          <div class="panel-card control-card" ref="configCard">
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
            <p class="registration-note">Diga ao Gemini: “Cadastre uma funcionária chamada Maria de Teste, usuário maria.teste, matrícula TEST-101”. Ele prepara os campos; só você confirma a gravação.</p>
            <p v-if="meta.demo_synthetic_only" class="registration-note">Ambiente de homologação: somente dados fictícios. Use um nome terminado em “de Teste”, usuário “.teste” e matrícula “TEST-...”.</p>
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
              <p class="registration-note">Esta etapa cria somente um rascunho protegido, sem senha nem biometria. Conclua o cadastro no formulário V2.</p>
              <div class="registration-actions">
                <button type="button" @click="cancelEmployeeDraft" :disabled="registrationBusy">Cancelar</button>
                <button type="submit" class="connect-button" :disabled="registrationBusy || registrationErrors.length > 0">
                  {{ registrationBusy ? 'Salvando…' : 'Continuar no cadastro V2' }}
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
      </div>
      <div class="persistent-voice-dock" v-show="!settingsVisible" role="group" aria-label="Controles persistentes do Copiloto">
        <span class="voice-dock-status" :class="{online:connected}">{{ connected?(micActive?'🎙 Ouvindo':'● Live conectado'):'○ Live desligado' }}</span>
        <button v-if="connected" type="button" @click="toggleMic"
          :disabled="formActive && onboardingQuestion && !onboardingQuestion.safe">
          {{ micActive?'Parar áudio':'Ativar voz' }}
        </button>
        <button v-if="!connected" type="button" @click="showConfig">Conectar</button>
        <button type="button" @click="copilotVisible=!copilotVisible">{{ copilotVisible?'Ocultar':'✦ Chat' }}</button>
      </div>
    </main>
  </div>
</template>
