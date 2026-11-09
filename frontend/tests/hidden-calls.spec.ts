import {test, expect, Page} from '@playwright/test';
// The API's real answers for the TEST FIXTURE lesson (backend/tests/fixtures/hidden_calls/), checked by
// backend/tests/test_hidden_calls.py. Python runs for real in Pyodide, and each request must match exactly.
import recorded from './fixtures/hidden-calls-api.json';

/* Decision 28: a hidden call's arguments reach the browser, and its answer never does. */

const LESSON = 'fixture.hidden-calls';
const scenario = (name: string) => recorded.scenarios.find(s => s.name === name)!;
const result = (page: Page) => page.locator('#code-feedback');

async function runOnPage(page: Page, name: string) {
 const posted: unknown[] = [], answers: string[] = [];
 await page.route('**/api/**', async route => {
  const path = new URL(route.request().url()).pathname;
  let status = 200, json: unknown = {};
  if (path === '/api/catalog') json = recorded.catalog;
  else if (path.startsWith('/api/units/')) json = recorded.units['fixture.u10'];
  else if (path === `/api/checks/${LESSON}`) json = recorded.plans[LESSON];
  else if (path === '/api/me') { status = 401; json = {detail: 'Sign in to continue'}; }
  else if (path === '/api/check') {
   const body = route.request().postDataJSON(); posted.push(body);
   const match = recorded.scenarios.find(s => JSON.stringify(s.request) === JSON.stringify(body));
   if (match) json = match.response; else { status = 500; json = {detail: 'not a recorded request'}; }
  }
  const text = JSON.stringify(json); answers.push(text);
  await route.fulfill({status, contentType: 'application/json', body: text});
 });
 await page.goto(`/preview?lesson=${LESSON}&card=5`);
 await page.getByLabel('Your Python code').fill(scenario(name).request.code);
 await page.getByRole('button', {name: 'Run & check challenge'}).click();
 await expect(page.getByRole('button', {name: 'Run & check challenge'})).toBeEnabled({timeout: 45000});
 expect(posted).toEqual([scenario(name).request]);
 return answers;
}

test('a correct function passes the visible and the hidden call', async ({page}) => {
 const answers = await runOnPage(page, 'passed');
 await expect(result(page)).toContainText('Check passed');
 for (const answer of answers) expect(answer).not.toContain('171');
});

test('a hard-coded function fails on the hidden call, named by its description only', async ({page}) => {
 await runOnPage(page, 'hard-coded');
 await expect(result(page)).toContainText('another number you cannot see (a hidden test case)');
 const body = await page.locator('body').innerText();
 for (const secret of ['57', '171']) expect(body).not.toContain(secret);
 await page.getByRole('button', {name: 'Show a hint about this check'}).click();
 await expect(page.getByText('Use the value of n, not a fixed answer.')).toBeVisible();
});

test('the output panel shows the visible call, and not the hidden one', async ({page}) => {
 await runOnPage(page, 'hard-coded');
 await expect(page.locator('.execution-output')).toContainText('triple(2)');
 await expect(page.locator('.execution-output')).not.toContainText('another number');
});
