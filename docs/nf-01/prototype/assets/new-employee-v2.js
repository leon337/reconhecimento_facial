(() => {
  const root = document.querySelector('[data-onboarding-v2]');
  if (!root) return;

  const STORAGE_KEY = 'cpp:nf01:new-employee-v2:draft:v3';
  const form = root.querySelector('[data-wizard-form]');
  const panels = [...root.querySelectorAll('[data-step-panel]')];
  const stepButtons = [...root.querySelectorAll('[data-step-button]')];
  const nextButton = root.querySelector('[data-next-step]');
  const backButton = root.querySelector('[data-back-step]');
  const saveExitButton = root.querySelector('[data-save-exit]');
  const discardButton = root.querySelector('[data-discard-draft]');
  const completeButton = root.querySelector('[data-complete-onboarding]');
  const mobileCurrent = root.querySelector('[data-mobile-current]');
  const mobileLabel = root.querySelector('[data-mobile-label]');
  const progressBar = root.querySelector('[data-progress-bar]');
  const stepKicker = root.querySelector('[data-step-kicker]');
  const stepTitle = root.querySelector('[data-step-title]');
  const stepDescription = root.querySelector('[data-step-description]');
  const stepStateBadge = root.querySelector('[data-step-state]');
  const saveState = root.querySelector('[data-save-state]');
  const toast = root.querySelector('[data-toast-v2]');
  const liveRegion = root.querySelector('[data-live-region]');
  const successPanel = root.querySelector('[data-success-panel]');
  const standardWorkspace = root.querySelector('[data-standard-workspace]');
  const errorSummary = root.querySelector('[data-error-summary]');
  const errorSummaryList = root.querySelector('[data-error-summary-list]');
  const dependencyImpact = root.querySelector('[data-dependency-impact]');
  const stepList = root.querySelector('[data-step-list]');
  const contextDrawer = root.querySelector('[data-context-drawer]');
  const contextBackdrop = root.querySelector('[data-context-backdrop]');
  const contextTrigger = root.querySelector('[data-open-context]');
  const permissionProfile = root.querySelector('[data-demo-permission-profile]');

  if (!form) return;
  if (stepList) stepList.tabIndex = -1;

  const steps = [
    { label: 'Tipo de relação', description: 'Defina a natureza operacional do cadastro. Essa escolha adapta as etapas seguintes.' },
    { label: 'Dados pessoais', description: 'Identificação, dados civis e contatos essenciais da pessoa.' },
    { label: 'Endereço', description: 'Registre o endereço residencial atual com estrutura adequada ao país e ao tipo de localidade.' },
    { label: 'Vínculo', description: 'Defina empresa, estrutura organizacional, contrato, jornada, remuneração e benefícios.' },
    { label: 'Pagamento', description: 'Informe como o vínculo será pago e o estado de validação dos dados financeiros.' },
    { label: 'Acesso ao sistema', description: 'Crie conta administrativa somente quando realmente necessária, com perfil e escopo.' },
    { label: 'Biometria', description: 'Cadastre biometria facial por câmera ao vivo ou deixe uma pendência para usuário autorizado.' },
    { label: 'Revisão e conclusão', description: 'Revise todas as seções, diferencie erros de pendências e conclua a demonstração.' }
  ];

  const permissionProfiles = {
    admin: ['users:create', 'biometrics:manage'],
    manager: ['users:create'],
    auditor: []
  };

  const dependencyMap = {
    relation_type: [3, 4, 5, 6, 7],
    company: [3, 5, 6, 7],
    unit: [3, 5, 6, 7]
  };

  let currentStep = 0;
  let maxReached = 0;
  let completedSteps = new Set();
  let needsReview = new Set();
  let errorSteps = new Set();
  let biometricMockState = 'AGUARDANDO_CAMERA';
  let runtimeState = root.dataset.wizardRuntimeState || 'READY';
  let revision = 0;
  let submissionId = null;
  let saveTimer = null;
  let dirty = false;
  let permissions = new Set((root.dataset.demoPermissions || '').split(/\s+/).filter(Boolean));
  const structuralSnapshot = new Map();

  const scrollBehavior = () => window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth';
  const hasPermission = (permission) => permissions.has(permission);
  const namedFields = (name) => [...form.elements].filter((el) => el.name === name);

  const showToast = (message) => {
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add('is-visible');
    window.clearTimeout(showToast.timer);
    showToast.timer = window.setTimeout(() => toast.classList.remove('is-visible'), 3200);
  };

  const announce = (message) => {
    if (!liveRegion) return;
    liveRegion.textContent = '';
    window.setTimeout(() => { liveRegion.textContent = message; }, 20);
  };

  const rawValue = (name) => {
    const fields = namedFields(name);
    if (!fields.length) return '';
    const first = fields[0];
    if (first.type === 'radio') return fields.find((field) => field.checked)?.value || '';
    if (first.type === 'checkbox') return first.checked ? 'Sim' : '';
    return String(first.value || '').trim();
  };

  const fieldValue = (name, fallback = '—') => {
    const fields = namedFields(name);
    if (!fields.length) return fallback;
    const first = fields[0];
    if (first.type === 'radio') return fields.find((field) => field.checked)?.value || fallback;
    if (first.type === 'checkbox') return first.checked ? 'Sim' : 'Não';
    if (first.tagName === 'SELECT') {
      if (!first.value) return fallback;
      return first.selectedOptions[0]?.text || first.value || fallback;
    }
    return String(first.value || '').trim() || fallback;
  };

  const fieldIsActive = (field) => {
    if (!field.name || field.disabled) return false;
    if (field.closest('[data-data-lifecycle="HIDDEN_RETAINED"]')) return false;
    const permissionOwner = field.closest('[data-requires-permission]');
    if (permissionOwner && !hasPermission(permissionOwner.dataset.requiresPermission)) return false;
    return true;
  };

  const collectData = ({ activeOnly = false } = {}) => {
    const data = {};
    [...form.elements].forEach((field) => {
      if (!field.name) return;
      if (activeOnly && !fieldIsActive(field)) return;
      if (field.type === 'radio') {
        if (field.checked) data[field.name] = field.value;
        return;
      }
      if (field.type === 'checkbox') {
        data[field.name] = field.checked;
        return;
      }
      data[field.name] = field.value;
    });
    return data;
  };

  const activePayloadPreview = () => collectData({ activeOnly: true });

  const serialize = () => ({
    version: 3,
    revision,
    currentStep,
    maxReached,
    completedSteps: [...completedSteps],
    needsReview: [...needsReview],
    errorSteps: [...errorSteps],
    biometricMockState,
    runtimeState,
    submissionId,
    permissions: [...permissions],
    updatedAt: new Date().toISOString(),
    draftData: collectData(),
    activePayloadPreview: activePayloadPreview()
  });

  const updateSaveState = (state, text) => {
    if (!saveState) return;
    saveState.classList.remove('is-saved', 'is-dirty', 'is-error');
    if (state === 'saved') saveState.classList.add('is-saved');
    if (state === 'dirty') saveState.classList.add('is-dirty');
    if (state === 'error') saveState.classList.add('is-error');
    saveState.textContent = text;
  };

  const setRuntimeState = (state) => {
    runtimeState = state;
    root.dataset.wizardRuntimeState = state;
    root.querySelectorAll('[data-runtime-panel]').forEach((panel) => { panel.hidden = panel.dataset.runtimePanel !== state; });
    if (state === 'SAVE_ERROR') updateSaveState('error', 'Falha ao salvar');
    if (state === 'CONFLICT') updateSaveState('error', 'Conflito — autosave pausado');
    if (state === 'OFFLINE') updateSaveState('dirty', 'Alterações locais — sem conexão');
    if (state === 'READY' && !dirty) updateSaveState('saved', revision ? `Rascunho local salvo · r${revision}` : 'Pronto para editar');
    updateActions();
    announce(state === 'READY' ? 'Estado crítico encerrado.' : `Estado demonstrativo ${state} ativo.`);
  };

  const persist = ({ quiet = false, force = false } = {}) => {
    if (!force && runtimeState === 'CONFLICT') {
      updateSaveState('error', 'Conflito — autosave pausado');
      return false;
    }
    if (!force && runtimeState === 'SAVE_ERROR') {
      updateSaveState('error', 'Falha ao salvar');
      return false;
    }
    revision += 1;
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(serialize()));
      dirty = false;
      if (runtimeState === 'OFFLINE') updateSaveState('dirty', 'Alterações locais — sem conexão');
      else {
        updateSaveState('saved', `Rascunho local salvo · r${revision}`);
        if (!quiet) showToast('Rascunho salvo neste navegador. Nenhum dado foi enviado ao backend.');
      }
      return true;
    } catch (error) {
      revision = Math.max(0, revision - 1);
      setRuntimeState('SAVE_ERROR');
      return false;
    }
  };

  const schedulePersist = () => {
    dirty = true;
    updateSaveState('dirty', runtimeState === 'OFFLINE' ? 'Alterações locais — sem conexão' : 'Alterações locais');
    window.clearTimeout(saveTimer);
    if (['CONFLICT', 'SAVE_ERROR'].includes(runtimeState)) return;
    saveTimer = window.setTimeout(() => persist({ quiet: true }), 500);
  };

  const restore = () => {
    let draft;
    try { draft = JSON.parse(localStorage.getItem(STORAGE_KEY) || 'null'); }
    catch (error) { return; }
    if (!draft?.draftData) return;

    Object.entries(draft.draftData).forEach(([name, value]) => {
      namedFields(name).forEach((field) => {
        if (field.type === 'radio') field.checked = field.value === value;
        else if (field.type === 'checkbox') field.checked = Boolean(value);
        else field.value = value ?? '';
      });
    });

    currentStep = Number.isInteger(draft.currentStep) ? Math.min(Math.max(draft.currentStep, 0), 7) : 0;
    maxReached = Number.isInteger(draft.maxReached) ? Math.min(Math.max(draft.maxReached, currentStep), 7) : currentStep;
    completedSteps = new Set(Array.isArray(draft.completedSteps) ? draft.completedSteps.filter((item) => Number.isInteger(item) && item >= 0 && item <= 7) : []);
    needsReview = new Set(Array.isArray(draft.needsReview) ? draft.needsReview.filter((item) => Number.isInteger(item) && item >= 0 && item <= 7) : []);
    errorSteps = new Set(Array.isArray(draft.errorSteps) ? draft.errorSteps.filter((item) => Number.isInteger(item) && item >= 0 && item <= 7) : []);
    biometricMockState = draft.biometricMockState || 'AGUARDANDO_CAMERA';
    revision = Number.isInteger(draft.revision) ? draft.revision : 0;
    submissionId = draft.submissionId || null;
    if (Array.isArray(draft.permissions)) permissions = new Set(draft.permissions);
    updateSaveState('saved', `Rascunho restaurado · r${revision}`);
  };

  const setupFieldSemantics = () => {
    [...form.elements].forEach((field, index) => {
      if (!field.name) return;
      if (field.matches('[data-required]')) field.setAttribute('aria-required', 'true');
      const wrapper = field.closest('.v2-field');
      if (!wrapper) return;
      const help = wrapper.querySelector('.v2-field__help');
      const error = wrapper.querySelector('.v2-field__error');
      const ids = [];
      if (help) {
        if (!help.id) help.id = `${field.id || field.name || `field-${index}`}-help`;
        ids.push(help.id);
      }
      if (error) {
        if (!error.id) error.id = `${field.id || field.name || `field-${index}`}-error`;
        ids.push(error.id);
      }
      if (ids.length) field.setAttribute('aria-describedby', ids.join(' '));
    });
  };

  const interactiveField = (field) => {
    if (!field) return null;
    const pickerInputId = field.dataset?.entityPickerInputId;
    return pickerInputId ? document.getElementById(pickerInputId) || field : field;
  };

  const clearFieldError = (field) => {
    if (!field) return;
    field.closest('.v2-field')?.classList.remove('has-error');
    field.closest('.v2-control')?.classList.remove('is-invalid');
    field.removeAttribute('aria-invalid');
    const interactive = interactiveField(field);
    if (interactive && interactive !== field) interactive.removeAttribute('aria-invalid');
  };

  const setFieldError = (field, message) => {
    if (!field) return;
    const wrapper = field.closest('.v2-field');
    wrapper?.classList.add('has-error');
    field.closest('.v2-control')?.classList.add('is-invalid');
    field.setAttribute('aria-invalid', 'true');
    const interactive = interactiveField(field);
    if (interactive && interactive !== field) interactive.setAttribute('aria-invalid', 'true');
    const error = wrapper?.querySelector('.v2-field__error');
    if (error && message) error.textContent = message;
  };

  const clearErrorSummary = () => {
    if (!errorSummary) return;
    errorSummary.hidden = true;
    if (errorSummaryList) errorSummaryList.innerHTML = '';
  };

  const renderErrorSummary = (errors) => {
    if (!errorSummary || !errorSummaryList || !errors.length) {
      clearErrorSummary();
      return;
    }
    errorSummaryList.innerHTML = errors.map((item, index) => `<li><button type="button" data-error-target="${item.id}" data-error-index="${index}">${item.label}</button></li>`).join('');
    errorSummary.hidden = false;
    errorSummary.querySelectorAll('[data-error-target]').forEach((button) => button.addEventListener('click', () => interactiveField(document.getElementById(button.dataset.errorTarget))?.focus()));
    errorSummary.focus({ preventScroll: true });
  };

  const requireNamed = (name, message, errors) => {
    const fields = namedFields(name).filter(fieldIsActive);
    if (!fields.length) return true;
    const first = fields[0];
    const valid = first.type === 'radio' ? fields.some((field) => field.checked) : first.type === 'checkbox' ? first.checked : Boolean(String(first.value || '').trim());
    if (!valid) {
      setFieldError(first, message);
      if (!first.id) first.id = `field-${name}`;
      errors.push({ id: first.id, label: message });
      return false;
    }
    fields.forEach(clearFieldError);
    return true;
  };

  const validateGenericRequired = (panel, errors) => {
    const required = [...panel.querySelectorAll('[data-required]')].filter(fieldIsActive);
    const radioNames = new Set();
    required.forEach((field) => {
      if (field.type === 'radio') { radioNames.add(field.name); return; }
      const valid = field.type === 'checkbox' ? field.checked : Boolean(String(field.value || '').trim());
      if (!valid) {
        setFieldError(field, 'Preencha este campo para continuar.');
        if (!field.id) field.id = `field-${field.name}`;
        const label = field.closest('.v2-field')?.querySelector('label,.field-label')?.textContent?.trim() || 'Campo obrigatório';
        errors.push({ id: field.id, label: `${label}: preencha este campo.` });
      } else clearFieldError(field);
    });
    radioNames.forEach((name) => requireNamed(name, 'Selecione uma opção para continuar.', errors));
  };

  const runtimeBlocksAdvance = () => ['OFFLINE', 'CONFLICT', 'PERMISSION_ERROR', 'SUBMIT_OUTCOME_UNKNOWN'].includes(runtimeState);

  const validateStep = (index) => {
    if (runtimeBlocksAdvance()) {
      announce('A etapa não pode avançar enquanto o estado crítico demonstrativo estiver ativo.');
      return false;
    }
    const panel = panels[index];
    if (!panel) return true;
    const errors = [];
    clearErrorSummary();
    validateGenericRequired(panel, errors);

    if (index === 0 && rawValue('relation_type') === 'Outros') requireNamed('other_relation', 'Selecione uma categoria cadastrada.', errors);
    if (index === 1) {
      const cpf = panel.querySelector('[name="cpf"]');
      if (cpf && cpf.value && cpf.value.replace(/\D/g, '').length !== 11) {
        setFieldError(cpf, 'Use 11 dígitos para esta demonstração de CPF.');
        errors.push({ id: cpf.id, label: 'CPF: use 11 dígitos.' });
      }
    }
    if (index === 2) {
      const country = rawValue('country');
      if (country === 'Brasil') {
        const type = rawValue('address_type') || 'Urbano';
        if (type === 'Urbano') {
          requireNamed('cep', 'Informe o CEP.', errors);
          requireNamed('street', 'Informe o logradouro.', errors);
          if (!namedFields('no_number')[0]?.checked) requireNamed('address_number', 'Informe o número ou marque “Sem número”.', errors);
          requireNamed('district', 'Informe o bairro.', errors);
          requireNamed('city', 'Informe a cidade.', errors);
          requireNamed('state', 'Selecione a UF.', errors);
        } else {
          requireNamed('rural_locality', 'Informe a localidade/comunidade.', errors);
          requireNamed('rural_city', 'Informe o município.', errors);
          requireNamed('rural_state', 'Selecione a UF.', errors);
        }
      } else {
        requireNamed('foreign_street', 'Informe o endereço/logradouro.', errors);
        requireNamed('foreign_city', 'Informe a cidade/localidade.', errors);
        requireNamed('foreign_region', 'Informe a região/estado/província.', errors);
      }
    }
    if (index === 3) {
      const relation = rawValue('relation_type');
      if (relation === 'CLT comum') {
        requireNamed('admission_date', 'Informe a data de admissão.', errors);
        requireNamed('salary', 'Informe a remuneração contratual.', errors);
      }
      if (relation === 'CLT intermitente') {
        requireNamed('intermittent_date', 'Informe a data de admissão.', errors);
        requireNamed('hour_value', 'Informe o valor contratual por hora.', errors);
      }
      if (relation === 'Sem vínculo empregatício') {
        requireNamed('non_employee_type', 'Selecione a natureza da relação.', errors);
        requireNamed('relation_start', 'Informe a data de início da relação.', errors);
      }
    }
    if (index === 4) {
      const payment = rawValue('payment_method') || 'Conta bancária';
      if (payment === 'Conta bancária') {
        requireNamed('bank', 'Selecione o banco.', errors);
        requireNamed('agency', 'Informe a agência.', errors);
        requireNamed('account', 'Informe a conta.', errors);
      }
      if (payment === 'Conta-salário') {
        requireNamed('salary_bank', 'Selecione o banco.', errors);
        requireNamed('salary_account', 'Informe a conta-salário.', errors);
      }
      if (payment === 'PIX') requireNamed('pix_key', 'Informe a chave PIX.', errors);
      if (payment === 'Outra') requireNamed('other_payment', 'Selecione uma forma autorizada.', errors);
      if (namedFields('third_party_holder')[0]?.checked) {
        requireNamed('third_party_name', 'Informe o titular.', errors);
        requireNamed('third_party_cpf', 'Informe o CPF do titular.', errors);
        requireNamed('third_party_reason', 'Justifique a exceção.', errors);
      }
    }
    if (index === 5 && namedFields('has_system_access')[0]?.checked) {
      requireNamed('access_role', 'Selecione o perfil RBAC.', errors);
      requireNamed('access_login', 'Informe o login/e-mail.', errors);
      requireNamed('access_scope', 'Selecione o escopo de acesso.', errors);
    }
    if (index === 6 && rawValue('biometric_timing') === 'Agora') {
      if (!hasPermission('biometrics:manage')) errors.push({ id: 'bio-later', label: 'Biometria: “Cadastrar agora” não está disponível para este perfil.' });
      const notice = namedFields('biometric_notice_ack')[0];
      if (!notice?.checked) {
        setFieldError(notice, 'Confirme que as informações de transparência foram apresentadas.');
        if (notice && !notice.id) notice.id = 'biometric_notice_ack';
        errors.push({ id: notice?.id || 'bio-later', label: 'Biometria: confirme a apresentação das informações de transparência.' });
      }
      if (biometricMockState !== 'SUCESSO') errors.push({ id: 'bio-later', label: 'Biometria: simule uma captura válida ou escolha “Configurar depois”.' });
    }
    if (index === 7 && needsReview.size) errors.push({ id: 'onboarding-step-list', label: `Revise ${needsReview.size} etapa(s) sinalizada(s) como NEEDS_REVIEW antes de concluir.` });

    if (errors.length) {
      errorSteps.add(index);
      completedSteps.delete(index);
      renderErrorSummary(errors);
      if (stepStateBadge) {
        stepStateBadge.classList.remove('is-valid', 'is-review');
        stepStateBadge.classList.add('is-error');
        stepStateBadge.textContent = 'Corrigir erros';
      }
      announce(`Há ${errors.length} problema(s) que precisam de revisão na etapa ${index + 1}.`);
      updateStepNavigation();
      return false;
    }

    errorSteps.delete(index);
    completedSteps.add(index);
    needsReview.delete(index);
    if (stepStateBadge) {
      stepStateBadge.classList.remove('is-review', 'is-error');
      stepStateBadge.classList.add('is-valid');
      stepStateBadge.textContent = 'Etapa revisada';
    }
    clearErrorSummary();
    updateStepNavigation();
    return true;
  };

  const stepStatus = (index) => {
    if (errorSteps.has(index)) return 'ERROR';
    if (index === currentStep) return 'CURRENT';
    if (needsReview.has(index)) return 'NEEDS_REVIEW';
    if (completedSteps.has(index)) return 'COMPLETED';
    return 'FUTURE';
  };

  const renderStepList = () => {
    if (!stepList) return;
    stepList.innerHTML = `<div class="step-list__grid">${steps.map((step, index) => {
      const status = stepStatus(index);
      const disabled = index > maxReached ? ' disabled' : '';
      const current = index === currentStep ? ' aria-current="step"' : '';
      return `<button class="step-list__button" type="button" data-step-list-button="${index}" data-step-status="${status}"${current}${disabled}>${index + 1}. ${step.label}</button>`;
    }).join('')}</div>`;
    stepList.querySelectorAll('[data-step-list-button]').forEach((button) => button.addEventListener('click', () => goToStep(Number(button.dataset.stepListButton))));
  };

  const updateStepNavigation = () => {
    stepButtons.forEach((button, index) => {
      const status = stepStatus(index);
      button.dataset.stepStatus = status;
      button.disabled = index > maxReached;
      if (index === currentStep) button.setAttribute('aria-current', 'step');
      else button.removeAttribute('aria-current');
      const suffix = status === 'ERROR' ? ', com erro' : status === 'NEEDS_REVIEW' ? ', precisa revisar' : status === 'COMPLETED' ? ', concluída' : status === 'CURRENT' ? ', atual' : ', futura';
      button.setAttribute('aria-label', `Etapa ${index + 1}: ${steps[index].label}${suffix}`);
    });
    renderStepList();
  };

  const updateHeader = () => {
    const step = steps[currentStep];
    if (stepKicker) stepKicker.textContent = `Etapa ${currentStep + 1} de 8`;
    if (stepTitle) stepTitle.textContent = step.label;
    if (stepDescription) stepDescription.textContent = step.description;
    if (mobileCurrent) mobileCurrent.textContent = `Etapa ${currentStep + 1} de 8`;
    if (mobileLabel) mobileLabel.textContent = step.label;
    if (progressBar) progressBar.style.width = `${((currentStep + 1) / 8) * 100}%`;
    if (stepStateBadge) {
      const status = stepStatus(currentStep);
      stepStateBadge.classList.toggle('is-valid', status === 'COMPLETED');
      stepStateBadge.classList.toggle('is-review', status === 'NEEDS_REVIEW');
      stepStateBadge.classList.toggle('is-error', status === 'ERROR');
      stepStateBadge.textContent = status === 'ERROR' ? 'Corrigir erros' : status === 'NEEDS_REVIEW' ? 'Precisa revisar' : status === 'COMPLETED' ? 'Etapa revisada' : 'Em preenchimento';
    }
  };

  function updateActions() {
    if (backButton) backButton.hidden = currentStep === 0;
    if (nextButton) {
      nextButton.hidden = currentStep === 7;
      nextButton.disabled = runtimeBlocksAdvance();
    }
    if (completeButton) {
      completeButton.hidden = currentStep !== 7;
      completeButton.disabled = runtimeBlocksAdvance() || needsReview.size > 0;
    }
    if (saveExitButton) saveExitButton.disabled = ['CONFLICT', 'SAVE_ERROR'].includes(runtimeState);
  }

  const setConditionalVisibility = (node, visible) => {
    if (!node) return;
    node.hidden = !visible;
    node.dataset.dataLifecycle = visible ? 'VISIBLE_ACTIVE' : 'HIDDEN_RETAINED';
  };

  const updateActivePayloadCount = () => {
    const count = Object.keys(activePayloadPreview()).length;
    const node = root.querySelector('[data-active-payload-count]');
    if (node) node.textContent = `${count} campo${count === 1 ? '' : 's'}`;
  };

  const updateSideSummary = () => {
    const map = {
      '[data-side-relation]': fieldValue('relation_type', 'Não definido'),
      '[data-side-name]': fieldValue('full_name', 'Nome ainda não informado'),
      '[data-side-company]': fieldValue('company', 'Empresa não definida'),
      '[data-side-unit]': fieldValue('unit', 'Unidade não definida'),
      '[data-side-biometric]': biometricMockState === 'SUCESSO' ? 'Captura demonstrada' : fieldValue('biometric_timing', 'Depois')
    };
    Object.entries(map).forEach(([selector, value]) => {
      const node = root.querySelector(selector);
      if (node) node.textContent = value;
    });
  };

  const updateDynamicUI = () => {
    const relation = rawValue('relation_type');
    root.querySelectorAll('[data-show-relation]').forEach((box) => setConditionalVisibility(box, box.dataset.showRelation.split(',').includes(relation)));
    const country = rawValue('country') || 'Brasil';
    root.querySelectorAll('[data-address-country]').forEach((box) => setConditionalVisibility(box, box.dataset.addressCountry === (country === 'Brasil' ? 'BR' : 'FOREIGN')));
    const addressType = rawValue('address_type') || 'Urbano';
    root.querySelectorAll('[data-address-type]').forEach((box) => setConditionalVisibility(box, box.dataset.addressType === addressType));
    const payment = rawValue('payment_method') || 'Conta bancária';
    root.querySelectorAll('[data-payment-type]').forEach((box) => setConditionalVisibility(box, box.dataset.paymentType === payment));
    root.querySelectorAll('[data-third-party]').forEach((box) => setConditionalVisibility(box, Boolean(namedFields('third_party_holder')[0]?.checked)));
    root.querySelectorAll('[data-access-details]').forEach((box) => setConditionalVisibility(box, Boolean(namedFields('has_system_access')[0]?.checked)));
    root.querySelectorAll('[data-biometric-now]').forEach((box) => setConditionalVisibility(box, rawValue('biometric_timing') === 'Agora' && hasPermission('biometrics:manage')));
    root.querySelectorAll('[data-emergency-extra]').forEach((box) => setConditionalVisibility(box, !namedFields('same_emergency_contact')[0]?.checked));
    root.querySelectorAll('[data-dependents]').forEach((box) => setConditionalVisibility(box, rawValue('has_dependents') === 'Sim'));
    root.querySelectorAll('[data-pcd]').forEach((box) => setConditionalVisibility(box, rawValue('pcd_record') === 'Sim'));

    const numberField = namedFields('address_number')[0];
    if (numberField) numberField.disabled = Boolean(namedFields('no_number')[0]?.checked);

    root.querySelectorAll('[data-requires-permission]').forEach((node) => {
      const allowed = hasPermission(node.dataset.requiresPermission);
      node.hidden = !allowed;
      node.dataset.permissionState = allowed ? 'ALLOWED' : 'NO_PERMISSION';
    });

    if (!hasPermission('biometrics:manage') && rawValue('biometric_timing') === 'Agora') {
      const later = namedFields('biometric_timing').find((field) => field.value === 'Depois');
      if (later) later.checked = true;
    }

    updateSideSummary();
    updateActivePayloadCount();
  };

  const renderPanels = () => {
    panels.forEach((panel, index) => { panel.hidden = index !== currentStep; });
    updateStepNavigation();
    updateHeader();
    updateActions();
    updateDynamicUI();
    if (currentStep === 7) buildReview();
  };

  const goToStep = (index, { focus = true } = {}) => {
    if (index > maxReached) return;
    currentStep = Math.min(Math.max(index, 0), 7);
    renderPanels();
    schedulePersist();
    if (focus) {
      stepTitle?.focus({ preventScroll: true });
      window.scrollTo({ top: 0, behavior: scrollBehavior() });
    }
    announce(`Etapa ${currentStep + 1} de 8: ${steps[currentStep].label}.`);
  };

  const markDependenciesForReview = (sourceName) => {
    const targets = dependencyMap[sourceName] || [];
    const affected = targets.filter((index) => index <= maxReached || completedSteps.has(index));
    if (!affected.length) return;
    affected.forEach((index) => {
      errorSteps.delete(index);
      needsReview.add(index);
      completedSteps.delete(index);
    });
    if (dependencyImpact) {
      dependencyImpact.hidden = false;
      dependencyImpact.innerHTML = `<svg class="icon icon--sm" aria-hidden="true"><use href="#i-alert"/></svg><span><strong>Alteração estrutural detectada.</strong> Revise: ${affected.map((index) => steps[index].label).join(', ')}. Dados compatíveis foram preservados; campos ocultos ficam HIDDEN_RETAINED e não entram no payload ativo.</span>`;
    }
    updateStepNavigation();
  };

  const detectStructuralChange = (name) => {
    if (!dependencyMap[name]) return;
    const next = rawValue(name);
    const previous = structuralSnapshot.get(name);
    if (previous !== undefined && previous !== '' && previous !== next) markDependenciesForReview(name);
    structuralSnapshot.set(name, next);
  };

  const maskCpf = (value) => {
    const digits = (value || '').replace(/\D/g, '');
    if (digits.length !== 11) return value || '—';
    return `***.***.***-${digits.slice(-2)}`;
  };

  const paymentReference = () => {
    const payment = rawValue('payment_method') || 'Conta bancária';
    if (payment === 'PIX') return fieldValue('pix_key', 'Não informado');
    if (payment === 'Conta-salário') return fieldValue('salary_bank', 'Não informado');
    if (payment === 'Outra') return fieldValue('other_payment', 'Não informado');
    return fieldValue('bank', 'Não informado');
  };

  function buildReview() {
    const review = root.querySelector('[data-review-list]');
    if (!review) return;
    const access = namedFields('has_system_access')[0]?.checked;
    const biometricTiming = fieldValue('biometric_timing', 'Depois');
    const biometricStatus = biometricMockState === 'SUCESSO' ? 'Ativa (demonstração)' : biometricTiming === 'Agora' ? 'Pendente de captura' : 'Pendente — configurar depois';
    const sections = [
      { step: 0, title: 'Tipo de relação', values: [['Relação', fieldValue('relation_type')], ['Categoria complementar', fieldValue('other_relation', 'Não se aplica')]] },
      { step: 1, title: 'Dados pessoais', values: [['Nome', fieldValue('full_name')], ['CPF', maskCpf(rawValue('cpf'))], ['Nascimento', fieldValue('birth_date')], ['Telefone', fieldValue('phone')]] },
      { step: 2, title: 'Endereço', values: [['País', fieldValue('country')], ['Tipo', fieldValue('address_type', 'Exterior')], ['Localidade', fieldValue('city', fieldValue('rural_city', fieldValue('foreign_city')))], ['UF/Região', fieldValue('state', fieldValue('rural_state', fieldValue('foreign_region')))]] },
      { step: 3, title: 'Vínculo', values: [['Empresa', fieldValue('company')], ['Unidade', fieldValue('unit')], ['Cargo/Função', fieldValue('job_role')], ['Jornada', fieldValue('schedule')], ['Matrícula', 'Será gerada na conclusão real']] },
      { step: 4, title: 'Pagamento', values: [['Forma', fieldValue('payment_method')], ['Banco / Chave', paymentReference()], ['Titularidade', namedFields('third_party_holder')[0]?.checked ? 'Terceiro — requer revisão' : 'Próprio funcionário'], ['Status', 'Pendente de validação']] },
      { step: 5, title: 'Acesso ao sistema', values: access ? [['Acesso', 'Sim'], ['Perfil', fieldValue('access_role')], ['Escopo', fieldValue('access_scope')], ['Ativação', 'Convite pendente']] : [['Acesso', 'Não solicitado'], ['Conta', 'Não será criada']] },
      { step: 6, title: 'Biometria', values: [['Quando cadastrar', biometricTiming], ['Status', biometricStatus], ['Método', 'Câmera ao vivo / multiquadro'], ['Permissão', hasPermission('biometrics:manage') ? 'biometrics:manage disponível' : 'Configurar agora oculto']] }
    ];
    review.innerHTML = sections.map((section) => {
      const status = needsReview.has(section.step) ? '<span class="review-pending review-pending--critical">NEEDS_REVIEW</span>' : '';
      return `<article class="review-card"><header class="review-card__head"><strong>${section.title}</strong><span>${status}<button class="review-card__edit" type="button" data-edit-step="${section.step}">Editar</button></span></header><div class="review-card__body">${section.values.map(([label, value]) => `<div class="review-value"><span>${label}</span><strong>${value || '—'}</strong></div>`).join('')}</div></article>`;
    }).join('');
    review.querySelectorAll('[data-edit-step]').forEach((button) => button.addEventListener('click', () => goToStep(Number(button.dataset.editStep))));
    const pending = root.querySelector('[data-review-pending]');
    const pendingItems = [];
    if (!rawValue('manager')) pendingItems.push('Gestor responsável não definido');
    pendingItems.push('Dados de pagamento aguardam validação');
    if (biometricMockState !== 'SUCESSO') pendingItems.push('Biometria pendente');
    needsReview.forEach((index) => pendingItems.push(`${steps[index].label}: NEEDS_REVIEW`));
    if (pending) pending.innerHTML = pendingItems.map((item) => `<span class="review-pending">${item}</span>`).join('');
  }

  const setCameraState = (state) => {
    biometricMockState = state;
    const panel = root.querySelector('[data-camera-panel]');
    const status = root.querySelector('[data-biometric-status]');
    if (panel) panel.dataset.cameraState = state;
    const messages = {
      AGUARDANDO_CAMERA: 'AGUARDANDO_CAMERA — o mockup não acessa câmera real.',
      CAPTURANDO: 'CAPTURANDO — sequência local demonstrativa iniciada.',
      VALIDANDO_QUALIDADE: 'VALIDANDO_QUALIDADE — enquadramento e iluminação demonstrativos.',
      PROCESSANDO: 'PROCESSANDO — sequência multiquadro demonstrativa.',
      SUCESSO: 'SUCESSO — captura demonstrada; nenhuma imagem foi enviada ou armazenada.'
    };
    if (status) status.textContent = messages[state] || state;
    updateSideSummary();
  };

  const demonstrateBiometricCapture = () => {
    const button = root.querySelector('[data-capture-biometric]');
    const checks = [...root.querySelectorAll('[data-capture-check]')];
    if (!button || !hasPermission('biometrics:manage')) return;
    if (!namedFields('biometric_notice_ack')[0]?.checked) {
      showToast('Primeiro confirme que as informações de transparência foram apresentadas.');
      namedFields('biometric_notice_ack')[0]?.focus();
      return;
    }
    button.disabled = true;
    checks.forEach((item) => item.classList.remove('is-ok'));
    setCameraState('CAPTURANDO');
    window.setTimeout(() => setCameraState('VALIDANDO_QUALIDADE'), 300);
    window.setTimeout(() => {
      checks.slice(0, 3).forEach((item) => item.classList.add('is-ok'));
      setCameraState('PROCESSANDO');
    }, 700);
    window.setTimeout(() => {
      checks.forEach((item) => item.classList.add('is-ok'));
      setCameraState('SUCESSO');
      button.textContent = 'Refazer demonstração';
      button.disabled = false;
      schedulePersist();
      showToast('Captura biométrica marcada como sucesso somente no Design Lab.');
    }, 1200);
  };

  const applyPermissionProfile = (profile) => {
    permissions = new Set(permissionProfiles[profile] || []);
    root.dataset.demoPermissions = [...permissions].join(' ');
    if (!hasPermission('users:create')) setRuntimeState('PERMISSION_ERROR');
    else if (runtimeState === 'PERMISSION_ERROR') setRuntimeState('READY');
    updateDynamicUI();
    updateActions();
    schedulePersist();
  };

  const openContextDrawer = () => {
    if (!contextDrawer || !contextBackdrop) return;
    contextDrawer.hidden = false;
    contextBackdrop.hidden = false;
    contextDrawer.setAttribute('aria-hidden', 'false');
    contextTrigger?.setAttribute('aria-expanded', 'true');
    contextDrawer.querySelector('[data-close-context]')?.focus();
  };

  const closeContextDrawer = () => {
    if (!contextDrawer || !contextBackdrop) return;
    contextDrawer.hidden = true;
    contextBackdrop.hidden = true;
    contextDrawer.setAttribute('aria-hidden', 'true');
    contextTrigger?.setAttribute('aria-expanded', 'false');
    contextTrigger?.focus();
  };

  const enhanceEntityPicker = (select, index) => {
    if (select.dataset.entityPickerReady === 'true') return;
    select.dataset.entityPickerReady = 'true';
    select.classList.add('entity-picker__native');
    const options = [...select.options].filter((option) => option.value);
    const id = `entity-picker-${index}`;
    const inputId = `${id}-input`;
    const wrapper = document.createElement('div');
    wrapper.className = 'entity-picker';
    const input = document.createElement('input');
    input.id = inputId;
    input.type = 'text';
    input.autocomplete = 'off';
    input.className = 'entity-picker__input';
    input.setAttribute('role', 'combobox');
    input.setAttribute('aria-autocomplete', 'list');
    input.setAttribute('aria-expanded', 'false');
    input.setAttribute('aria-controls', `${id}-listbox`);
    if (select.getAttribute('aria-required') === 'true') input.setAttribute('aria-required', 'true');
    const describedBy = select.getAttribute('aria-describedby');
    if (describedBy) input.setAttribute('aria-describedby', describedBy);
    input.placeholder = select.options[0]?.text || 'Pesquisar';

    const label = select.closest('.v2-field')?.querySelector(`label[for="${select.id}"]`);
    if (label) label.setAttribute('for', inputId);
    else input.setAttribute('aria-label', select.name || 'Selecionar entidade');

    select.tabIndex = -1;
    select.setAttribute('aria-hidden', 'true');
    select.dataset.entityPickerInputId = inputId;

    const selected = select.selectedOptions[0];
    if (selected?.value) input.value = selected.text;
    const listbox = document.createElement('div');
    listbox.id = `${id}-listbox`;
    listbox.className = 'entity-picker__listbox';
    listbox.setAttribute('role', 'listbox');
    listbox.hidden = true;
    wrapper.append(input, listbox);
    select.after(wrapper);

    let filtered = options;
    let activeIndex = -1;

    const renderOptions = () => {
      listbox.innerHTML = filtered.length ? filtered.map((option, optionIndex) => `<button class="entity-picker__option" type="button" role="option" data-option-index="${optionIndex}" aria-selected="${option.value === select.value}">${option.text}</button>`).join('') : '<div class="entity-picker__empty">Nenhum resultado nesta fixture local.</div>';
      listbox.querySelectorAll('[data-option-index]').forEach((button) => {
        button.addEventListener('mousedown', (event) => event.preventDefault());
        button.addEventListener('click', () => choose(Number(button.dataset.optionIndex)));
      });
    };

    const open = () => {
      renderOptions();
      listbox.hidden = false;
      input.setAttribute('aria-expanded', 'true');
    };
    const close = () => {
      listbox.hidden = true;
      input.setAttribute('aria-expanded', 'false');
      activeIndex = -1;
    };
    const choose = (optionIndex) => {
      const option = filtered[optionIndex];
      if (!option) return;
      select.value = option.value;
      input.value = option.text;
      clearFieldError(select);
      close();
      select.dispatchEvent(new Event('change', { bubbles: true }));
    };

    input.addEventListener('focus', () => { filtered = options; open(); });
    input.addEventListener('input', () => {
      clearFieldError(select);
      const query = input.value.trim().toLocaleLowerCase('pt-BR');
      filtered = options.filter((option) => option.text.toLocaleLowerCase('pt-BR').includes(query));
      if (select.selectedOptions[0]?.text !== input.value) select.value = '';
      activeIndex = -1;
      open();
    });
    input.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') { close(); return; }
      if (!['ArrowDown', 'ArrowUp', 'Enter'].includes(event.key)) return;
      event.preventDefault();
      if (listbox.hidden) open();
      if (event.key === 'ArrowDown') activeIndex = Math.min(activeIndex + 1, filtered.length - 1);
      if (event.key === 'ArrowUp') activeIndex = Math.max(activeIndex - 1, 0);
      if (event.key === 'Enter' && activeIndex >= 0) { choose(activeIndex); return; }
      listbox.querySelectorAll('[data-option-index]').forEach((button, buttonIndex) => button.setAttribute('aria-selected', String(buttonIndex === activeIndex)));
    });
    input.addEventListener('blur', () => window.setTimeout(close, 120));
    select.addEventListener('change', () => {
      const option = select.selectedOptions[0];
      input.value = option?.value ? option.text : '';
      clearFieldError(select);
    });
  };

  const initializeEntityPickers = () => root.querySelectorAll('select[data-entity-picker]').forEach(enhanceEntityPicker);
  const initializeStructuralSnapshot = () => Object.keys(dependencyMap).forEach((name) => structuralSnapshot.set(name, rawValue(name)));

  form.addEventListener('input', (event) => {
    if (!event.target.matches('input, textarea, select')) return;
    clearFieldError(event.target);
    errorSteps.delete(currentStep);
    completedSteps.delete(currentStep);
    updateDynamicUI();
    updateStepNavigation();
    updateHeader();
    schedulePersist();
  });

  form.addEventListener('change', (event) => {
    if (!event.target.matches('input, select')) return;
    clearFieldError(event.target);
    errorSteps.delete(currentStep);
    completedSteps.delete(currentStep);
    detectStructuralChange(event.target.name);
    updateDynamicUI();
    updateStepNavigation();
    updateHeader();
    schedulePersist();
  });

  nextButton?.addEventListener('click', () => {
    if (!validateStep(currentStep)) return;
    maxReached = Math.max(maxReached, currentStep + 1);
    goToStep(currentStep + 1);
  });
  backButton?.addEventListener('click', () => goToStep(currentStep - 1));
  stepButtons.forEach((button, index) => button.addEventListener('click', () => { if (index <= maxReached) goToStep(index); }));

  root.querySelector('[data-toggle-step-list]')?.addEventListener('click', (event) => {
    const expanded = event.currentTarget.getAttribute('aria-expanded') === 'true';
    event.currentTarget.setAttribute('aria-expanded', String(!expanded));
    if (stepList) stepList.hidden = expanded;
  });

  saveExitButton?.addEventListener('click', () => {
    if (!persist()) return;
    window.location.href = '03.01-funcionarios.html';
  });

  discardButton?.addEventListener('click', () => {
    const confirmed = window.confirm('Descartar o rascunho deste protótipo? Os dados locais desta demonstração serão removidos.');
    if (!confirmed) return;
    localStorage.removeItem(STORAGE_KEY);
    form.reset();
    currentStep = 0;
    maxReached = 0;
    revision = 0;
    submissionId = null;
    biometricMockState = 'AGUARDANDO_CAMERA';
    completedSteps = new Set();
    needsReview = new Set();
    errorSteps = new Set();
    dirty = false;
    structuralSnapshot.clear();
    setRuntimeState('READY');
    renderPanels();
    initializeStructuralSnapshot();
    showToast('Rascunho local descartado.');
  });

  root.querySelector('[data-capture-biometric]')?.addEventListener('click', demonstrateBiometricCapture);

  completeButton?.addEventListener('click', () => {
    if (!validateStep(7) || needsReview.size) return;
    submissionId ||= `demo-${Date.now().toString(36)}`;
    persist({ quiet: true });
    completeButton.disabled = true;
    completeButton.textContent = 'Concluindo demonstração…';
    window.setTimeout(() => {
      if (runtimeState === 'SUBMIT_OUTCOME_UNKNOWN') return;
      if (standardWorkspace) standardWorkspace.hidden = true;
      if (successPanel) successPanel.hidden = false;
      localStorage.removeItem(STORAGE_KEY);
      dirty = false;
      announce('Demonstração concluída. Nenhum cadastro foi enviado ao backend.');
      window.scrollTo({ top: 0, behavior: scrollBehavior() });
    }, 450);
  });

  root.querySelector('[data-success-back]')?.addEventListener('click', () => { window.location.href = '03.01-funcionarios.html'; });
  root.querySelector('[data-success-new]')?.addEventListener('click', () => { window.location.reload(); });
  contextTrigger?.addEventListener('click', openContextDrawer);
  root.querySelector('[data-close-context]')?.addEventListener('click', closeContextDrawer);
  contextBackdrop?.addEventListener('click', closeContextDrawer);
  document.addEventListener('keydown', (event) => { if (event.key === 'Escape' && contextDrawer && !contextDrawer.hidden) closeContextDrawer(); });
  permissionProfile?.addEventListener('change', () => applyPermissionProfile(permissionProfile.value));
  root.querySelectorAll('[data-simulate-state]').forEach((button) => button.addEventListener('click', () => setRuntimeState(button.dataset.simulateState)));
  root.querySelector('[data-resolve-conflict]')?.addEventListener('click', () => { setRuntimeState('READY'); persist({ quiet: true, force: true }); });
  root.querySelector('[data-retry-save]')?.addEventListener('click', () => { setRuntimeState('READY'); persist({ quiet: false, force: true }); });
  root.querySelector('[data-reconcile-submit]')?.addEventListener('click', () => { setRuntimeState('READY'); showToast('Reconciliação demonstrativa: nenhuma submissão real foi encontrada.'); });

  window.addEventListener('beforeunload', (event) => {
    if (!dirty) return;
    event.preventDefault();
    event.returnValue = '';
  });

  setupFieldSemantics();
  restore();
  initializeEntityPickers();
  initializeStructuralSnapshot();
  if (permissionProfile) permissionProfile.value = hasPermission('biometrics:manage') ? 'admin' : hasPermission('users:create') ? 'manager' : 'auditor';
  setRuntimeState(hasPermission('users:create') ? runtimeState : 'PERMISSION_ERROR');
  setCameraState(biometricMockState);
  renderPanels();
  updateDynamicUI();
})();
