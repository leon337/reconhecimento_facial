import { chromium } from 'playwright';
import AxeBuilder from '@axe-core/playwright';
import fs from 'node:fs/promises';
import path from 'node:path';

const BASE = process.env.NF01_BASE_URL || 'http://127.0.0.1:4173';
const OUT = process.env.NF01_EVIDENCE_DIR || path.resolve('../../evidence/phase-n/automation-run');
const SHOTS = path.join(OUT, 'screenshots');
const results = [];
const surfaces = [
  ['app-shell', 'AppShell', 'screens/01.01-app-shell.html'],
  ['dashboard', 'Dashboard', 'screens/02.01-dashboard.html'],
  ['employees', 'Funcionários', 'screens/03.01-funcionarios.html'],
  ['onboarding', 'Novo Funcionário', 'screens/03.04-novo-funcionario-v2.html']
];
const widths = [360, 480, 768, 900, 1024, 1280, 1440];

function add({ id, phase, surface, viewport = 'N/A', zoom = '100%', profile = 'admin', state = 'READY', action = '', expected = '', actual = '', result, severity = 'MEDIUM', evidence = '' }) {
  results.push({ CASE_ID: id, PHASE: phase, SURFACE: surface, VIEWPORT_OR_CONTAINER: viewport, ZOOM: zoom, PROFILE: profile, STATE: state, PRECONDITION: '', ACTION: action, EXPECTED: expected, ACTUAL: actual, RESULT: result, SEVERITY_IF_FAIL: severity, EVIDENCE_REF: evidence, FOLLOW_UP_REF: '' });
}
async function visible(locator) { try { return await locator.isVisible(); } catch { return false; } }
async function screenshot(page, name) { const rel = `screenshots/${name}`; await page.screenshot({ path: path.join(SHOTS, name), fullPage: true }); return rel; }
async function snapshot(page) {
  return page.evaluate(() => ({
    viewport: innerWidth,
    scrollWidth: Math.max(document.documentElement.scrollWidth, document.body?.scrollWidth || 0),
    globalOverflow: Math.max(document.documentElement.scrollWidth, document.body?.scrollWidth || 0) > innerWidth + 2,
    bodyTextLength: (document.body?.innerText || '').trim().length,
    mainCount: document.querySelectorAll('main').length,
    shellCount: document.querySelectorAll('[data-app-shell-root]').length
  }));
}
async function tabUntil(page, selector, max = 80) {
  for (let i = 0; i < max; i += 1) {
    if (await page.evaluate((s) => document.activeElement?.matches?.(s) || false, selector)) return true;
    await page.keyboard.press('Tab');
  }
  return false;
}

