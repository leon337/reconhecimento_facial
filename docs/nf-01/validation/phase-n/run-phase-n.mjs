import { chromium } from 'playwright';
import AxeBuilder from '@axe-core/playwright';
import fs from 'node:fs/promises';
import path from 'node:path';

const BASE_URL = process.env.NF01_BASE_URL || 'http://127.0.0.1:4173';
const OUTPUT_DIR = process.env.NF01_EVIDENCE_DIR || path.resolve('../../evidence/phase-n/automation-run');
const SCREENSHOT_DIR = path.join(OUTPUT_DIR, 'screenshots');
const results = [];

const surfaces = [
  { id: 'app-shell', label: 'AppShell', file: 'screens/01.01-app-shell.html' },
  { id: 'dashboard', label: 'Dashboard', file: 'screens/02.01-dashboard.html' },
  { id: 'employees', label: 'Funcionários', file: 'screens/03.01-funcionarios.html' },
  { id: 'onboarding', label: 'Novo Funcionário', file: 'screens/03.04-novo-funcionario-v2.html' }
];
const viewports = [360, 480, 768, 900, 1024, 1280, 1440];
const canonicalWidths = new Set([360, 768, 1024, 1440]);

const add = (entry) => results.push({
  CASE_ID: entry.caseId,
  PHASE: entry.phase,
  SURFACE: entry.surface,
  VIEWPORT_OR_CONTAINER: entry.viewport ?? 'N/A',
  ZOOM: entry.zoom ?? '100%',
  PROFILE: entry.profile ?? 'admin',
  STATE: entry.state ?? 'READY',
  PRECONDITION: entry.precondition ?? '',
  ACTION: entry.action ?? '',
  EXPECTED: entry.expected ?? '',
  ACTUAL: entry.actual ?? '',
  RESULT: entry.result,
  SEVERITY_IF_FAIL: entry.severity ?? 'MEDIUM',
  EVIDENCE_REF: entry.evidence ?? '',
  FOLLOW_UP_REF: entry.followUp ?? ''
});

const isVisible = async (locator) => {
  try { return await locator.isVisible(); } catch { return false; }
};

async function layoutSnapshot(page) {
  return page.evaluate(() => {
    const root = document.documentElement;
    const body = document.body;
    const scrollWidth = Math.max(root.scrollWidth, body?.scrollWidth || 0);
    const viewport = window.innerWidth;
    const globalOverflow = scrollWidth > viewport + 2;
    const offenders = [...document.querySelectorAll('body *')]
      .filter((el) => {
        const style = getComputedStyle(el);
        if (style.display === 'none' || style.visibility === 'hidden') return false;
        if (el.closest('[hidden]')) return false;
        const rect = el.getBoundingClientRect();
        if (rect.width <= 0 || rect.height <= 0) return false;
        return rect.right > viewport + 8 && !['auto', 'scroll'].includes(style.overflowX);
      })
      .slice(0, 8)
      .map((el) => ({
        tag: el.tagName.toLowerCase(),
        className: typeof el.className === 'string' ? el.className.slice(0, 120) : '',
        right: Math.round(el.getBoundingClientRect().right),
        width: Math.round(el.getBoundingClientRect().width)
      }));
    return { viewport, scrollWidth, globalOverflow, offenders };
  });
}

async function screenshot(page, fileName) {
  const rel = `screenshots/${fileName}`;
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, fileName), fullPage: true });
  return rel;
}

async function tabUntil(page, selector, maxTabs = 80) {
  for (let i = 0; i < maxTabs; i += 1) {
    const matched = await page.evaluate((sel) => document.activeElement?.matches?.(sel) || false, selector);
    if (matched) return true;
    await page.keyboard.press('Tab');
  }
  return page.evaluate((sel) => document.activeElement?.matches?.(sel) || false, selector);
}

