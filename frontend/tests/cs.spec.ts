import {test, expect, Page} from '@playwright/test';
import path from 'path';
// Computer Science Foundations, units 1 and 3, end to end with real Pyodide. The API answers come from
// backend/tests/test_cs_recordings.py, which proves they are the real API's; the mock answers a check only
// when the browser's request is exactly the recorded one.
import recorded from './fixtures/cs-api.json';
import goals from '../../backend/tests/fixtures/goals_v1.json';

type Entry = {reference: string; request: unknown; response: {result: string}};
const LESSONS = recorded.lessons as unknown as Record<string, Entry>;
const UNITS = recorded.units as unknown as Record<string, {id: string; title: string}[]>;
const ALL = Object.values(UNITS).flat();

async function mockApi(page: Page) {
 const posted: Record<string, unknown>[] = [];
 await page.route('**/api/**', async route => {
  const where = new URL(route.request().url()).pathname;
  let status = 200, json: unknown = {};
  const unit = /^\/api\/units\/([^/]+)\/lessons$/.exec(where)?.[1], plan = /^\/api\/checks\/(.+)$/.exec(where)?.[1];
  if (where === '/api/catalog') json = recorded.catalog;
  else if (where === '/api/me') { status = 401; json = {detail: 'Sign in to continue'}; }
  else if (where === '/api/goals') json = goals;
  else if (where === '/api/goal') json = {goal: 'scratch', chosen: true, asked: true};
  else if (where === '/api/progress' || where === '/api/history' || where === '/api/family') json = [];
  else if (where === '/api/insights') json = {insights: []};
  else if (unit) ({status, json} = UNITS[unit] ? {status: 200, json: UNITS[unit]} : {status: 404, json: {detail: 'Not Found'}});
  else if (plan) json = (recorded.plans as Record<string, unknown>)[plan];
  else if (where === '/api/check' || where === '/api/attempts') {
   const body = route.request().postDataJSON(); posted.push(body);
   const match = [...Object.values(LESSONS), recorded.wrong].find(e => JSON.stringify(e.request) === JSON.stringify(body));
   ({status = 200, json} = match ? {json: match.response} : {status: 500, json: {detail: 'not a recorded request'}});
  }
  await route.fulfill({status, contentType: 'application/json', body: JSON.stringify(json)});
 });
 return {posted};
}
const violations = new WeakMap<Page, string[]>();
test.beforeEach(async ({page}) => {
 const found: string[] = []; violations.set(page, found);
 page.on('pageerror', e => found.push(`page error: ${e.message}`));
 await page.exposeFunction('reportCspViolation', (v: string) => found.push(v));
 await page.addInitScript(() => document.addEventListener('securitypolicyviolation', e => (window as unknown as {reportCspViolation: (v: string) => void}).reportCspViolation(`${e.effectiveDirective} blocked ${e.blockedURI || 'inline'}`)));
});
test.afterEach(async ({page}) => { expect(violations.get(page)).toEqual([]); });

const scene = (page: Page) => page.locator('figure.scene');
const caption = (page: Page) => scene(page).locator('figcaption');

test('the catalog opens Computer Science Foundations, with units 1 and 3 and the rest on the way', async ({page}) => {
 await mockApi(page);
 await page.goto('/courses/cs');
 await expect(page.getByRole('heading', {level: 1, name: /Computer Science Foundations/})).toBeVisible();
 await expect(page.getByText('How data is stored')).toBeVisible();
 await expect(page.getByText('Searching', {exact: true})).toBeVisible();
 await expect(page.getByText('Sorting', {exact: true})).toBeVisible();
});

test('every CS lesson has its own scene title', async ({page}) => {
 await mockApi(page);
 const titles = new Set<string>();
 for (const lesson of ALL) {
  await page.goto(`/preview?lesson=${lesson.id}&card=2`);
  await expect(page.locator('.unit-lesson.current')).toHaveAttribute('href', `/preview?lesson=${lesson.id}`);
  titles.add((await scene(page).locator('.scene-title').textContent()) ?? '');
 }
 expect(titles.size).toBe(ALL.length);
});

