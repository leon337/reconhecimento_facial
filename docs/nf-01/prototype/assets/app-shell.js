(() => {
  if (window.NF01AppShell?.mount) {
    window.NF01AppShell.mount();
    return;
  }

  const VERSION = 'i8';
  const STORAGE_KEY = 'nf01.designLab.appShell.compact';
  const DESKTOP_QUERY = window.matchMedia('(min-width: 70rem)');
  const MOBILE_QUERY = window.matchMedia('(max-width: 47.99rem)');

  const shellMarkup = `
    <a class="skip-link" href="#conteudo" data-app-shell-skip>Ir para o conteúdo</a>

    <svg class="icon-sprite" aria-hidden="true" data-app-shell-icons>
      <symbol id="app-icon-grid" viewBox="0 0 24 24"><path d="M4 4h6v6H4zM14 4h6v6h-6zM4 14h6v6H4zM14 14h6v6h-6z" fill="none" stroke="currentColor" stroke-width="1.8"/></symbol>
      <symbol id="app-icon-clock" viewBox="0 0 24 24"><circle cx="12" cy="12" r="8" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M12 7v5l3 2" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></symbol>
      <symbol id="app-icon-scan" viewBox="0 0 24 24"><path d="M8 3H5a2 2 0 0 0-2 2v3M16 3h3a2 2 0 0 1 2 2v3M8 21H5a2 2 0 0 1-2-2v-3M16 21h3a2 2 0 0 0 2-2v-3" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/><circle cx="12" cy="12" r="3.5" fill="none" stroke="currentColor" stroke-width="1.8"/></symbol>
      <symbol id="app-icon-users" viewBox="0 0 24 24"><circle cx="9" cy="8" r="3" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M3.5 19c.6-3.2 2.4-5 5.5-5s4.9 1.8 5.5 5M15 6.5c2 .2 3.2 1.4 3.2 3.1S17 12.5 15 12.8M17 14.2c2 .6 3 2.1 3.5 4.3" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></symbol>
      <symbol id="app-icon-building" viewBox="0 0 24 24"><path d="M5 21V5l7-2v18M12 8h7v13M3 21h18M8 8h1M8 12h1M8 16h1M15 12h1M15 16h1" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></symbol>
      <symbol id="app-icon-pulse" viewBox="0 0 24 24"><path d="M3 12h4l2-5 3 10 2-6 2 3h5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></symbol>
      <symbol id="app-icon-list" viewBox="0 0 24 24"><path d="M8 6h11M8 12h11M8 18h11M4 6h.01M4 12h.01M4 18h.01" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></symbol>
      <symbol id="app-icon-settings" viewBox="0 0 24 24"><circle cx="12" cy="12" r="3" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M5 12a7 7 0 0 1 .2-1.7L3.7 9.1l2-3.4 1.8.7A7 7 0 0 1 10 5V3h4v2a7 7 0 0 1 2.5 1.4l1.8-.7 2 3.4-1.5 1.2A7 7 0 0 1 19 12c0 .6-.1 1.2-.2 1.7l1.5 1.2-2 3.4-1.8-.7A7 7 0 0 1 14 19v2h-4v-2a7 7 0 0 1-2.5-1.4l-1.8.7-2-3.4 1.5-1.2A7 7 0 0 1 5 12Z" fill="none" stroke="currentColor" stroke-width="1.5"/></symbol>
      <symbol id="app-icon-menu" viewBox="0 0 24 24"><path d="M4 7h16M4 12h16M4 17h16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></symbol>
      <symbol id="app-icon-panel" viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="16" rx="2" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M9 4v16M14 9l3 3-3 3" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></symbol>
      <symbol id="app-icon-bell" viewBox="0 0 24 24"><path d="M6 10a6 6 0 0 1 12 0v4l2 3H4l2-3zM10 20h4" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></symbol>
      <symbol id="app-icon-chevron" viewBox="0 0 24 24"><path d="m9 6 6 6-6 6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></symbol>
    </svg>

    <div class="app-shell" data-app-shell-root>
      <aside class="app-shell__sidebar" id="app-shell-sidebar" aria-label="Navegação principal" data-app-shell-sidebar>
        <div class="app-shell__brand">
          <div class="app-shell__brand-mark" aria-hidden="true">CP</div>
          <div class="app-shell__brand-copy"><strong>Controle de Ponto</strong><span>POTIGUAR</span></div>
        </div>

        <div class="app-shell__sidebar-toolbar">
          <button class="app-shell__collapse" type="button" aria-controls="app-shell-sidebar" aria-expanded="true" aria-label="Recolher navegação" data-app-shell-collapse>
            <svg class="icon" aria-hidden="true"><use href="#app-icon-panel"/></svg>
          </button>
        </div>

        <nav class="app-shell__nav" aria-label="Áreas administrativas">
          <div class="app-shell__nav-section">
            <div class="app-shell__nav-list">
              <a class="app-shell__nav-item" href="02.01-dashboard.html" data-app-shell-nav="dashboard" data-label="Dashboard"><svg class="icon" aria-hidden="true"><use href="#app-icon-grid"/></svg><span class="app-shell__nav-text">Dashboard</span></a>
            </div>
          </div>
          <div class="app-shell__nav-section">
            <div class="app-shell__nav-label">Operação</div>
            <div class="app-shell__nav-list">
              <a class="app-shell__nav-item" href="#" data-app-shell-placeholder data-app-shell-nav="records" data-label="Registros"><svg class="icon" aria-hidden="true"><use href="#app-icon-clock"/></svg><span class="app-shell__nav-text">Registros</span></a>
              <a class="app-shell__nav-item" href="#" data-app-shell-placeholder data-app-shell-independent data-app-shell-nav="punch" data-label="Registrar ponto — fluxo independente"><svg class="icon" aria-hidden="true"><use href="#app-icon-scan"/></svg><span class="app-shell__nav-text">Registrar ponto</span><span class="app-shell__nav-external" aria-hidden="true">↗</span></a>
            </div>
          </div>
          <div class="app-shell__nav-section">
            <div class="app-shell__nav-label">Gestão</div>
            <div class="app-shell__nav-list">
              <a class="app-shell__nav-item" href="03.01-funcionarios.html" data-app-shell-nav="employees" data-label="Funcionários"><svg class="icon" aria-hidden="true"><use href="#app-icon-users"/></svg><span class="app-shell__nav-text">Funcionários</span></a>
              <a class="app-shell__nav-item" href="#" data-app-shell-placeholder data-app-shell-nav="companies" data-label="Empresas e obras"><svg class="icon" aria-hidden="true"><use href="#app-icon-building"/></svg><span class="app-shell__nav-text">Empresas / Obras</span></a>
            </div>
          </div>
          <div class="app-shell__nav-section">
            <div class="app-shell__nav-label">Sistema</div>
            <div class="app-shell__nav-list">
              <a class="app-shell__nav-item" href="#" data-app-shell-placeholder data-app-shell-nav="health" data-label="Saúde operacional"><svg class="icon" aria-hidden="true"><use href="#app-icon-pulse"/></svg><span class="app-shell__nav-text">Saúde operacional</span></a>
              <a class="app-shell__nav-item" href="#" data-app-shell-placeholder data-app-shell-nav="events" data-label="Eventos e logs"><svg class="icon" aria-hidden="true"><use href="#app-icon-list"/></svg><span class="app-shell__nav-text">Eventos / Logs</span></a>
              <a class="app-shell__nav-item" href="#" data-app-shell-placeholder data-app-shell-nav="settings" data-label="Configurações"><svg class="icon" aria-hidden="true"><use href="#app-icon-settings"/></svg><span class="app-shell__nav-text">Configurações</span></a>
            </div>
          </div>
        </nav>
      </aside>

      <button class="app-shell__backdrop" type="button" tabindex="-1" aria-label="Fechar navegação" data-app-shell-backdrop></button>

      <div class="app-shell__main-region" data-app-shell-main-region>
        <header class="app-shell__topbar">
          <div class="app-shell__topbar-start">
            <button class="icon-button app-shell__mobile-menu" type="button" aria-controls="app-shell-sidebar" aria-expanded="false" aria-label="Abrir navegação" data-app-shell-mobile-menu>
              <svg class="icon" aria-hidden="true"><use href="#app-icon-menu"/></svg>
            </button>
            <button class="app-shell__context" type="button" data-app-shell-context>
              <svg class="icon" aria-hidden="true"><use href="#app-icon-building"/></svg>
              <span class="app-shell__context-copy"><strong data-app-shell-context-title></strong><span data-app-shell-context-subtitle></span></span>
              <svg class="icon icon--sm" aria-hidden="true"><use href="#app-icon-chevron"/></svg>
            </button>
          </div>
          <div class="app-shell__topbar-end">
            <button class="icon-button" type="button" aria-label="Notificações demonstrativas"><svg class="icon" aria-hidden="true"><use href="#app-icon-bell"/></svg></button>
            <button class="app-shell__profile" type="button" aria-label="Abrir perfil demonstrativo">
              <span class="app-shell__profile-avatar" aria-hidden="true" data-app-shell-profile-avatar>AD</span>
              <span class="app-shell__profile-copy"><strong data-app-shell-profile-name></strong><span data-app-shell-profile-role></span></span>
            </button>
          </div>
        </header>
      </div>
    </div>`;

  const getStoredCompact = () => {
    try { return localStorage.getItem(STORAGE_KEY) === '1'; } catch (_) { return false; }
  };

  const storeCompact = (compact) => {
    try { localStorage.setItem(STORAGE_KEY, compact ? '1' : '0'); } catch (_) { /* visual preference only */ }
  };

  const mount = () => {
    const body = document.body;
    if (!body || body.dataset.appShellMounted === 'true') return;

    const contentCandidates = [...document.querySelectorAll('[data-app-shell-content]')];
    if (
      contentCandidates.length !== 1 ||
      !(contentCandidates[0] instanceof HTMLElement) ||
      contentCandidates[0].tagName !== 'MAIN'
    ) {
      console.warn('NF-01 AppShell: expected exactly one <main data-app-shell-content>.');
      return;
    }
    const [content] = contentCandidates;

    if (document.querySelector('[data-app-shell-root]')) {
      console.warn('NF-01 AppShell: root already exists before canonical mount; mount aborted.');
      return;
    }

    if (!content.id) content.id = 'conteudo';
    content.classList.add('app-shell__workspace');

    const template = document.createElement('template');
    template.innerHTML = shellMarkup.trim();
    const fragment = template.content;
    const shell = fragment.querySelector('[data-app-shell-root]');
    const sidebar = fragment.querySelector('[data-app-shell-sidebar]');
    const mainRegion = fragment.querySelector('[data-app-shell-main-region]');
    const collapseButton = fragment.querySelector('[data-app-shell-collapse]');
    const mobileButton = fragment.querySelector('[data-app-shell-mobile-menu]');
    const backdrop = fragment.querySelector('[data-app-shell-backdrop]');
    const skipLink = fragment.querySelector('[data-app-shell-skip]');

    if (!(shell && sidebar && mainRegion && collapseButton && mobileButton && backdrop && skipLink)) return;
    skipLink.setAttribute('href', `#${content.id}`);

    const contextTitle = body.dataset.appShellContextTitle || 'Potiguar Locações';
    const contextSubtitle = body.dataset.appShellContextSubtitle || 'Galpão principal · contexto demonstrativo';
    const profileName = body.dataset.appShellProfileName || 'Administrador Demo';
    const profileRole = body.dataset.appShellProfileRole || 'Perfil fictício';
    const profileAvatar = body.dataset.appShellProfileAvatar || 'AD';

    fragment.querySelector('[data-app-shell-context-title]').textContent = contextTitle;
    fragment.querySelector('[data-app-shell-context-subtitle]').textContent = contextSubtitle;
    fragment.querySelector('[data-app-shell-profile-name]').textContent = profileName;
    fragment.querySelector('[data-app-shell-profile-role]').textContent = profileRole;
    fragment.querySelector('[data-app-shell-profile-avatar]').textContent = profileAvatar;
    fragment.querySelector('[data-app-shell-context]').setAttribute(
      'aria-label',
      `Contexto atual: ${contextTitle}, ${contextSubtitle}. Demonstração; não altera dados do formulário.`
    );

    const activeKey = body.dataset.appShellActive || '';
    fragment.querySelectorAll('[data-app-shell-nav]').forEach((link) => {
      if (link.dataset.appShellNav === activeKey) link.setAttribute('aria-current', 'page');
      else link.removeAttribute('aria-current');
    });

    document.body.append(fragment);
    mainRegion.append(content);
    body.dataset.appShellMounted = 'true';
    body.dataset.appShellVersion = VERSION;

    let mobileTrigger = null;

    const setCompact = (compact, { persist = true } = {}) => {
      if (!DESKTOP_QUERY.matches) compact = false;
      body.classList.toggle('app-shell-is-compact', compact);
      collapseButton.setAttribute('aria-expanded', String(!compact));
      collapseButton.setAttribute('aria-label', compact ? 'Expandir navegação' : 'Recolher navegação');
      collapseButton.title = compact ? 'Expandir navegação' : 'Recolher navegação';
      if (persist) storeCompact(compact);
    };

    const setSidebarAvailability = (available) => {
      sidebar.toggleAttribute('inert', !available);
      if (available) sidebar.removeAttribute('aria-hidden');
      else sidebar.setAttribute('aria-hidden', 'true');
    };

    const getSidebarFocusables = () => [...sidebar.querySelectorAll(
      'a[href], button:not([disabled]), [tabindex]:not([tabindex="-1"])'
    )].filter((element) => (
      element instanceof HTMLElement &&
      !element.hasAttribute('inert') &&
      !element.hidden &&
      element.getClientRects().length > 0 &&
      window.getComputedStyle(element).visibility !== 'hidden'
    ));

    const setMobileOpen = (open, { restoreFocus = false } = {}) => {
      if (open) {
        const activeElement = document.activeElement;
        mobileTrigger = activeElement instanceof HTMLElement && mainRegion.contains(activeElement)
          ? activeElement
          : mobileButton;
      }

      body.classList.toggle('app-shell-is-nav-open', open);
      mobileButton.setAttribute('aria-expanded', String(open));

      if (MOBILE_QUERY.matches) {
        setSidebarAvailability(open);
        mainRegion.toggleAttribute('inert', open);
      } else {
        setSidebarAvailability(true);
        mainRegion.removeAttribute('inert');
      }

      if (open) {
        requestAnimationFrame(() => {
          const [first] = getSidebarFocusables();
          if (first) first.focus();
        });
      } else if (restoreFocus && mobileTrigger instanceof HTMLElement) {
        mobileTrigger.focus();
      }
    };

    const syncViewportMode = () => {
      setMobileOpen(false);
      if (MOBILE_QUERY.matches) {
        setCompact(false, { persist: false });
        setSidebarAvailability(false);
        mainRegion.removeAttribute('inert');
        return;
      }
      setSidebarAvailability(true);
      mainRegion.removeAttribute('inert');
      if (DESKTOP_QUERY.matches) setCompact(getStoredCompact(), { persist: false });
      else setCompact(false, { persist: false });
    };

    const trapMobileFocus = (event) => {
      if (event.key !== 'Tab' || !MOBILE_QUERY.matches || !body.classList.contains('app-shell-is-nav-open')) return;
      const focusables = getSidebarFocusables();
      if (!focusables.length) return;
      const first = focusables[0];
      const last = focusables[focusables.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    };

    collapseButton.addEventListener('click', () => {
      setCompact(!body.classList.contains('app-shell-is-compact'));
    });

    mobileButton.addEventListener('click', () => {
      setMobileOpen(!body.classList.contains('app-shell-is-nav-open'), { restoreFocus: true });
    });

    backdrop.addEventListener('click', () => setMobileOpen(false, { restoreFocus: true }));

    sidebar.querySelectorAll('[data-app-shell-placeholder]').forEach((link) => {
      link.addEventListener('click', (event) => {
        event.preventDefault();
        if (MOBILE_QUERY.matches) setMobileOpen(false, { restoreFocus: true });
      });
    });

    sidebar.addEventListener('click', (event) => {
      if (!MOBILE_QUERY.matches) return;
      const target = event.target instanceof Element ? event.target.closest('a[href]:not([data-app-shell-placeholder])') : null;
      if (target) setMobileOpen(false, { restoreFocus: false });
    });

    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && body.classList.contains('app-shell-is-nav-open')) {
        event.preventDefault();
        setMobileOpen(false, { restoreFocus: true });
        return;
      }
      trapMobileFocus(event);
    });

    DESKTOP_QUERY.addEventListener?.('change', syncViewportMode);
    MOBILE_QUERY.addEventListener?.('change', syncViewportMode);
    syncViewportMode();
  };

  window.NF01AppShell = Object.freeze({ version: VERSION, mount });

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', mount, { once: true });
  } else {
    mount();
  }
})();