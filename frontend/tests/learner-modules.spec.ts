import {test, expect, Page} from '@playwright/test';
// The API's real answers for the TEST FIXTURE lesson (backend/tests/fixtures/learner_modules/), checked
// against the API by backend/tests/test_learner_modules.py. Python runs for real in Pyodide here.
import recorded from './fixtures/learner-modules-api.json';
import lessons from '../../backend/tests/fixtures/legacy_lessons_v1.json';

/* ENG-08b: the learner's own files, in tabs beside the program. browser-checks.md section 12 and
 * decision 30: no file may stand in for one of Python's own modules, and the import guard applies
 * inside the learner's files as it does in the program. */

type Report = {id: string; status: string; output: string; errorType: string | null; line: number | null};
const LESSON = 'fixture.modules';
const scenario = (name: string) => recorded.scenarios.find(s => s.name === name)!;

const violations = new WeakMap<Page, string[]>();
test.beforeEach(async ({page}) => {
 const found: string[] = []; violations.set(page, found);
 await page.exposeFunction('reportCspViolation', (v: string) => found.push(v));
 await page.addInitScript(() => document.addEventListener('securitypolicyviolation', e => (window as unknown as {reportCspViolation: (v: string) => void}).reportCspViolation(`${e.effectiveDirective} blocked ${e.blockedURI || 'inline'}`)));
});
test.afterEach(async ({page}) => { expect(violations.get(page)).toEqual([]); });

// The worker, with no API

type Case = {id: string; inputs?: string[]; files?: Record<string, string>};
async function cases(page: Page, code: string, modules: Record<string, string>, list: Case[] = [{id: 'a'}, {id: 'b'}]): Promise<Report[]> {
 await page.goto('/no-such-page');
 return page.evaluate(async ({code, modules, list}) => {
  const runner = await import('/check-runner.js' as string);
  return runner.runCases(code, {time_limit_ms: 3000, output_limit: 10000, cases: list.map(c => ({inputs: [], ...c}))}, {modules});
 }, {code, modules, list});
}
/** One run, as "Try it" does it. */
async function once(page: Page, code: string, modules: Record<string, string> = {}, files: Record<string, string> = {}) {
 await page.goto('/no-such-page');
 return page.evaluate(({code, modules, files}) => new Promise<{output: string; error?: string; errorType?: string}>(resolve => {
  const worker = new Worker('/python-worker.js');
  worker.onmessage = ({data}) => { worker.terminate(); resolve(data); };
  worker.postMessage({code, inputs: [], files, modules});
 }), {code, modules, files});
}

test('the program imports the learner\'s own file, which may use allowed modules', async ({page}) => {
 const found = await cases(page, 'import helpers\nprint(helpers.half(9))', {'helpers.py': 'import math\ndef half(n):\n    return math.floor(n / 2)\n'});
 expect(found.map(r => [r.status, r.output])).toEqual([['ok', '4\n'], ['ok', '4\n']]);
});

test('decision 30: the import guard applies inside the learner\'s own file', async ({page}) => {
 for (const blocked of ['import os', 'import sys', 'import js', 'from . import other']) {
  const [report] = await cases(page, 'import helpers', {'helpers.py': blocked + '\n'}, [{id: 'a'}]);
  expect([blocked, report.status, report.errorType]).toEqual([blocked, 'error', blocked.startsWith('from .') ? 'ModuleNotFoundError' : 'ModuleNotFoundError']);
 }
});

test('decision 30: a learner file named like one of Python\'s modules is refused, not run', async ({page}) => {
 for (const name of ['random.py', 'os.py', 'math.py']) {
  const result = await once(page, `import ${name.slice(0, -3)}\nprint("ran")`, {[name]: 'print("pretending")\n'});
  expect(result.errorType).toBe('ImportError');
  expect(result.output).toBe('');
 }
});

test('decision 30: a file the program writes cannot stand in for one of Python\'s modules', async ({page}) => {
 // Before ENG-08b this printed "RUNTIME" from a fake datetime.py, which could then import os.
 const result = await once(page, 'open("datetime.py", "w").write("print(\\"RUNTIME\\")")\nimport datetime\nprint(datetime.date(2026, 1, 2))');
 expect(result.output).toBe('2026-01-02\n');
});

