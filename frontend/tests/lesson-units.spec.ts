import {test, expect, Page} from '@playwright/test';
import legacy from '../../backend/tests/fixtures/legacy_lessons_v1.json';
// The API's real answers for the TEST FIXTURE units (backend/tests/fixtures/lesson_units/), checked
// against the API by backend/tests/test_lesson_units.py. Python runs for real in Pyodide here.
import recorded from './fixtures/lesson-units-api.json';

/* UI-05: lessons load one unit at a time, and a challenge with a browser check (ENG-03) runs its
 * cases in the browser and shows the judge's result through the ENG-04 feedback. */

type Scenario = (typeof recorded.scenarios)[number];
const scenario = (name: string) => recorded.scenarios.find(s => s.name === name)!;
const HIDDEN_EXPECTED = ['6144', '42'];

async function mockApi(page: Page, {check, unitsRoute = true}: {check?: (body: Record<string, unknown>) => {status?: number; json: unknown}; unitsRoute?: boolean} = {}) {
 const requests: string[] = [], posted: Record<string, unknown>[] = [], answers: string[] = [];
 await page.route('**/api/**', async route => {
  const path = new URL(route.request().url()).pathname;
  requests.push(path);
  let status = 200, json: unknown = {};
  const unit = /^\/api\/units\/([^/]+)\/lessons$/.exec(path)?.[1], plan = /^\/api\/checks\/(.+)$/.exec(path)?.[1];
  if (path === '/api/catalog') json = recorded.catalog;
  else if (path === '/api/lessons') json = legacy;
  else if (unit && unitsRoute && unit in recorded.units) json = recorded.units[unit as keyof typeof recorded.units];
  else if (unit) { status = 404; json = {detail: 'Not Found'}; }
  else if (plan) json = recorded.plans[plan as keyof typeof recorded.plans];
  else if (path === '/api/check') {
   const body = route.request().postDataJSON(); posted.push(body);
   // The recorded answer only for exactly the recorded request (same code and the same reports).
   const match = recorded.scenarios.find(s => JSON.stringify(s.request) === JSON.stringify(body));
   ({status = 200, json} = check ? check(body) : match ? {json: match.response} : {status: 500, json: {detail: 'not a recorded request'}});
  }
  const text = JSON.stringify(json); answers.push(text);
  await route.fulfill({status, contentType: 'application/json', body: text});
 });
 return {requests, posted, answers};
}
const violations = new WeakMap<Page, string[]>();
test.beforeEach(async ({page}) => {
 const found: string[] = []; violations.set(page, found);
 await page.exposeFunction('reportCspViolation', (v: string) => found.push(v));
 await page.addInitScript(() => document.addEventListener('securitypolicyviolation', e => (window as unknown as {reportCspViolation: (v: string) => void}).reportCspViolation(`${e.effectiveDirective} blocked ${e.blockedURI || 'inline'}`)));
});
test.afterEach(async ({page}) => { expect(violations.get(page)).toEqual([]); });

const result = (page: Page) => page.locator('#code-feedback');
async function runScenario(page: Page, s: Scenario) {
 await page.goto(`/preview?lesson=${s.request.lesson_id}&card=5`);
 await page.getByLabel('Your Python code').fill(s.request.code);
 await page.getByRole('button', {name: 'Run & check challenge'}).click();
 await expect(page.getByRole('button', {name: 'Run & check challenge'})).toBeEnabled({timeout: 45000});
}

// Loading per unit

test('a lesson in another unit loads that unit only, with its own title and count', async ({page}) => {
 const {requests} = await mockApi(page);
 await page.goto('/preview?lesson=fixture.double');
 await expect(page.getByRole('heading', {level: 1, name: 'TEST FIXTURE unit two'})).toBeVisible();
 await expect(page.getByText('UNIT 02 · TEST FIXTURE (NEVER SHOWN TO LEARNERS)')).toBeVisible();
 const nav = page.getByRole('navigation', {name: 'Lessons in this unit'});
 await expect(nav.getByRole('listitem')).toHaveText([/Double a number/]);
 await expect(page.getByText('Quest 1 of 1 · Fixture doubler')).toBeVisible();
 await expect(page.locator('.story-world')).toHaveCount(0);  // unit 1's pictures stay in unit 1
 expect(requests).toContain('/api/units/fixture.u02/lessons');
 expect(requests.filter(p => p.startsWith('/api/units/'))).toEqual(['/api/units/fixture.u02/lessons']);
 expect(requests).not.toContain('/api/lessons');
});