async function runN2(browser) {
  for (const [id, label, file] of surfaces) {
    for (const width of widths) {
      const context = await browser.newContext({ viewport: { width, height: width <= 480 ? 820 : 900 } });
      const page = await context.newPage();
      await page.goto(`${BASE}/${file}`, { waitUntil: 'domcontentloaded' });
      await page.waitForTimeout(180);
      const s = await snapshot(page);
      const evidence = await screenshot(page, `N2-${id}-${width}.png`);
      const blank = id !== 'app-shell' && s.bodyTextLength < 80;
      add({ id: `N2-${id.toUpperCase()}-${width}-REFLOW`, phase: 'N2', surface: label, viewport: width, action: 'Renderizar viewport e medir reflow/overflow.', expected: 'Conteúdo renderizado, um main e sem overflow horizontal global.', actual: JSON.stringify(s), result: !s.globalOverflow && !blank && s.mainCount === 1 ? 'PASS' : 'FAIL', severity: blank || s.mainCount !== 1 ? 'BLOCKER' : 'HIGH', evidence });
      if (id === 'onboarding' && width === 360) {
        const current = await visible(page.locator('[data-mobile-current]'));
        const toggle = await visible(page.locator('[data-toggle-step-list]'));
        add({ id: 'N2-ONBOARDING-360-MOBILE_STEPPER', phase: 'N2', surface: label, viewport: width, action: 'Inspecionar stepper mobile.', expected: 'Etapa X de 8 e Ver etapas visíveis.', actual: `current=${current}; toggle=${toggle}`, result: current && toggle ? 'PASS' : 'FAIL', severity: 'HIGH', evidence });
      }
      await context.close();
    }
  }

  for (const [id, label, file] of surfaces) {
    const context = await browser.newContext({ viewport: { width: 720, height: 900 }, deviceScaleFactor: 2 });
    const page = await context.newPage();
    await page.goto(`${BASE}/${file}`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(180);
    const s = await snapshot(page);
    const evidence = await screenshot(page, `N2-${id}-zoom200-equivalent.png`);
    add({ id: `N2-${id.toUpperCase()}-ZOOM200_EQUIVALENT`, phase: 'N2', surface: label, viewport: '1440 physical / 720 CSS', zoom: '200%-equivalent', action: 'Capturar reflow equivalente a 200% em headless.', expected: 'Conteúdo renderizado e sem overflow global impeditivo.', actual: JSON.stringify(s), result: !s.globalOverflow && s.bodyTextLength >= 80 ? 'PASS' : 'FAIL', severity: 'HIGH', evidence });
    await context.close();
  }
  add({ id: 'N2-MANUAL_BROWSER_ZOOM_200', phase: 'N2', surface: 'Todas', zoom: '200%', action: 'Operar controle real de zoom do navegador.', expected: 'Zoom real 200% validado manualmente.', actual: 'Chromium headless não expõe UI de navegador; equivalente 720 CSS @2x foi capturado.', result: 'BLOCKED_TOOLING', severity: 'HIGH', evidence: 'N2-*-zoom200-equivalent.png' });

  const context = await browser.newContext({ viewport: { width: 1024, height: 900 } });
  const page = await context.newPage();
  await page.goto(`${BASE}/screens/02.01-dashboard.html`, { waitUntil: 'domcontentloaded' });
  const handoff = page.locator('[data-cross-screen-handoff="biometric-missing"]');
  const exists = (await handoff.count()) === 1;
  if (exists) await Promise.all([page.waitForURL(/03\.01-funcionarios\.html/).catch(() => null), handoff.click()]);
  await page.waitForTimeout(150);
  const onEmployees = page.url().includes('03.01-funcionarios.html');
  const value = onEmployees ? await page.locator('[data-biometric-filter]').inputValue().catch(() => '') : '';
  const rows = onEmployees ? await page.locator('[data-employee-row]:visible').count() : 0;
  const evidence = await screenshot(page, 'N2-crossscreen-dashboard-employees.png');
  add({ id: 'N2-CROSSSCREEN-DASHBOARD_EMPLOYEES_HANDOFF', phase: 'N2', surface: 'Dashboard → Funcionários', viewport: 1024, action: 'Ativar biometrias pendentes.', expected: 'Abrir Funcionários com biometric=missing e 2 resultados.', actual: `exists=${exists}; url=${page.url()}; biometric=${value}; rows=${rows}`, result: exists && onEmployees && value === 'missing' && rows === 2 ? 'PASS' : 'FAIL', severity: 'BLOCKER', evidence });

  if (onEmployees) {
    await page.locator('[data-employee-search]').fill('João');
    const link = page.locator('[data-new-employee-link]');
    if (await visible(link)) {
      await Promise.all([page.waitForURL(/03\.04-novo-funcionario-v2\.html/).catch(() => null), link.click()]);
      await page.goBack({ waitUntil: 'domcontentloaded' });
      await page.waitForTimeout(120);
      const restored = await page.locator('[data-employee-search]').inputValue().catch(() => '');
      add({ id: 'N2-CROSSSCREEN-LIST_STATE_RESTORE', phase: 'N2', surface: 'Funcionários ↔ Novo Funcionário', viewport: 1024, action: 'Pesquisar João, entrar no onboarding e voltar.', expected: 'Busca João restaurada.', actual: `search=${restored}`, result: restored === 'João' ? 'PASS' : 'FAIL', severity: 'HIGH', evidence: await screenshot(page, 'N2-crossscreen-list-state-restore.png') });
    }
  }
  await context.close();
}

async function employeeVariant(browser, role, permissions, state = 'ready') {
  const context = await browser.newContext({ viewport: { width: 1024, height: 900 } });
  const page = await context.newPage();
  await page.route('**/screens/03.01-funcionarios.html*', async (route) => {
    const response = await route.fetch();
    let html = await response.text();
    html = html.replace(/data-employee-demo-role="[^"]*"/, `data-employee-demo-role="${role}"`)
      .replace(/data-employee-demo-permissions="[^"]*"/, `data-employee-demo-permissions="${permissions.join(' ')}"`)
      .replace(/data-employee-demo-state="[^"]*"/, `data-employee-demo-state="${state}"`);
    await route.fulfill({ response, body: html });
  });
  await page.goto(`${BASE}/screens/03.01-funcionarios.html`, { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(150);
  return { context, page };
}

async function runN3(browser) {
  for (const [id, label, file] of surfaces) {
    for (const width of [360, 1440]) {
      const context = await browser.newContext({ viewport: { width, height: 900 } });
      const page = await context.newPage();
      await page.goto(`${BASE}/${file}`, { waitUntil: 'domcontentloaded' });
      await page.waitForTimeout(180);
      try {
        const scan = await new AxeBuilder({ page }).analyze();
        const severe = scan.violations.filter((v) => ['critical', 'serious'].includes(v.impact));
        const details = severe.map((v) => ({ id: v.id, impact: v.impact, nodes: v.nodes.map((n) => ({ target: n.target, html: n.html.slice(0, 180), summary: n.failureSummary })) }));
        add({ id: `N3-${id.toUpperCase()}-${width}-AXE`, phase: 'N3', surface: label, viewport: width, action: 'Executar axe-core.', expected: '0 violações critical/serious.', actual: JSON.stringify(details), result: severe.length ? 'FAIL' : 'PASS', severity: 'HIGH', evidence: await screenshot(page, `N3-${id}-${width}-axe.png`) });
      } catch (error) {
        add({ id: `N3-${id.toUpperCase()}-${width}-AXE`, phase: 'N3', surface: label, viewport: width, action: 'Executar axe-core.', expected: 'Scan executável.', actual: String(error), result: 'BLOCKED_TOOLING', severity: 'HIGH' });
      }
      await context.close();
    }
  }

  // Testes de teclado independentes para não depender da posição relativa dos triggers no DOM.
  {
    const context = await browser.newContext({ viewport: { width: 1024, height: 900 } });
    const page = await context.newPage();
    await page.goto(`${BASE}/screens/03.04-novo-funcionario-v2.html`, { waitUntil: 'domcontentloaded' });
    await page.evaluate(() => localStorage.clear());
    await page.reload({ waitUntil: 'domcontentloaded' });
    const reachedSteps = await tabUntil(page, '[data-toggle-step-list]');
    if (reachedSteps) await page.keyboard.press('Enter');
    const stepsExpanded = await page.locator('[data-toggle-step-list]').getAttribute('aria-expanded').catch(() => 'false');

    await page.reload({ waitUntil: 'domcontentloaded' });
    const reachedDrawer = await tabUntil(page, '[data-open-context]');
    if (reachedDrawer) await page.keyboard.press('Enter');
    const drawerExpanded = await page.locator('[data-open-context]').getAttribute('aria-expanded').catch(() => 'false');
    if (drawerExpanded === 'true') await page.keyboard.press('Escape');
    const drawerAfterEsc = await page.locator('[data-open-context]').getAttribute('aria-expanded').catch(() => 'true');

    add({ id: 'N3-ONBOARDING-KEYBOARD-STEPPER_DRAWER', phase: 'N3', surface: 'Novo Funcionário', viewport: 1024, action: 'Operar Ver etapas e ContextDrawer por teclado em navegações independentes.', expected: 'Ambos alcançáveis; drawer abre e fecha com Escape.', actual: `steps=${reachedSteps}/${stepsExpanded}; drawer=${reachedDrawer}/${drawerExpanded}/${drawerAfterEsc}`, result: reachedSteps && stepsExpanded === 'true' && reachedDrawer && drawerExpanded === 'true' && drawerAfterEsc === 'false' ? 'PASS' : 'FAIL', severity: 'BLOCKER', evidence: await screenshot(page, 'N3-onboarding-keyboard.png') });

    const pickerCount = await page.locator('[role="combobox"]').count();
    let pickerFocused = false;
    if (pickerCount) {
      const picker = page.locator('[role="combobox"]').first();
      await picker.focus();
      await picker.press('ArrowDown').catch(() => {});
      await picker.press('Escape').catch(() => {});
      pickerFocused = await picker.evaluate((el) => document.activeElement === el);
    }
    add({ id: 'N3-ONBOARDING-ENTITY_PICKER-KEYBOARD', phase: 'N3', surface: 'Novo Funcionário', viewport: 1024, action: 'ArrowDown/Escape em EntityPicker.', expected: '6 comboboxes locais e foco preservado.', actual: `count=${pickerCount}; focused=${pickerFocused}`, result: pickerCount >= 6 && pickerFocused ? 'PASS' : 'FAIL', severity: 'HIGH' });

    let aria = '';
    try { aria = await page.locator('body').ariaSnapshot(); } catch (error) { aria = `ERROR ${error}`; }
    await fs.writeFile(path.join(OUT, 'onboarding-aria-snapshot.txt'), aria, 'utf8');
    add({ id: 'N3-ONBOARDING-ARIA-SNAPSHOT', phase: 'N3', surface: 'Novo Funcionário', viewport: 1024, action: 'Capturar árvore ARIA.', expected: 'Snapshot disponível.', actual: aria ? 'captured' : 'empty', result: aria ? 'PASS' : 'FAIL', severity: 'HIGH', evidence: 'onboarding-aria-snapshot.txt' });
    await context.close();
  }

  const roles = {
    super_admin: ['users:view', 'users:create', 'biometrics:manage', 'punch:view', 'punch:create'],
    admin: ['users:view', 'users:create', 'biometrics:manage', 'punch:view', 'punch:create'],
    manager: ['users:view', 'users:create', 'punch:view'],
    auditor: ['users:view', 'punch:view'],
    operator: ['punch:create']
  };
  for (const [role, permissions] of Object.entries(roles)) {
    const { context, page } = await employeeVariant(browser, role, permissions);
    const canView = permissions.includes('users:view');
    const canCreate = permissions.includes('users:create');
    const canBio = permissions.includes('biometrics:manage');
    const ready = await visible(page.locator('[data-employee-ready-content]'));
    const denied = await visible(page.locator('[data-employee-state-panel="no_permission"]'));
    const create = await visible(page.locator('[data-new-employee-link]'));
    const bio = await page.locator('[data-employee-mutation]:visible').count();
    const pass = (canView ? ready : denied) && create === canCreate && (canBio ? bio > 0 : bio === 0);
    add({ id: `N3-RBAC-${role.toUpperCase()}`, phase: 'N3', surface: 'Funcionários', viewport: 1024, profile: role, action: 'Renderizar variante RBAC.', expected: `view=${canView}; create=${canCreate}; biometrics=${canBio}`, actual: `ready=${ready}; denied=${denied}; create=${create}; bio=${bio}`, result: pass ? 'PASS' : 'FAIL', severity: 'BLOCKER', evidence: await screenshot(page, `N3-rbac-${role}.png`) });
    await context.close();
  }

  for (const state of ['loading', 'empty', 'error', 'offline', 'no_permission']) {
    const permissions = state === 'no_permission' ? [] : ['users:view'];
    const { context, page } = await employeeVariant(browser, 'auditor', permissions, state);
    const shown = await visible(page.locator(`[data-employee-state-panel="${state}"]`));
    add({ id: `N3-EMPLOYEES-STATE-${state.toUpperCase()}`, phase: 'N3', surface: 'Funcionários', viewport: 1024, state: state.toUpperCase(), action: `Ativar estado ${state}.`, expected: 'Painel persistente correspondente visível.', actual: `visible=${shown}`, result: shown ? 'PASS' : 'FAIL', severity: 'HIGH', evidence: await screenshot(page, `N3-state-${state}.png`) });
    await context.close();
  }

  add({ id: 'N3-MANUAL-SCREEN-READER-CRITICAL-JOURNEY', phase: 'N3', surface: 'Jornada crítica', action: 'Executar jornada com screen reader real.', expected: 'Operação compreensível e navegável por NVDA/JAWS/VoiceOver/Orca.', actual: 'CI headless fornece axe e árvore ARIA, mas não sessão manual de screen reader.', result: 'BLOCKED_TOOLING', severity: 'HIGH', evidence: 'onboarding-aria-snapshot.txt' });
}

async function main() {
  await fs.rm(OUT, { recursive: true, force: true });
  await fs.mkdir(SHOTS, { recursive: true });
  const browser = await chromium.launch({ headless: true });
  try { await runN2(browser); await runN3(browser); } finally { await browser.close(); }
  const summary = { PASS: 0, FAIL: 0, BLOCKED_TOOLING: 0, NOT_APPLICABLE: 0, failures: [], blocked: [] };
  for (const item of results) {
    summary[item.RESULT] = (summary[item.RESULT] || 0) + 1;
    if (item.RESULT === 'FAIL') summary.failures.push({ caseId: item.CASE_ID, severity: item.SEVERITY_IF_FAIL, actual: item.ACTUAL });
    if (item.RESULT === 'BLOCKED_TOOLING') summary.blocked.push({ caseId: item.CASE_ID, severity: item.SEVERITY_IF_FAIL });
  }
  await fs.writeFile(path.join(OUT, 'results.json'), JSON.stringify({ generatedAt: new Date().toISOString(), summary, results }, null, 2));
  await fs.writeFile(path.join(OUT, 'summary.txt'), [`PASS=${summary.PASS}`, `FAIL=${summary.FAIL}`, `BLOCKED_TOOLING=${summary.BLOCKED_TOOLING}`, ...summary.failures.map((x) => `FAIL ${x.severity} ${x.caseId} ${x.actual}`), ...summary.blocked.map((x) => `BLOCKED ${x.severity} ${x.caseId}`)].join('\n'));
  console.log(JSON.stringify(summary, null, 2));
  if (summary.FAIL) process.exitCode = 1;
}

main().catch(async (error) => {
  console.error(error);
  await fs.mkdir(OUT, { recursive: true }).catch(() => {});
  await fs.writeFile(path.join(OUT, 'runner-error.txt'), String(error?.stack || error)).catch(() => {});
  process.exitCode = 2;
});
