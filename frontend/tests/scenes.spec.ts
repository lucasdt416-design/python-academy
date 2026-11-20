import {test, expect, Page} from '@playwright/test';
import path from 'path';
// Lesson scenes (app/lesson-scenes.tsx) and units 4 to 11, end to end with real Pyodide. The API answers
// come from backend/tests/test_units_4_to_11_recordings.py, which proves they are the real API's, and
// the mock answers a check only when the browser's request is exactly the recorded one.
import recorded from './fixtures/units-4-11-api.json';
import goals from '../../backend/tests/fixtures/goals_v1.json';

type Entry = {reference: string; modules: Record<string, string>; request: unknown; response: {result: string}};
const LESSONS = recorded.lessons as unknown as Record<string, Entry>;
const UNITS = recorded.units as unknown as Record<string, {id: string; title: string; badge: string}[]>;
const ALL = Object.values(UNITS).flat();
const NEW = Object.keys(LESSONS);

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
  else if (unit) ({status, json} = UNITS[unit] ? {status: 200, json: UNITS[unit]} : {status: 404, json: {detail: 'Not Found'}});
  else if (plan) json = (recorded.plans as Record<string, unknown>)[plan];
  else if (where === '/api/check' || where === '/api/attempts') {
   const body = route.request().postDataJSON(); posted.push(body);
   const match = Object.values(LESSONS).find(e => JSON.stringify(e.request) === JSON.stringify(body));
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
async function playExample(page: Page, id: string) {
 await page.goto(`/preview?lesson=${id}&card=2`);
 await expect(page.locator('.unit-lesson.current')).toHaveAttribute('href', `/preview?lesson=${id}`);
 await scene(page).getByRole('button', {name: 'Run the example'}).click();
 await expect(scene(page).getByRole('button', {name: 'Run it again'})).toBeVisible({timeout: 45000});
}

// Every lesson has a scene, and its worked example draws one

test('every released lesson has its own scene title', async ({page}) => {
 await mockApi(page);
 const titles = new Map<string, string>();
 for (const lesson of ALL) {
  await page.goto(`/preview?lesson=${lesson.id}&card=2`);
  await expect(page.locator('.unit-lesson.current')).toHaveAttribute('href', `/preview?lesson=${lesson.id}`);
  titles.set(lesson.id, (await scene(page).locator('.scene-title').textContent()) ?? '');
 }
 expect(titles.size).toBe(52);
 // No two lessons share a scene: the same drawing thirty times is what this work replaces.
 expect(new Set(titles.values()).size).toBe(52);
});

for (const lesson of ALL) {
 test(`${lesson.title}: the worked example runs and its scene draws what happened`, async ({page}) => {
  await mockApi(page);
  await playExample(page, lesson.id);
  const art = scene(page).locator('svg.scene-art.live');
  await expect(art).toBeVisible();
  const caption = (await scene(page).locator('figcaption').textContent()) ?? '';
  expect(caption).not.toContain('Run the code to fill this scene');
  expect(caption).not.toContain("can't be drawn");
  // The picture's accessible name is the sentence under it.
  expect(await art.getAttribute('aria-label')).toBe(caption.replace(/ Python stopped with .*$/, ''));
  expect(await art.locator('*').count()).toBeGreaterThan(5);
 });
}

// Every new lesson's reference program passes in real Pyodide, exactly as recorded

for (const id of NEW) {
 test(`${id}: the reference program passes in the browser, and only the reports are sent`, async ({page}) => {
  const {posted} = await mockApi(page);
  const entry = LESSONS[id];
  await page.goto(`/preview?lesson=${id}&card=5`);
  for (const [name, code] of Object.entries(entry.modules)) {
   await page.getByRole('tab', {name}).click();
   await page.getByLabel(`Your Python code: ${name}`).fill(code);
  }
  if (Object.keys(entry.modules).length) await page.getByRole('tab', {name: 'main.py'}).click();
  await page.getByLabel('Your Python code', {exact: true}).fill(entry.reference);
  await page.getByRole('button', {name: 'Run & check challenge'}).click();
  await expect(page.locator('#code-feedback')).toContainText('Check passed', {timeout: 60000});
  expect(posted).toEqual([entry.request]);
  // The names a program made (the scene's snapshot) never leave the browser.
  expect(JSON.stringify(posted)).not.toContain('"vars"');
  await expect(scene(page).locator('svg.scene-art.live')).toBeVisible();
 });
}

// Scenes from a Try it run use the program's own names

test('Create your hero, Try it: the hero takes the name stored in hero', async ({page}) => {
 await mockApi(page);
 await page.goto('/preview?lesson=variables&card=4');
 await page.getByLabel('Your Python code').fill('hero = "Zephyr"\ntool = "rope"\nprint(hero)\nprint(tool)');
 await page.getByRole('button', {name: 'Run Python →'}).click();
 await expect(scene(page).locator('figcaption')).toHaveText('A hero named Zephyr appears, holding a rope.', {timeout: 45000});
 await expect(scene(page).locator('svg')).toContainText('Zephyr');
});

test('Pack the bag, Try it: a variable called list does not break the scene', async ({page}) => {
 await mockApi(page);
 await page.goto('/preview?lesson=py.lists&card=4');
 await page.getByLabel('Your Python code').fill('list = 3\ntype = 2\npack = ["rope", "map", "lamp"]\nprint("packed")');
 await page.getByRole('button', {name: 'Run Python →'}).click();
 await expect(scene(page).locator('figcaption')).toContainText('The pack holds 3 items: rope, map, lamp', {timeout: 45000});
});

test('a program that stops with an error still gets a scene, which says so', async ({page}) => {
 await mockApi(page);
 await page.goto('/preview?lesson=py.tracebacks&card=4');
 await page.getByLabel('Your Python code').fill('prices = ["5", "12"]\ntotal = 0\nfor price in prices:\n    total = total + price');
 await page.getByRole('button', {name: 'Run Python →'}).click();
 await expect(scene(page).locator('figcaption')).toContainText('Python stopped with TypeError on line 4', {timeout: 45000});
});

test('scenes do not move for people who ask for less motion', async ({page}) => {
 await page.emulateMedia({reducedMotion: 'reduce'});
 await mockApi(page);
 await playExample(page, 'variables');
 const names = await scene(page).locator('.pop, .drop, .slide, .type').evaluateAll(els => els.map(e => getComputedStyle(e).animationName));
 expect(names.length).toBeGreaterThan(0);
 expect(new Set(names)).toEqual(new Set(['none']));
});

test('with motion allowed, the same scene animates', async ({page}) => {
 await page.emulateMedia({reducedMotion: 'no-preference'});
 await mockApi(page);
 await playExample(page, 'variables');
 const names = await scene(page).locator('.pop').evaluateAll(els => els.map(e => getComputedStyle(e).animationName));
 expect(names).toContain('scene-pop');
});

// Accessibility of scene cards

test.describe('axe', () => {
 test.use({bypassCSP: true});
 const AXE = path.join(__dirname, '..', 'node_modules', 'axe-core', 'axe.min.js');
 for (const size of [{name: 'desktop', width: 1280, height: 900}, {name: 'phone', width: 375, height: 812}]) {
  for (const id of ['hello', 'py.lists', 'py.functions', 'py.csv', 'py.classes']) {
   test(`${id} worked example with its scene, ${size.name}: no WCAG A or AA findings`, async ({page}) => {
    await page.setViewportSize(size);
    await mockApi(page);
    await playExample(page, id);
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
 }
});
