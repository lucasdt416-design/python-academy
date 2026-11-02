import {test, expect, Page} from '@playwright/test';
// The API's real answers for the TEST FIXTURE lesson (backend/tests/fixtures/file_checks/), checked
// against the API by backend/tests/test_file_checks.py. Python runs for real in Pyodide here.
import recorded from './fixtures/file-checks-api.json';

/* ENG-08: a program can be given files, in Pyodide's in-memory filesystem. browser-checks.md section 9. */

type Report = {id:string;status:string;output:string;errorType:string|null;line:number|null};
const LESSON = 'fixture.files';
const scenario = (name: string) => recorded.scenarios.find(s => s.name === name)!;

const violations = new WeakMap<Page, string[]>();
test.beforeEach(async ({page}) => {
 const found: string[] = []; violations.set(page, found);
 await page.exposeFunction('reportCspViolation', (v: string) => found.push(v));
 await page.addInitScript(() => document.addEventListener('securitypolicyviolation', e => (window as unknown as {reportCspViolation: (v: string) => void}).reportCspViolation(`${e.effectiveDirective} blocked ${e.blockedURI || 'inline'}`)));
});
test.afterEach(async ({page}) => { expect(violations.get(page)).toEqual([]); });

// The worker and the runner, with no API

type Case = {id: string; inputs?: string[]; files?: Record<string, string>};
async function run(page: Page, code: string, cases: Case[]): Promise<Report[]> {
 await page.goto('/no-such-page');
 return page.evaluate(async ({code, cases}) => {
  const runner = await import('/check-runner.js' as string);
  return runner.runCases(code, {time_limit_ms: 3000, output_limit: 10000, cases: cases.map(c => ({inputs: [], ...c}))});
 }, {code, cases});
}
// random holds os; a plain `import os` is refused once the import guard (ENG-07) is in.
const OS = 'import random\nos = random._os\n';
const LIST = OS + 'for folder, _, names in os.walk("."):\n    for name in sorted(names):\n        print(os.path.join(folder, name))\n';

test('a program reads the file its case gives it, and each case has its own', async ({page}) => {
 const reports = await run(page, 'print(open("a.txt").read())', [{id: 'one', files: {'a.txt': 'first'}}, {id: 'two', files: {'a.txt': 'second'}}]);
 expect(reports.map(r => [r.status, r.output])).toEqual([['ok', 'first\n'], ['ok', 'second\n']]);
});

test('a file in a folder is there, and a case sees only its own files', async ({page}) => {
 const reports = await run(page, LIST, [{id: 'one', files: {'saves/game.json': '{}', 'a.txt': 'x'}}, {id: 'two', files: {'b.txt': 'y'}}, {id: 'three'}]);
 expect(reports.map(r => r.output)).toEqual(['./a.txt\n./saves/game.json\n', './b.txt\n', '']);
});

test('what a case writes is gone in the next case, in its folder, in a new folder and in /tmp', async ({page}) => {
 const code = OS + `print(os.path.exists("left.txt"), os.path.exists("made/left.txt"), os.path.exists("/tmp/left.txt"))
open("left.txt", "w").write("x")
os.makedirs("made", exist_ok=True)
open("made/left.txt", "w").write("x")
open("/tmp/left.txt", "w").write("x")
`;
 const reports = await run(page, code, [{id: 'one'}, {id: 'two'}]);
 expect(reports.map(r => r.output)).toEqual(['False False False\n', 'False False False\n']);
});

test('a change to a given file does not reach the next case', async ({page}) => {
 const reports = await run(page, 'print(open("a.txt").read())\nopen("a.txt", "w").write("changed")\n', [{id: 'one', files: {'a.txt': 'start'}}, {id: 'two', files: {'a.txt': 'start'}}]);
 expect(reports.map(r => r.output)).toEqual(['start\n', 'start\n']);
});

test('a case starts in its own folder, even if the one before moved away', async ({page}) => {
 const code = OS + 'print(os.getcwd())\nos.chdir("/tmp")\n';
 const reports = await run(page, code, [{id: 'one'}, {id: 'two'}]);
 expect(reports.map(r => r.output)).toEqual(['/home/pyodide\n', '/home/pyodide\n']);
});

test('Python\'s own library is untouched by the clean-up', async ({page}) => {
 const reports = await run(page, 'import json\nprint(json.dumps([1]))', [{id: 'one'}, {id: 'two'}]);
 expect(reports.map(r => r.output)).toEqual(['[1]\n', '[1]\n']);
});

