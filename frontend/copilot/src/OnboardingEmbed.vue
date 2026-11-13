<script setup>
import { ref, nextTick, onMounted, onUnmounted } from 'vue';
import { PotiguarLive } from './live.js';
const props=defineProps({csrf:{type:String,required:true}});
const meta=ref({enabled:false,configured:false,can_create_with_ai:false});
const model=ref('gemini-3.8-live'),consent=ref(false),connected=ref(false),busy=ref(false),micOn=ref(false);
const currentStep=ref(0),text=ref(''),error=ref(''),question=ref(null),reviewMode=ref(false);
const names=['Tipo de relação','Dados pessoais','Endereço','Vínculo','Pagamento','Acesso','Biometria','Revisão'];
const messages=ref([{role:'guide',text:'Conecte o Copiloto para iniciar o cadastro orientado. Uma pergunta por vez; campos protegidos somente no formulário.'}]);
const logEnd=ref(null);
let assistantIndex=-1,voiceIndex=-1;
function add(role,value){messages.value.push({role,text:value});if(messages.value.length>45)messages.value.splice(1,messages.value.length-45);nextTick(()=>logEnd.value?.scrollIntoView({block:'end'}));}
const live=new PotiguarLive({
  onStatus(s){connected.value=s==='connected';if(!connected.value)micOn.value=false;},
  onAssistantText(s){voiceIndex=-1;if(assistantIndex<0){add('assistant',s);assistantIndex=messages.value.length-1;}else messages.value[assistantIndex].text+=s;},
  onUserSpeech(s){assistantIndex=-1;if(voiceIndex<0){add('user',s);voiceIndex=messages.value.length-1;}else messages.value[voiceIndex].text+=s;},
  onTurnComplete(){assistantIndex=-1;voiceIndex=-1;},
  onOnboardingSuggestions(step,suggestions){window.parent.postMessage({type:'potiguar:onboarding:proposal',step,suggestions},location.origin);},
  onOnboardingNavigation(navigation){window.parent.postMessage({type:'potiguar:onboarding:navigate',...navigation},location.origin);},
  onError(message){error.value=message;},
});
function receive(event){
  if(event.origin!==location.origin || event.source!==window.parent || !event.data)return;
  const data=event.data;
  if(data.type==='potiguar:onboarding:pause'){live.disconnect().catch(()=>{});micOn.value=false;question.value=null;return;}
  if(data.type==='potiguar:onboarding:mute'){live.stopMic().catch(()=>{});micOn.value=false;return;}
  if(data.type==='potiguar:onboarding:context'&&Number.isInteger(data.step)&&data.step>=0&&data.step<8){
    currentStep.value=data.step;live.setOnboardingStep(data.step);
    return;
  }
  if(data.type==='potiguar:onboarding:question'&&Number.isInteger(data.step)&&data.step>=0&&data.step<8
      &&typeof data.field==='string'&&typeof data.label==='string'){
    currentStep.value=data.step;live.setOnboardingStep(data.step);
    live.setOnboardingField(data.safe?data.field:null);
    question.value={step:data.step,field:data.field,label:data.label,safe:!!data.safe,required:!!data.required};
    reviewMode.value=false;assistantIndex=-1;voiceIndex=-1;
    if(!data.safe){
      if(micOn.value){live.stopMic().catch(()=>{});micOn.value=false;}
      add('guide',`Etapa ${data.step+1}. Preencha "${data.label}" no formulário protegido. Não envie esse dado por voz ou chat. Use "Pular campo" se for opcional.`);
      return;
    }
    add('guide',`Campo atual: ${data.label}.`);
    if(connected.value)live.sendText(`CONTROLE DO FORMULÁRIO: etapa ${data.step+1}, campo ${data.field} (${data.label}), ${data.required?'obrigatório':'opcional'}; opções válidas: ${Array.isArray(data.options)?data.options.join(', '):'texto livre'}. Faça SOMENTE uma pergunta objetiva para obter ESSE campo, em português do Brasil. Se o usuário responder, invoque suggest_onboarding_fields somente para ${data.field}. Não peça outros dados, não declare que salvou.`);
    return;
  }
  if(data.type==='potiguar:onboarding:filled'){
    if(question.value?.field===data.field && question.value.step===data.step)question.value=null;
    add('guide','Campo validado e salvo no rascunho.');
    return;
  }
  if(data.type==='potiguar:onboarding:review'){
    question.value=null;live.setOnboardingField(null);reviewMode.value=true;
    add('guide','Etapa 8: confira o resumo na tela. A criação exige confirmação humana no botão Concluir cadastro.');
    return;
  }
  if(data.type==='potiguar:onboarding:error'){add('guide','Não foi possível validar ou salvar. Corrija o campo no formulário antes de continuar.');}
}
async function load(){try{const r=await fetch('/admin/copilot/meta',{credentials:'same-origin',cache:'no-store'});if(!r.ok)throw Error('Permissões indisponíveis.');meta.value=await r.json();}catch(e){error.value=e.message;}}
async function connect(){
  if(busy.value)return;busy.value=true;error.value='';
  try{
    if(connected.value){await live.disconnect();question.value=null;window.parent.postMessage({type:'potiguar:onboarding:stop'},location.origin);return;}
    if(!consent.value)throw Error('Confirme o aviso de privacidade.');
    if(!meta.value.enabled||!meta.value.configured||!meta.value.can_create_with_ai)throw Error('Copiloto indisponível para este usuário.');
    await live.connect(model.value,props.csrf,{allowOnboardingSuggestions:true});
    live.setOnboardingStep(currentStep.value);
    window.parent.postMessage({type:'potiguar:onboarding:begin'},location.origin);
  }catch(e){error.value=e.message;}finally{busy.value=false;}
}
function send(){
  const value=text.value.trim();
  if(!value||value.length>1000||!connected.value)return;
  error.value='';
  const normalized=value.toLocaleLowerCase('pt-BR');
  const localNavigation=[
    [/^(?:corrija|corrigir|altere|alterar) (?:o |a )?cargo\b/,3,'job_role'],
    [/^(?:corrija|corrigir|altere|alterar) (?:a )?jornada\b/,3,'schedule'],
    [/^(?:volte|voltar) (?:para (?:o |a )?)?endere[cç]o\b/,2,null],
  ].find(([pattern])=>pattern.test(normalized));
  if(localNavigation){
    window.parent.postMessage({type:'potiguar:onboarding:navigate',
      kind:localNavigation[2]?'correct_field':'open_step',
      step:localNavigation[1],field:localNavigation[2]},location.origin);
    add('user',value);text.value='';return;
  }
  if(!question.value?.safe){error.value='Para este campo, use o formulário protegido. Não envie o valor ao Gemini.';return;}
  if(/\b\d{3}[. -]?\d{3}[. -]?\d{3}[- ]?\d{2}\b|\b[\w.+-]+@[\w.-]+\.[a-z]{2,}\b/i.test(value)){
    error.value='Possível documento ou contato identificado. Preencha diretamente no formulário protegido.';return;
  }
  try{
    live.sendText(`Resposta para o campo ${question.value.field}, etapa ${currentStep.value+1}: ${value}. Se for válido, invoque suggest_onboarding_fields somente para ${question.value.field}; não repita dados protegidos.`);
    add('user',value);text.value='';assistantIndex=-1;voiceIndex=-1;
  }catch(e){error.value=e.message;}
}
async function mic(){error.value='';if(!question.value?.safe){error.value='Microfone desativado para campos protegidos. Use o formulário.';return;}try{if(micOn.value){await live.stopMic();micOn.value=false;}else{await live.startMic('automatic');micOn.value=true;}}catch{error.value='Não foi possível ativar o microfone. Verifique permissões do navegador.';micOn.value=false;}}
function skip(){if(!question.value||question.value.required)return;window.parent.postMessage({type:'potiguar:onboarding:skip',step:question.value.step,field:question.value.field},location.origin);question.value=null;}
onMounted(()=>{window.addEventListener('message',receive);load();window.parent.postMessage({type:'potiguar:onboarding:ready'},location.origin);});
onUnmounted(()=>{window.removeEventListener('message',receive);live.disconnect().catch(()=>{});});
</script>
<template>
<div class="embedded">
  <header><strong>✦ Copiloto Potiguar</strong><span>{{connected?'Conectado':'Desconectado'}}</span></header>
  <p class="step-title">Etapa {{currentStep+1}} de 8 · {{names[currentStep]}}</p>
  <p class="privacy">Só suas mensagens e falas são enviadas ao Gemini. Não dite documentos, contatos, endereço completo, finanças, dados sensíveis, biometria ou senhas. Para esses dados, use apenas o formulário protegido.</p>
  <section v-if="question" class="field-prompt" aria-live="polite"><strong>Campo atual: {{question.label}}</strong><span>{{question.safe?"Responda por voz ou texto.":"Preencha diretamente no formulário, sem ditar o valor."}}</span><button v-if="!question.required" type="button" @click="skip">Pular campo opcional</button></section>
  <section v-else-if="reviewMode" class="field-prompt">Revise os dados no formulário antes de concluir. A IA não pode criar o funcionário.</section>
  <section class="config">
    <label for="onb-model">Modelo da conversa</label><select id="onb-model" v-model="model" :disabled="connected||busy"><option value="gemini-3.8-live">Gemini 3.8 Live</option><option value="gemini-3.8-live-extended-thinking">Gemini 3.8 Extended</option></select>
    <small v-if="model.endsWith('extended-thinking')">Modo avançado fornece orientação; sugestões estruturadas dependem do modelo Live padrão.</small>
    <label class="consent"><input type="checkbox" v-model="consent" :disabled="connected"> Autorizo o processamento das mensagens ou falas que eu enviar ao Gemini.</label>
    <button @click="connect" :disabled="busy||(!connected&&(!consent||!meta.enabled||!meta.configured))" type="button">{{busy?'Aguarde…':connected?'Desconectar':'Conectar Copiloto'}}</button>
  </section>
  <div class="messages" role="log" aria-live="polite"><div v-for="(m,i) in messages" :key="i" :class="['bubble',m.role]"><strong>{{m.role==='user'?'Você':m.role==='assistant'?'Copiloto':'Orientação'}}</strong><p>{{m.text}}</p></div><span ref="logEnd"></span></div>
  <p v-if="error" class="error" role="alert">{{error}}</p>
  <form class="composer" @submit.prevent="send"><label for="onb-text">Pergunte ou solicite preenchimento de campos permitidos</label><textarea id="onb-text" v-model="text" maxlength="1000" rows="2" :disabled="!connected" placeholder="Ex.: a função é Analista de Teste"></textarea><div class="actions"><button type="submit" :disabled="!connected||!text.trim()">Enviar</button><button type="button" @click="mic" :aria-pressed="micOn" :disabled="!connected||!question?.safe">{{micOn?'Parar microfone':'🎙 Falar'}}</button></div></form>
  <small>Respostas permitidas são aplicadas e salvas automaticamente no rascunho. Criar o funcionário exige confirmação humana na revisão.</small>
