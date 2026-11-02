import {test, expect, Page} from '@playwright/test';
// TEST FIXTURE, never shown to learners: the one lesson with a browser behaviour check (ENG-03).
import fixture from '../../backend/tests/fixtures/browser_checks/fixture/u01/fixture.sum-two.json';

type Report = {id:string;status:string;output:string;errorType:string|null;line:number|null;message:string|null};
const check = (fixture.tasks[4] as unknown as {check:{time_limit_ms:number;cases:{id:string;inputs:string[];expected:string}[]}}).check;
// What GET /api/checks/fixture.sum-two serves (the backend tests check that endpoint); the expected
// output of hidden cases is never in it, so the runner never sees it either.
const plan = {time_limit_ms: check.time_limit_ms, output_limit: 10000, cases: check.cases.map(({id, inputs}) => ({id, inputs}))};
const expected = Object.fromEntries(check.cases.map(c => [c.id, c.expected]));

// Like academy.spec.ts: any Content-Security-Policy report fails the test.
const violations = new WeakMap<Page, string[]>();
test.beforeEach(async ({page}) => {
 const found: string[] = []; violations.set(page, found);
 await page.exposeFunction('reportCspViolation', (v: string) => found.push(v));
 await page.addInitScript(() => document.addEventListener('securitypolicyviolation', e => (window as unknown as {reportCspViolation:(v:string)=>void}).reportCspViolation(`${e.effectiveDirective} blocked ${e.blockedURI || 'inline'}`)));
 // A real app page, with the real page and worker policies. It makes no API requests.
 await page.goto('/no-such-page');
});
test.afterEach(async ({page}) => { expect(violations.get(page)).toEqual([]); });

async function run(page: Page, code: string, overrides: Partial<typeof plan> = {}): Promise<{reports:Report[];ms:number}> {
 return page.evaluate(async ({code, plan}) => {
  const runner = await import('/check-runner.js' as string);
  const start = performance.now();
  const reports = await runner.runCases(code, plan);
  return {reports, ms: performance.now() - start};
 }, {code, plan: {...plan, ...overrides}});
}

test('a correct solution prints the expected output for every case, hidden ones included', async ({page}) => {
 const {reports} = await run(page, 'a = int(input("First? "))\nb = int(input("Second? "))\nprint(a + b)');
 expect(reports.map(r => [r.id, r.status, r.output.trim()])).toEqual(check.cases.map(c => [c.id, 'ok', expected[c.id]]));
});

test('a wrong solution runs, and its output differs from the expected output', async ({page}) => {
 // The API turns this into needs_work with the first different line (backend tests cover the message).
 const {reports} = await run(page, 'a = int(input())\nb = int(input())\nprint(a - b)');
 expect(reports.map(r => r.status)).toEqual(['ok', 'ok', 'ok']);
 expect(reports.map(r => r.output.trim())).toEqual(['-1', '14', '2048']);
});

test('an endless loop is stopped at the time limit and the later cases are not run', async ({page}) => {
 const {reports, ms} = await run(page, 'while True:\n    pass', {time_limit_ms: 1000});
 expect(reports.map(r => r.status)).toEqual(['timeout', 'not_run', 'not_run']);
 expect(ms).toBeLessThan(30000);
 // The page is still responsive and a fresh worker runs normally afterwards.
 const again = await run(page, 'print(int(input()) + int(input()))');
 expect(again.reports.map(r => r.status)).toEqual(['ok', 'ok', 'ok']);
});

test('runaway output is capped and the program stopped', async ({page}) => {
 const {reports} = await run(page, 'while True:\n    print("x" * 100)');
 expect(reports[0].status).toBe('output_limit');
 expect(reports[0].output.length).toBeLessThanOrEqual(10000);
 expect(reports[0].output.length).toBeGreaterThan(9000);
 // Each case starts fresh, so every case hits the cap on its own.
 expect(reports.map(r => r.status)).toEqual(['output_limit', 'output_limit', 'output_limit']);
});

test('output left over from a case stopped at the cap does not leak into the next case', async ({page}) => {
 // Found in EDU-03 part 1: the next case's output began with text the capped case had not flushed.
 const {reports} = await run(page, 'a = int(input())\nif a == 2:\n    while True:\n        print("x")\nprint("clean", a)');
 expect(reports.map(r => r.status)).toEqual(['output_limit', 'ok', 'ok']);
 expect(reports.slice(1).map(r => r.output)).toEqual(['clean 10\n', 'clean 4096\n']);
});

test('output with no final newline is still reported', async ({page}) => {
 const {reports} = await run(page, 'print(int(input()) + int(input()), end="")');
 expect(reports.map(r => r.output.trim())).toEqual(['5', '6', '6144']);
});

test('errors report their type and line for the feedback engine, and the message stays in the browser', async ({page}) => {
 const {reports} = await run(page, 'a = int(input())\nprint(a + missing)');
 expect(reports[0]).toMatchObject({status: 'error', errorType: 'NameError', line: 2});
 expect(reports[0].message).toContain("name 'missing' is not defined");
 const submitted = await page.evaluate(async reports => (await import('/check-runner.js' as string)).forSubmission(reports), reports);
 expect(Object.keys(submitted[0]).sort()).toEqual(['error_type', 'id', 'line', 'output', 'status']);
});

test('a syntax error and a missing reply are reported as errors with their type', async ({page}) => {
 const syntax = await run(page, 'print("unclosed)');
 expect(syntax.reports[0]).toMatchObject({status: 'error', errorType: 'SyntaxError', line: 1});
 const replies = await run(page, 'input()\ninput()\ninput()');
 expect(replies.reports[0]).toMatchObject({status: 'error', errorType: 'EOFError', line: 3});
});

test('learner code cannot reach the network', async ({page}) => {
 const attempts = [
  'import js\njs.fetch("https://cdn.jsdelivr.net/pyodide/v0.27.7/full/pyodide.js")',
  'import js\njs.XMLHttpRequest.new()',
  'import js\njs.importScripts("https://cdn.jsdelivr.net/pyodide/v0.27.7/full/pyodide.js")',
  'from pyodide.http import open_url\nopen_url("https://cdn.jsdelivr.net/pyodide/v0.27.7/full/pyodide.js")',
 ];
 for (const code of attempts) {
  const {reports} = await run(page, code);
  expect(reports[0].status, code).toBe('error');
 }
});

test('each case starts with fresh variables', async ({page}) => {
 // A value left over from an earlier case must not leak into the next one.
 const {reports} = await run(page, 'try:\n    seen\n    print("leaked")\nexcept NameError:\n    seen = 1\n    print(int(input()) + int(input()))');
 expect(reports.map(r => r.output.trim())).toEqual(['5', '6', '6144']);
});