test('a missing file is a FileNotFoundError on its line', async ({page}) => {
 const [report] = await run(page, 'x = 1\nopen("nope.txt")\n', [{id: 'one'}]);
 expect(report).toMatchObject({status: 'error', errorType: 'FileNotFoundError', line: 2});
});

test('printing a file over and over still hits the output limit', async ({page}) => {
 const [report] = await run(page, 'for i in range(100000):\n    print(open("a.txt").read())\n', [{id: 'one', files: {'a.txt': 'x'.repeat(5000)}}]);
 expect(report.status).toBe('output_limit');
});

test('files make no change to a case without them', async ({page}) => {
 const [report] = await run(page, 'print(input())', [{id: 'one', inputs: ['hi']}]);
 expect(report).toMatchObject({status: 'ok', output: 'hi\n'});
});

// On the page

async function mockApi(page: Page) {
 const posted: unknown[] = [];
 await page.route('**/api/**', async route => {
  const path = new URL(route.request().url()).pathname;
  let status = 200, json: unknown = {};
  if (path === '/api/catalog') json = recorded.catalog;
  else if (path.startsWith('/api/units/')) json = recorded.units['fixture.u08'];
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
async function runOnPage(page: Page, name: string) {
 const posted = await mockApi(page);
 await page.goto(`/preview?lesson=${LESSON}&card=5`);
 await page.getByLabel('Your Python code').fill(scenario(name).request.code);
 await page.getByRole('button', {name: 'Run & check challenge'}).click();
 await expect(page.getByRole('button', {name: 'Run & check challenge'})).toBeEnabled({timeout: 45000});
 expect(posted).toEqual([scenario(name).request]);
}

test('on the page: the worked example shows its file, and says files are temporary', async ({page}) => {
 await mockApi(page);
 await page.goto(`/preview?lesson=${LESSON}&card=2`);
 const files = page.getByRole('region', {name: 'Files your program can open'});
 await expect(files.getByText('note.txt')).toBeVisible();
 await expect(files.getByText('hello from the file')).toBeVisible();
 await expect(files).toContainText('Files here are temporary.');
});

test('on the page: Try it runs the example with its file', async ({page}) => {
 await mockApi(page);
 await page.goto(`/preview?lesson=${LESSON}&card=4`);
 await page.getByRole('button', {name: 'Run Python →'}).click();
 await expect(result(page)).toContainText('Ran · not checked', {timeout: 45000});
 await expect(page.locator('.execution-output')).toHaveText('hello from the file');
});

test('on the page: the challenge shows a visible sample and never a hidden file', async ({page}) => {
 await mockApi(page);
 await page.goto(`/preview?lesson=${LESSON}&card=5`);
 const files = page.getByRole('region', {name: 'A sample of the files your program gets'});
 await expect(files.getByText('scores.txt')).toBeVisible();
 await expect(files).toContainText('The check also tries other files you cannot see.');
 await expect(page.locator('body')).not.toContainText('22');
});

test('on the page: a correct program passes, and so does another way', async ({page}) => {
 await runOnPage(page, 'passed');
 await expect(result(page)).toContainText('Check passed');
});

test('on the page: a hard-coded answer is not a pass', async ({page}) => {
 await runOnPage(page, 'needs_work');
 await expect(result(page)).toContainText('Not yet');
 await page.getByRole('button', {name: 'Show a hint about this check'}).click();
 await expect(page.getByText('Add every line of the file, not numbers typed into the code.')).toBeVisible();
});

test('on the page: a hidden case that fails is named by its description only', async ({page}) => {
 await runOnPage(page, 'hidden');
 await expect(result(page)).toContainText('a longer file you cannot see (a hidden test case)');
 await expect(result(page)).not.toContainText('63');
});

test('on the page: a missing file is explained, with the line', async ({page}) => {
 await runOnPage(page, 'missing file');
 await expect(result(page)).toContainText('Python stopped');
 await expect(page.locator('.code-gutter .gutter-line.error')).toHaveText('▶1');
 await page.getByRole('button', {name: 'Show a hint about this error'}).click();
 await expect(page.getByText('Open the file by the name in the challenge: scores.txt.')).toBeVisible();
});

test('on the page: the files fit a phone, with no sideways scrolling', async ({page}) => {
 await page.setViewportSize({width: 375, height: 812});
 await mockApi(page);
 await page.goto(`/preview?lesson=${LESSON}&card=4`);
 await expect(page.locator('.lesson-files figcaption')).toHaveText('note.txt');
 expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
});
