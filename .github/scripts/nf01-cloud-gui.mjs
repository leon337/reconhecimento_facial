import { createRequire } from 'node:module';
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';

const require = createRequire(path.join(process.cwd(), 'package.json'));
const { chromium } = require('playwright');

const base = 'http://127.0.0.1:4173/screens';
const evidence = process.env.EVIDENCE;
if (!evidence) throw new Error('EVIDENCE is required');

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
const shell = (command) => execFileSync('bash', ['-lc', command], { encoding: 'utf8' }).trim();
const activateWindow = (wid) => execFileSync('xdotool', ['windowactivate', '--sync', wid], { stdio: 'ignore' });
const zoomKey = (wid, key) => {
  activateWindow(wid);
  execFileSync('xdotool', ['key', key], { stdio: 'ignore' });
};
const capture = (wid, name) => execFileSync('/usr/bin/import', ['-window', wid, path.join(evidence, name)], { stdio: 'ignore' });
const checkpoint = (label) => console.log(`NF01_CLOUD_CHECKPOINT=${label}`);
const nativeKey = (wid, key) => {
  activateWindow(wid);
  execFileSync('xdotool', ['key', '--clearmodifiers', key], { stdio: 'ignore' });
};
const focusWebContentForOrca = async (wid, label) => {
  activateWindow(wid);
  nativeKey(wid, 'F6');
  await sleep(700);
  checkpoint(`ORCA_WEB_FOCUS_${label.replaceAll(' ', '_')}`);
};
const atspiFocusForOrca = async (target) => {
  const probe = path.join(process.env.GITHUB_WORKSPACE || '', '.github/scripts/nf01-orca-atspi-focus.py');
  try {
    const output = execFileSync('python3', [probe, target], { encoding: 'utf8', env: process.env }).trim();
    console.log(`NF01_ATSPI_FOCUS_TARGET=${target};${output}`);
    nativeKey(wid, 'Tab');
    await sleep(250);
    nativeKey(wid, 'shift+Tab');
  } catch (error) {
    const stderr = String(error?.stderr || '').trim();
    console.log(`NF01_ATSPI_FOCUS_TARGET=${target};ERROR=${stderr || error.message}`);
  }
  await sleep(900);
};

const context = await chromium.launchPersistentContext('/tmp/nf01-cloud-profile', {
  headless: false,
  viewport: null,
  args: [
    '--no-sandbox',
    '--disable-dev-shm-usage',
    '--force-renderer-accessibility',
    '--no-first-run',
    '--no-default-browser-check',
    '--disable-infobars',
    '--disable-notifications',
    '--app=http://127.0.0.1:4173/screens/02.01-dashboard.html',
    '--disable-translate',
    '--disable-features=Translate,TranslateUI',
    '--lang=pt-BR',
    '--window-size=1920,1040',
  ],
});

const page = context.pages()[0] ?? await context.newPage();
checkpoint('BROWSER_LAUNCHED');
await page.goto(`${base}/02.01-dashboard.html`, { waitUntil: 'networkidle' });
await sleep(1200);

let wid = '';
for (let attempt = 0; attempt < 60 && !wid; attempt += 1) {
  try {
    wid = shell("xdotool search --onlyvisible --class 'chrome|chromium' | head -n 1");
  } catch {}
  if (!wid) {
    try {
      wid = shell("xdotool search --onlyvisible --name 'NF-01|Dashboard|Chromium|Chrome' | head -n 1");
    } catch {}
  }
  if (!wid) await sleep(500);
}
if (!wid) throw new Error('No headed Chromium window found in Xvfb');
checkpoint(`WINDOW_FOUND_${wid}`);

activateWindow(wid);
zoomKey(wid, 'ctrl+0');
for (let i = 0; i < 5; i += 1) {
  zoomKey(wid, 'ctrl+plus');
  await sleep(250);
}
await sleep(1200);
checkpoint('BROWSER_ZOOM_APPLIED');
await focusWebContentForOrca(wid, 'INITIAL_DASHBOARD');

const rows = [];
const interactions = [];
const nativeScreenReaderJourney = [];

