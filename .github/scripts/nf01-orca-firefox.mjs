import { createRequire } from 'node:module';
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';

const require = createRequire(path.join(process.cwd(), 'package.json'));
const { firefox } = require('playwright');

const base = 'http://127.0.0.1:4173/screens';
const evidence = process.env.EVIDENCE;
if (!evidence) throw new Error('EVIDENCE is required');

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
const checkpoint = (label) => console.log(`NF01_FIREFOX_ORCA_CHECKPOINT=${label}`);

const activateWindow = (wid) => execFileSync('xdotool', ['windowactivate', '--sync', wid], { stdio: 'ignore' });
const nativeKey = (wid, key) => {
  activateWindow(wid);
  execFileSync('xdotool', ['key', '--clearmodifiers', key], { stdio: 'ignore' });
};

const context = await firefox.launchPersistentContext('/tmp/nf01-firefox-profile', {
  headless: false,
  viewport: null,
  firefoxUserPrefs: {
    'accessibility.force_disabled': -1,
  },
  env: {
    ...process.env,
    MOZ_ACCESSIBILITY_ATSPI: '1',
  },
});
const page = context.pages()[0] ?? await context.newPage();

await page.goto(`${base}/02.01-dashboard.html`, { waitUntil: 'networkidle' });
await sleep(1200);

let wid = '';
for (let attempt = 0; attempt < 80 && !wid; attempt += 1) {
  for (const args of [
    ['search', '--onlyvisible', '--class', 'firefox'],
    ['search', '--onlyvisible', '--name', 'NF-01|Dashboard|Mozilla Firefox|Firefox'],
  ]) {
    try {
      const output = execFileSync('xdotool', args, { encoding: 'utf8' }).trim();
      wid = output.split(/\s+/).filter(Boolean)[0] || '';
      if (wid) break;
    } catch {}
  }
  if (!wid) await sleep(250);
}
if (!wid) throw new Error('No headed Firefox window found');

activateWindow(wid);
checkpoint(`WINDOW_FOUND_${wid}`);

const journey = [];