// What each worked example's scene says, worked out by hand from the example.
const SAYS: Record<string, string> = {
 'cs.binary': '1101 lights 8 + 4 + 1, which is 13.',
 'cs.hexadecimal': 'The flag is #ff8800: red 255 (ff), green 136 (88), blue 0 (00).',
 'cs.text-encoding': '"café" is 4 characters and 5 bytes in UTF-8',
 'cs.float-limits': 'One line has the tiny error of a float that is not exact.',
 'cs.linear-search': '3 looks along a shelf of 4 items: found at position 2.',
 'cs.binary-search': 'Looked at 21, then 42: found in 2 looks, out of 7 items.',
 'cs.counting-steps': '1 item: 1 look one by one, 1 look by halving; 2 items',
};
for (const lesson of ALL) {
 test(`${lesson.title}: the worked example's scene draws what happened`, async ({page}) => {
  await mockApi(page);
  await page.goto(`/preview?lesson=${lesson.id}&card=2`);
  await scene(page).getByRole('button', {name: 'Run the example'}).click();
  await expect(caption(page)).toContainText(SAYS[lesson.id], {timeout: 45000});
  const art = scene(page).locator('svg.scene-art.live');
  expect(await art.getAttribute('aria-label')).toBe(await caption(page).textContent());
 });
}

for (const id of Object.keys(LESSONS)) {
 test(`${id}: the reference program passes in the browser, and its checked call is drawn`, async ({page}) => {
  const {posted} = await mockApi(page);
  await page.goto(`/preview?lesson=${id}&card=5`);
  await page.getByLabel('Your Python code', {exact: true}).fill(LESSONS[id].reference);
  await page.getByRole('button', {name: 'Run & check challenge'}).click();
  await expect(page.locator('#code-feedback')).toContainText('Check passed', {timeout: 60000});
  expect(posted).toEqual([LESSONS[id].request]);
  await expect(caption(page)).not.toContainText('Run the code to fill this scene');
  await expect(caption(page)).not.toContainText("can't be drawn");
 });
}

test('a linear search handed in as a binary search: the scene shows the halving it should have done', async ({page}) => {
 await mockApi(page);
 await page.goto('/preview?lesson=cs.binary-search&card=5');
 await page.getByLabel('Your Python code', {exact: true}).fill(recorded.wrong.code);
 await page.getByRole('button', {name: 'Run & check challenge'}).click();
 await expect(page.locator('#code-feedback')).toContainText('it returned [5, 6]', {timeout: 60000});
 await expect(caption(page)).toContainText('Your function returned [5, 6], but halving finds 5 in 2 looks.');
});

test('Try it: a shifted message is drawn letter by letter', async ({page}) => {
 await mockApi(page);
 await page.goto('/preview?lesson=cs.text-encoding&card=4');
 await page.getByLabel('Your Python code').fill('message = "hi"\nprint(chr(ord("h") + 1))');
 await page.getByRole('button', {name: 'Run Python →'}).click();
 await expect(caption(page)).toContainText('"hi" is 2 characters and 2 bytes in UTF-8: h is 104, i is 105.', {timeout: 45000});
});

test('Try it: a red amount too big for a byte is said, not hidden', async ({page}) => {
 await mockApi(page);
 await page.goto('/preview?lesson=cs.hexadecimal&card=4');
 await page.getByLabel('Your Python code').fill('red = 300\ngreen = 0\nblue = 255\nprint(red, green, blue)');
 await page.getByRole('button', {name: 'Run Python →'}).click();
 await expect(caption(page)).toContainText('300 cannot fit in one byte', {timeout: 45000});
});

test.describe('axe', () => {
 test.use({bypassCSP: true});
 const AXE = path.join(__dirname, '..', 'node_modules', 'axe-core', 'axe.min.js');
 for (const size of [{name: 'desktop', width: 1280, height: 900}, {name: 'phone', width: 375, height: 812}]) {
  test(`a CS scene, drawn, ${size.name}: no WCAG A or AA findings, no sideways scroll`, async ({page}) => {
   await page.setViewportSize(size);
   await mockApi(page);
   await page.goto('/preview?lesson=cs.binary-search&card=2');
   await scene(page).getByRole('button', {name: 'Run the example'}).click();
   await expect(caption(page)).toContainText('found in 2 looks', {timeout: 45000});
   await page.addScriptTag({path: AXE});
   const found = await page.evaluate(async () => {
    const axe = (window as unknown as {axe: {run: (c: Document, o: object) => Promise<{violations: {id: string; nodes: {target: string[]}[]}[]}>}}).axe;
    const result = await axe.run(document, {runOnly: {type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa']}});
    return result.violations.map(v => `${v.id}: ${v.nodes.slice(0, 3).map(n => n.target.join(' ')).join(', ')}`);
   });
   expect(found).toEqual([]);
   expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  });
 }
});
