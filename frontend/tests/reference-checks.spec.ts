import {test, expect, Page} from '@playwright/test';
// The API's real answers for the TEST FIXTURE lesson (backend/tests/fixtures/reference_checks/), checked by
// backend/tests/test_reference_checks.py. Python runs for real in Pyodide, and each request must match exactly.
import recorded from './fixtures/reference-checks-api.json';

/* ENG-10: a learner's tests run against correct and broken reference programs. browser-checks.md section 11. */

const LESSON = 'fixture.tests';
const scenario = (name: string) => recorded.scenarios.find(s => s.name === name)!;
const result = (page: Page) => page.locator('#code-feedback');

async function runOnPage(page: Page, name: string) {
 const posted: unknown[] = [];
 await page.route('**/api/**', async route => {
  const path = new URL(route.request().url()).pathname;
  let status = 200, json: unknown = {};
  if (path === '/api/catalog') json = recorded.catalog;
  else if (path.startsWith('/api/units/')) json = recorded.units['fixture.u11'];
  else if (path === `/api/checks/${LESSON}`) json = recorded.plans[LESSON];
  else if (path === '/api/me') { status = 401; json = {detail: 'Sign in to continue'}; }
  else if (path === '/api/check') {
   const body = route.request().postDataJSON(); posted.push(body);
   const match = recorded.scenarios.find(s => JSON.stringify(s.request) === JSON.stringify(body));
   if (match) json = match.response; else { status = 500; json = {detail: 'not a recorded request'}; }
  }
  await route.fulfill({status, contentType: 'application/json', body: JSON.stringify(json)});
 });
 await page.goto(`/preview?lesson=${LESSON}&card=5`);
 await page.getByLabel('Your Python code').fill(scenario(name).request.code);
 await page.getByRole('button', {name: 'Run & check challenge'}).click();
 await expect(page.getByRole('button', {name: 'Run & check challenge'})).toBeEnabled({timeout: 45000});
 expect(posted).toEqual([scenario(name).request]);
}

test('good tests pass on the correct program and catch every bug', async ({page}) => {
 await runOnPage(page, 'passed');
 await expect(result(page)).toContainText('Check passed');
 const output = page.locator('.execution-output');
 await expect(output).toContainText('With the correct scorer:\n(your tests all passed)');
 await expect(output).toContainText('With a scorer with a bug:\n(a test stopped here)');
 await expect(output).not.toContainText('scorer you cannot see');
});

for (const name of ['always true', 'no tests', 'prints only']) test(`${name}: tests that catch nothing do not pass`, async ({page}) => {
 await runOnPage(page, name);
 await expect(result(page)).toContainText('Your tests all passed on a scorer with a bug, which has a bug.');
 await page.getByRole('button', {name: 'Show a hint about this check'}).click();
 await expect(page.getByText('Try a guess that is not exact.')).toBeVisible();
});

test('a test that fails on correct code says so, with its own hint', async ({page}) => {
 await runOnPage(page, 'wrong test');
 await expect(result(page)).toContainText('A test failed on the correct scorer, which is correct.');
 await page.getByRole('button', {name: 'Show a hint about this check'}).click();
 await expect(page.getByText('Check what your assert expects from correct code.')).toBeVisible();
});

test('a missed hidden bug is named by its description, and its code is not shown', async ({page}) => {
 await runOnPage(page, 'misses the hidden bug');
 await expect(result(page)).toContainText('a scorer you cannot see (a hidden test case)');
 await expect(page.locator('body')).not.toContainText('return 10 if');
 await page.getByRole('button', {name: 'Show a hint about this check'}).click();
 await expect(page.getByText('Try a guess that is far away.')).toBeVisible();
});

test('a typo is explained as a Python error, on the learner\'s own line', async ({page}) => {
 await runOnPage(page, 'name error');
 await expect(result(page)).toContainText('Python stopped');
 await expect(result(page)).toContainText('Python does not know scor');
 await expect(page.locator('.code-gutter .gutter-line.error')).toHaveText('▶1');
});

test('each case gets only its own reference, and the import guard still applies', async ({page}) => {
 await page.goto('/no-such-page');
 const reports = await page.evaluate(async () => {
  const runner = await import('/check-runner.js' as string);
  const plan = {time_limit_ms: 3000, output_limit: 10000, cases: [{id: 'a', inputs: [], reference: 'x = 1\ny = 2\n'}, {id: 'b', inputs: [], reference: 'x = 3\n'}]};
  const first = await runner.runCases('print(x)\nprint(globals().get("y"))\n', plan);
  const second = await runner.runCases('import os\n', {...plan, cases: [plan.cases[0]]});
  const third = await runner.runCases('print(1)\n', {...plan, cases: [{id: 'c', inputs: [], reference: 'import os\n'}]});
  return {first, second, third};
 });
 expect(reports.first.map((r: {output: string}) => r.output)).toEqual(['1\n2\n', '3\nNone\n']);
 expect(reports.second[0]).toMatchObject({status: 'error', errorType: 'ModuleNotFoundError', line: 1});
 expect(reports.third[0]).toMatchObject({status: 'error', errorType: 'ModuleNotFoundError', line: null});
});
