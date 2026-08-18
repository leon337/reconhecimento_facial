import { chromium } from 'playwright';
import AxeBuilder from '@axe-core/playwright';
import fs from 'node:fs/promises';
import path from 'node:path';

const BASE = process.env.NF01_BASE_URL || 'http://127.0.0.1:4173';
const OUT = process.env.NF01_EVIDENCE_DIR || path.resolve('../../evidence/phase-n/automation-run');
const RESULTS_PATH = path.join(OUT, 'results.json');
const SUPERSEDED = new Set([
  'N3-EMPLOYEES-360-AXE',
  'N3-ONBOARDING-ENTITY_PICKER-KEYBOARD'
]);

const source = JSON.parse(await fs.readFile(RESULTS_PATH, 'utf8'));
const retainedFailures = source.results.filter((item) => item.RESULT === 'FAIL' && !SUPERSEDED.has(item.CASE_ID));
const followup = [];

const browser = await chromium.launch({ headless: true });
try {
  {
    const context = await browser.newContext({ viewport: { width: 360, height: 900 } });
    const page = await context.newPage();
    await page.goto(`${BASE}/screens/03.01-funcionarios.html`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(180);
    const scan = await new AxeBuilder({ page }).analyze();
    const severe = scan.violations.filter((v) => ['critical', 'serious'].includes(v.impact));
    followup.push({
      CASE_ID: 'N3-EMPLOYEES-360-AXE-RETEST',
      RESULT: severe.length ? 'FAIL' : 'PASS',
      ACTUAL: severe.map((v) => ({ id: v.id, impact: v.impact, target: v.nodes.map((n) => n.target) }))
    });
    await page.screenshot({ path: path.join(OUT, 'screenshots/N3-employees-360-axe-retest.png'), fullPage: true });
    await context.close();
  }

  {
    const context = await browser.newContext({ viewport: { width: 1024, height: 900 } });
    const page = await context.newPage();
    await page.goto(`${BASE}/screens/03.04-novo-funcionario-v2.html`, { waitUntil: 'domcontentloaded' });
    await page.evaluate(() => {
      localStorage.setItem('cpp:nf01:new-employee-v2:draft:v3', JSON.stringify({
        version: 3,
        revision: 1,
        currentStep: 3,
        maxReached: 3,
        completedSteps: [0, 1, 2],
        needsReview: [],
        errorSteps: [],
        biometricMockState: 'AGUARDANDO_CAMERA',
        runtimeState: 'READY',
        submissionId: null,
        permissions: ['users:create', 'biometrics:manage'],
        updatedAt: new Date().toISOString(),
        draftData: {},
        activePayloadPreview: {}
      }));
    });
    await page.reload({ waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(180);
    const visiblePickers = page.locator('[role="combobox"]:visible');
    const count = await visiblePickers.count();
    let focusedAfterEscape = false;
    let expandedAfterArrow = 'false';
    let expandedAfterEscape = 'true';
    if (count) {
      const picker = visiblePickers.first();
      await picker.focus();
      await picker.press('ArrowDown');
      expandedAfterArrow = await picker.getAttribute('aria-expanded');
      await picker.press('Escape');
      expandedAfterEscape = await picker.getAttribute('aria-expanded');
      focusedAfterEscape = await picker.evaluate((el) => document.activeElement === el);
    }
    const pass = count >= 6 && expandedAfterArrow === 'true' && expandedAfterEscape === 'false' && focusedAfterEscape;
    followup.push({
      CASE_ID: 'N3-ONBOARDING-ENTITY_PICKER-KEYBOARD-RETEST',
      RESULT: pass ? 'PASS' : 'FAIL',
      ACTUAL: { visiblePickers: count, expandedAfterArrow, expandedAfterEscape, focusedAfterEscape }
    });
    await page.screenshot({ path: path.join(OUT, 'screenshots/N3-onboarding-entity-picker-retest.png'), fullPage: true });
    await context.close();
  }
} finally {
  await browser.close();
}

const followupFailures = followup.filter((item) => item.RESULT === 'FAIL');
const final = {
  generatedAt: new Date().toISOString(),
  originalSummary: source.summary,
  supersededCaseIds: [...SUPERSEDED],
  retainedFailures,
  followup,
  finalFailCount: retainedFailures.length + followupFailures.length,
  blockedTooling: source.results.filter((item) => item.RESULT === 'BLOCKED_TOOLING').map((item) => item.CASE_ID)
};

await fs.writeFile(path.join(OUT, 'final-summary.json'), JSON.stringify(final, null, 2));
await fs.writeFile(path.join(OUT, 'final-summary.txt'), [
  `FINAL_FAIL=${final.finalFailCount}`,
  `BLOCKED_TOOLING=${final.blockedTooling.length}`,
  ...retainedFailures.map((item) => `FAIL ${item.SEVERITY_IF_FAIL} ${item.CASE_ID}`),
  ...followup.map((item) => `${item.RESULT} ${item.CASE_ID} ${JSON.stringify(item.ACTUAL)}`),
  ...final.blockedTooling.map((id) => `BLOCKED_TOOLING ${id}`)
].join('\n'));

console.log(JSON.stringify(final, null, 2));
if (final.finalFailCount > 0) process.exitCode = 1;
