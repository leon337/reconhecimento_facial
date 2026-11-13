(() => {
  'use strict';
  const app = document.getElementById('onboarding-v2');
  if (!app) return;
  const form = document.getElementById('onboarding-form');
  const panels = Array.from(document.querySelectorAll('.step-panel'));
  const steps = Array.from(document.querySelectorAll('[data-step-target]'));
  const csrf = document.getElementById('csrf_token').value;
  const status = document.getElementById('save-status');
  const errorPanel = document.getElementById('form-errors');
  const next = document.getElementById('next-button');
  const back = document.getElementById('back-button');
  const complete = document.getElementById('complete-button');
  const saveButton = document.getElementById('save-button');
  const discardButton = document.getElementById('discard-button');
  const controls = [next,back,complete,saveButton,discardButton];
  const titles = ['Tipo de relação','Dados pessoais','Endereço','Vínculo','Pagamento','Acesso','Biometria','Revisão'];
  let current = 0, maxVisited = 0, version = Number(app.dataset.version);
  let generation = 0, savedGeneration = 0, saving = null, blocked = false;
  let timer;

  function alertError(message) {
    errorPanel.textContent = message;
    errorPanel.hidden = false;
    errorPanel.scrollIntoView({behavior:'smooth',block:'nearest'});
  }
  function clearError() { errorPanel.textContent=''; errorPanel.hidden=true; }
  function busy(on) { controls.forEach(el => {if (el && !el.hidden) el.disabled = !!on;}); }
  function serialize() {
    const out = {};
    form.querySelectorAll('[name]').forEach(input => {
      if (input.name === 'csrf_token' || input.disabled) return;
      if (input.type === 'checkbox') out[input.name] = input.checked;
      else out[input.name] = (input.value || '').trim();
    });
    return out;
  }
  async function send(url, payload) {
    let response;
    try {
      response = await fetch(url, {
        method:'POST', credentials:'same-origin', cache:'no-store',
        headers:{'Content-Type':'application/json','X-CSRFToken':csrf,'Accept':'application/json'},
        body:JSON.stringify(payload),
      });
    } catch (err) { throw Error('Sem conexão. Verifique a rede e tente novamente.'); }
    const result = await response.json().catch(()=>({error:'resposta_invalida'}));
    if (!response.ok) {
      if (response.status === 409) {
        blocked = true;
        throw Error('Conflito de edição. Recarregue a página antes de continuar para não sobrescrever outra versão.');
      }
      if (result.messages && Array.isArray(result.messages)) throw Error(result.messages.join(' '));
      if (response.status === 403 || response.status === 401) throw Error('Sua sessão expirou ou não possui permissão para esta operação.');
      throw Error('Falha ao salvar ou validar (' + response.status + '). ' + (result.error || 'Tente novamente.'));
    }
    return result;
  }
  async function saveDraft() {
    if (blocked) throw Error('Atualize a página para resolver o conflito de edição.');
    if (saving) await saving;
    if (generation === savedGeneration) return;
    const generationAtStart = generation;
    const payload = serialize();
    status.textContent = 'Salvando rascunho...';
    busy(true);
    saving = send(app.dataset.save, {version, fields:payload})
      .then(data => {
        version = Number(data.version);
        savedGeneration = generationAtStart;
        status.textContent = 'Rascunho salvo no servidor';
        clearError();
      }).catch(err => {
        status.textContent = 'Não foi possível salvar';
        alertError(err.message);
        throw err;
      }).finally(()=>{saving=null;busy(false);});
    await saving;
    if (generation !== savedGeneration) return saveDraft();
  }
  function validateCurrent() {
    for (const input of panels[current].querySelectorAll('[required]')) {
      if (!input.checkValidity()) {
        alertError('Preencha o campo obrigatório: ' + (input.closest('.field-item')?.querySelector('label')?.textContent || input.name));
        input.focus(); return false;
      }
    }
    return true;
  }
  function showStep(index) {
    if (index < 0 || index >= panels.length || index > maxVisited || blocked) return;
    current = index;
    panels.forEach((panel,i) => panel.hidden = i !== index);
    steps.forEach((button,i) => {
      button.disabled = i > maxVisited;
      if (i === index) button.setAttribute('aria-current','step');
      else button.removeAttribute('aria-current');
    });
    back.hidden = index === 0;
    next.hidden = index === panels.length - 1;
    complete.hidden = index !== panels.length - 1;
    document.getElementById('current-step-label').textContent = `Etapa ${index+1} de ${panels.length}`;
    document.getElementById('current-step-name').textContent = titles[index];
    document.getElementById('progress-fill').style.width = `${(index+1)/panels.length*100}%`;
    clearError();
    if (index === panels.length - 1) review();
    panels[index].querySelector('h2')?.setAttribute('tabindex','-1');
    panels[index].querySelector('h2')?.focus({preventScroll:true});
    panels[index].scrollIntoView({behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'start'});
  }
  function review() {
    const data = serialize();
    const values = [
      ['Nome completo', data.full_name], ['Tipo de relação', data.relation_type],
      ['Empresa', data.company], ['Unidade/obra', data.unit],
      ['Cargo', data.job_role], ['Jornada', data.schedule],
      ['País', data.country], ['Endereço', data.address_type],
      ['Pagamento', data.payment_method || 'Não informado'],
      ['Acesso ao sistema', data.has_system_access ? 'Solicitado, pendente de ativação' : 'Não solicitado'],
      ['Biometria', data.biometric_timing || 'Não definido'],
    ];
    const target=document.getElementById('review-details');
    target.replaceChildren();
    const wrap=document.createElement('div');wrap.className='review-items';
    for (const [label,value] of values) {
      const item=document.createElement('div');item.className='review-item';
      const title=document.createElement('strong');title.textContent=label;
      const span=document.createElement('span');span.textContent=value || 'Não informado';
      item.append(title,span);wrap.append(item);
    }
    target.append(wrap);
  }
  form.addEventListener('input',()=>{
    generation++;
    clearTimeout(timer);
    timer=setTimeout(()=>{saveDraft().catch(()=>{});},1250);
    status.textContent='Alterações ainda não salvas';
  });
  form.addEventListener('submit',e=>e.preventDefault());
  next.addEventListener('click',async()=>{
    if (!validateCurrent()) return;
    try {await saveDraft(); maxVisited=Math.max(maxVisited,current+1);showStep(current+1);} catch(_){}
  });
  back.addEventListener('click',()=>showStep(current-1));
  steps.forEach((button,i)=>button.addEventListener('click',()=>showStep(i)));
  saveButton.addEventListener('click',async()=>{
    try {await saveDraft();window.location.assign('/admin/onboarding/drafts');}catch(_){}
  });
  discardButton.addEventListener('click',async()=>{
    if (!window.confirm('Descartar definitivamente este rascunho? Nenhum funcionário será criado.')) return;
    try {busy(true);const data=await send(app.dataset.discard,{});window.location.assign(data.redirect);} catch(e){alertError(e.message);busy(false);}
  });
  complete.addEventListener('click',async()=>{
    if (!window.confirm('Confirmar o cadastro do funcionário? Os dados serão salvos no servidor.')) return;
    try {
      await saveDraft();
      busy(true);status.textContent='Concluindo cadastro...';
      const data=await send(app.dataset.complete,{version});
      status.textContent='Funcionário criado com sucesso.';
      window.location.assign(data.redirect);
    } catch(e){alertError(e.message);busy(false);}
  });
  window.addEventListener('beforeunload',e=>{
    if (generation!==savedGeneration && !blocked) {e.preventDefault();e.returnValue='';}
  });
  // Copiloto: comunicação mínima, somente mesma origem; nunca envia valores existentes.
  const openCopilot=document.getElementById('copilot-open');
  const closeCopilot=document.getElementById('copilot-close');
  const minimizeCopilot=document.getElementById('copilot-minimize');
  const copilotDrawer=document.getElementById('onboarding-copilot-drawer');
  const copilotBackdrop=document.getElementById('onboarding-copilot-backdrop');
  const copilotFrame=document.getElementById('onboarding-copilot-frame');
  const proposalPanel=document.getElementById('copilot-proposal');
  const proposalDetails=document.getElementById('copilot-proposal-details');
  const applyProposal=document.getElementById('copilot-apply');
  const rejectProposal=document.getElementById('copilot-reject');
  const safeFields={
    0:['relation_type','other_relation'],
    1:['full_name','social_name','nationality','education'],
    2:['country','address_type','city','state'],
    3:['department','job_role','manager','schedule','contract_type','transport_benefit','benefit_policy'],
    4:[],5:[],6:[],7:[],
  };
  let pendingProposal=null;
  const guide = window.PotiguarOnboardingController;
  const guidedFieldLabel = document.getElementById('guided-field');
  let guided=false, activeField=null, forcedField=null, guideBusy=false, guidedApplying=false;
  let reviewAnnounced=false, advanceTimer=null;
  const visitedFields=new Set();
  function sendToCopilot(payload) {
    if (copilotDrawer.hidden || !copilotFrame.contentWindow) return;
    copilotFrame.contentWindow.postMessage(payload, window.location.origin);
  }
  function fieldLabel(control) {
    return control.closest('.field-item')?.querySelector('label')?.textContent?.replace('*','').trim() || control.name;
  }
  function announceField(control) {
    activeField=control;
    const safe=guide.isSafe(current,control.name);
    const options=control.tagName==='SELECT'
      ? Array.from(control.options).map(option=>option.value).filter(Boolean) : [];
    guidedFieldLabel.hidden=false;
    guidedFieldLabel.textContent=`Campo atual: ${fieldLabel(control)}`;
    sendToCopilot({type:'potiguar:onboarding:question',step:current,field:control.name,
      label:fieldLabel(control),safe,required:control.required,options});
    // O campo protegido só recebe foco quando o usuário abre o formulário.
  }
  async function guideNext() {
    if (!guided || !guide || guideBusy || blocked || copilotDrawer.hidden) return;
    guideBusy=true;
    try {
      const data=serialize();
      const eligible=new Set(Array.from(visitedFields).filter(k=>k.startsWith(`${current}:`)).map(k=>k.split(':')[1]));
      const fields=Array.from(panels[current].querySelectorAll('[name]'));
      const chosen=forcedField && fields.includes(forcedField) && guide.applicable(forcedField.name,data)
        ? forcedField : guide.nextField(fields,data,eligible);
      forcedField=null;
      if (chosen) { announceField(chosen); return; }
      activeField=null;
      guidedFieldLabel.hidden=true;
      if (current===7) {
        if (!reviewAnnounced) { reviewAnnounced=true; sendToCopilot({type:'potiguar:onboarding:review'}); }
        return;
      }
      if (!validateCurrent()) return;
      await saveDraft();
      maxVisited=Math.max(maxVisited,current+1);
      showStep(current+1);
    } catch(e) { alertError(e.message); sendToCopilot({type:'potiguar:onboarding:error'}); }
    finally { guideBusy=false; }
  }
  async function fieldCompleted(control) {
    if (!guided || blocked || !control || activeField!==control || guidedApplying) return;
    if (!guide.hasValue(control) || !control.checkValidity()) return;
    if (guide.isSafe(current,control.name) && !guide.validSafeValue(control,control.value)) return;
    try {
      await saveDraft();
      if (activeField!==control) return;
      visitedFields.add(`${current}:${control.name}`);
      activeField=null;
      sendToCopilot({type:'potiguar:onboarding:filled',step:current,field:control.name});
      await guideNext();
    } catch(e) { alertError(e.message); }
  }
  async function applyGuidedSuggestion(item) {
    if (guidedApplying || !activeField || !guide.isSafe(current,activeField.name)) return;
    const control=activeField;
    if (item.field!==control.name || !validSuggestion(item) || !guide.validSafeValue(control,item.value)) return;
    const previous=control.value;
    guidedApplying=true;
    try {
      control.value=item.value.trim();
      control.dispatchEvent(new Event('input',{bubbles:true}));
      if (!control.checkValidity()) throw Error('Valor inválido para o campo.');
      await saveDraft();
      visitedFields.add(`${current}:${control.name}`);
      activeField=null;
      sendToCopilot({type:'potiguar:onboarding:filled',step:current,field:control.name});
    } catch(e) {
      control.value=previous;
      control.dispatchEvent(new Event('input',{bubbles:true}));
      alertError(e.message);
      sendToCopilot({type:'potiguar:onboarding:error'});
      return;
    } finally { guidedApplying=false; }
    await guideNext();
  }
  function sendStepContext(){
    if(!copilotFrame.contentWindow || !copilotFrame.getAttribute('src'))return;
    copilotFrame.contentWindow.postMessage({type:'potiguar:onboarding:context',step:current},window.location.origin);
  }
  const originalShowStep=showStep;
  showStep=function(index){
    originalShowStep(index);
    pendingProposal=null;
    proposalPanel.hidden=true;
    reviewAnnounced=false;
    sendStepContext();
    if (guided) setTimeout(()=>guideNext(),0);
  };
  function openDrawer(){
    copilotDrawer.hidden=false;copilotBackdrop.hidden=false;
    copilotDrawer.setAttribute('aria-hidden','false');
    openCopilot.setAttribute('aria-expanded','true');
    if(!copilotFrame.getAttribute('src'))copilotFrame.setAttribute('src',copilotFrame.dataset.src);
    else sendStepContext();
    if(guided)setTimeout(()=>{if(activeField)announceField(activeField);else guideNext();},0);
    closeCopilot.focus();
  }
  function minimizeDrawer(){
    sendToCopilot({type:'potiguar:onboarding:mute'});
    copilotDrawer.hidden=true;copilotBackdrop.hidden=true;
    copilotDrawer.setAttribute('aria-hidden','true');
    openCopilot.setAttribute('aria-expanded','false');
    if(activeField)activeField.focus({preventScroll:false});
    else openCopilot.focus();
  }
  function closeDrawer(){
    copilotFrame.contentWindow?.postMessage({type:'potiguar:onboarding:pause'},window.location.origin);
    copilotDrawer.hidden=true;copilotBackdrop.hidden=true;
    copilotDrawer.setAttribute('aria-hidden','true');openCopilot.setAttribute('aria-expanded','false');
    guided=false;activeField=null;forcedField=null;
    guidedFieldLabel.hidden=true;
    clearTimeout(advanceTimer);
    pendingProposal=null;proposalPanel.hidden=true;openCopilot.focus();
  }
  openCopilot.addEventListener('click',openDrawer);
  closeCopilot.addEventListener('click',closeDrawer);
  minimizeCopilot.addEventListener('click',minimizeDrawer);
  copilotBackdrop.addEventListener('click',closeDrawer);
  copilotFrame.addEventListener('load',sendStepContext);
  window.addEventListener('keydown',event=>{if(event.key==='Escape' && !copilotDrawer.hidden)closeDrawer();});
  function validSuggestion(item){
    if(!item || typeof item!=='object' || typeof item.field!=='string' || typeof item.value!=='string')return false;
    if(!safeFields[current].includes(item.field) || item.value.length>120 || !item.value.trim() || /[<>\x00-\x1f]/.test(item.value))return false;
    const panel=panels[current];
    const control=Array.from(panel.querySelectorAll('[name]')).find(el=>el.name===item.field);
    if(!control || control.type==='checkbox' || control.disabled)return false;
    if(control.tagName==='SELECT' && !Array.from(control.options).some(option=>option.value===item.value))return false;
    return true;
  }
  window.addEventListener('message',event=>{
    if(event.origin!==window.location.origin || event.source!==copilotFrame.contentWindow)return;
    const message=event.data;
    if(!message || typeof message!=='object')return;
    if(message.type==='potiguar:onboarding:ready'){sendStepContext();return;}
    if(message.type==='potiguar:onboarding:stop'){
      guided=false;activeField=null;forcedField=null;clearTimeout(advanceTimer);guidedFieldLabel.hidden=true;return;
    }
    if(message.type==='potiguar:onboarding:begin'){
      if(!guide || blocked || copilotDrawer.hidden)return;
      guided=true;reviewAnnounced=false;
      guideNext().catch(e=>alertError(e.message));
      return;
    }
    if(message.type==='potiguar:onboarding:skip'){
      if(!guided || !activeField || activeField.required || message.field!==activeField.name || message.step!==current)return;
      visitedFields.add(`${current}:${activeField.name}`);
      activeField=null;guideNext().catch(e=>alertError(e.message));return;
    }
    if(message.type==='potiguar:onboarding:navigate'){
      if(!guided || !Number.isInteger(message.step) || message.step<0 || message.step>maxVisited || blocked)return;
      if(!['open_step','correct_field'].includes(message.kind))return;
      const index=message.step;
      const fields=Array.from(panels[index].querySelectorAll('[name]'));
      let control=null;
      if(message.kind==='correct_field'){
        if(typeof message.field!=='string' || !/^[a-z_]{2,40}$/.test(message.field))return;
        control=fields.find(el=>el.name===message.field);
      }else{
        control=fields.find(el=>guide.applicable(el.name,serialize())) || null;
      }
      if(!control || !guide.applicable(control.name,serialize()))return;
      clearTimeout(advanceTimer);forcedField=control;
      visitedFields.delete(`${index}:${control.name}`);
      showStep(index);return;
    }
    if(message.type!=='potiguar:onboarding:proposal' || message.step!==current || copilotDrawer.hidden)return;
    if(!Array.isArray(message.suggestions) || message.suggestions.length>5)return;
    if(guided){
      if(activeField){
        const eligible=message.suggestions.find(item=>item?.field===activeField.name);
        if(eligible)applyGuidedSuggestion(eligible).catch(e=>alertError(e.message));
      }
      return;
    }
    const unique=new Set();
    const suggestions=message.suggestions.filter(item=>{
      if(!validSuggestion(item)||unique.has(item.field))return false;
      unique.add(item.field);return true;
    });
    if(!suggestions.length)return;
    pendingProposal={step:current,suggestions};
    proposalDetails.replaceChildren();
    for(const item of suggestions){
      const label=Array.from(panels[current].querySelectorAll('.field-item')).find(el=>el.querySelector(`[name="${item.field}"]`))?.querySelector('label')?.textContent?.trim() || item.field;
      const line=document.createElement('p');
      const b=document.createElement('strong');b.textContent=label+': ';
      const value=document.createElement('span');value.textContent=item.value;
      line.append(b,value);proposalDetails.append(line);
    }
    proposalPanel.hidden=false;
    proposalPanel.scrollIntoView({block:'nearest'});
  });
  rejectProposal.addEventListener('click',()=>{pendingProposal=null;proposalPanel.hidden=true;});
  applyProposal.addEventListener('click',()=>{
    if(!pendingProposal || pendingProposal.step!==current)return;
    for(const item of pendingProposal.suggestions){
      if(!validSuggestion(item))continue;
      const control=Array.from(panels[current].querySelectorAll('[name]')).find(el=>el.name===item.field);
      if(control){control.value=item.value;control.dispatchEvent(new Event('input',{bubbles:true}));}
    }
    pendingProposal=null;proposalPanel.hidden=true;
    status.textContent='Sugestões aplicadas localmente; salvando rascunho...';
  });
  // Campos protegidos são preenchidos somente no formulário local. Nunca enviamos valores à IA.
  form.addEventListener('input',event=>{
    if(!guided || guidedApplying || !activeField || event.target!==activeField
        || !guide.isSafe(current,activeField.name))return;
    clearTimeout(advanceTimer);
    const control=activeField;
    advanceTimer=setTimeout(()=>fieldCompleted(control),1200);
  });
  form.addEventListener('change',event=>{
    if(!guided || guidedApplying || !activeField || event.target!==activeField
        || guide.isSafe(current,activeField.name))return;
    clearTimeout(advanceTimer);
    const control=activeField;
    advanceTimer=setTimeout(()=>fieldCompleted(control),100);
  });
  showStep(0);
})();
