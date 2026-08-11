(() => {
  const search = document.querySelector('[data-employee-search]');
  const biometric = document.querySelector('[data-biometric-filter]');
  const role = document.querySelector('[data-role-filter]');
  const clear = document.querySelector('[data-clear-filters]');
  const rows = Array.from(document.querySelectorAll('[data-employee-row]'));
  const empty = document.querySelector('[data-employee-empty]');
  const tableWrap = document.querySelector('[data-employee-table-wrap]');
  const summary = document.querySelector('[data-result-summary]');
  const totalVisible = document.querySelector('[data-total-visible]');

  const normalize = (value) => (value || '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .trim();

  const applyFilters = () => {
    const query = normalize(search?.value);
    const biometricValue = biometric?.value || 'all';
    const roleValue = role?.value || 'all';
    let visible = 0;

    rows.forEach((row) => {
      const matchesQuery = !query
        || normalize(row.dataset.name).includes(query)
        || normalize(row.dataset.registration).includes(query);
      const matchesBiometric = biometricValue === 'all' || row.dataset.biometric === biometricValue;
      const matchesRole = roleValue === 'all' || normalize(row.dataset.role) === normalize(roleValue);
      const show = matchesQuery && matchesBiometric && matchesRole;
      row.hidden = !show;
      if (show) visible += 1;
    });

    if (empty) empty.classList.toggle('is-visible', visible === 0);
    if (tableWrap) tableWrap.hidden = visible === 0;
    if (summary) summary.textContent = visible === 1
      ? 'Mostrando 1 funcionário demonstrativo'
      : `Mostrando ${visible} funcionários demonstrativos`;
    if (totalVisible) totalVisible.textContent = String(visible);
  };

  search?.addEventListener('input', applyFilters);
  biometric?.addEventListener('change', applyFilters);
  role?.addEventListener('change', applyFilters);

  clear?.addEventListener('click', () => {
    if (search) search.value = '';
    if (biometric) biometric.value = 'all';
    if (role) role.value = 'all';
    applyFilters();
    search?.focus();
  });

  applyFilters();
})();
