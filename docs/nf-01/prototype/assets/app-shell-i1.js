(() => {
  const body = document.body;
  const sidebar = document.querySelector('[data-i1-sidebar]');
  const main = document.querySelector('.i1-main');
  const collapseButton = document.querySelector('[data-i1-collapse]');
  const mobileButton = document.querySelector('[data-i1-mobile-menu]');
  const backdrop = document.querySelector('[data-i1-backdrop]');
  const storageKey = 'nf01.designLab.appShell.compact';
  const desktopQuery = window.matchMedia('(min-width: 70rem)');
  const mobileQuery = window.matchMedia('(max-width: 47.99rem)');
  let mobileTrigger = null;

  const setCompact = (compact, { persist = true } = {}) => {
    if (!desktopQuery.matches) compact = false;
    body.classList.toggle('i1-shell-compact', compact);
    if (collapseButton) {
      collapseButton.setAttribute('aria-expanded', String(!compact));
      collapseButton.setAttribute('aria-label', compact ? 'Expandir navegação' : 'Recolher navegação');
      collapseButton.title = compact ? 'Expandir navegação' : 'Recolher navegação';
    }
    if (persist) {
      try { localStorage.setItem(storageKey, compact ? '1' : '0'); } catch (_) { /* preference only */ }
    }
  };

  const getStoredCompact = () => {
    try { return localStorage.getItem(storageKey) === '1'; } catch (_) { return false; }
  };

  const setSidebarAvailability = (available) => {
    if (!sidebar) return;
    sidebar.toggleAttribute('inert', !available);
    if (available) sidebar.removeAttribute('aria-hidden');
    else sidebar.setAttribute('aria-hidden', 'true');
  };

  const setMobileOpen = (open, { restoreFocus = false } = {}) => {
    body.classList.toggle('i1-nav-open', open);
    if (mobileButton) mobileButton.setAttribute('aria-expanded', String(open));

    if (mobileQuery.matches) {
      setSidebarAvailability(open);
      main?.toggleAttribute('inert', open);
    } else {
      setSidebarAvailability(true);
      main?.removeAttribute('inert');
    }

    if (open) {
      mobileTrigger = document.activeElement instanceof HTMLElement ? document.activeElement : mobileButton;
      requestAnimationFrame(() => {
        const firstLink = sidebar?.querySelector('a, button');
        if (firstLink instanceof HTMLElement) firstLink.focus();
      });
    } else if (restoreFocus && mobileTrigger instanceof HTMLElement) {
      mobileTrigger.focus();
    }
  };

  const syncViewportMode = () => {
    setMobileOpen(false);
    if (mobileQuery.matches) {
      setCompact(false, { persist: false });
      setSidebarAvailability(false);
      main?.removeAttribute('inert');
      return;
    }
    setSidebarAvailability(true);
    main?.removeAttribute('inert');
    if (desktopQuery.matches) setCompact(getStoredCompact(), { persist: false });
    else setCompact(false, { persist: false });
  };

  collapseButton?.addEventListener('click', () => {
    setCompact(!body.classList.contains('i1-shell-compact'));
  });

  mobileButton?.addEventListener('click', () => {
    setMobileOpen(!body.classList.contains('i1-nav-open'), { restoreFocus: true });
  });

  backdrop?.addEventListener('click', () => setMobileOpen(false, { restoreFocus: true }));

  document.querySelectorAll('.i1-nav__item[href="#"]').forEach((link) => {
    link.addEventListener('click', (event) => event.preventDefault());
  });

  sidebar?.addEventListener('click', (event) => {
    if (!mobileQuery.matches) return;
    const target = event.target instanceof Element ? event.target.closest('a') : null;
    if (target) setMobileOpen(false, { restoreFocus: false });
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && body.classList.contains('i1-nav-open')) {
      event.preventDefault();
      setMobileOpen(false, { restoreFocus: true });
    }
  });

  desktopQuery.addEventListener?.('change', syncViewportMode);
  mobileQuery.addEventListener?.('change', syncViewportMode);
  syncViewportMode();
})();