test('decision 30: nor can a file for a module Python loads later, behind the scenes', async ({page}) => {
 // datetime loads _strptime only when strptime() is first used, so it is not loaded in advance.
 const result = await once(page, 'open("_strptime.py", "w").write("print(\\"RUNTIME\\")")\nimport datetime\nprint(datetime.datetime.strptime("2026", "%Y").year)');
 expect(result.output).toBe('2026\n');
});

test('decision 30: a given file named like one of Python\'s modules does not replace it either', async ({page}) => {
 const result = await once(page, 'import random\nprint(random.randint(5, 5))', {}, {'random.py': 'print("pretending")\n'});
 expect(result.output).toBe('5\n');
});

test('only the learner\'s own files may be imported: a .py file that is not one of them is refused', async ({page}) => {
 const result = await once(page, 'import other', {}, {'other.py': 'print("other")\n'});
 expect(result.errorType).toBe('ModuleNotFoundError');
 expect(result.output).toBe('');
});

test('the learner\'s file starts again in every case: nothing it changed carries over', async ({page}) => {
 const code = 'import helpers\nhelpers.seen.append(1)\nprint(len(helpers.seen))\nopen("helpers.py", "w").write("seen = [1, 2, 3]")\n';
 const found = await cases(page, code, {'helpers.py': 'seen = []\n'});
 expect(found.map(r => r.output)).toEqual(['1\n', '1\n']);
});

test('a program with no learner files runs as it always did', async ({page}) => {
 const found = await cases(page, 'import random\nprint(random.randint(1, 1))', {});
 expect(found.map(r => [r.status, r.output])).toEqual([['ok', '1\n'], ['ok', '1\n']]);
});

// On the page

async function mockApi(page: Page) {
 const posted: unknown[] = [];
 await page.route('**/api/**', async route => {
  const path = new URL(route.request().url()).pathname;
  let status = 200, json: unknown = {};
  if (path === '/api/catalog') json = recorded.catalog;
  else if (path.startsWith('/api/units/')) json = recorded.units['fixture.u09'];
  else if (path === `/api/checks/${LESSON}`) json = recorded.plans[LESSON];
  else if (path === '/api/me') { status = 401; json = {detail: 'Sign in to continue'}; }
  else if (path === '/api/check') {
   const body = route.request().postDataJSON(); posted.push(body);
   const match = recorded.scenarios.find(s => JSON.stringify(s.request) === JSON.stringify(body));
   if (match) json = match.response; else { status = 500; json = {detail: 'not a recorded request'}; }
  }
  await route.fulfill({status, contentType: 'application/json', body: JSON.stringify(json)});
 });
 return posted;
}
const result = (page: Page) => page.locator('#code-feedback');
const editor = (page: Page) => page.getByLabel('Your Python code');
const tab = (page: Page, name: string) => page.getByRole('tab', {name});

async function runOnPage(page: Page, name: string) {
 const posted = await mockApi(page);
 await page.goto(`/preview?lesson=${LESSON}&card=5`);
 await tab(page, 'scores.py').click();
 await editor(page).fill(scenario(name).module);
 await page.getByRole('button', {name: 'Run & check challenge'}).click();
 await expect(page.getByRole('button', {name: 'Run & check challenge'})).toBeEnabled({timeout: 45000});
 // The request is exactly the recorded one: the program and the reports, and never the learner's file.
 expect(posted).toEqual([scenario(name).request]);
 expect(JSON.stringify(posted)).not.toContain('def total');
}

test('on the page: Try it shows a tab for each file, and runs the example with its own file', async ({page}) => {
 await mockApi(page);
 await page.goto(`/preview?lesson=${LESSON}&card=4`);
 await expect(page.getByRole('tablist', {name: 'Your files'}).getByRole('tab')).toHaveText(['main.py', 'greet.py']);
 await expect(tab(page, 'main.py')).toHaveAttribute('aria-selected', 'true');
 await tab(page, 'greet.py').click();
 await expect(editor(page)).toHaveValue(/def hello/);
 await page.getByRole('button', {name: 'Run Python →'}).click();
 await expect(page.locator('.execution-output')).toHaveText('Hello, Kai', {timeout: 45000});
});

