(() => {
  const body = document.body;
  const collection = document.querySelector('[data-employee-collection]');
  if (!collection) return;

  const search = collection.querySelector('[data-employee-search]');
  const biometric = collection.querySelector('[data-biometric-filter]');
  const employeeFunction = collection.querySelector('[data-function-filter]');
  const clear = collection.querySelector('[data-clear-filters]');
  const rows = Array.from(collection.querySelectorAll('[data-employee-row]'));
  const filterEmpty = collection.querySelector('[data-employee-filter-empty]');
  const tableWrap = collection.querySelector('[data-employee-table-wrap]');
  const readyContent = collection.querySelector('[data-employee-ready-content]');
  const statePanels = Array.from(collection.querySelectorAll('[data-employee-state-panel]'));
  const summary = collection.querySelector('[data-result-summary]');
  const summaryRegion = document.querySelector('[data-employee-summary-region]');
  const totalDataset = document.querySelector('[data-total-dataset]');
  const biometricPending = document.querySelector('[data-biometric-pending]');
  const accessSummary = document.querySelector('[data-employee-access-summary]');

  const permissions = new Set((body.dataset.employeeDemoPermissions || '')
    .split(/\s+/)
    .filter(Boolean));
  const role = body.dataset.employeeDemoRole || 'unknown';
  const allowedStates = new Set(['ready', 'loading', 'empty', 'error', 'offline', 'no_permission']);
  const requestedState = allowedStates.has(body.dataset.employeeDemoState)
    ? body.dataset.employeeDemoState
    : 'ready';
  const collectionState = permissions.has('users:view') ? requestedState : 'no_permission';

  const normalize = (value) => (value || '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .trim();

  const hasPermission = (rule) => rule
    .split(/\s+/)
    .filter(Boolean)
    .every((permission) => permissions.has(permission));

  const applyPermissionVisibility = () => {
    document.querySelectorAll('[data-requires-permission]').forEach((element) => {
      const allowed = hasPermission(element.dataset.requiresPermission || '');
      element.hidden = !allowed;
    });

    rows.forEach((row) => {
      const mutationActions = Array.from(row.querySelectorAll('[data-employee-mutation]'));
      const hasVisibleMutation = mutationActions.some((action) => !action.hidden);
      const readonly = row.querySelector('[data-employee-readonly]');
      if (readonly) readonly.hidden = hasVisibleMutation;
    });
  };

  const applyCollectionState = () => {
    const isReady = collectionState === 'ready';
    if (readyContent) readyContent.hidden = !isReady;
    if (summaryRegion) summaryRegion.hidden = !isReady;

    statePanels.forEach((panel) => {
      panel.hidden = panel.dataset.employeeStatePanel !== collectionState;
    });
  };

  const syncFixtureMetrics = () => {
    if (totalDataset) totalDataset.textContent = String(rows.length);
    if (biometricPending) {
      const pending = rows.filter((row) => row.dataset.biometric !== 'active').length;
      biometricPending.textContent = String(pending);
    }
  };

  const applyFilters = () => {
    if (collectionState !== 'ready') return;

    const query = normalize(search?.value);
    const biometricValue = biometric?.value || 'all';
    const functionValue = employeeFunction?.value || 'all';
    let visible = 0;

    rows.forEach((row) => {
      const matchesQuery = !query
        || normalize(row.dataset.name).includes(query)
        || normalize(row.dataset.registration).includes(query);
      const matchesBiometric = biometricValue === 'all' || row.dataset.biometric === biometricValue;
      const matchesFunction = functionValue === 'all'
        || normalize(row.dataset.function) === normalize(functionValue);
      const show = matchesQuery && matchesBiometric && matchesFunction;
      row.hidden = !show;
      if (show) visible += 1;
    });

    const noFilterResults = visible === 0;
    if (filterEmpty) filterEmpty.hidden = !noFilterResults;
    if (tableWrap) tableWrap.hidden = noFilterResults;
    if (summary) {
      summary.textContent = visible === 1
        ? `Mostrando 1 de ${rows.length} funcionários demonstrativos`
        : `Mostrando ${visible} de ${rows.length} funcionários demonstrativos`;
    }
  };

  if (accessSummary) {
    const relevantPermissions = ['users:view', 'users:create', 'biometrics:manage']
      .filter((permission) => permissions.has(permission));
    accessSummary.textContent = `Perfil demo: ${role} · permissões visuais: ${relevantPermissions.join(', ') || 'nenhuma'}.`;
  }

  applyPermissionVisibility();
  syncFixtureMetrics();
  applyCollectionState();

  if (collectionState === 'ready') {
    search?.addEventListener('input', applyFilters);
    biometric?.addEventListener('change', applyFilters);
    employeeFunction?.addEventListener('change', applyFilters);

    clear?.addEventListener('click', () => {
      if (search) search.value = '';
      if (biometric) biometric.value = 'all';
      if (employeeFunction) employeeFunction.value = 'all';
      applyFilters();
      search?.focus();
    });

    applyFilters();
  }
})();
