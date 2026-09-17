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

const context = await chromium.launchPersistentContext('/tmp/nf01-cloud-profile', {
  headless: false,
  viewport: null,
  args: [
    '--no-sandbox',
    '--disable-dev-shm-usage',
    '--force-renderer-accessibility',
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

async function visit(relative, label, shot) {
  checkpoint(`VISIT_${label.replaceAll(' ', '_')}`);
  await page.goto(`${base}/${relative}`, { waitUntil: 'networkidle' });
  await sleep(900);
  await inspect(label);
  capture(wid, shot);
  await focusWebContentForOrca(wid, label);
  await sleep(350);
}

await visit('02.01-dashboard.html', 'Dashboard', 'N2-dashboard-real-browser-zoom.png');
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

await visit('01.01-app-shell.html', 'AppShell', 'N2-appshell-real-browser-zoom.png');
await visit('03.01-funcionarios.html', 'Funcionários', 'N2-funcionarios-real-browser-zoom.png');
await visit('03.04-novo-funcionario-v2.html', 'Novo Funcionário', 'N2-novo-funcionario-real-browser-zoom.png');

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
capture(wid, 'N3-error-summary.png');

checkpoint('RETURN_TO_EMPLOYEES_ASSISTED');
const employeesBreadcrumb = page.locator('nav[aria-label="Breadcrumb"] a[href="03.01-funcionarios.html"]').last();
await employeesBreadcrumb.focus();
await page.keyboard.press('Enter');
await page.waitForURL(/03\.01-funcionarios\.html$/, { timeout: 10000 });
await sleep(700);
await inspect('Retorno a Funcionários');
interactions.push({ case: 'RETURN_TO_EMPLOYEES', input: 'PLAYWRIGHT_KEYBOARD', result: 'PASS_ASSISTED' });

writePartial('COMPLETE_ASSISTED_EVIDENCE');
checkpoint('SUMMARY_WRITTEN');
await context.close();
checkpoint('COMPLETE');
