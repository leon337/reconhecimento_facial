(() => {
  const body = document.body;
  const toast = document.querySelector('[data-toast]');
  const dateTargets = document.querySelectorAll('[data-current-date]');
  let toastTimer;

  const ensureNativeHiddenContract = () => {
    if (document.querySelector('[data-design-lab-hidden-contract]')) return;
    const style = document.createElement('style');
    style.dataset.designLabHiddenContract = 'true';
    style.textContent = '[hidden] { display: none !important; } .employee-account { color: var(--text-secondary) !important; }';
    document.head.append(style);
  };

  const crossScreenSession = {
    contextTitle: 'Potiguar Locações',
    contextSubtitle: 'Galpão principal · contexto demonstrativo',
    profileName: 'Administrador Demo',
    profileRole: 'Admin · perfil fictício',
    permissions: 'users:view users:create biometrics:manage punch:view punch:create'
  };

  const syncVisibleShell = () => {
    body.dataset.appShellContextTitle = crossScreenSession.contextTitle;
    body.dataset.appShellContextSubtitle = crossScreenSession.contextSubtitle;
    body.dataset.appShellProfileName = crossScreenSession.profileName;
    body.dataset.appShellProfileRole = crossScreenSession.profileRole;
    body.dataset.appShellProfileAvatar = 'AD';

    const shellRoot = document.querySelector('[data-app-shell-root]');
    if (shellRoot) {
      shellRoot.querySelectorAll('[data-app-shell-context-title]').forEach((node) => { node.textContent = crossScreenSession.contextTitle; });
      shellRoot.querySelectorAll('[data-app-shell-context-subtitle]').forEach((node) => { node.textContent = crossScreenSession.contextSubtitle; });
      shellRoot.querySelectorAll('[data-app-shell-profile-name]').forEach((node) => { node.textContent = crossScreenSession.profileName; });
      shellRoot.querySelectorAll('[data-app-shell-profile-role]').forEach((node) => { node.textContent = crossScreenSession.profileRole; });
      shellRoot.querySelectorAll('[data-app-shell-context]').forEach((node) => {
        node.setAttribute('aria-label', `Contexto atual: ${crossScreenSession.contextTitle}, ${crossScreenSession.contextSubtitle}. Demonstração; não altera dados do formulário.`);
      });
    }

    const onboarding = document.querySelector('[data-onboarding-v2]');
    if (!onboarding) return;
    onboarding.dataset.demoPermissions = crossScreenSession.permissions;
    document.title = 'Novo Funcionário — NF-01 Design Lab';

    const breadcrumb = onboarding.querySelector('.breadcrumb');
    if (breadcrumb) {
      const links = [...breadcrumb.querySelectorAll('a')];
      if (links[0]?.textContent.trim() === 'Gestão') {
        const separator = links[0].nextElementSibling;
        links[0].remove();
        if (separator?.textContent.trim() === '›') separator.remove();
      }
      const current = breadcrumb.querySelector('[aria-current="page"]');
      if (current) current.textContent = 'Novo funcionário';
    }

    const profileSelector = onboarding.querySelector('[data-demo-permission-profile]');
    if (profileSelector) {
      const adminOption = profileSelector.querySelector('option[value="admin"]');
      if (adminOption) adminOption.textContent = 'Administrador — override explícito do fluxo';
    }

    const successCopy = onboarding.querySelector('[data-success-panel] .success-screen > p');
    if (successCopy) successCopy.textContent = 'O comportamento visual da conclusão foi executado. Nenhum funcionário, matrícula, conta, dado bancário ou template biométrico foi enviado ao backend; a lista de Funcionários não é alterada por esta demonstração.';
  };

  ensureNativeHiddenContract();
  syncVisibleShell();

  if (dateTargets.length) {
    const formatted = new Intl.DateTimeFormat('pt-BR', { day: '2-digit', month: 'long', year: 'numeric' }).format(new Date());
    dateTargets.forEach((node) => { node.textContent = formatted; });
  }

  const showToast = (message) => {
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add('is-visible');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove('is-visible'), 2200);
  };

  document.querySelectorAll('[data-demo-action]').forEach((control) => {
    control.addEventListener('click', (event) => {
      event.preventDefault();
      const label = control.dataset.demoAction || 'Ação';
      showToast(`${label}: interação visual demonstrativa da NF-01. Nenhuma ação de produção foi executada.`);
    });
  });
})();