async function activeElementSnapshot() {
  return page.evaluate(() => {
    const el = document.activeElement;
    if (!el) return { tag: null, role: null, name: null };
    const name = (
      el.getAttribute?.('aria-label')
      || el.innerText
      || el.textContent
      || el.getAttribute?.('title')
      || ''
    ).replace(/\s+/g, ' ').trim();
    const tag = el.tagName || null;
    const role = el.getAttribute?.('role') || null;
    const interactive = Boolean(
      ['A', 'BUTTON', 'INPUT', 'SELECT', 'TEXTAREA'].includes(tag)
      || el.hasAttribute?.('tabindex')
      || ['button', 'link', 'textbox', 'combobox', 'menuitem'].includes(role)
    );
    return {
      tag,
      role,
      name,
      href: el.getAttribute?.('href') || null,
      ariaExpanded: el.getAttribute?.('aria-expanded') || null,
      interactive,
    };
  });
}

async function nativeTabUntil(label, needle, maxTabs = 45) {
  const wanted = needle.toLocaleLowerCase('pt-BR');
  for (let index = 0; index <= maxTabs; index += 1) {
    const snap = await activeElementSnapshot();
    if (snap.interactive && (snap.name || '').toLocaleLowerCase('pt-BR').includes(wanted)) {
      nativeScreenReaderJourney.push({
        label,
        target: needle,
        tabs: index,
        activeElement: snap,
        result: 'FOCUSED_NATIVE_KEYBOARD',
      });
      console.log(`NF01_NATIVE_SR_FOCUS=${label};TARGET=${needle};NAME=${snap.name};TABS=${index}`);
      await sleep(1400);
      return snap;
    }
    nativeKey(wid, 'Tab');
    await sleep(320);
  }
  const snap = await activeElementSnapshot();
  nativeScreenReaderJourney.push({
    label,
    target: needle,
    activeElement: snap,
    result: 'TARGET_NOT_REACHED',
  });
  console.log(`NF01_NATIVE_SR_FOCUS=${label};TARGET=${needle};RESULT=NOT_REACHED;ACTIVE=${snap.name || ''}`);
  return null;
}

async function nativeScreenReaderCriticalJourney() {
  checkpoint('NATIVE_SCREEN_READER_BEGIN');
  await page.goto(`${base}/02.01-dashboard.html`, { waitUntil: 'networkidle' });
  await sleep(900);
  activateWindow(wid);
  nativeKey(wid, 'F6');
  await sleep(700);

  const attention = await nativeTabUntil('DASHBOARD_ATTENTION', 'biometrias pendentes', 35);
  if (!attention) return;
  nativeKey(wid, 'Return');
  await page.waitForURL(/03\.01-funcionarios\.html\?biometric=missing/, { timeout: 10000 });
  await sleep(1200);

  nativeKey(wid, 'F6');
  await sleep(650);
  const createEmployee = await nativeTabUntil('EMPLOYEES_NEW_EMPLOYEE', 'Novo funcionário', 40);
  if (!createEmployee) return;
  nativeKey(wid, 'Return');
  await page.waitForURL(/03\.04-novo-funcionario-v2\.html/, { timeout: 10000 });
  await sleep(1200);

  nativeKey(wid, 'F6');
  await sleep(650);
  const steps = await nativeTabUntil('ONBOARDING_STEP_LIST', 'Ver etapas', 50);
  if (!steps) return;
  nativeKey(wid, 'Return');
  await sleep(1200);

  const summary = await nativeTabUntil('ONBOARDING_CONTEXT_TRIGGER', 'Resumo', 25);
  if (!summary) return;
  nativeKey(wid, 'Return');
  await page.locator('[data-context-drawer]').waitFor({ state: 'visible', timeout: 10000 });
  await sleep(900);

  const close = await nativeTabUntil('CONTEXT_DRAWER_CLOSE', 'Fechar resumo', 20);
  await sleep(900);
  nativeKey(wid, 'Escape');
  await sleep(900);
  const afterEscape = await activeElementSnapshot();
  nativeScreenReaderJourney.push({
    label: 'CONTEXT_DRAWER_ESCAPE',
    activeElement: afterEscape,
    result: (afterEscape.name || '').includes('Resumo') ? 'FOCUS_RETURNED' : 'FOCUS_RETURN_UNCONFIRMED',
  });

  const next = await nativeTabUntil('ONBOARDING_CONTINUE', 'Continuar', 45);
  if (!next) return;
  nativeKey(wid, 'Return');
  await page.locator('[data-error-summary]').waitFor({ state: 'visible', timeout: 10000 });
  await sleep(1800);
  const errorSnap = await activeElementSnapshot();
  nativeScreenReaderJourney.push({
    label: 'ERROR_SUMMARY_AFTER_ENTER',
    activeElement: errorSnap,
    errorText: (await page.locator('[data-error-summary]').innerText()).replace(/\s+/g, ' ').trim(),
    result: 'ERROR_VISIBLE',
  });
  console.log(`NF01_NATIVE_SR_ERROR=${nativeScreenReaderJourney.at(-1).errorText}`);

  nativeKey(wid, 'alt+Left');
  await page.waitForURL(/03\.01-funcionarios\.html/, { timeout: 10000 });
  await sleep(1000);
  nativeScreenReaderJourney.push({
    label: 'RETURN_TO_EMPLOYEES',
    url: page.url(),
    result: 'RETURNED_NATIVE_KEYBOARD',
  });
  checkpoint('NATIVE_SCREEN_READER_COMPLETE');
}

