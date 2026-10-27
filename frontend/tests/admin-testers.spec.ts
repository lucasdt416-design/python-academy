import fs from 'node:fs';
import path from 'node:path';
import {test, expect, Page, Route} from '@playwright/test';

/* The testers page (FB-04). The API decides who may see it: these tests mock its answers for each
 * kind of visitor (backend/tests/test_admin.py proves the real API gives 401 and 403). The page
 * itself must show nothing to anyone the API refuses, send the right change, and never store or
 * show the admin's own email. */

const ADMIN_EMAIL = 'owner-admin@example.com';
const STUDENTS = [
 {id: 2, email: 'kid-one@example.com', tester: false},
 {id: 5, email: 'kid-two@example.com', tester: true},
];
type Posted = {user_id: number; tester: boolean};

/** who: 'signed out' | 'student' | 'parent' | 'admin'. save decides how POST /api/admin/testers answers. */
async function mockApi(page: Page, who: string, save: (body: Posted, route: Route) => Promise<void> | void = (body, route) => route.fulfill({json: {id: body.user_id, tester: body.tester}})) {
 const calls: string[] = [], posted: Posted[] = [];
 await page.route('**/api/**', async route => {
  const path = new URL(route.request().url()).pathname;
  calls.push(`${route.request().method()} ${path}`);
  const refused = who === 'signed out' ? {status: 401, json: {detail: 'Sign in to continue'}} : {status: 403, json: {detail: 'This action is unavailable for this account'}};
  if (path === '/api/me') return route.fulfill(who === 'signed out' ? refused : {json: {id: 1, email: ADMIN_EMAIL, role: who === 'admin' ? 'parent' : who, admin: who === 'admin', tester: who === 'admin'}});
  if (path.startsWith('/api/admin/') && who !== 'admin') return route.fulfill(refused);
  if (path === '/api/admin/students') return route.fulfill({json: STUDENTS});
  if (path === '/api/admin/testers') { const body = route.request().postDataJSON(); posted.push(body); return save(body, route); }
  return route.fulfill({json: {}});
 });
 return {calls, posted};
}

const violations = new WeakMap<Page, string[]>();
test.beforeEach(async ({page}) => {
 const found: string[] = []; violations.set(page, found);
 await page.exposeFunction('reportCspViolation', (v: string) => found.push(v));
 await page.addInitScript(() => document.addEventListener('securitypolicyviolation', e => (window as unknown as {reportCspViolation: (v: string) => void}).reportCspViolation(`${e.effectiveDirective} blocked ${e.blockedURI || 'inline'}`)));
});
test.afterEach(async ({page}) => { expect(violations.get(page)).toEqual([]); });

const switchFor = (page: Page, email: string) => page.getByRole('switch', {name: `Tester ${email}`});

for (const who of ['signed out', 'student', 'parent']) test(`${who}: a plain "not available" page with nothing about admins or students`, async ({page}) => {
 await mockApi(page, who);
 await page.goto('/admin/testers');
 await expect(page.getByRole('heading', {level: 1, name: 'Page not available'})).toBeVisible();
 await expect(page.getByText('This page is not available.')).toBeVisible();
 const text = (await page.locator('body').innerText()).toLowerCase();
 for (const word of ['admin', 'tester', 'student', '@']) expect(text, word).not.toContain(word);
 await expect(page.getByRole('switch')).toHaveCount(0);
 await expect(page.getByRole('button', {name: 'Sign out'})).toHaveCount(0);
});

test('admin: students with their ID, email and tester state', async ({page}) => {
 const {calls} = await mockApi(page, 'admin');
 await page.goto('/admin/testers');
 await expect(page.getByRole('heading', {level: 1, name: 'Testers'})).toBeVisible();
 const rows = page.getByRole('table').getByRole('row');
 await expect(rows).toHaveCount(3);
 await expect(rows.nth(1)).toHaveText(/^2kid-one@example\.comOff$/);
 await expect(rows.nth(2)).toHaveText(/^5kid-two@example\.comOn$/);
 await expect(switchFor(page, 'kid-one@example.com')).toHaveAttribute('aria-checked', 'false');
 await expect(switchFor(page, 'kid-two@example.com')).toHaveAttribute('aria-checked', 'true');
 // The page never asks who is signed in, so it never has the admin's email.
 expect(calls).toEqual(['GET /api/admin/students']);
});

test('no page links to the testers page: the owner opens it by address', () => {
 // Every page and component outside app/admin; a link in any of them would show in the learner UI.
 const app = path.join(__dirname, '..', 'app');
 const files = fs.readdirSync(app, {recursive: true}).map(String).filter(f => /\.tsx?$/.test(f) && !f.startsWith('admin'));
 expect(files.length).toBeGreaterThan(10);
 for (const file of files) expect(fs.readFileSync(path.join(app, file), 'utf8'), file).not.toMatch(/\/admin/);
});

test('a toggle sends that student and the new state, then shows what the server saved', async ({page}) => {
 const {posted} = await mockApi(page, 'admin');
 await page.goto('/admin/testers');
 await switchFor(page, 'kid-one@example.com').click();
 await expect(page.getByRole('status')).toHaveText('Tester turned on for student 2 (kid-one@example.com).');
 expect(posted).toEqual([{user_id: 2, tester: true}]);
 await expect(switchFor(page, 'kid-one@example.com')).toHaveAttribute('aria-checked', 'true');
 await expect(switchFor(page, 'kid-two@example.com')).toHaveAttribute('aria-checked', 'true');
 await switchFor(page, 'kid-two@example.com').click();
 await expect(page.getByRole('status')).toHaveText('Tester turned off for student 5 (kid-two@example.com).');
 expect(posted).toEqual([{user_id: 2, tester: true}, {user_id: 5, tester: false}]);
 await expect(switchFor(page, 'kid-two@example.com')).toHaveAttribute('aria-checked', 'false');
 await expect(switchFor(page, 'kid-one@example.com')).toHaveAttribute('aria-checked', 'true');
});

