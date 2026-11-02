import {test, expect, Page} from '@playwright/test';
// ENG-07: what the import guard does in real Pyodide, in both of the worker's modes.
// backend/tests/test_allowed_imports.py holds the list to one place and covers the API's side.
import seeded from './fixtures/seeded-random.json';

const BLOCKED = ['os', 'sys', 'subprocess', 'socket', 'urllib', 'requests', 'pyodide', 'js', 'ctypes', 'importlib', 'pyodide_js', 'shutil', 'pathlib', 'builtins', 'http'];
const ALLOWED = ['math', 'random', 'datetime', 'json', 'csv', 're'];
const OUTPUT_LIMIT = 10000;

type TryIt = {output?: string; error?: string; errorType?: string | null};
type CaseReport = {type: string; id: string; status: string; output: string; errorType: string | null; line: number | null};

async function open(page: Page) {
 await page.route('**/api/**', r => r.fulfill({status: 401, contentType: 'application/json', body: '{"detail":"Sign in to continue"}'}));
 await page.goto('/courses');
}
const tryIt = (page: Page, code: string) => page.evaluate(code => new Promise<TryIt>(done => {
 const worker = new Worker('/python-worker.js');
 worker.onmessage = e => { worker.terminate(); done(e.data); };
 worker.postMessage({code, inputs: []});
}), code);
const inCases = (page: Page, code: string, cases: object[] = [{id: 'a', inputs: []}]) => page.evaluate(({code, cases, limit}) => new Promise<CaseReport[]>(done => {
 const worker = new Worker('/python-worker.js'), found: CaseReport[] = [];
 worker.onmessage = e => {
  if (e.data.type === 'case') found.push(e.data);
  if (e.data.type === 'done') { worker.terminate(); done(found); }
 };
 worker.postMessage({mode: 'cases', code, cases, outputLimit: limit});
}), {code, cases, limit: OUTPUT_LIMIT});

// One worker tries them all, so these tests stay quick.
const attempt = (statement: string) => `try:\n    ${statement}\n    print(${JSON.stringify(statement)}, "imported")\nexcept ModuleNotFoundError as e:\n    print(${JSON.stringify(statement)}, "refused", e.name)\n`;

for (const mode of ['Try it', 'a check'] as const) {
 const run = async (page: Page, code: string) => mode === 'Try it' ? (await tryIt(page, code)).output! : (await inCases(page, code))[0].output;

 test(`${mode}: every blocked module is refused`, async ({page}) => {
  await open(page);
  const lines = (await run(page, BLOCKED.map(name => attempt(`import ${name}`)).join(''))).trim().split('\n');
  expect(lines).toEqual(BLOCKED.map(name => `import ${name} refused ${name}`));
 });

 test(`${mode}: every allowed module works, including the parts that use other modules inside`, async ({page}) => {
  await open(page);
  const output = await run(page, `
${ALLOWED.map(name => `import ${name}`).join('\n')}
print(math.floor(2.5))
random.seed(1)
print(1 <= random.randint(1, 6) <= 6)
print(datetime.datetime.strptime("2026-11-02", "%Y-%m-%d").date() + datetime.timedelta(days=1))
print(json.loads(json.dumps({"a": [1, 2]})))
print(next(csv.reader(["x,y"])))
print(re.findall(r"[a-z]+", "ab 12 cd"))
from math import sqrt as root
from datetime import date
import json.decoder
print(root(9), date(2026, 1, 2).isoformat(), json.decoder.__name__)
`);
  expect(output.trim().split('\n')).toEqual(['2', 'True', '2026-11-03', "{'a': [1, 2]}", "['x', 'y']", "['ab', 'cd']", '3.0 2026-01-02 json.decoder']);
 });

 test(`${mode}: the other ways to write an import are refused too`, async ({page}) => {
  await open(page);
  const statements = ['from os import path', 'import os.path', 'import os as allowed', 'from urllib.request import urlopen', '__import__("os")', '__import__("os", {})',
                      '__import__("os", {"__name__": "json"})', 'exec("import os")', 'eval("__import__(\'js\')")'];
  const lines = (await run(page, statements.map(attempt).join(''))).trim().split('\n');
  expect(lines).toHaveLength(statements.length);
  for (const line of lines) expect(line).toMatch(/ refused (os|js|urllib)/);
 });

 test(`${mode}: a program that pretends to be a module is still refused`, async ({page}) => {
  await open(page);
  const output = await run(page, '__name__ = "json"\n' + attempt('import os'));
  expect(output.trim()).toBe('import os refused os');
 });

 test(`${mode}: a module the browser does not have is still ModuleNotFoundError, for an allowed-looking name too`, async ({page}) => {
  await open(page);
  expect((await run(page, attempt('import turtle'))).trim()).toBe('import turtle refused turtle');
 });

 test(`${mode}: a way round the guard exists, as documented, and it still reaches no network`, async ({page}) => {
  await open(page);
  // Python cannot sandbox itself. This test records that honestly, and that the real boundary holds.
  const output = await run(page, `
import random
sys = random._os.sys
print(random._os.__name__)
js = sys.modules.get("js") or sys.modules["pyodide"].code.__dict__.get("js")
if js is None:
    print("no js module loaded")
else:
    print(js.fetch, js.XMLHttpRequest, js.WebSocket, js.importScripts)
`);
  const lines = output.trim().split('\n');
  expect(lines[0]).toBe('os');
  if (lines[1] !== 'no js module loaded') expect(lines[1]).toBe('None None None None');
 });
}

