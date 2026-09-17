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
const osKey = (wid, ...keys) => execFileSync('xdotool', ['key', '--window', wid, ...keys], { stdio: 'ignore' });
const capture = (wid, name) => execFileSync('/usr/bin/import', ['-window', wid, path.join(evidence, name)], { stdio: 'ignore' });

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

execFileSync('xdotool', ['windowactivate', '--sync', wid], { stdio: 'ignore' });
osKey(wid, 'ctrl+0');
for (let i = 0; i < 5; i += 1) {
  osKey(wid, 'ctrl+plus');
  await sleep(250);
}
await sleep(1200);

const rows = [];
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
}

async function visit(relative, label, shot) {
  await page.goto(`${base}/${relative}`, { waitUntil: 'networkidle' });
  await sleep(900);
  await inspect(label);
  capture(wid, shot);
}

await visit('02.01-dashboard.html', 'Dashboard', 'N2-dashboard-real-browser-zoom.png');
await page.locator('[data-cross-screen-handoff="biometric-missing"]').focus();
osKey(wid, 'Return');
await page.waitForURL(/03\.01-funcionarios\.html\?biometric=missing/);
await sleep(700);
await inspect('Funcionários filtrados via Dashboard');
capture(wid, 'N3-dashboard-to-employees-filtered.png');

await visit('01.01-app-shell.html', 'AppShell', 'N2-appshell-real-browser-zoom.png');
await visit('03.01-funcionarios.html', 'Funcionários', 'N2-funcionarios-real-browser-zoom.png');
await visit('03.04-novo-funcionario-v2.html', 'Novo Funcionário', 'N2-novo-funcionario-real-browser-zoom.png');

const stepToggle = page.locator('[data-toggle-step-list]');
await stepToggle.focus();
osKey(wid, 'Return');
await sleep(400);
capture(wid, 'N3-step-list-open.png');

const summary = page.locator('[data-open-context]');
await summary.focus();
osKey(wid, 'Return');
await page.locator('[data-context-drawer]').waitFor({ state: 'visible' });
capture(wid, 'N2-N3-context-drawer-open.png');
osKey(wid, 'Escape');
await sleep(400);
const focusReturned = await summary.evaluate((el) => document.activeElement === el);

const continueButton = page.locator('[data-next-step]');
await continueButton.focus();
osKey(wid, 'Return');
await page.locator('[data-error-summary]').waitFor({ state: 'visible' });
await sleep(400);
const errorText = (await page.locator('[data-error-summary]').innerText()).replace(/\s+/g, ' ').trim();
capture(wid, 'N3-error-summary.png');

const employeesBreadcrumb = page.locator('nav[aria-label="Breadcrumb"] a[href="03.01-funcionarios.html"]').last();
await employeesBreadcrumb.focus();
osKey(wid, 'Return');
await page.waitForURL(/03\.01-funcionarios\.html$/);
await sleep(700);
await inspect('Retorno a Funcionários');

const summaryJson = {
  execution: 'CLOUD_HEADED_GUI_AUTOMATION',
  browserControl: 'PLAYWRIGHT_LAUNCH_PERSISTENT_CONTEXT',
  browserZoomMethod: 'OS_LEVEL_CTRL_PLUS_ON_HEADED_CHROMIUM',
  expectedZoom: '200%',
  zoom200SignalsAllPass: rows.every((row) => row.zoom200Signal),
  noHorizontalOverflowAllPass: rows.every((row) => !row.horizontalOverflow),
  surfaces: rows,
  contextDrawerFocusReturned: focusReturned,
  errorSummaryText: errorText,
};
fs.writeFileSync(path.join(evidence, 'cloud-gui-summary.json'), JSON.stringify(summaryJson, null, 2));
await context.close();