</div>
</template>
<style scoped>
.embedded{min-height:100vh;background:#f5faf7;color:#17482d;display:flex;flex-direction:column;gap:9px;padding:12px;font:13px system-ui,Arial,sans-serif;box-sizing:border-box}
header{display:flex;align-items:center;justify-content:space-between;gap:8px}header strong{font-size:17px;color:#146542}header span,small{color:#577061;font-size:11px}.step-title{font-weight:700;color:#146542;margin:0}.privacy{margin:0;padding:9px;background:#e8f4ec;border-radius:8px;font-size:11px;line-height:1.5}
.config{display:flex;flex-direction:column;gap:7px;background:#fff;padding:10px;border:1px solid #d7e4da;border-radius:9px}.config>label:not(.consent){font-weight:700}.consent{display:flex;gap:7px;font-size:11px;line-height:1.45}.consent input{align-self:start}
select,textarea{border:1px solid #a9c5b4;border-radius:8px;padding:9px;width:100%;box-sizing:border-box;font:inherit;background:white;color:#17482d}button{border:0;background:#176143;color:#fff;font-weight:700;border-radius:8px;padding:10px;cursor:pointer}button:disabled{opacity:.48;cursor:not-allowed}button[aria-pressed=true]{background:#a13635}
 .field-prompt{display:flex;flex-direction:column;gap:7px;background:#fff;padding:10px;border:1px solid #aad1b7;border-radius:9px}.field-prompt span{font-size:12px}.field-prompt button{align-self:flex-start}
.messages{min-height:160px;max-height:31vh;overflow:auto;flex:1;display:flex;flex-direction:column;gap:8px}.bubble{background:#fff;border:1px solid #dfebe2;border-radius:10px;padding:8px;max-width:95%;align-self:flex-start;overflow-wrap:anywhere}.bubble.user{background:#dcefe5;align-self:flex-end}.bubble strong{font-size:11px;color:#46735a}.bubble p{white-space:pre-wrap;margin:5px 0 0;line-height:1.45}.composer{display:flex;flex-direction:column;gap:7px}.composer label{font-size:11px;font-weight:700}.actions{display:flex;gap:8px}.actions button{flex:1}.error{margin:0;padding:9px;border-radius:8px;background:#fee;border:1px solid #e5b7b7;color:#8d2626}
</style>