test('with no lesson named, unit 1 loads per unit, exactly as before', async ({page}) => {
 const {requests} = await mockApi(page);
 await page.goto('/preview');
 await expect(page.getByRole('heading', {level: 1, name: 'Build Your Own Adventure.'})).toBeVisible();
 await expect(page.getByRole('navigation', {name: 'Lessons in this unit'}).getByRole('listitem')).toHaveCount(5);
 expect(requests).toContain('/api/units/py.u01/lessons');
 expect(requests).not.toContain('/api/lessons');
});

test('an API without the per-unit route (during a deploy) still gives unit 1 from /api/lessons', async ({page}) => {
 const {requests} = await mockApi(page, {unitsRoute: false});
 await page.goto('/preview?lesson=variables&card=1');
 await expect(page.getByRole('heading', {name: 'Remember a detail with a variable'})).toBeVisible();
 await expect(page.getByRole('navigation', {name: 'Breadcrumb'})).toContainText('Unit 1: Build Your Own Adventure');
 expect(requests).toContain('/api/lessons');
});

// A browser-check challenge, end to end

test('passed: every case printed what was expected, so the badge and other ways appear', async ({page}) => {
 const s = scenario('passed');
 const {posted} = await mockApi(page);
 await runScenario(page, s);
 await expect(result(page)).toContainText('Check passed');
 await expect(page.getByText('Fixture adder badge earned!')).toBeVisible();
 await expect(page.getByRole('region', {name: 'Other ways to do it'})).toBeVisible();
 // The Output panel shows the visible cases only.
 await expect(page.locator('.execution-output')).toHaveText('With the numbers 2 and 3:\n5\n\nWith 10 and -4:\n6');
 // Exactly what the ENG-03 contract sends: the code, the first output, and per case id, status,
 // output, error type and line. Never Python's message.
 expect(posted).toEqual([s.request]);
 expect(Object.keys((posted[0].runs as object[])[0]).sort()).toEqual(['error_type', 'id', 'line', 'output', 'status']);
});

test('needs_work: wrong output names its case, and the hint tagged for that case comes first', async ({page}) => {
 const s = scenario('needs_work');
 const {posted} = await mockApi(page);
 await runScenario(page, s);
 await expect(result(page)).toHaveText('Not yet' + s.response.feedback);
 await expect(page.getByText(/badge earned!/)).toHaveCount(0);
 const hints = page.getByRole('region', {name: 'Hints'});
 await expect(hints.getByRole('button')).toHaveText('Show a hint about this check');
 await hints.getByRole('button').click();
 await expect(hints.getByRole('listitem')).toHaveText(['About this check. A negative number is still a number: adding -4 takes 4 away. Check that you add the two replies as they are.']);
 expect(posted).toEqual([s.request]);
});

test('a hidden case that fails is named by its description only', async ({page}) => {
 const s = scenario('hidden case fails');
 await mockApi(page);
 await runScenario(page, s);
 await expect(result(page)).toContainText('two larger numbers (a hidden test case)');
 const shown = await page.locator('body').innerText();
 for (const value of [...HIDDEN_EXPECTED, '4096', '2048']) expect(shown).not.toContain(value);
});

test('execution_error: the friendly explanation, the line, and Python’s message, which stays in the browser', async ({page}) => {
 const s = scenario('execution_error');
 const {posted} = await mockApi(page);
 await runScenario(page, s);
 await expect(result(page)).toContainText('Python stopped');
 await expect(result(page)).toContainText('Python does not know c yet');
 await expect(result(page)).toContainText('Line 3');
 await expect(page.locator('.code-gutter .gutter-line.error')).toHaveText('▶3');
 await page.getByText('Show Python’s message').click();
 await expect(page.locator('.python-message')).toHaveText("NameError: name 'c' is not defined");
 await expect(page.getByRole('region', {name: 'Hints'}).getByRole('button')).toHaveText('Show a hint about this error');
 expect(JSON.stringify(posted)).not.toContain('is not defined');
 expect(posted).toEqual([s.request]);
 await expect(page.getByText(/badge earned!/)).toHaveCount(0);
});

test('an endless loop is stopped at the 3-second limit', async ({page}) => {
 const s = scenario('timeout');
 await mockApi(page);
 const started = Date.now();
 await runScenario(page, s);
 expect(Date.now() - started).toBeLessThan(30000);
 await expect(result(page)).toContainText('Your program kept running');
 await expect(result(page)).toContainText('It did not finish within 3 seconds');
 await expect(page.locator('.execution-output')).toContainText('(stopped: still running after 3 seconds)');
 await expect(page.locator('.execution-output')).toContainText('With 10 and -4:\n(not run)');
 // Python stopped, so this is not a pass.
 await expect(page.getByText(/badge earned!/)).toHaveCount(0);
 await expect(page.getByRole('button', {name: 'Revisit this quest'})).toBeDisabled();
});

