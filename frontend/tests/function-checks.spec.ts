import {test, expect, Page} from '@playwright/test';
// The API's real answers for the TEST FIXTURE lesson (backend/tests/fixtures/function_checks/), checked
// against the API by backend/tests/test_function_checks.py. Python runs for real in Pyodide here.
import recorded from './fixtures/function-checks-api.json';

/* ENG-06: a check can call a function the learner defined. docs/plan/browser-checks.md section 8. */

type Report = {id:string;status:string;output:string;errorType:string|null;line:number|null;message:string|null;returned?:string;shown?:string};
type Call = {function:string;args?:unknown[];kwargs?:Record<string,unknown>};
const scenario = (name: string) => recorded.scenarios.find(s => s.name === name)!;
const LESSON = 'fixture.calls';

const violations = new WeakMap<Page, string[]>();
test.beforeEach(async ({page}) => {
 const found: string[] = []; violations.set(page, found);
 await page.exposeFunction('reportCspViolation', (v: string) => found.push(v));
 await page.addInitScript(() => document.addEventListener('securitypolicyviolation', e => (window as unknown as {reportCspViolation: (v: string) => void}).reportCspViolation(`${e.effectiveDirective} blocked ${e.blockedURI || 'inline'}`)));
});
test.afterEach(async ({page}) => { expect(violations.get(page)).toEqual([]); });

// The worker and the runner, with no API

async function run(page: Page, code: string, call: Call, {inputs = [] as string[], time_limit_ms = 3000} = {}): Promise<{report: Report; ms: number}> {
 await page.goto('/no-such-page');
 return page.evaluate(async ({code, call, inputs, time_limit_ms}) => {
  const runner = await import('/check-runner.js' as string);
  const start = performance.now();
  const reports = await runner.runCases(code, {time_limit_ms, output_limit: 10000, cases: [{id: 'c', inputs, call}]});
  return {report: reports[0], ms: performance.now() - start};
 }, {code, call, inputs, time_limit_ms});
}

const DOUBLE = {function: 'double', args: [2]};

test('a correct function reports its value, and it can be sent', async ({page}) => {
 const {report} = await run(page, 'def double(n):\n    return n * 2', DOUBLE);
 expect(report).toMatchObject({status: 'ok', returned: '4', shown: '4', output: ''});
 const sent = await page.evaluate(async r => (await import('/check-runner.js' as string)).forSubmission([r]), report);
 expect(sent).toEqual([{id: 'c', status: 'ok', output: '', error_type: null, line: null, returned: '4'}]);
});

test('a wrong function reports the wrong value', async ({page}) => {
 expect((await run(page, 'def double(n):\n    return n + 1', DOUBLE)).report).toMatchObject({status: 'ok', returned: '3'});
});

test('printing instead of returning reports None and the output', async ({page}) => {
 expect((await run(page, 'def double(n):\n    print(n * 2)', DOUBLE)).report).toMatchObject({status: 'ok', returned: 'null', shown: 'None', output: '4\n'});
});

test('only what the call prints is reported, not what the program printed first', async ({page}) => {
 const {report} = await run(page, 'print("the program starts")\ndef double(n):\n    print("in the call")\n    return n * 2\nprint(double(10))', DOUBLE);
 expect(report).toMatchObject({status: 'ok', returned: '4', output: 'in the call\n'});
});

test('a missing function, or the wrong name, is reported as no_function', async ({page}) => {
 expect((await run(page, 'x = 1', DOUBLE)).report.status).toBe('no_function');
 expect((await run(page, 'def twice(n):\n    return n * 2', DOUBLE)).report.status).toBe('no_function');
 expect((await run(page, 'double = 5', DOUBLE)).report.status).toBe('no_function');
});

test('the wrong number of parameters is reported as bad_signature', async ({page}) => {
 expect((await run(page, 'def double():\n    return 4', DOUBLE)).report.status).toBe('bad_signature');
 expect((await run(page, 'def double(a, b):\n    return 4', DOUBLE)).report.status).toBe('bad_signature');
});

test('every way of accepting the arguments is accepted', async ({page}) => {
 for (const code of ['def double(n, times=2):\n    return n * times', 'def double(*numbers):\n    return numbers[0] * 2', 'double = lambda n: n * 2', 'class Maker:\n    def __call__(self, n):\n        return n * 2\ndouble = Maker()'])
  expect((await run(page, code, DOUBLE)).report, code).toMatchObject({status: 'ok', returned: '4'});
});