async function activeElementSnapshot() {
  return page.evaluate(() => {
    const el = document.activeElement;
    if (!el) return { tag: null, role: null, name: null, interactive: false };
    const tag = el.tagName || null;
    const role = el.getAttribute?.('role') || null;
    const name = (
      el.getAttribute?.('aria-label')
      || el.innerText
      || el.textContent
      || el.getAttribute?.('title')
      || ''
    ).replace(/\s+/g, ' ').trim();
    const interactive = Boolean(
      ['A', 'BUTTON', 'INPUT', 'SELECT', 'TEXTAREA'].includes(tag)
      || el.hasAttribute?.('tabindex')
      || ['button', 'link', 'textbox', 'combobox', 'menuitem', 'alert'].includes(role)
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

async function orcaWhereAmI(label) {
  nativeKey(wid, 'KP_Enter');
  checkpoint(`WHERE_AM_I_${label}`);
  await sleep(1800);
}

async function nativeTabUntil(label, needle, maxTabs = 80) {
  const wanted = needle.toLocaleLowerCase('pt-BR');
  for (let index = 0; index <= maxTabs; index += 1) {
    const snap = await activeElementSnapshot();
    if (snap.interactive && (snap.name || '').toLocaleLowerCase('pt-BR').includes(wanted)) {
      journey.push({ label, target: needle, tabs: index, activeElement: snap, result: 'FOCUSED_NATIVE_KEYBOARD' });
      console.log(`NF01_FIREFOX_ORCA_FOCUS=${label};TARGET=${needle};NAME=${snap.name};TABS=${index}`);
      await sleep(700);
      await orcaWhereAmI(label);
      return snap;
    }
    await page.keyboard.press('Tab');
    await sleep(300);
  }
  const snap = await activeElementSnapshot();
  journey.push({ label, target: needle, activeElement: snap, result: 'TARGET_NOT_REACHED' });
  throw new Error(`Native keyboard target not reached: ${label} / ${needle}; active=${snap.name || ''}`);
}

async function resetWebFocus() {
  activateWindow(wid);
  const skip = page.getByText('Ir para o conteúdo', { exact: false }).first();
  if (await skip.count()) {
    await skip.focus();
    await sleep(500);
    const snap = await activeElementSnapshot();
    console.log(`NF01_FIREFOX_ORCA_SEED_FOCUS=${snap.name || ''}`);
    journey.push({
      label: 'WEB_FOCUS_SEED',
      activeElement: snap,
      result: 'PLAYWRIGHT_SKIP_LINK_SEED_ONLY',
    });
    return;
  }
  nativeKey(wid, 'F6');
  await sleep(650);
}

checkpoint('JOURNEY_BEGIN');
await resetWebFocus();

await nativeTabUntil('DASHBOARD_ATTENTION', 'biometrias pendentes');
await page.keyboard.press('Enter');
await page.waitForURL(/03\.01-funcionarios\.html\?biometric=missing/, { timeout: 10000 });
await sleep(1100);
journey.push({ label: 'DASHBOARD_TO_EMPLOYEES', url: page.url(), result: 'NAVIGATED_NATIVE_KEYBOARD' });

await resetWebFocus();
await nativeTabUntil('EMPLOYEES_NEW_EMPLOYEE', 'Novo funcionário');
await page.keyboard.press('Enter');
await page.waitForURL(/03\.04-novo-funcionario-v2\.html/, { timeout: 10000 });
await sleep(1100);

await resetWebFocus();
await nativeTabUntil('ONBOARDING_STEP_LIST', 'Ver etapas');
await page.keyboard.press('Enter');
await page.locator('[data-step-list]').waitFor({ state: 'visible', timeout: 10000 });
await sleep(700);
journey.push({
  label: 'STEP_LIST_OPEN',
  count: await page.locator('[data-step-list-button]').count(),
  result: 'OPENED_NATIVE_KEYBOARD',
});

const summaryTrigger = page.getByRole('button', { name: /Resumo/i }).first();
await summaryTrigger.focus();
await sleep(500);
const summarySnap = await activeElementSnapshot();
journey.push({
  label: 'ONBOARDING_CONTEXT_TRIGGER',
  target: 'Resumo',
  activeElement: summarySnap,
  result: 'PLAYWRIGHT_FOCUS_SEED_THEN_KEYBOARD_ACTIVATION',
});
console.log(`NF01_FIREFOX_ORCA_FOCUS=ONBOARDING_CONTEXT_TRIGGER;TARGET=Resumo;NAME=${summarySnap.name || ''}`);
await orcaWhereAmI('ONBOARDING_CONTEXT_TRIGGER');
await page.keyboard.press('Enter');
await page.locator('[data-context-drawer]').waitFor({ state: 'visible', timeout: 10000 });
await sleep(700);

await nativeTabUntil('CONTEXT_DRAWER_CLOSE', 'Fechar resumo', 30);
await page.keyboard.press('Escape');
await sleep(700);
const afterEscape = await activeElementSnapshot();
journey.push({
  label: 'CONTEXT_DRAWER_ESCAPE',
  activeElement: afterEscape,
  result: (afterEscape.name || '').includes('Resumo') ? 'FOCUS_RETURNED' : 'FOCUS_RETURN_UNCONFIRMED',
});

await nativeTabUntil('ONBOARDING_CONTINUE', 'Continuar', 60);
await page.keyboard.press('Enter');
const errorSummary = page.locator('[data-error-summary]');
await errorSummary.waitFor({ state: 'visible', timeout: 10000 });
await sleep(1200);
const errorSnap = await activeElementSnapshot();
await orcaWhereAmI('ERROR_SUMMARY');
const errorText = (await errorSummary.innerText()).replace(/\s+/g, ' ').trim();
journey.push({
  label: 'ERROR_SUMMARY',
  activeElement: errorSnap,
  errorText,
  result: 'ERROR_VISIBLE',
});
console.log(`NF01_FIREFOX_ORCA_ERROR=${errorText}`);

await page.keyboard.press('Alt+ArrowLeft');
await page.waitForURL(/03\.01-funcionarios\.html/, { timeout: 10000 });
await sleep(900);
journey.push({ label: 'RETURN_TO_EMPLOYEES', url: page.url(), result: 'RETURNED_NATIVE_KEYBOARD' });

const summary = {
  execution: 'CLOUD_FIREFOX_ORCA_ASSISTED_EVIDENCE',
  browser: 'FIREFOX_PLAYWRIGHT_HEADED',
  interactionInput: 'PLAYWRIGHT_KEYBOARD_ASSISTED_WITH_ORCA',
  orcaPrompting: 'KP_ENTER_WHERE_AM_I',
  journey,
  journeyCompleted: journey.some((x) => x.label === 'RETURN_TO_EMPLOYEES' && x.result === 'RETURNED_NATIVE_KEYBOARD'),
  manualAcceptanceClaimed: false,
};

fs.writeFileSync(path.join(evidence, 'firefox-orca-summary.json'), JSON.stringify(summary, null, 2));
checkpoint('JOURNEY_COMPLETE');
await context.close();
