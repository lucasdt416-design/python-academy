import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {test, expect, Page} from '@playwright/test';

/* SEC-05: Pyodide is pinned, and every file it starts from is checked against a SHA-256 hash in
 * public/python-worker.js before it is used. browser-checks.md section 13. Python is real here. */

const WORKER = fs.readFileSync(path.join(__dirname, '..', 'public', 'python-worker.js'), 'utf8');
const BASE = WORKER.match(/const PYODIDE = '([^']+)'/)![1];
const PINNED: Record<string, string> = Object.fromEntries([...WORKER.matchAll(/ '([\w.-]+)': '([0-9a-f]{64})'/g)].map(m => [m[1], m[2]]));

async function once(page: Page, code: string) {
 await page.goto('/no-such-page');
 return page.evaluate(code => new Promise<Record<string, unknown>>(resolve => {
  const worker = new Worker('/python-worker.js');
  worker.onmessage = ({data}) => { worker.terminate(); resolve(data); };
  worker.postMessage({code, inputs: [], files: {}, modules: {}});
 }), code);
}
async function cases(page: Page, code: string) {
 await page.goto('/no-such-page');
 return page.evaluate(async code => {
  const runner = await import('/check-runner.js' as string);
  return runner.runCases(code, {time_limit_ms: 3000, output_limit: 10000, cases: [{id: 'a', inputs: []}]});
 }, code);
}

test('the pin covers the five files Pyodide starts from, at one version', () => {
 expect(BASE).toBe('https://cdn.jsdelivr.net/pyodide/v0.27.7/full/');
 expect(Object.keys(PINNED).sort()).toEqual(['pyodide-lock.json', 'pyodide.asm.js', 'pyodide.asm.wasm', 'pyodide.js', 'python_stdlib.zip']);
});

test('every pinned hash matches the file the CDN serves today', async ({request}) => {
 test.setTimeout(120000);
 for (const [name, hash] of Object.entries(PINNED)) {
  const answer = await request.get(BASE + name);
  expect(answer.ok()).toBe(true);
  expect([name, crypto.createHash('sha256').update(await answer.body()).digest('hex')]).toEqual([name, hash]);
 }
});

test('a run fetches only the pinned files, and Python works', async ({page}) => {
 const fetched: string[] = [];
 page.on('request', r => { if (r.url().startsWith('https://cdn.jsdelivr.net/')) fetched.push(r.url().slice(BASE.length)); });
 expect((await once(page, 'import math\nprint(math.floor(2.5))')).output).toBe('2\n');
 expect(fetched.sort()).toEqual(Object.keys(PINNED).sort());
});

for (const name of ['pyodide.js', 'pyodide.asm.js', 'pyodide.asm.wasm', 'python_stdlib.zip', 'pyodide-lock.json']) {
 test(`a changed ${name} is never used: Python is unavailable, in a check and in Try it`, async ({page}) => {
  await page.route(BASE + name, async route => {
   const original = await route.fetch();
   const body = Buffer.from(await original.body());
   body[body.length - 1] ^= 1;
   await route.fulfill({response: original, body});
  });
  const [report] = await cases(page, 'print("ran")');
  expect(report.status).toBe('unavailable');
  const result = await once(page, 'print("ran")');
  expect(result.output).toBe('');
  expect(String(result.error)).toContain('does not match its pinned hash');
 });
}

test('a file the CDN cannot serve is unavailable too, not a crash', async ({page}) => {
 await page.route(BASE + 'python_stdlib.zip', route => route.fulfill({status: 503, body: ''}));
 const [report] = await cases(page, 'print("ran")');
 expect(report.status).toBe('unavailable');
});

test('once Python has loaded, the worker keeps no way to fetch for learner code to find', async ({page}) => {
 // The guard is not a sandbox (section 9), so this goes round it on purpose to reach JavaScript.
 const code = 'import random\njs = __import__("js", vars(random))\nprint(js.eval("[typeof fetch, typeof realFetch === \\"function\\", typeof importScripts].join(\\" \\")"))';
 const [report] = await cases(page, code);
 expect([report.status, report.output]).toEqual(['ok', 'undefined false undefined\n']);
});

test('the worker\'s policy allows no scripts from anywhere, only connections to the CDN', async ({request}) => {
 const answer = await request.get('/python-worker.js');
 expect(answer.headers()['content-security-policy']).toBe("default-src 'none'; script-src 'unsafe-eval'; connect-src https://cdn.jsdelivr.net");
});