test('keyword arguments and defaults reach the function', async ({page}) => {
 const {report} = await run(page, 'def scene(name, place="cave"):\n    return name + " in " + place', {function: 'scene', args: ['Kai'], kwargs: {place: 'Mars'}});
 expect(report.returned).toBe('"Kai in Mars"');
});

test('an exception inside the function reports its type and line, and the message stays in the browser', async ({page}) => {
 const {report} = await run(page, 'def double(n):\n    return n + missing', DOUBLE);
 expect(report).toMatchObject({status: 'error', errorType: 'NameError', line: 2});
 expect(report.message).toContain("name 'missing' is not defined");
 const sent = await page.evaluate(async r => (await import('/check-runner.js' as string)).forSubmission([r]), report);
 expect(Object.keys(sent[0]).sort()).toEqual(['error_type', 'id', 'line', 'output', 'status']);
});

test('an error before the function is reached is reported as a Python error', async ({page}) => {
 expect((await run(page, 'print(missing)\ndef double(n):\n    return 4', DOUBLE)).report).toMatchObject({status: 'error', errorType: 'NameError', line: 1});
});

test('an endless loop inside the function is stopped at the time limit', async ({page}) => {
 const {report, ms} = await run(page, 'def double(n):\n    while True:\n        pass', DOUBLE, {time_limit_ms: 1000});
 expect(report.status).toBe('timeout');
 expect(ms).toBeLessThan(30000);
});

test('runaway output inside the function is stopped at the limit', async ({page}) => {
 const {report} = await run(page, 'def double(n):\n    while True:\n        print("x" * 100)', DOUBLE);
 expect(report.status).toBe('output_limit');
 expect(report.output.length).toBeLessThanOrEqual(10000);
});

test('a tuple is reported as a list, so returning several values compares simply', async ({page}) => {
 expect((await run(page, 'def f():\n    return 1, "a", None, True', {function: 'f'})).report).toMatchObject({status: 'ok', returned: '[1, "a", null, true]', shown: "(1, 'a', None, True)"});
});

test('a float, a dictionary and big numbers are reported as they are', async ({page}) => {
 expect((await run(page, 'def f():\n    return 0.1 + 0.2', {function: 'f'})).report.returned).toBe('0.30000000000000004');
 expect((await run(page, 'def f():\n    return {"a": [1, 2]}', {function: 'f'})).report.returned).toBe('{"a": [1, 2]}');
 expect((await run(page, 'def f():\n    return 2 ** 70', {function: 'f'})).report.returned).toBe('1180591620717411303424');
});

test('a value the check cannot compare names its type and never breaks the run', async ({page}) => {
 const cases: [string, string][] = [
  ['def f():\n    return {1, 2}', 'set'],
  ['def f():\n    return {1: "a"}', 'dict'],
  ['def f():\n    return float("nan")', 'float'],
  ['def f():\n    return float("inf")', 'float'],
  ['class Hero:\n    pass\ndef f():\n    return Hero()', 'Hero'],
  ['class Pack(list):\n    pass\ndef f():\n    return Pack()', 'Pack'],
  ['class Éa:\n    pass\ndef f():\n    return Éa()', 'unknown'],
  ['def f():\n    x = []\n    x.append(x)\n    return x', 'list'],
  ['def f():\n    return "x" * 20000', 'str'],
  ['def f():\n    yield 1', 'generator'],
  ['def f():\n    return f', 'function'],
 ];
 for (const [code, type] of cases) expect((await run(page, code, {function: 'f'})).report, code).toMatchObject({status: 'not_comparable', errorType: type});
});

test('replies are shared by the program and the call', async ({page}) => {
 const {report} = await run(page, 'first = input()\ndef f():\n    return first + input()', {function: 'f'}, {inputs: ['a', 'b']});
 expect(report).toMatchObject({status: 'ok', returned: '"ab"'});
});

test('changing an argument in one case does not reach the next', async ({page}) => {
 await page.goto('/no-such-page');
 const reports: Report[] = await page.evaluate(async () => {
  const runner = await import('/check-runner.js' as string);
  const call = {function: 'f', args: [[1]]};
  return runner.runCases('def f(items):\n    items.append(2)\n    return items', {time_limit_ms: 3000, output_limit: 10000, cases: [{id: 'a', inputs: [], call}, {id: 'b', inputs: [], call}]});
 });
 expect(reports.map(r => r.returned)).toEqual(['[1, 2]', '[1, 2]']);
});

