(() => {
  const form = document.querySelector('[data-new-employee-form]');
  const dialog = document.querySelector('[data-success-dialog]');
  const password = document.querySelector('[data-password]');
  const togglePassword = document.querySelector('[data-password-toggle]');
  const cancel = document.querySelector('[data-cancel-form]');

  if (togglePassword && password) {
    togglePassword.addEventListener('click', () => {
      const showing = password.type === 'text';
      password.type = showing ? 'password' : 'text';
      togglePassword.setAttribute('aria-pressed', String(!showing));
      togglePassword.setAttribute('aria-label', showing ? 'Mostrar senha' : 'Ocultar senha');
      password.focus();
    });
  }

  const clearError = (field) => {
    const wrapper = field.closest('.form-field');
    const shell = field.closest('.input-shell');
    wrapper?.classList.remove('has-error');
    shell?.classList.remove('is-invalid');
    field.removeAttribute('aria-invalid');
  };

  const setError = (field) => {
    const wrapper = field.closest('.form-field');
    const shell = field.closest('.input-shell');
    wrapper?.classList.add('has-error');
    shell?.classList.add('is-invalid');
    field.setAttribute('aria-invalid', 'true');
  };

  form?.querySelectorAll('input, textarea').forEach((field) => {
    field.addEventListener('input', () => clearError(field));
  });

  form?.addEventListener('submit', (event) => {
    event.preventDefault();

    const requiredFields = [...form.querySelectorAll('[data-required]')];
    let firstInvalid = null;

    requiredFields.forEach((field) => {
      if (!field.value.trim()) {
        setError(field);
        firstInvalid ||= field;
      } else {
        clearError(field);
      }
    });

    if (firstInvalid) {
      firstInvalid.focus();
      return;
    }

    if (dialog?.showModal) {
      dialog.showModal();
    }
  });

  cancel?.addEventListener('click', () => {
    window.location.href = '03.01-funcionarios.html';
  });

  document.querySelectorAll('[data-close-dialog]').forEach((button) => {
    button.addEventListener('click', () => dialog?.close());
  });

  document.querySelector('[data-demo-biometric]')?.addEventListener('click', () => {
    dialog?.close();
    const toast = document.querySelector('[data-toast]');
    if (!toast) return;
    toast.textContent = 'Demonstração NF-01: o próximo passo abriria Cadastro biométrico somente para perfis com biometrics:manage.';
    toast.classList.add('is-visible');
    window.setTimeout(() => toast.classList.remove('is-visible'), 4200);
  });
})();