function writePartial(status) {
  fs.writeFileSync(path.join(evidence, 'cloud-gui-summary.json'), JSON.stringify({
    execution: 'CLOUD_HEADED_GUI_ASSISTED_VALIDATION',
    status,
    browserControl: 'PLAYWRIGHT_LAUNCH_PERSISTENT_CONTEXT',
    interactionInput: 'PLAYWRIGHT_KEYBOARD_ASSISTED',
    browserZoomMethod: 'OS_LEVEL_CTRL_PLUS_ON_HEADED_CHROMIUM',
    expectedZoom: '200%',
    zoom200SignalsAllPass: rows.length > 0 && rows.every((row) => row.zoom200Signal),
    noHorizontalOverflowAllPass: rows.length > 0 && rows.every((row) => !row.horizontalOverflow),
    surfaces: rows,
    interactions,
    nativeScreenReaderJourney,
    manualAcceptanceClaimed: false,
  }, null, 2));
}

async function inspect(label) {
  const metrics = await page.evaluate(() => ({
    url: location.href,
    title: document.title,
    innerWidth: window.innerWidth,
    outerWidth: window.outerWidth,
    devicePixelRatio: window.devicePixelRatio,
    visualViewportScale: window.visualViewport?.scale ?? null,
    clientWidth: document.documentElement.clientWidth,
    scrollWidth: document.documentElement.scrollWidth,
    horizontalOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 1,
  }));
  const zoomRatio = metrics.outerWidth / metrics.innerWidth;
  rows.push({
    label,
    ...metrics,
    zoomRatio: Number(zoomRatio.toFixed(2)),
    zoom200Signal: (metrics.devicePixelRatio >= 1.9 && metrics.devicePixelRatio <= 2.1) || (zoomRatio >= 1.85 && zoomRatio <= 2.15),
  });
  console.log(`NF01_SURFACE=${label};URL=${metrics.url};ZOOM_RATIO=${zoomRatio.toFixed(2)};OVERFLOW=${metrics.horizontalOverflow}`);
  writePartial(`INSPECTED_${label}`);
}

async function visit(relative, label, shot, orcaTarget = '') {
  checkpoint(`VISIT_${label.replaceAll(' ', '_')}`);
  await page.goto(`${base}/${relative}`, { waitUntil: 'networkidle' });
  await sleep(900);
  await inspect(label);
  capture(wid, shot);
  await focusWebContentForOrca(wid, label);
  if (orcaTarget) await atspiFocusForOrca(orcaTarget);
  await sleep(350);
}

await visit('02.01-dashboard.html', 'Dashboard', 'N2-dashboard-real-browser-zoom.png', 'Biometrias pendentes');
checkpoint('DASHBOARD_HANDOFF_ASSISTED');
const handoff = page.locator('[data-cross-screen-handoff="biometric-missing"]');
await handoff.focus();
const handoffFocused = await handoff.evaluate((el) => document.activeElement === el);
await page.keyboard.press('Enter');
await page.waitForURL(/03\.01-funcionarios\.html\?biometric=missing/, { timeout: 10000 });
interactions.push({ case: 'DASHBOARD_TO_EMPLOYEES', input: 'PLAYWRIGHT_KEYBOARD', focusConfirmed: handoffFocused, result: 'PASS_ASSISTED' });
checkpoint('DASHBOARD_HANDOFF_NAVIGATED');
await sleep(700);
await inspect('Funcionários filtrados via Dashboard');
capture(wid, 'N3-dashboard-to-employees-filtered.png');