test('calls and ordinary cases can run side by side, and an ordinary case reports nothing new', async ({page}) => {
 await page.goto('/no-such-page');
 const reports: Report[] = await page.evaluate(async () => {
  const runner = await import('/check-runner.js' as string);
  const plan = {time_limit_ms: 3000, output_limit: 10000, cases: [{id: 'plain', inputs: []}, {id: 'called', inputs: [], call: {function: 'f'}}]};
  return runner.runCases('print("hi")\ndef f():\n    return 1', plan);
 });
 expect(Object.keys(reports[0]).sort()).toEqual(['errorType', 'id', 'line', 'message', 'output', 'status']);
 expect(reports[0].output).toBe('hi\n');
 expect(reports[1]).toMatchObject({returned: '1', output: ''});
});

test('learner code in a called function cannot reach the network', async ({page}) => {
 const {report} = await run(page, 'def f():\n    import js\n    js.fetch("https://cdn.jsdelivr.net/pyodide/v0.27.7/full/pyodide.js")', {function: 'f'});
 expect(report.status).toBe('error');
});

// The lesson page, with the API's recorded answers

async function mockApi(page: Page) {
 const posted: unknown[] = [];
 await page.route('**/api/**', async route => {
  const path = new URL(route.request().url()).pathname;
  let status = 200, json: unknown = {};
  if (path === '/api/catalog') json = recorded.catalog;
  else if (path.startsWith('/api/units/')) json = recorded.units['fixture.u09'];
  else if (path === `/api/checks/${LESSON}`) json = recorded.plans[LESSON];
  else if (path === '/api/check') {
   const body = route.request().postDataJSON(); posted.push(body);
   const match = recorded.scenarios.find(s => JSON.stringify(s.request) === JSON.stringify(body));
   if (match) json = match.response; else { status = 500; json = {detail: 'not a recorded request'}; }
  }
  await route.fulfill({status, contentType: 'application/json', body: JSON.stringify(json)});
 });
 return posted;
}

async function runOnPage(page: Page, name: string) {
 const posted = await mockApi(page);
 const s = scenario(name);
 await page.goto(`/preview?lesson=${LESSON}&card=5`);
 await page.getByLabel('Your Python code').fill(s.request.code);
 await page.getByRole('button', {name: 'Run & check challenge'}).click();
 await expect(page.getByRole('button', {name: 'Run & check challenge'})).toBeEnabled({timeout: 45000});
 expect(posted).toEqual([s.request]);
 return page.locator('#code-feedback');
}

test('on the page: correct functions pass, and the output shows what each returned', async ({page}) => {
 const result = await runOnPage(page, 'passed');
 await expect(result).toContainText('Check passed');
 await expect(page.getByText('Returned: 4', {exact: false})).toBeVisible();
});

test('on the page: a wrong return says both values and offers the hint tagged for that case', async ({page}) => {
 const result = await runOnPage(page, 'wrong return');
 await expect(result).toContainText('For double(2), your function should return 4, but it returned 3.');
 await page.getByRole('button', {name: 'Show a hint about this check'}).click();
 await expect(page.getByText('Look at what double hands back when it is called.')).toBeVisible();
});

test('on the page: printing instead of returning is explained', async ({page}) => {
 await expect(await runOnPage(page, 'printed instead')).toContainText('printing shows a value, and return hands it back');
});

test('on the page: a missing function says what to define', async ({page}) => {
 await expect(await runOnPage(page, 'no function')).toContainText('Your program should define a function called double that takes 1 argument.');
});

test('on the page: the wrong parameters say what to define', async ({page}) => {
 await expect(await runOnPage(page, 'wrong parameters')).toContainText('Your program should define a function called double that takes 1 argument.');
});

test('on the page: an exception in the function is explained, with its line marked', async ({page}) => {
 const result = await runOnPage(page, 'exception');
 await expect(result).toContainText('Python stopped');
 await expect(result).toContainText('Python does not know missing');
 await expect(page.getByRole('button', {name: 'Go to line 2'})).toBeVisible();
});

test('on the page: an endless loop in the function is stopped at 3 seconds', async ({page}) => {
 test.setTimeout(90000);
 const start = Date.now();
 const result = await runOnPage(page, 'endless');
 await expect(result).toContainText('3 seconds');
 expect(Date.now() - start).toBeLessThan(60000);
});

test('on the page: a value the check cannot compare is named', async ({page}) => {
 await expect(await runOnPage(page, 'not comparable')).toContainText('a value this check cannot compare (set)');
});