test('output over the cap is stopped', async ({page}) => {
 const s = scenario('output_limit');
 await mockApi(page);
 await runScenario(page, s);
 await expect(result(page)).toContainText('Too much output');
 await expect(result(page)).toContainText('more than 10,000 characters');
 await expect(page.locator('.execution-output')).toContainText('(stopped: too much output)');
 // Python stopped, so this is not a pass.
 await expect(page.getByText(/badge earned!/)).toHaveCount(0);
 await expect(page.getByRole('button', {name: 'Revisit this quest'})).toBeDisabled();
});

test('unsupported and missing replies each keep their own state', async ({page}) => {
 await mockApi(page);
 for (const [name, label] of [['unsupported', 'Not checked'], ['missing_input', 'Not yet']] as const) {
  const s = scenario(name);
  await runScenario(page, s);
  await expect(result(page)).toHaveText(label + s.response.feedback);
  await expect(page.getByText(/badge earned!/)).toHaveCount(0);
 }
});

test('service_error: Python cannot start, so the check is unavailable', async ({page}) => {
 const s = scenario('service_error');
 const {posted} = await mockApi(page);
 await page.route('https://cdn.jsdelivr.net/**', route => route.abort());
 await runScenario(page, s);
 expect(posted).toEqual([s.request]);
 await expect(result(page)).toHaveText('Check unavailable' + s.response.feedback);
 await expect(page.getByText(/badge earned!/)).toHaveCount(0);
});

test('when the API fails, the draft stays and nothing counts as a pass', async ({page}) => {
 await mockApi(page, {check: () => ({status: 500, json: {detail: 'Internal Server Error'}})});
 const s = scenario('passed');
 await runScenario(page, s);
 await expect(page.locator('main .notice[role=alert]')).toHaveText('Internal Server Error');
 await expect(page.getByText(/badge earned!/)).toHaveCount(0);
 await expect(page.getByLabel('Your Python code')).toHaveValue(s.request.code);
 await expect(page.getByRole('button', {name: 'Next quest →'})).toHaveCount(0);
 await expect(page.getByRole('button', {name: 'Revisit this quest'})).toBeDisabled();
});

test('a lesson in the second unit passes end to end', async ({page}) => {
 const s = scenario('unit two passed');
 const {posted} = await mockApi(page);
 await runScenario(page, s);
 await expect(result(page)).toContainText('Check passed');
 await expect(page.getByText('Fixture doubler badge earned!')).toBeVisible();
 expect(posted).toEqual([s.request]);
});

test('no answer the page receives holds a hidden expected output', async ({page}) => {
 const {answers} = await mockApi(page);
 for (const name of ['passed', 'needs_work', 'hidden case fails']) await runScenario(page, scenario(name));
 await page.goto('/preview?lesson=fixture.double&card=5');
 await expect(page.getByLabel('Your Python code')).toBeVisible();
 expect(answers.length).toBeGreaterThan(10);
 for (const answer of answers) for (const value of HIDDEN_EXPECTED) expect(answer).not.toMatch(new RegExp(`(^|[^0-9])${value}([^0-9]|$)`));
});

test('keyboard: run from the keyboard, then go to the failing line', async ({page}) => {
 await mockApi(page);
 const s = scenario('execution_error');
 await page.goto(`/preview?lesson=${s.request.lesson_id}&card=5`);
 await page.getByLabel('Your Python code').fill(s.request.code);
 await page.getByRole('button', {name: 'Run & check challenge'}).focus();
 await page.keyboard.press('Enter');
 await expect(page.getByRole('button', {name: 'Go to line 3'})).toBeVisible({timeout: 45000});
 await page.getByRole('button', {name: 'Go to line 3'}).focus();
 await page.keyboard.press('Enter');
 await expect(page.getByLabel('Your Python code')).toBeFocused();
});

test('the browser-check card fits a phone, and nothing moves with reduced motion', async ({page}) => {
 await page.setViewportSize({width: 375, height: 812});
 await page.emulateMedia({reducedMotion: 'reduce'});
 await mockApi(page);
 await runScenario(page, scenario('needs_work'));
 await expect(page.getByText('This challenge runs your program with its own replies')).toBeVisible();
 await expect(page.getByRole('group', {name: 'Player replies'})).toHaveCount(0);
 expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
 expect(await page.locator('.result, .result *').evaluateAll(els => els.every(el => getComputedStyle(el).animationName === 'none'))).toBe(true);
});
