import {test, expect, Page} from '@playwright/test';
import path from 'path';
// "Watch it run" (app/stepper.tsx, the worker's trace mode) with real Pyodide, and the profile page
// (app/profile.tsx). The profile answers are in fixtures/profile-api.json, whose shape
// backend/tests/test_profiles.py checks against the real /api/profile.
import recorded from './fixtures/units-4-11-api.json';
import profile from './fixtures/profile-api.json';
import goals from '../../backend/tests/fixtures/goals_v1.json';

const UNITS = recorded.units as unknown as Record<string, unknown>;
async function mockApi(page: Page, {role = null as string | null} = {}) {
 const requests: {method: string; path: string; body: unknown}[] = [];
 let saved = {...profile.student};
 await page.route('**/api/**', async route => {
  const req = route.request(), where = new URL(req.url()).pathname;
  requests.push({method: req.method(), path: where, body: req.postDataJSON?.() ?? null});
  let status = 200, json: unknown = {};
  const unit = /^\/api\/units\/([^/]+)\/lessons$/.exec(where)?.[1], plan = /^\/api\/checks\/(.+)$/.exec(where)?.[1];
  if (where === '/api/catalog') json = recorded.catalog;
  else if (where === '/api/me') ({status, json} = role ? {status: 200, json: {id: 1, email: 'learner@example.com', role}} : {status: 401, json: {detail: 'Sign in to continue'}});
  else if (where === '/api/goals') json = goals;
  else if (where === '/api/goal') json = {goal: 'scratch', chosen: true, asked: true};
  else if (where === '/api/awards') json = {xp: 700, completed: ['hello'], badges: []};
  else if (where === '/api/progress' || where === '/api/history' || where === '/api/family') json = [];
  else if (where === '/api/recommendation') json = {kind: 'continue', reason: '', course: 'py', unit: 'py.u01', lesson: 'variables', options: [], notes: [], rules_version: 2};
  else if (unit) json = UNITS[unit];
  else if (plan) json = (recorded.plans as Record<string, unknown>)[plan];
  else if (where === '/api/profile' && req.method() === 'PUT') { const body = req.postDataJSON(); saved = {...saved, ...body, saved: true}; json = saved; }
  else if (where === '/api/profile') json = role === 'parent' ? profile.parent : saved;
  await route.fulfill({status, contentType: 'application/json', body: JSON.stringify(json)});
 });
 return requests;
}
const violations = new WeakMap<Page, string[]>();
test.beforeEach(async ({page}) => {
 const found: string[] = []; violations.set(page, found);
 page.on('pageerror', e => found.push(`page error: ${e.message}`));
 await page.exposeFunction('reportCspViolation', (v: string) => found.push(v));
 await page.addInitScript(() => document.addEventListener('securitypolicyviolation', e => (window as unknown as {reportCspViolation: (v: string) => void}).reportCspViolation(`${e.effectiveDirective} blocked ${e.blockedURI || 'inline'}`)));
});
test.afterEach(async ({page}) => { expect(violations.get(page)).toEqual([]); });

const stepper = (page: Page) => page.getByRole('region', {name: 'Watch it run'});
const say = (page: Page) => stepper(page).locator('.stepper-say');

// Watch it run

test('the worked example steps line by line, naming what changed and what was printed', async ({page}) => {
 const requests = await mockApi(page);
 await page.goto('/preview?lesson=variables&card=2');
 await page.getByRole('button', {name: 'Watch it run, step by step'}).click();
 await expect(stepper(page).getByText(/^Step 1 of \d+$/)).toBeVisible({timeout: 45000});
 await expect(say(page)).toHaveText('The program is about to start, at line 1: hero = "Nova"');
 await expect(stepper(page).locator('.stepper-line.next')).toContainText('hero = "Nova"');
 await stepper(page).getByRole('button', {name: 'Next →'}).click();
 await expect(say(page)).toHaveText("Line 1 ran. hero is now 'Nova'. Next is line 2.");
 await expect(stepper(page).locator('tr.changed')).toContainText("hero'Nova' new");
 await stepper(page).getByRole('button', {name: 'Next →'}).click();
 await stepper(page).getByRole('button', {name: 'Next →'}).click();
 await expect(say(page)).toHaveText('Line 3 ran. No name changed. It printed "Nova". Next is line 4.');
 await stepper(page).getByRole('button', {name: 'Next →'}).click();
 await expect(say(page)).toHaveText('Line 4 ran. It printed "lantern". That is the end of the program.');
 await expect(stepper(page).getByRole('button', {name: 'Last'})).toBeDisabled();
 await expect(stepper(page).getByText('The program finished.')).toBeVisible();
 await expect(stepper(page).locator('.stepper-output')).toHaveText('Nova\nlantern\n');
 await stepper(page).getByRole('button', {name: '← Back'}).click();
 await expect(stepper(page).getByRole('button', {name: 'Next →'})).toBeEnabled();
 // Stepping sends nothing: the only requests are the page's own loading.
 expect(requests.filter(r => r.method !== 'GET')).toEqual([]);
});

