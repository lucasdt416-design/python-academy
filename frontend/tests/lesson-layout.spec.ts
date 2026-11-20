import {test, expect, Page} from '@playwright/test';
// The lesson page rules (docs/plan/lesson-page-rules.md, L1 to L6), checked on every released lesson with
// real Pyodide. The API answers are the recorded ones (units-4-11-api.json, cs-api.json).
import py from './fixtures/units-4-11-api.json';
import cs from './fixtures/cs-api.json';
import goals from '../../backend/tests/fixtures/goals_v1.json';

const UNITS = {...py.units, ...cs.units} as unknown as Record<string, {id: string; title: string}[]>;
const PLANS = {...py.plans, ...cs.plans} as Record<string, unknown>;
const LESSONS = Object.values(UNITS).flat();

async function mockApi(page: Page) {
 await page.route('**/api/**', async route => {
  const where = new URL(route.request().url()).pathname;
  let status = 200, json: unknown = [];
  const unit = /^\/api\/units\/([^/]+)\/lessons$/.exec(where)?.[1], plan = /^\/api\/checks\/(.+)$/.exec(where)?.[1];
  if (where === '/api/catalog') json = cs.catalog;
  else if (where === '/api/me') { status = 401; json = {detail: 'Sign in to continue'}; }
  else if (where === '/api/goals') json = goals;
  else if (where === '/api/goal') json = {goal: 'scratch', chosen: true, asked: true};
  else if (unit) ({status, json} = UNITS[unit] ? {status: 200, json: UNITS[unit]} : {status: 404, json: {detail: 'Not Found'}});
  else if (plan) ({status, json} = PLANS[plan] ? {status: 200, json: PLANS[plan]} : {status: 404, json: {detail: 'Not Found'}});
  await route.fulfill({status, contentType: 'application/json', body: JSON.stringify(json)});
 });
}

/** Scene labels that are clipped by the frame or smaller than 9 px on screen. */
async function badLabels(page: Page) {
 return page.locator('.see-scene svg.scene-art').evaluate(svg => {
  const frame = svg.getBoundingClientRect(), scale = frame.width / 320, bad: string[] = [];
  for (const t of Array.from(svg.querySelectorAll('text'))) {
   const text = (t.textContent ?? '').trim();
   if (!text || t.closest('.scene-note')) continue;
   const r = t.getBoundingClientRect(), size = Number(t.getAttribute('font-size') ?? getComputedStyle(t).fontSize.replace('px', '')) * scale;
   if (size < 9) bad.push(`"${text}" is ${size.toFixed(1)}px`);
   if (r.width && (r.left < frame.left - 1 || r.right > frame.right + 1 || r.top < frame.top - 1 || r.bottom > frame.bottom + 1)) bad.push(`"${text}" runs outside the frame`);
  }
  return bad;
 });
}

for (const lesson of LESSONS) {
 test(`${lesson.id}: the worked example and its scene follow the page rules`, async ({page}) => {
  await mockApi(page);
  await page.setViewportSize({width: 1280, height: 900});
  await page.goto(`/preview?lesson=${lesson.id}&card=2`);
  await page.getByRole('button', {name: 'Run the example'}).click();
  await expect(page.getByRole('button', {name: 'Run it again'})).toBeVisible({timeout: 60000});
  // L1: the picture of the run sits beside what the run printed.
  const code = await page.locator('.see-code').boundingBox(), scene = await page.locator('.see-scene').boundingBox();
  expect(Math.abs(code!.y - scene!.y), 'scene and output share a row').toBeLessThan(40);
  expect(scene!.x).toBeGreaterThan(code!.x + code!.width - 1);
  // L2: every label in the scene is inside its frame and big enough to read.
  expect(await badLabels(page)).toEqual([]);
  // L3: nothing scrolls sideways. L4: no placeholder picture.
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  await expect(page.locator('svg.art[data-art="fallback"]')).toHaveCount(0);
 });
}

test('L5: on the challenge, the task, what counts as done and the hints sit together, and each case reads on one line', async ({page}) => {
 await mockApi(page);
 await page.setViewportSize({width: 1280, height: 900});
 await page.goto('/preview?lesson=py.lists&card=5');
 const teaching = page.locator('.teaching-panel');
 await expect(teaching.getByRole('region', {name: 'Done when your program gives'})).toBeVisible();
 await expect(teaching.getByRole('heading', {name: 'Hints'})).toBeVisible();
 for (const label of await page.locator('.cases li.case-visible > span:not(.box):not(.expect)').all()) {
  expect((await label.boundingBox())!.width).toBeGreaterThan(200);
 }
 // L6: no empty scene before anything has run.
 await expect(page.locator('.editor-panel figure.scene')).toHaveCount(0);
});

test('L1 on a phone: the scene comes after the output, and nothing scrolls sideways', async ({page}) => {
 await mockApi(page);
 await page.setViewportSize({width: 375, height: 812});
 await page.goto('/preview?lesson=py.lists&card=2');
 await page.getByRole('button', {name: 'Run the example'}).click();
 await expect(page.getByRole('button', {name: 'Run it again'})).toBeVisible({timeout: 60000});
 const out = await page.locator('.see-code').boundingBox(), scene = await page.locator('.see-scene').boundingBox();
 expect(scene!.y).toBeGreaterThan(out!.y + out!.height - 1);
 expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
});