test('a check reports a refused import with its type and the line in the learner\'s code', async ({page}) => {
 await open(page);
 const [report] = await inCases(page, 'x = 1\n\nimport os\nprint(x)\n');
 expect(report).toMatchObject({status: 'error', errorType: 'ModuleNotFoundError', line: 3, output: ''});
});

test('Try it reports a refused import with a clear message', async ({page}) => {
 await open(page);
 const answer = await tryIt(page, 'import os\n');
 expect(answer.errorType).toBe('ModuleNotFoundError');
 expect(answer.error).toContain("The module 'os' is not available here.");
 expect(answer.error).toContain('line 1');
});

test('a function-call case still works with the guard on', async ({page}) => {
 await open(page);
 const [report] = await inCases(page, 'def double(n):\n    return n * 2\n', [{id: 'a', inputs: [], call: {function: 'double', args: [4]}}]);
 expect(report.status).toBe('ok');
 expect(report).toMatchObject({returned: '8'});
});

test('Pyodide\'s random gives what CPython gives, for a set seed and for no seed', async ({page}) => {
 await open(page);
 const [withSeed, noSeed] = await inCases(page, seeded.code, [{id: 'a', inputs: [], seed: seeded.seed}, {id: 'b', inputs: []}]);
 expect(withSeed.output).toBe(seeded.output);
 expect(noSeed.output).toBe(seeded.default_output);
});

test('every case starts again from its seed, even after another case used random', async ({page}) => {
 await open(page);
 const reports = await inCases(page, seeded.code, [{id: 'a', inputs: [], seed: 7}, {id: 'b', inputs: [], seed: 8}, {id: 'c', inputs: [], seed: 7}]);
 expect(reports[0].output).toBe(reports[2].output);
 expect(reports[0].output).not.toBe(reports[1].output);
});


test('the page\'s runner passes a seed from the plan to the worker', async ({page}) => {
 await open(page);
 const output = await page.evaluate(async code => {
  const {runCases} = await import(`${location.origin}/check-runner.js`);
  const plan = {time_limit_ms: 3000, output_limit: 10000, cases: [{id: 'a', visibility: 'visible', description: 'd', inputs: [], seed: 7}]};
  return (await runCases(code, plan))[0].output;
 }, seeded.code);
 expect(output).toBe(seeded.output);
});

test('Try it is not seeded, so a learner sees different numbers', async ({page}) => {
 await open(page);
 const code = 'import random\nprint([random.randint(1, 1000000) for _ in range(5)])\n';
 const [first, second] = [await tryIt(page, code), await tryIt(page, code)];
 expect(first.output).not.toBe(second.output);
});

test('the worker\'s Content-Security-Policy is unchanged', async ({request}) => {
 const answer = await request.get('/python-worker.js');
 expect(answer.headers()['content-security-policy']).toBe("default-src 'none'; script-src 'unsafe-eval' https://cdn.jsdelivr.net; connect-src https://cdn.jsdelivr.net");
});