test('stepping into a function shows its own names, and what it gives back', async ({page}) => {
 await mockApi(page);
 await page.goto('/preview?lesson=py.return-values&card=2');
 await page.getByRole('button', {name: 'Watch it run, step by step'}).click();
 await expect(stepper(page).getByText(/^Step 1 of \d+$/)).toBeVisible({timeout: 45000});
 const next = stepper(page).getByRole('button', {name: 'Next →'});
 await expect(async () => { await next.click(); await expect(say(page)).toContainText('called points(), which starts with tries = 1', {timeout: 200}); }).toPass({timeout: 20000});
 await expect(stepper(page).getByRole('heading', {name: 'Inside points()'})).toBeVisible();
 await expect(async () => { await next.click(); await expect(say(page)).toContainText('points() finishes on line 4 and gives back 10', {timeout: 200}); }).toPass({timeout: 20000});
 await expect(stepper(page).locator('.stepper-return')).toHaveText('Gives back 10');
});

test('a loop that never ends is stopped and explained, and the slider moves through it', async ({page}) => {
 await mockApi(page);
 await page.goto('/preview?lesson=py.while-loops&card=4');
 await page.getByLabel('Your Python code').fill('count = 0\nwhile count < 5:\n    print(count)');
 await page.getByRole('button', {name: 'Watch it run', exact: true}).click();
 await expect(stepper(page).getByText('Step 1 of 400')).toBeVisible({timeout: 45000});
 await stepper(page).getByRole('slider', {name: 'Step'}).fill('399');
 await expect(stepper(page).getByText(/Stopped recording after 400 steps/)).toBeVisible();
 await expect(say(page)).toContainText('No name changed.');
});

test('a program that stops with an error says where', async ({page}) => {
 await mockApi(page);
 await page.goto('/preview?lesson=py.int-float&card=4');
 await page.getByLabel('Your Python code').fill('coins = 10\nfriends = 0\nprint(coins / friends)');
 await page.getByRole('button', {name: 'Watch it run', exact: true}).click();
 await stepper(page).getByRole('button', {name: 'Last'}).click({timeout: 45000});
 await expect(stepper(page).getByText('Python stopped here with ZeroDivisionError on line 3.')).toBeVisible();
});

test('editing the code closes the steps, so they always match the code', async ({page}) => {
 await mockApi(page);
 await page.goto('/preview?lesson=variables&card=4');
 await page.getByRole('button', {name: 'Watch it run', exact: true}).click();
 await expect(stepper(page).getByText(/^Step 1 of/)).toBeVisible({timeout: 45000});
 await page.getByLabel('Your Python code').fill('hero = "Kai"');
 await expect(stepper(page)).toHaveCount(0);
});

test('Play steps on its own and stops at the end', async ({page}) => {
 await mockApi(page);
 await page.goto('/preview?lesson=hello&card=2');
 await page.getByRole('button', {name: 'Watch it run, step by step'}).click();
 await stepper(page).getByRole('button', {name: 'Play'}).click({timeout: 45000});
 await expect(stepper(page).getByText('The program finished.')).toBeVisible({timeout: 15000});
 await expect(stepper(page).getByRole('button', {name: 'Play'})).toBeDisabled();
});

// Profiles

