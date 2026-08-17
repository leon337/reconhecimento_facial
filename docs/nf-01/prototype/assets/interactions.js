(() => {
  const toast = document.querySelector('[data-toast]');
  const dateTargets = document.querySelectorAll('[data-current-date]');
  let toastTimer;

  if (dateTargets.length) {
    const formatted = new Intl.DateTimeFormat('pt-BR', {
      day: '2-digit',
      month: 'long',
      year: 'numeric'
    }).format(new Date());
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