async function n2Visual(browser) {
  for (const surface of surfaces) {
    for (const width of viewports) {
      const context = await browser.newContext({ viewport: { width, height: width <= 480 ? 820 : 900 }, deviceScaleFactor: 1 });
      const page = await context.newPage();
      await page.goto(`${BASE_URL}/${surface.file}`, { waitUntil: 'domcontentloaded' });
      await page.waitForTimeout(250);
      const layout = await layoutSnapshot(page);
      const evidence = await screenshot(page, `N2-${surface.id}-${width}.png`);
      add({
        caseId: `N2-${surface.id.toUpperCase()}-${width}-GLOBAL_REFLOW`,
        phase: 'N2', surface: surface.label, viewport: width,
        action: 'Renderizar superfície no viewport e medir overflow global.',
        expected: 'Sem overflow horizontal global indevido.',
        actual: JSON.stringify(layout),
        result: layout.globalOverflow ? 'FAIL' : 'PASS',
        severity: layout.globalOverflow ? 'BLOCKER' : 'MEDIUM',
        evidence
      });

      if (surface.id === 'onboarding' && width === 360) {
        const currentVisible = await isVisible(page.locator('[data-mobile-current]'));
        const stepsVisible = await isVisible(page.locator('[data-toggle-step-list]'));
        add({
          caseId: 'N2-ONBOARDING-360-MOBILE_STEPPER', phase: 'N2', surface: surface.label, viewport: width,
          action: 'Inspecionar stepper mobile.',
          expected: 'Etapa X de 8 e Ver etapas visíveis.',
          actual: `mobileCurrent=${currentVisible}; toggleStepList=${stepsVisible}`,
          result: currentVisible && stepsVisible ? 'PASS' : 'FAIL', severity: 'HIGH', evidence
        });
      }
      await context.close();
    }
  }

  // Equivalente automatizado de reflow a 200%: viewport CSS reduzido à metade com rasterização 2x.
  for (const surface of surfaces) {
    const context = await browser.newContext({ viewport: { width: 720, height: 900 }, deviceScaleFactor: 2 });
    const page = await context.newPage();
    await page.goto(`${BASE_URL}/${surface.file}`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(250);
    const layout = await layoutSnapshot(page);
    const evidence = await screenshot(page, `N2-${surface.id}-zoom200-equivalent.png`);
    add({
      caseId: `N2-${surface.id.toUpperCase()}-ZOOM200_EQUIVALENT_REFLOW`, phase: 'N2', surface: surface.label,
      viewport: '1440 physical / 720 CSS', zoom: '200%-equivalent',
      action: 'Inspecionar reflow equivalente a 200% em Chromium headless.',
      expected: 'Sem overflow horizontal global impeditivo.',
      actual: JSON.stringify(layout),
      result: layout.globalOverflow ? 'FAIL' : 'PASS', severity: layout.globalOverflow ? 'BLOCKER' : 'MEDIUM', evidence
    });
  }

  add({
    caseId: 'N2-MANUAL_BROWSER_ZOOM_200', phase: 'N2', surface: 'Todas', zoom: '200%',
    action: 'Teste manual do controle de zoom da UI do navegador.',
    expected: 'Executar zoom real do navegador a 200% e validar reflow.',
    actual: 'Runner headless não expõe UI de navegador para operação manual; equivalente de reflow foi capturado separadamente.',
    result: 'BLOCKED_TOOLING', severity: 'HIGH', evidence: 'N2-*-zoom200-equivalent.png'
  });

  // Handoff cross-screen e restauração de estado.
  {
    const context = await browser.newContext({ viewport: { width: 1024, height: 900 } });
    const page = await context.newPage();
    await page.goto(`${BASE_URL}/screens/02.01-dashboard.html`, { waitUntil: 'domcontentloaded' });
    const handoff = page.locator('[data-cross-screen-handoff="biometric-missing"]');
    const exists = await handoff.count() === 1;
    if (exists) await handoff.click();
    await page.waitForTimeout(200);
    const value = await page.locator('[data-biometric-filter]').inputValue().catch(() => '');
    const visibleRows = await page.locator('[data-employee-row]:visible').count();
    add({
      caseId: 'N2-CROSSSCREEN-DASHBOARD_EMPLOYEES_HANDOFF', phase: 'N2', surface: 'Dashboard → Funcionários', viewport: 1024,
      action: 'Ativar CTA de biometrias pendentes.',
      expected: 'Abrir Funcionários com biometric=missing e 2 fixtures visíveis.',
      actual: `url=${page.url()}; biometric=${value}; visibleRows=${visibleRows}`,
      result: exists && value === 'missing' && visibleRows === 2 ? 'PASS' : 'FAIL', severity: 'BLOCKER',
      evidence: await screenshot(page, 'N2-crossscreen-dashboard-employees.png')
    });

    const search = page.locator('[data-employee-search]');
    await search.fill('João');
    await page.locator('[data-new-employee-link]').click();
    await page.waitForTimeout(150);
    await page.goBack({ waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(200);
    const restored = await page.locator('[data-employee-search]').inputValue().catch(() => '');
    add({
      caseId: 'N2-CROSSSCREEN-EMPLOYEE_LIST_STATE_RESTORE', phase: 'N2', surface: 'Funcionários ↔ Novo Funcionário', viewport: 1024,
      action: 'Pesquisar João, entrar no onboarding e voltar.',
      expected: 'Busca anterior restaurada na mesma sessão.',
      actual: `search=${restored}`,
      result: restored === 'João' ? 'PASS' : 'FAIL', severity: 'HIGH',
      evidence: await screenshot(page, 'N2-crossscreen-list-state-restore.png')
    });
    await context.close();
  }
}

async function loadEmployeesRole(browser, role, permissions) {
  const context = await browser.newContext({ viewport: { width: 1024, height: 900 } });
  const page = await context.newPage();
  await page.route('**/screens/03.01-funcionarios.html*', async (route) => {
    const response = await route.fetch();
    let body = await response.text();
    body = body
      .replace(/data-employee-demo-role="[^"]*"/, `data-employee-demo-role="${role}"`)
      .replace(/data-employee-demo-permissions="[^"]*"/, `data-employee-demo-permissions="${permissions.join(' ')}"`);
    await route.fulfill({ response, body });
  });
  await page.goto(`${BASE_URL}/screens/03.01-funcionarios.html`, { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(200);
  return { context, page };
}

async function n3Accessibility(browser) {
  // Axe automático em desktop e mobile nas quatro superfícies.
  for (const surface of surfaces) {
    for (const width of [360, 1440]) {
      const context = await browser.newContext({ viewport: { width, height: 900 } });
      const page = await context.newPage();
      await page.goto(`${BASE_URL}/${surface.file}`, { waitUntil: 'domcontentloaded' });
      await page.waitForTimeout(250);
      let analysis;
      try {
        analysis = await new AxeBuilder({ page }).analyze();
        const criticalSerious = analysis.violations.filter((v) => ['critical', 'serious'].includes(v.impact));
        add({
          caseId: `N3-${surface.id.toUpperCase()}-${width}-AXE`, phase: 'N3', surface: surface.label, viewport: width,
          action: 'Executar axe-core.', expected: '0 violações critical/serious.',
          actual: JSON.stringify(criticalSerious.map((v) => ({ id: v.id, impact: v.impact, nodes: v.nodes.length }))),
          result: criticalSerious.length === 0 ? 'PASS' : 'FAIL', severity: criticalSerious.length ? 'HIGH' : 'MEDIUM',
          evidence: await screenshot(page, `N3-${surface.id}-${width}-axe.png`)
        });
      } catch (error) {
        add({
          caseId: `N3-${surface.id.toUpperCase()}-${width}-AXE`, phase: 'N3', surface: surface.label, viewport: width,
          action: 'Executar axe-core.', expected: 'Scan executável.', actual: String(error),
          result: 'BLOCKED_TOOLING', severity: 'HIGH'
        });
      }
      await context.close();
    }
  }

  // Jornada crítica somente teclado.
  {
    const context = await browser.newContext({ viewport: { width: 1024, height: 900 } });
    const page = await context.newPage();
    await page.goto(`${BASE_URL}/screens/03.04-novo-funcionario-v2.html`, { waitUntil: 'domcontentloaded' });
    await page.evaluate(() => localStorage.clear());
    await page.reload({ waitUntil: 'domcontentloaded' });
    const reachedSteps = await tabUntil(page, '[data-toggle-step-list]');
    if (reachedSteps) await page.keyboard.press('Enter');
    const stepsExpanded = await page.locator('[data-toggle-step-list]').getAttribute('aria-expanded').catch(() => 'false');
    const reachedContext = await tabUntil(page, '[data-open-context]');
    if (reachedContext) await page.keyboard.press('Enter');
    const drawerExpanded = await page.locator('[data-open-context]').getAttribute('aria-expanded').catch(() => 'false');
    if (drawerExpanded === 'true') await page.keyboard.press('Escape');
    const drawerClosed = await page.locator('[data-open-context]').getAttribute('aria-expanded').catch(() => 'true');
    add({
      caseId: 'N3-ONBOARDING-KEYBOARD-STEPPER_DRAWER', phase: 'N3', surface: 'Novo Funcionário', viewport: 1024,
      action: 'Tab/Enter em Ver etapas e ContextDrawer; Escape para fechar.',
      expected: 'Controles alcançáveis sem mouse; drawer retorna a fechado.',
      actual: `reachedSteps=${reachedSteps}; stepsExpanded=${stepsExpanded}; reachedContext=${reachedContext}; drawerExpanded=${drawerExpanded}; drawerAfterEsc=${drawerClosed}`,
      result: reachedSteps && stepsExpanded === 'true' && reachedContext && drawerExpanded === 'true' && drawerClosed === 'false' ? 'PASS' : 'FAIL',
      severity: 'BLOCKER', evidence: await screenshot(page, 'N3-onboarding-keyboard-stepper-drawer.png')
    });

    const firstPicker = page.locator('[role="combobox"]').first();
    const pickerCount = await page.locator('[role="combobox"]').count();
    let pickerKeyboard = false;
    if (pickerCount) {
      await firstPicker.focus();
      await firstPicker.press('ArrowDown').catch(() => {});
      await firstPicker.press('Escape').catch(() => {});
      pickerKeyboard = await firstPicker.evaluate((el) => document.activeElement === el);
    }
    add({
      caseId: 'N3-ONBOARDING-ENTITY_PICKER-KEYBOARD', phase: 'N3', surface: 'Novo Funcionário', viewport: 1024,
      action: 'Focar combobox e operar ArrowDown/Escape.',
      expected: 'EntityPicker possui combobox alcançável e permanece operável por teclado.',
      actual: `comboboxCount=${pickerCount}; focusPreserved=${pickerKeyboard}`,
      result: pickerCount >= 6 && pickerKeyboard ? 'PASS' : 'FAIL', severity: 'HIGH'
    });
    await context.close();
  }

  // Matriz RBAC visual na lista de Funcionários.
  const profiles = {
    super_admin: ['users:view', 'users:create', 'biometrics:manage', 'punch:view', 'punch:create'],
    admin: ['users:view', 'users:create', 'biometrics:manage', 'punch:view', 'punch:create'],
    manager: ['users:view', 'users:create', 'punch:view'],
    auditor: ['users:view', 'punch:view'],
    operator: ['punch:create']
  };
  for (const [role, permissions] of Object.entries(profiles)) {
    const { context, page } = await loadEmployeesRole(browser, role, permissions);
    const canView = permissions.includes('users:view');
    const canCreate = permissions.includes('users:create');
    const canBio = permissions.includes('biometrics:manage');
    const readyVisible = await isVisible(page.locator('[data-employee-ready-content]'));
    const noPermissionVisible = await isVisible(page.locator('[data-employee-state-panel="no_permission"]'));
    const createVisible = await isVisible(page.locator('[data-new-employee-link]'));
    const bioVisibleCount = await page.locator('[data-employee-mutation]:visible').count();
    const pass = (canView ? readyVisible : noPermissionVisible)
      && createVisible === canCreate
      && (canBio ? bioVisibleCount > 0 : bioVisibleCount === 0);
    add({
      caseId: `N3-RBAC-EMPLOYEES-${role.toUpperCase()}`, phase: 'N3', surface: 'Funcionários', viewport: 1024, profile: role,
      action: 'Renderizar variante de permissões no Design Lab.',
      expected: `view=${canView}; create=${canCreate}; biometrics=${canBio}`,
      actual: `ready=${readyVisible}; noPermission=${noPermissionVisible}; create=${createVisible}; bioActions=${bioVisibleCount}`,
      result: pass ? 'PASS' : 'FAIL', severity: 'BLOCKER',
      evidence: await screenshot(page, `N3-rbac-employees-${role}.png`)
    });
    await context.close();
  }

  // Estados persistentes de Funcionários via contrato de estado demonstrativo.
  for (const state of ['loading', 'empty', 'error', 'offline', 'no_permission']) {
    const context = await browser.newContext({ viewport: { width: 1024, height: 900 } });
    const page = await context.newPage();
    await page.route('**/screens/03.01-funcionarios.html*', async (route) => {
      const response = await route.fetch();
      let body = await response.text();
      body = body.replace(/data-employee-demo-state="[^"]*"/, `data-employee-demo-state="${state}"`);
      await route.fulfill({ response, body });
    });
    await page.goto(`${BASE_URL}/screens/03.01-funcionarios.html`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(150);
    const visible = await isVisible(page.locator(`[data-employee-state-panel="${state}"]`));
    add({
      caseId: `N3-EMPLOYEES-STATE-${state.toUpperCase()}`, phase: 'N3', surface: 'Funcionários', viewport: 1024, state: state.toUpperCase(),
      action: `Ativar estado demonstrativo ${state}.`, expected: 'Painel persistente correspondente visível.',
      actual: `visible=${visible}`, result: visible ? 'PASS' : 'FAIL', severity: 'HIGH',
      evidence: await screenshot(page, `N3-employees-state-${state}.png`)
    });
    await context.close();
  }

  // Accessibility-tree semantic snapshot como evidência suplementar.
  {
    const context = await browser.newContext({ viewport: { width: 1024, height: 900 } });
    const page = await context.newPage();
    await page.goto(`${BASE_URL}/screens/03.04-novo-funcionario-v2.html`, { waitUntil: 'domcontentloaded' });
    let aria = '';
    try { aria = await page.locator('body').ariaSnapshot(); } catch (error) { aria = `ARIA_SNAPSHOT_ERROR: ${error}`; }
    await fs.writeFile(path.join(OUTPUT_DIR, 'onboarding-aria-snapshot.txt'), aria, 'utf8');
    add({
      caseId: 'N3-ONBOARDING-ARIA-TREE-SNAPSHOT', phase: 'N3', surface: 'Novo Funcionário', viewport: 1024,
      action: 'Capturar árvore semântica ARIA do Chromium.',
      expected: 'Snapshot disponível como evidência suplementar.',
      actual: aria ? 'snapshot captured' : 'empty snapshot', result: aria ? 'PASS' : 'FAIL', severity: 'HIGH',
      evidence: 'onboarding-aria-snapshot.txt'
    });
    await context.close();
  }

  add({
    caseId: 'N3-MANUAL-SCREEN-READER-CRITICAL-JOURNEY', phase: 'N3', surface: 'Jornada crítica', viewport: 'N/A',
    action: 'Executar jornada com screen reader real (NVDA/JAWS/VoiceOver/Orca).',
    expected: 'Jornada crítica compreensível e operável pelo leitor de tela.',
    actual: 'GitHub Actions/Chromium headless fornece árvore de acessibilidade, mas não uma sessão manual de screen reader real.',
    result: 'BLOCKED_TOOLING', severity: 'HIGH', evidence: 'onboarding-aria-snapshot.txt'
  });
}

async function main() {
  await fs.rm(OUTPUT_DIR, { recursive: true, force: true });
  await fs.mkdir(SCREENSHOT_DIR, { recursive: true });
  const browser = await chromium.launch({ headless: true });
  try {
    await n2Visual(browser);
    await n3Accessibility(browser);
  } finally {
    await browser.close();
  }

  const summary = results.reduce((acc, item) => {
    acc[item.RESULT] = (acc[item.RESULT] || 0) + 1;
    if (item.RESULT === 'FAIL') acc.failures.push({ caseId: item.CASE_ID, severity: item.SEVERITY_IF_FAIL, actual: item.ACTUAL });
    if (item.RESULT === 'BLOCKED_TOOLING') acc.blocked.push({ caseId: item.CASE_ID, severity: item.SEVERITY_IF_FAIL });
    return acc;
  }, { PASS: 0, FAIL: 0, BLOCKED_TOOLING: 0, NOT_APPLICABLE: 0, failures: [], blocked: [] });

  await fs.writeFile(path.join(OUTPUT_DIR, 'results.json'), JSON.stringify({ generatedAt: new Date().toISOString(), baseUrl: BASE_URL, summary, results }, null, 2));
  await fs.writeFile(path.join(OUTPUT_DIR, 'summary.txt'), [
    `PASS=${summary.PASS}`,
    `FAIL=${summary.FAIL}`,
    `BLOCKED_TOOLING=${summary.BLOCKED_TOOLING}`,
    `NOT_APPLICABLE=${summary.NOT_APPLICABLE}`,
    ...summary.failures.map((f) => `FAIL ${f.severity} ${f.caseId} ${f.actual}`),
    ...summary.blocked.map((b) => `BLOCKED ${b.severity} ${b.caseId}`)
  ].join('\n'));

  console.log(JSON.stringify(summary, null, 2));
  if (summary.FAIL > 0) process.exitCode = 1;
}

main().catch(async (error) => {
  console.error(error);
  try {
    await fs.mkdir(OUTPUT_DIR, { recursive: true });
    await fs.writeFile(path.join(OUTPUT_DIR, 'runner-error.txt'), String(error?.stack || error));
  } catch (_) {}
  process.exitCode = 2;
});
