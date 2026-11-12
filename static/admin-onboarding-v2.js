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
  showStep(0);
})();
