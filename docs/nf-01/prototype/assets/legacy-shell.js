(() => {
  const body = document.querySelector('body[data-legacy-shell]');
  if (!body) return;

  const menuButton = body.querySelector('[data-nav-toggle]');
  const sidebar = body.querySelector('.sidebar');
  if (!menuButton || !sidebar) return;

  const setNav = (open) => {
    body.classList.toggle('nav-open', open);
    menuButton.setAttribute('aria-expanded', String(open));
  };

  menuButton.addEventListener('click', () => {
    setNav(!body.classList.contains('nav-open'));
  });

  document.addEventListener('click', (event) => {
    if (!body.classList.contains('nav-open')) return;
    if (sidebar.contains(event.target) || menuButton.contains(event.target)) return;
    setNav(false);
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') setNav(false);
  });
})();