test('a signed-out visitor is asked to sign in with Google', async ({page}) => {
 await mockApi(page);
 await page.goto('/profile');
 await expect(page.getByRole('heading', {name: 'Your profile'})).toBeVisible();
 await expect(page.getByRole('link', {name: 'Sign in with Google'})).toHaveAttribute('href', '/auth/google');
 await expect(page.getByRole('link', {name: 'Profile'})).toHaveCount(0);
});

test('a student sees their level, progress and badges, builds an avatar and saves it', async ({page}) => {
 const requests = await mockApi(page, {role: 'student'});
 await page.goto('/');
 await page.getByRole('navigation', {name: 'Main'}).getByRole('link', {name: 'Profile'}).click();
 await expect(page).toHaveURL('/profile');
 await expect(page.getByText('Level 2 · Pathfinder')).toBeVisible();
 await expect(page.getByText('300 XP to level 3.')).toBeVisible();
 await expect(page.getByText('of 52 lessons done')).toBeVisible();
 await expect(page.getByRole('list').filter({hasText: 'Pack keeper'})).toBeVisible();
 await expect(page.getByText('You earned XP on 2 days in the last twelve weeks.')).toBeVisible();
 const save = page.getByRole('button', {name: 'Save my profile'});
 await page.getByRole('group', {name: 'Hair colour'}).getByRole('button', {name: 'teal'}).click();
 await expect(page.getByRole('group', {name: 'Hair colour'}).getByRole('button', {name: 'teal'})).toHaveAttribute('aria-pressed', 'true');
 await expect(page.locator('.avatar-large .hair-teal')).toHaveCount(1);
 await page.getByLabel(/Nickname/).fill('Nova');
 await save.click();
 await expect(page.getByRole('status').filter({hasText: 'Saved to your account.'})).toBeVisible();
 await expect(page.getByRole('heading', {level: 1, name: 'Nova'})).toBeVisible();
 const put = requests.find(r => r.method === 'PUT');
 expect(put).toEqual({method: 'PUT', path: '/api/profile', body: {nickname: 'Nova', avatar: {...profile.student.avatar, hair_colour: 'teal'}}});
 await expect(page.getByRole('button', {name: 'Save changes'})).toBeDisabled();
});

test('a parent has an avatar and nickname, without a learning summary', async ({page}) => {
 await mockApi(page, {role: 'parent'});
 await page.goto('/profile');
 await expect(page.getByRole('heading', {name: 'Make your avatar'})).toBeVisible();
 await expect(page.getByText(/lessons done/)).toHaveCount(0);
 await expect(page.getByRole('heading', {name: 'Badges'})).toHaveCount(0);
});

test.describe('axe', () => {
 test.use({bypassCSP: true});
 const AXE = path.join(__dirname, '..', 'node_modules', 'axe-core', 'axe.min.js');
 async function audit(page: Page) {
  await page.addScriptTag({path: AXE});
  return page.evaluate(async () => {
   const axe = (window as unknown as {axe: {run: (c: Document, o: object) => Promise<{violations: {id: string; nodes: {target: string[]}[]}[]}>}}).axe;
   const result = await axe.run(document, {runOnly: {type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa']}});
   return result.violations.map(v => `${v.id}: ${v.nodes.slice(0, 3).map(n => n.target.join(' ')).join(', ')}`);
  });
 }
 for (const size of [{name: 'desktop', width: 1280, height: 900}, {name: 'phone', width: 375, height: 812}]) {
  test(`profile page, ${size.name}: no WCAG A or AA findings, no sideways scroll`, async ({page}) => {
   await page.setViewportSize(size);
   await mockApi(page, {role: 'student'});
   await page.goto('/profile');
   await expect(page.getByText('Level 2 · Pathfinder')).toBeVisible();
   expect(await audit(page)).toEqual([]);
   expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  });
  test(`Watch it run, ${size.name}: no WCAG A or AA findings, no sideways scroll`, async ({page}) => {
   await page.setViewportSize(size);
   await mockApi(page);
   await page.goto('/preview?lesson=py.return-values&card=2');
   await page.getByRole('button', {name: 'Watch it run, step by step'}).click();
   await stepper(page).getByRole('button', {name: 'Next →'}).click({timeout: 45000});
   expect(await audit(page)).toEqual([]);
   expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  });
 }
});