for (const failure of ['server error', 'refused', 'network down']) test(`a failed save (${failure}) shows an error and leaves the switch as it was`, async ({page}) => {
 await mockApi(page, 'admin', (_, route) => failure === 'network down' ? route.abort() : route.fulfill({status: failure === 'refused' ? 422 : 500, json: {detail: 'Only student accounts can be testers'}}));
 await page.goto('/admin/testers');
 const kid = switchFor(page, 'kid-one@example.com');
 await kid.click();
 await expect(page.locator('main').getByRole('alert')).toHaveText('That did not save, so student 2 (kid-one@example.com) is unchanged. Check your connection and try again.');
 await expect(kid).toHaveAttribute('aria-checked', 'false');
 await expect(kid).toHaveAttribute('aria-disabled', 'false');
 await expect(page.getByRole('status')).toHaveText('');
});

test('while saving, every switch is unavailable and a second press sends nothing', async ({page}) => {
 let release = () => {};
 const {posted} = await mockApi(page, 'admin', (body, route) => new Promise<void>(done => { release = () => { route.fulfill({json: {id: body.user_id, tester: body.tester}}); done(); }; }));
 await page.goto('/admin/testers');
 const kid = switchFor(page, 'kid-one@example.com');
 await kid.click();
 await expect(kid).toHaveAttribute('aria-disabled', 'true');
 await expect(kid).toContainText('Saving…');
 await expect(switchFor(page, 'kid-two@example.com')).toHaveAttribute('aria-disabled', 'true');
 await kid.dispatchEvent('click');
 await switchFor(page, 'kid-two@example.com').dispatchEvent('click');
 expect(posted).toHaveLength(1);
 release();
 await expect(kid).toHaveAttribute('aria-checked', 'true');
 await expect(kid).toHaveAttribute('aria-disabled', 'false');
});

test('keyboard: Tab reaches each switch, Space and Enter toggle it, and focus stays put', async ({page}) => {
 const {posted} = await mockApi(page, 'admin');
 await page.goto('/admin/testers');
 await expect(switchFor(page, 'kid-one@example.com')).toBeVisible();
 await switchFor(page, 'kid-one@example.com').focus();
 await page.keyboard.press('Space');
 await expect(switchFor(page, 'kid-one@example.com')).toHaveAttribute('aria-checked', 'true');
 await expect(switchFor(page, 'kid-one@example.com')).toBeFocused();
 await page.keyboard.press('Tab');
 await expect(switchFor(page, 'kid-two@example.com')).toBeFocused();
 await page.keyboard.press('Enter');
 await expect(switchFor(page, 'kid-two@example.com')).toHaveAttribute('aria-checked', 'false');
 await expect(switchFor(page, 'kid-two@example.com')).toBeFocused();
 expect(posted).toEqual([{user_id: 2, tester: true}, {user_id: 5, tester: false}]);
});

test('if the list cannot load, the page says so and offers to try again', async ({page}) => {
 let fail = true;
 await page.route('**/api/admin/students', route => fail ? route.fulfill({status: 500, json: {detail: 'oops'}}) : route.fulfill({json: STUDENTS}));
 await page.goto('/admin/testers');
 await expect(page.locator('main').getByRole('alert')).toHaveText('The student list could not load. Nothing was changed.');
 fail = false;
 await page.getByRole('button', {name: 'Try again'}).click();
 await expect(page.getByRole('switch')).toHaveCount(2);
});

test('no student accounts yet', async ({page}) => {
 await mockApi(page, 'admin');
 await page.route('**/api/admin/students', route => route.fulfill({json: []}));
 await page.goto('/admin/testers');
 await expect(page.getByText('No student accounts yet.')).toBeVisible();
 await expect(page.getByRole('table')).toHaveCount(0);
});

test('the page source and browser storage hold no email, and nothing is stored', async ({page, request}) => {
 const html = await (await request.get('/admin/testers')).text();
 expect(html).not.toMatch(/[\w.+-]+@[\w-]+\.[\w.]+/);
 for (const word of ['kid-one', ADMIN_EMAIL]) expect(html).not.toContain(word);
 await mockApi(page, 'admin');
 await page.goto('/admin/testers');
 await switchFor(page, 'kid-one@example.com').click();
 await expect(page.getByRole('status')).not.toHaveText('');
 const stored = await page.evaluate(() => ({local: {...localStorage}, session: {...sessionStorage}, cookie: document.cookie}));
 expect(stored).toEqual({local: {}, session: {}, cookie: ''});
 expect(await page.content()).not.toContain(ADMIN_EMAIL);
});

test('fits a phone, and nothing moves with reduced motion', async ({page}) => {
 await page.setViewportSize({width: 375, height: 812});
 await page.emulateMedia({reducedMotion: 'reduce'});
 await mockApi(page, 'admin');
 await page.route('**/api/admin/students', route => route.fulfill({json: [...STUDENTS, {id: 123456, email: 'a-very-long-student-address-that-keeps-going@school.example.org', tester: false}]}));
 await page.goto('/admin/testers');
 await expect(page.getByRole('switch')).toHaveCount(3);
 expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
 expect(await page.locator('.tester-switch, .tester-switch *').evaluateAll(els => els.every(el => getComputedStyle(el).animationName === 'none' && getComputedStyle(el).transitionDuration === '0s'))).toBe(true);
});