test('on the page: a change to the learner\'s file is what runs, and each tab keeps its own code', async ({page}) => {
 await mockApi(page);
 await page.goto(`/preview?lesson=${LESSON}&card=4`);
 await tab(page, 'greet.py').click();
 await editor(page).fill('def hello(name):\n    return "Hi, " + name\n');
 await tab(page, 'main.py').click();
 await expect(editor(page)).toHaveValue('import greet\nprint(greet.hello("Kai"))');
 await page.getByRole('button', {name: 'Run Python →'}).click();
 await expect(page.locator('.execution-output')).toHaveText('Hi, Kai', {timeout: 45000});
 await tab(page, 'greet.py').click();
 await expect(editor(page)).toHaveValue(/Hi, /);
});

test('on the page: the tabs work from the keyboard, with the arrow keys, Home and End', async ({page}) => {
 await mockApi(page);
 await page.goto(`/preview?lesson=${LESSON}&card=5`);
 await tab(page, 'main.py').focus();
 await page.keyboard.press('ArrowRight');
 await expect(tab(page, 'scores.py')).toBeFocused();
 await expect(tab(page, 'scores.py')).toHaveAttribute('aria-selected', 'true');
 await expect(editor(page)).toHaveValue(/Write total/);
 await page.keyboard.press('ArrowRight');
 await expect(tab(page, 'main.py')).toBeFocused();
 await page.keyboard.press('End');
 await expect(tab(page, 'scores.py')).toBeFocused();
 await page.keyboard.press('Home');
 await expect(tab(page, 'main.py')).toBeFocused();
 // Only the selected tab is a Tab stop, so Tab goes on into the editor.
 await page.keyboard.press('Tab');
 await expect(editor(page)).toBeFocused();
});

test('on the page: Reset code resets only the file on show', async ({page}) => {
 await mockApi(page);
 await page.goto(`/preview?lesson=${LESSON}&card=5`);
 await editor(page).fill('print("changed main")');
 await tab(page, 'scores.py').click();
 await editor(page).fill('def total(numbers):\n    return 0\n');
 await page.getByRole('button', {name: 'Reset code'}).click();
 await expect(editor(page)).toHaveValue(/Write total/);
 await tab(page, 'main.py').click();
 await expect(editor(page)).toHaveValue('print("changed main")');
});

test('on the page: a correct file passes, and the learner\'s file never goes to the API', async ({page}) => {
 await runOnPage(page, 'passed');
 await expect(result(page)).toContainText('Check passed');
});

test('on the page: a wrong total is not a pass', async ({page}) => {
 await runOnPage(page, 'needs_work');
 await expect(result(page)).toContainText('Not yet');
});

test('on the page: an error in the learner\'s file is explained, and "Go to line" opens main.py', async ({page}) => {
 await runOnPage(page, 'error in the module');
 await expect(result(page)).toContainText('Python stopped');
 await expect(tab(page, 'scores.py')).toHaveAttribute('aria-selected', 'true');
 await page.getByRole('button', {name: 'Go to line 4 of main.py'}).click();
 await expect(tab(page, 'main.py')).toHaveAttribute('aria-selected', 'true');
 await expect(editor(page)).toBeFocused();
 await expect(page.locator('.code-gutter .gutter-line.error')).toHaveText('▶4');
});

test('on the page: a lesson with no learner files has no tabs, as before', async ({page}) => {
 await page.route('**/api/**', route => { const path = new URL(route.request().url()).pathname; return route.fulfill({status: path === '/api/me' ? 401 : 200, contentType: 'application/json', body: JSON.stringify(path === '/api/lessons' ? lessons : {})}); });
 await page.goto('/preview?lesson=hello&card=5');
 await expect(page.locator('.editor-top')).toContainText('story.py');
 await expect(page.getByRole('tablist')).toHaveCount(0);
});

test('on the page: the tabs fit a phone, with no sideways scrolling', async ({page}) => {
 await page.setViewportSize({width: 375, height: 812});
 await mockApi(page);
 await page.goto(`/preview?lesson=${LESSON}&card=5`);
 await expect(tab(page, 'scores.py')).toBeVisible();
 expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
});
