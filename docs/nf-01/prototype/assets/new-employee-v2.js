(() => {
  const root = document.querySelector('[data-onboarding-v2]');
  if (!root) return;

  const STORAGE_KEY = 'cpp:nf01:new-employee-v2:draft';
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

  const steps = [
    { label: 'Tipo de relação', description: 'Defina a natureza operacional do cadastro. Essa escolha adapta as etapas seguintes.' },
    { label: 'Dados pessoais', description: 'Identificação, dados civis e contatos essenciais da pessoa.' },
    { label: 'Endereço', description: 'Registre o endereço residencial atual com estrutura adequada ao país e ao tipo de localidade.' },
    { label: 'Vínculo', description: 'Defina empresa, estrutura organizacional, contrato, jornada, remuneração e benefícios.' },
    { label: 'Pagamento', description: 'Informe como o vínculo será pago e o estado de validação dos dados financeiros.' },
    { label: 'Acesso ao sistema', description: 'Crie conta administrativa somente quando realmente necessária, com perfil e escopo.' },
    { label: 'Biometria', description: 'Cadastre biometria facial por câmera ao vivo ou deixe uma pendência para usuário autorizado.' },
    { label: 'Revisão e conclusão', description: 'Revise todas as seções, diferencie erros de pendências e conclua o cadastro.' }
  ];

  let currentStep = 0;
  let maxReached = 0;
  let saveTimer = null;
  let biometricMockState = 'PENDENTE';
  let completedSteps = new Set();

  const showToast = (message) => {
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add('is-visible');
    window.clearTimeout(showToast.timer);
    showToast.timer = window.setTimeout(() => toast.classList.remove('is-visible'), 3800);
  };

  const announce = (message) => {
    if (!liveRegion) return;
    liveRegion.textContent = '';
    window.setTimeout(() => { liveRegion.textContent = message; }, 20);
  };

  const namedFields = (name) => [...form.elements].filter((el) => el.name === name);

  const rawValue = (name) => {
    const fields = namedFields(name);
    if (!fields.length) return '';
    const first = fields[0];
    if (first.type === 'radio') return fields.find((el) => el.checked)?.value || '';
    if (first.type === 'checkbox') return first.checked ? 'Sim' : '';
    return String(first.value || '').trim();
  };

  const fieldValue = (name, fallback = '—') => {
    const fields = namedFields(name);
    if (!fields.length) return fallback;
    const first = fields[0];
    if (first.type === 'radio') return fields.find((el) => el.checked)?.value || fallback;
    if (first.type === 'checkbox') return first.checked ? 'Sim' : 'Não';
    if (first.tagName === 'SELECT') {
      if (!first.value) return fallback;
      return first.selectedOptions[0]?.text || first.value || fallback;
    }
    return first.value.trim() || fallback;
  };

  const serialize = () => {
    const data = {};
    [...form.elements].forEach((field) => {
      if (!field.name || field.disabled) return;
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
    return {
      version: 2,
      currentStep,
      maxReached,
      completedSteps: [...completedSteps],
      biometricMockState,
      updatedAt: new Date().toISOString(),
      data
    };
  };

  const persist = ({ quiet = false } = {}) => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(serialize()));
      if (saveState) {
        saveState.classList.add('is-saved');
        saveState.textContent = 'Rascunho salvo';
      }
      if (!quiet) showToast('Rascunho salvo neste navegador. Nenhum dado foi enviado ao backend.');
    } catch (error) {
      if (saveState) {
        saveState.classList.remove('is-saved');
        saveState.textContent = 'Falha ao salvar';
      }
      showToast('Não foi possível salvar o rascunho local desta demonstração.');
    }
  };

  const schedulePersist = () => {
    if (saveState) {
      saveState.classList.remove('is-saved');
      saveState.textContent = 'Salvando…';
    }
    window.clearTimeout(saveTimer);
    saveTimer = window.setTimeout(() => persist({ quiet: true }), 450);
  };

  const restore = () => {
    let draft;
    try {
      draft = JSON.parse(localStorage.getItem(STORAGE_KEY) || 'null');
    } catch (error) {
      return;
    }
    if (!draft?.data) return;

    Object.entries(draft.data).forEach(([name, value]) => {
      const fields = namedFields(name);
      fields.forEach((field) => {
        if (field.type === 'radio') field.checked = field.value === value;
        else if (field.type === 'checkbox') field.checked = Boolean(value);
        else field.value = value ?? '';
      });
    });

    currentStep = Number.isInteger(draft.currentStep) ? Math.min(Math.max(draft.currentStep, 0), 7) : 0;
    maxReached = Number.isInteger(draft.maxReached) ? Math.min(Math.max(draft.maxReached, currentStep), 7) : currentStep;
    completedSteps = new Set(Array.isArray(draft.completedSteps) ? draft.completedSteps.filter((item) => Number.isInteger(item) && item >= 0 && item <= 7) : []);
    biometricMockState = draft.biometricMockState || 'PENDENTE';
    if (saveState) {
      saveState.classList.add('is-saved');
      saveState.textContent = 'Rascunho restaurado';
    }
  };

  const clearFieldError = (field) => {
    const wrapper = field.closest('.v2-field');
    const shell = field.closest('.v2-control');
    wrapper?.classList.remove('has-error');
    shell?.classList.remove('is-invalid');
    field.removeAttribute('aria-invalid');
  };

  const setFieldError = (field, message) => {
    const wrapper = field.closest('.v2-field');
    const shell = field.closest('.v2-control');
    const error = wrapper?.querySelector('.v2-field__error');
    wrapper?.classList.add('has-error');
    shell?.classList.add('is-invalid');
    field.setAttribute('aria-invalid', 'true');
    if (error && message) error.textContent = message;
  };

  const requireNamed = (name, message, firstInvalidRef) => {
    const fields = namedFields(name).filter((field) => !field.disabled && !field.closest('[hidden]'));
    if (!fields.length) return true;
    const first = fields[0];
    let valid;
    if (first.type === 'radio') valid = fields.some((field) => field.checked);
    else if (first.type === 'checkbox') valid = first.checked;
    else valid = Boolean(first.value.trim());

    if (!valid) {
      setFieldError(first, message);
      if (!firstInvalidRef.value) firstInvalidRef.value = first;
      return false;
    }
    fields.forEach(clearFieldError);
    return true;
  };

  const validateGenericRequired = (panel, firstInvalidRef) => {
    const required = [...panel.querySelectorAll('[data-required]')].filter((field) => !field.disabled && !field.closest('[hidden]'));
    const radioNames = new Set();

    required.forEach((field) => {
      if (field.type === 'radio') {
        radioNames.add(field.name);
        return;
      }
      const valid = field.type === 'checkbox' ? field.checked : Boolean(field.value.trim());
      if (!valid) {
        setFieldError(field, 'Preencha este campo para continuar.');
        if (!firstInvalidRef.value) firstInvalidRef.value = field;
      } else clearFieldError(field);
    });

    radioNames.forEach((name) => requireNamed(name, 'Selecione uma opção para continuar.', firstInvalidRef));
  };

  const validateStep = (index) => {
    const panel = panels[index];
    if (!panel) return true;
    const firstInvalidRef = { value: null };
    validateGenericRequired(panel, firstInvalidRef);

    if (index === 0 && rawValue('relation_type') === 'Outros') {
      requireNamed('other_relation', 'Selecione uma categoria cadastrada.', firstInvalidRef);
    }

    if (index === 1) {
      const cpf = panel.querySelector('[name="cpf"]');
      if (cpf && cpf.value && cpf.value.replace(/\D/g, '').length !== 11) {
        setFieldError(cpf, 'Use 11 dígitos para esta demonstração de CPF.');
        if (!firstInvalidRef.value) firstInvalidRef.value = cpf;
      }
    }

    if (index === 2) {
      const country = rawValue('country');
      if (country === 'Brasil') {
        const type = rawValue('address_type') || 'Urbano';
        if (type === 'Urbano') {
          requireNamed('cep', 'Informe o CEP.', firstInvalidRef);
          requireNamed('street', 'Informe o logradouro.', firstInvalidRef);
          const noNumber = namedFields('no_number')[0]?.checked;
          if (!noNumber) requireNamed('address_number', 'Informe o número ou marque “Sem número”.', firstInvalidRef);
          requireNamed('district', 'Informe o bairro.', firstInvalidRef);
          requireNamed('city', 'Informe a cidade.', firstInvalidRef);
          requireNamed('state', 'Selecione a UF.', firstInvalidRef);
        } else {
          requireNamed('rural_locality', 'Informe a localidade/comunidade.', firstInvalidRef);
          requireNamed('rural_city', 'Informe o município.', firstInvalidRef);
          requireNamed('rural_state', 'Selecione a UF.', firstInvalidRef);
        }
      } else {
        requireNamed('foreign_street', 'Informe o endereço/logradouro.', firstInvalidRef);
        requireNamed('foreign_city', 'Informe a cidade/localidade.', firstInvalidRef);
        requireNamed('foreign_region', 'Informe a região/estado/província.', firstInvalidRef);
      }
    }

    if (index === 3) {
      const relation = rawValue('relation_type');
      if (relation === 'CLT comum') {
        requireNamed('admission_date', 'Informe a data de admissão.', firstInvalidRef);
        requireNamed('salary', 'Informe a remuneração contratual.', firstInvalidRef);
      }
      if (relation === 'CLT intermitente') {
        requireNamed('intermittent_date', 'Informe a data de admissão.', firstInvalidRef);
        requireNamed('hour_value', 'Informe o valor contratual por hora.', firstInvalidRef);
      }
      if (relation === 'Sem vínculo empregatício') {
        requireNamed('non_employee_type', 'Selecione a natureza da relação.', firstInvalidRef);
        requireNamed('relation_start', 'Informe a data de início da relação.', firstInvalidRef);
      }
    }

    if (index === 4) {
      const payment = rawValue('payment_method') || 'Conta bancária';
      if (payment === 'Conta bancária') {
        requireNamed('bank', 'Selecione o banco.', firstInvalidRef);
        requireNamed('agency', 'Informe a agência.', firstInvalidRef);
        requireNamed('account', 'Informe a conta.', firstInvalidRef);
      }
      if (payment === 'Conta-salário') {
        requireNamed('salary_bank', 'Selecione o banco.', firstInvalidRef);
        requireNamed('salary_account', 'Informe a conta-salário.', firstInvalidRef);
      }
      if (payment === 'PIX') requireNamed('pix_key', 'Informe a chave PIX.', firstInvalidRef);
      if (payment === 'Outra') requireNamed('other_payment', 'Selecione uma forma autorizada.', firstInvalidRef);

      if (namedFields('third_party_holder')[0]?.checked) {
        requireNamed('third_party_name', 'Informe o titular.', firstInvalidRef);
        requireNamed('third_party_cpf', 'Informe o CPF do titular.', firstInvalidRef);
        requireNamed('third_party_reason', 'Justifique a exceção.', firstInvalidRef);
      }
    }

    if (index === 5 && namedFields('has_system_access')[0]?.checked) {
      requireNamed('access_role', 'Selecione o perfil RBAC.', firstInvalidRef);
      requireNamed('access_login', 'Informe o login/e-mail.', firstInvalidRef);
      requireNamed('access_scope', 'Selecione o escopo de acesso.', firstInvalidRef);
    }

    if (index === 6 && rawValue('biometric_timing') === 'Agora') {
      const notice = namedFields('biometric_notice_ack')[0];
      if (!notice?.checked) {
        setFieldError(notice, 'Confirme que as informações de transparência foram apresentadas.');
        if (!firstInvalidRef.value) firstInvalidRef.value = notice;
      }
      if (biometricMockState !== 'ATIVA') {
        if (!firstInvalidRef.value) firstInvalidRef.value = root.querySelector('[data-capture-biometric]');
        showToast('Simule uma captura válida ou escolha “Configurar depois”.');
      }
    }

    if (firstInvalidRef.value) {
      firstInvalidRef.value.focus?.();
      completedSteps.delete(index);
      stepStateBadge?.classList.remove('is-valid');
      if (stepStateBadge) stepStateBadge.textContent = 'Revisar campos';
      announce(`Há campos que precisam de revisão na etapa ${index + 1}.`);
      updateStepButtons();
      return false;
    }

    completedSteps.add(index);
    stepStateBadge?.classList.add('is-valid');
    if (stepStateBadge) stepStateBadge.textContent = 'Etapa revisada';
    updateStepButtons();
    return true;
  };

  const updateStepButtons = () => {
    stepButtons.forEach((button, index) => {
      button.classList.toggle('is-complete', completedSteps.has(index));
      if (index === currentStep) button.setAttribute('aria-current', 'step');
      else button.removeAttribute('aria-current');
      button.disabled = index > maxReached;
      const stateIcon = button.querySelector('[data-step-check]');
      if (stateIcon) stateIcon.hidden = !completedSteps.has(index);
    });
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
      const valid = completedSteps.has(currentStep);
      stepStateBadge.classList.toggle('is-valid', valid);
      stepStateBadge.textContent = valid ? 'Etapa revisada' : 'Em preenchimento';
    }
  };

  const updateActions = () => {
    if (backButton) backButton.disabled = currentStep === 0;
    if (nextButton) nextButton.hidden = currentStep === 7;
    if (completeButton) completeButton.hidden = currentStep !== 7;
  };

  const renderPanels = () => {
    panels.forEach((panel, index) => { panel.hidden = index !== currentStep; });
    updateStepButtons();
    updateHeader();
    updateActions();
    updateDynamicUI();
    if (currentStep === 7) buildReview();
  };

  const goToStep = (index, { focus = true } = {}) => {
    currentStep = Math.min(Math.max(index, 0), 7);
    maxReached = Math.max(maxReached, currentStep);
    renderPanels();
    schedulePersist();
    if (focus) {
      stepTitle?.setAttribute('tabindex', '-1');
      stepTitle?.focus({ preventScroll: true });
      stepTitle?.removeAttribute('tabindex');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
    announce(`Etapa ${currentStep + 1} de 8: ${steps[currentStep].label}.`);
  };

  const updateDynamicUI = () => {
    const relation = rawValue('relation_type');
    root.querySelectorAll('[data-show-relation]').forEach((box) => {
      const accepted = box.dataset.showRelation.split(',');
      box.hidden = !accepted.includes(relation);
    });

    const country = rawValue('country') || 'Brasil';
    root.querySelectorAll('[data-address-country]').forEach((box) => {
      box.hidden = box.dataset.addressCountry !== (country === 'Brasil' ? 'BR' : 'FOREIGN');
    });

    const addressType = rawValue('address_type') || 'Urbano';
    root.querySelectorAll('[data-address-type]').forEach((box) => {
      box.hidden = box.dataset.addressType !== addressType;
    });

    const payment = rawValue('payment_method') || 'Conta bancária';
    root.querySelectorAll('[data-payment-type]').forEach((box) => {
      box.hidden = box.dataset.paymentType !== payment;
    });

    const thirdParty = namedFields('third_party_holder')[0]?.checked;
    root.querySelectorAll('[data-third-party]').forEach((box) => { box.hidden = !thirdParty; });

    const access = namedFields('has_system_access')[0]?.checked;
    root.querySelectorAll('[data-access-details]').forEach((box) => { box.hidden = !access; });

    const biometricNow = rawValue('biometric_timing') || 'Depois';
    root.querySelectorAll('[data-biometric-now]').forEach((box) => { box.hidden = biometricNow !== 'Agora'; });

    const sameEmergency = namedFields('same_emergency_contact')[0]?.checked;
    root.querySelectorAll('[data-emergency-extra]').forEach((box) => { box.hidden = Boolean(sameEmergency); });

    const hasDependents = rawValue('has_dependents') || 'Não';
    root.querySelectorAll('[data-dependents]').forEach((box) => { box.hidden = hasDependents !== 'Sim'; });

    const pcd = rawValue('pcd_record') || 'Não';
    root.querySelectorAll('[data-pcd]').forEach((box) => { box.hidden = pcd !== 'Sim'; });

    const noNumber = namedFields('no_number')[0]?.checked;
    const numberField = namedFields('address_number')[0];
    if (numberField) {
      numberField.disabled = Boolean(noNumber);
      if (noNumber) numberField.value = '';
    }

    updateSideSummary();
  };

  const updateSideSummary = () => {
    const map = {
      '[data-side-relation]': fieldValue('relation_type', 'Não definido'),
      '[data-side-name]': fieldValue('full_name', 'Nome ainda não informado'),
      '[data-side-company]': fieldValue('company', 'Empresa não definida'),
      '[data-side-unit]': fieldValue('unit', 'Unidade não definida'),
      '[data-side-biometric]': biometricMockState === 'ATIVA' ? 'Captura demonstrada' : fieldValue('biometric_timing', 'Depois')
    };
    Object.entries(map).forEach(([selector, value]) => {
      const node = root.querySelector(selector);
      if (node) node.textContent = value;
    });
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

  const buildReview = () => {
    const review = root.querySelector('[data-review-list]');
    if (!review) return;
    const access = namedFields('has_system_access')[0]?.checked;
    const biometricTiming = fieldValue('biometric_timing', 'Depois');
    const biometricStatus = biometricMockState === 'ATIVA' ? 'Ativa (demonstração)' : (biometricTiming === 'Agora' ? 'Pendente de captura' : 'Pendente — configurar depois');

    const sections = [
      {
        step: 0,
        title: 'Tipo de relação',
        values: [['Relação', fieldValue('relation_type')], ['Categoria complementar', fieldValue('other_relation', 'Não se aplica')]]
      },
      {
        step: 1,
        title: 'Dados pessoais',
        values: [['Nome', fieldValue('full_name')], ['CPF', maskCpf(rawValue('cpf'))], ['Nascimento', fieldValue('birth_date')], ['Telefone', fieldValue('phone')]]
      },
      {
        step: 2,
        title: 'Endereço',
        values: [['País', fieldValue('country')], ['Tipo', fieldValue('address_type', 'Exterior')], ['Localidade', fieldValue('city', fieldValue('rural_city', fieldValue('foreign_city')))], ['UF/Região', fieldValue('state', fieldValue('rural_state', fieldValue('foreign_region')))]]
      },
      {
        step: 3,
        title: 'Vínculo',
        values: [['Empresa', fieldValue('company')], ['Unidade', fieldValue('unit')], ['Cargo/Função', fieldValue('job_role')], ['Jornada', fieldValue('schedule')], ['Matrícula', 'Será gerada na conclusão']]
      },
      {
        step: 4,
        title: 'Pagamento',
        values: [['Forma', fieldValue('payment_method')], ['Banco / Chave', paymentReference()], ['Titularidade', namedFields('third_party_holder')[0]?.checked ? 'Terceiro — requer revisão' : 'Próprio funcionário'], ['Status', 'Pendente de validação']]
      },
      {
        step: 5,
        title: 'Acesso ao sistema',
        values: access ? [['Acesso', 'Sim'], ['Perfil', fieldValue('access_role')], ['Escopo', fieldValue('access_scope')], ['Ativação', 'Convite pendente']] : [['Acesso', 'Não solicitado'], ['Conta', 'Não será criada']]
      },
      {
        step: 6,
        title: 'Biometria',
        values: [['Quando cadastrar', biometricTiming], ['Status', biometricStatus], ['Método', 'Câmera ao vivo / multiquadro'], ['Foto administrativa', 'Separada da biometria']]
      }
    ];

    review.innerHTML = sections.map((section) => `
      <article class="review-card">
        <header class="review-card__head">
          <strong>${section.title}</strong>
          <button class="review-card__edit" type="button" data-edit-step="${section.step}">Editar</button>
        </header>
        <div class="review-card__body">
          ${section.values.map(([label, value]) => `<div class="review-value"><span>${label}</span><strong>${value || '—'}</strong></div>`).join('')}
        </div>
      </article>
    `).join('');

    review.querySelectorAll('[data-edit-step]').forEach((button) => {
      button.addEventListener('click', () => goToStep(Number(button.dataset.editStep)));
    });

    const pending = root.querySelector('[data-review-pending]');
    const pendingItems = [];
    if (!rawValue('manager')) pendingItems.push('Gestor responsável não definido');
    pendingItems.push('Dados de pagamento aguardam validação');
    if (biometricMockState !== 'ATIVA') pendingItems.push('Biometria pendente');
    if (pending) pending.innerHTML = pendingItems.map((item) => `<span class="review-pending">${item}</span>`).join('');
  };

  const demonstrateBiometricCapture = () => {
    const button = root.querySelector('[data-capture-biometric]');
    const status = root.querySelector('[data-biometric-status]');
    const checks = [...root.querySelectorAll('[data-capture-check]')];
    if (!button || !status) return;
    if (!namedFields('biometric_notice_ack')[0]?.checked) {
      showToast('Primeiro confirme que as informações de transparência foram apresentadas.');
      namedFields('biometric_notice_ack')[0]?.focus();
      return;
    }

    button.disabled = true;
    button.textContent = 'Validando captura…';
    status.textContent = 'Processando sequência multiquadro desta demonstração.';
    checks.forEach((item) => item.classList.remove('is-ok'));
    window.setTimeout(() => {
      checks.forEach((item, index) => {
        window.setTimeout(() => item.classList.add('is-ok'), index * 180);
      });
    }, 250);
    window.setTimeout(() => {
      biometricMockState = 'ATIVA';
      status.textContent = 'Captura demonstrada com sucesso. Nenhuma imagem foi enviada ou armazenada.';
      button.textContent = 'Refazer demonstração';
      button.disabled = false;
      updateSideSummary();
      schedulePersist();
      showToast('Biometria marcada como ativa apenas no mockup local.');
    }, 1200);
  };

  form.addEventListener('input', (event) => {
    if (event.target.matches('input, textarea, select')) {
      clearFieldError(event.target);
      completedSteps.delete(currentStep);
      updateDynamicUI();
      updateStepButtons();
      updateHeader();
      schedulePersist();
    }
  });

  form.addEventListener('change', (event) => {
    if (event.target.matches('input, select')) {
      clearFieldError(event.target);
      completedSteps.delete(currentStep);
      updateDynamicUI();
      updateStepButtons();
      updateHeader();
      schedulePersist();
    }
  });

  nextButton?.addEventListener('click', () => {
    if (!validateStep(currentStep)) return;
    goToStep(currentStep + 1);
  });

  backButton?.addEventListener('click', () => goToStep(currentStep - 1));

  stepButtons.forEach((button, index) => {
    button.addEventListener('click', () => {
      if (index <= maxReached) goToStep(index);
    });
  });

  saveExitButton?.addEventListener('click', () => {
    persist();
    window.setTimeout(() => { window.location.href = '03.01-funcionarios.html'; }, 300);
  });

  discardButton?.addEventListener('click', () => {
    const confirmed = window.confirm('Descartar o rascunho deste protótipo? Os dados locais desta demonstração serão removidos.');
    if (!confirmed) return;
    localStorage.removeItem(STORAGE_KEY);
    form.reset();
    currentStep = 0;
    maxReached = 0;
    biometricMockState = 'PENDENTE';
    completedSteps = new Set();
    renderPanels();
    updateDynamicUI();
    showToast('Rascunho local descartado.');
  });

  root.querySelector('[data-capture-biometric]')?.addEventListener('click', demonstrateBiometricCapture);

  completeButton?.addEventListener('click', () => {
    if (!validateStep(7)) return;
    persist({ quiet: true });
    if (standardWorkspace) standardWorkspace.hidden = true;
    if (successPanel) successPanel.hidden = false;
    localStorage.removeItem(STORAGE_KEY);
    announce('Demonstração concluída. Nenhum cadastro foi enviado ao backend.');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });

  root.querySelector('[data-success-back]')?.addEventListener('click', () => {
    window.location.href = '03.01-funcionarios.html';
  });

  root.querySelector('[data-success-new]')?.addEventListener('click', () => {
    window.location.reload();
  });

  restore();
  renderPanels();
  updateDynamicUI();
})();