await visit('01.01-app-shell.html', 'AppShell', 'N2-appshell-real-browser-zoom.png', 'Dashboard');
await visit('03.01-funcionarios.html', 'Funcionários', 'N2-funcionarios-real-browser-zoom.png', 'Novo funcionário');
await visit('03.04-novo-funcionario-v2.html', 'Novo Funcionário', 'N2-novo-funcionario-real-browser-zoom.png', 'Ver etapas');

checkpoint('STEP_LIST_OPEN_ASSISTED');
const stepToggle = page.locator('[data-toggle-step-list]');
const stepList = page.locator('[data-step-list]');
await stepToggle.focus();
await page.keyboard.press('Enter');
await sleep(500);
const stepExpanded = await stepToggle.getAttribute('aria-expanded');
const stepHidden = await stepList.evaluate((el) => el.hidden);
await stepList.scrollIntoViewIfNeeded();
await sleep(300);
const stepRect = await stepList.boundingBox();
interactions.push({
  case: 'STEP_LIST_OPEN',
  input: 'PLAYWRIGHT_KEYBOARD',
  ariaExpanded: stepExpanded,
  hidden: stepHidden,
  boundingBox: stepRect,
  result: stepExpanded === 'true' && stepHidden === false ? 'PASS_ASSISTED' : 'FAIL',
});
capture(wid, 'N3-step-list-open.png');

checkpoint('CONTEXT_DRAWER_ASSISTED');
const summary = page.locator('[data-open-context]');
const drawer = page.locator('[data-context-drawer]');
await summary.focus();
await atspiFocusForOrca('Resumo');
await page.keyboard.press('Enter');
await drawer.waitFor({ state: 'visible', timeout: 10000 });
await sleep(500);
const drawerState = await drawer.evaluate((el) => ({
  hidden: el.hidden,
  ariaHidden: el.getAttribute('aria-hidden'),
  rect: (() => {
    const r = el.getBoundingClientRect();
    return { x: r.x, y: r.y, width: r.width, height: r.height, right: r.right, bottom: r.bottom };
  })(),
}));
capture(wid, 'N2-N3-context-drawer-open.png');
await page.keyboard.press('Escape');
await sleep(400);
const focusReturned = await summary.evaluate((el) => document.activeElement === el);
interactions.push({
  case: 'CONTEXT_DRAWER_OPEN_CLOSE',
  input: 'PLAYWRIGHT_KEYBOARD',
  openState: drawerState,
  focusReturned,
  result: !drawerState.hidden && drawerState.ariaHidden === 'false' && drawerState.rect.width > 0 && focusReturned ? 'PASS_ASSISTED' : 'FAIL',
});
console.log(`NF01_CONTEXT_DRAWER_FOCUS_RETURNED=${focusReturned}`);

checkpoint('ERROR_SUMMARY_ASSISTED');
const continueButton = page.locator('[data-next-step]');
const errorSummary = page.locator('[data-error-summary]');
await continueButton.focus();
await page.keyboard.press('Enter');
await errorSummary.waitFor({ state: 'visible', timeout: 10000 });
await sleep(300);
const errorText = (await errorSummary.innerText()).replace(/\s+/g, ' ').trim();
await errorSummary.scrollIntoViewIfNeeded();
await sleep(300);
const errorRect = await errorSummary.boundingBox();
interactions.push({
  case: 'ERROR_SUMMARY',
  input: 'PLAYWRIGHT_KEYBOARD',
  actual: errorText,
  boundingBox: errorRect,
  result: errorText && errorRect ? 'PASS_ASSISTED' : 'FAIL',
});
console.log(`NF01_ERROR_SUMMARY=${errorText}`);
await atspiFocusForOrca('Revise as informações desta etapa');
capture(wid, 'N3-error-summary.png');

checkpoint('RETURN_TO_EMPLOYEES_ASSISTED');
const employeesBreadcrumb = page.locator('nav[aria-label="Breadcrumb"] a[href="03.01-funcionarios.html"]').last();
await employeesBreadcrumb.focus();
await page.keyboard.press('Enter');
await page.waitForURL(/03\.01-funcionarios\.html$/, { timeout: 10000 });
await sleep(700);
await inspect('Retorno a Funcionários');
interactions.push({ case: 'RETURN_TO_EMPLOYEES', input: 'PLAYWRIGHT_KEYBOARD', result: 'PASS_ASSISTED' });

await nativeScreenReaderCriticalJourney();
writePartial('COMPLETE_ASSISTED_EVIDENCE');
checkpoint('SUMMARY_WRITTEN');
await context.close();
checkpoint('COMPLETE');
