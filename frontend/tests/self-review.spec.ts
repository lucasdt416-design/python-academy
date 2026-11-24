import {test, expect, Page} from '@playwright/test';
import path from 'path';
// ENG-09: a self-reviewed challenge (app/self-review.tsx). The API answers are the real ones,
// recorded by backend/tests/test_self_review.py; the mock answers only a request equal to a recorded one.
import recorded from './fixtures/self-review-api.json';
import py from './fixtures/units-4-11-api.json';
import goals from '../../backend/tests/fixtures/goals_v1.json';

const UNITS = py.units as unknown as Record<string, unknown>;
const canon = (v: unknown): string => JSON.stringify(v, (_k, x) => x && typeof x === 'object' && !Array.isArray(x) ? Object.fromEntries(Object.entries(x).sort(([a], [b]) => a.localeCompare(b))) : x);

async function mockApi(page: Page, role: string | null = null, kept = false) {
 const posted: {path: string; body: unknown}[] = [];
 await page.route('**/api/**', async route => {
  const where = new URL(route.request().url()).pathname;
  let status = 200, json: unknown = [];
  const unit = /^\/api\/units\/([^/]+)\/lessons$/.exec(where)?.[1];
  if (where === '/api/catalog') json = py.catalog;
  else if (where === '/api/me') ({status, json} = role ? {status: 200, json: {id: 1, email: 'learner@example.com', role}} : {status: 401, json: {detail: 'Sign in to continue'}});
  else if (where === '/api/goals') json = goals;
  else if (where === '/api/goal') json = {goal: 'scratch', chosen: true, asked: true};
  else if (where === '/api/awards') json = {xp: 0, completed: [], badges: []};
  else if (unit) json = UNITS[unit];
  else if (where === '/api/self-review/py.final-brief' && route.request().method() === 'GET') { posted.push({path: where, body: null}); json = kept ? recorded.reads.after : recorded.reads.before; }
  else if (where.startsWith('/api/self-review')) {
   const body = route.request().postDataJSON(); posted.push({path: where, body});
   const match = recorded.calls.find(c => c.path === where && canon(c.request) === canon(body));
   ({status = 200, json} = match ? {json: match.response} : {status: 500, json: {detail: 'not a recorded request'}});
  }
  await route.fulfill({status, contentType: 'application/json', body: JSON.stringify(json)});
 });
 return posted;
}
const violations = new WeakMap<Page, string[]>();
test.beforeEach(async ({page}) => {
 const found: string[] = []; violations.set(page, found);
 page.on('pageerror', e => found.push(`page error: ${e.message}`));
 await page.exposeFunction('reportCspViolation', (v: string) => found.push(v));
 await page.addInitScript(() => document.addEventListener('securitypolicyviolation', e => (window as unknown as {reportCspViolation: (v: string) => void}).reportCspViolation(`${e.effectiveDirective} blocked ${e.blockedURI || 'inline'}`)));
});
test.afterEach(async ({page}) => { expect(violations.get(page)).toEqual([]); });

const form = (page: Page) => page.getByRole('region', {name: 'Your review'});
const ASKS: Record<string, string> = {choice: 'Which one, and why does it suit you right now?', user: 'Who will use it, and what do they want from it?', must: 'List three to five things it must do.', 'not-yet': 'What are you leaving out of the first version?', milestones: 'What are your first three milestones, each something you can run and show?'};
const TICKS: Record<string, string> = {choice: 'I chose one of the three projects.', user: 'I named who it is for.', must: 'I listed what it must do.', 'not-yet': 'I listed what it will not do yet.', milestones: 'I split it into milestones I can run.'};
async function fill(page: Page, answers: Record<string, {done: boolean; evidence: string}>) {
 for (const [id, a] of Object.entries(answers)) {
  if (a.done) await form(page).getByLabel(TICKS[id]).check();
  await form(page).getByLabel(ASKS[id]).fill(a.evidence);
 }
}

test('a review with parts to change says what, beside each part, and the page keeps what was written', async ({page}) => {
 const posted = await mockApi(page);
 await page.goto('/preview?lesson=py.final-brief&card=5');
 await expect(page.getByRole('region', {name: 'Python playground'})).toHaveCount(0);
 await fill(page, recorded.short);
 await expect(form(page).getByText('2 words · at least 8')).toBeVisible();
 await form(page).getByRole('button', {name: 'Check my review'}).click();
 await expect(form(page).getByRole('status')).toHaveText('Not recorded yet. Each note below says what to change.');
 const user = form(page).getByLabel(ASKS.user);
 await expect(user).toHaveAccessibleDescription(/2 words · at least 8 .*Say a little more, in your own words: at least 8 words \(2 so far\)\./);
 await expect(form(page).getByText('Tick this when you have done it.')).toHaveCount(3);
 await expect(user).toHaveValue('my cousin');
 expect(posted.map(p => p.path)).toEqual(['/api/self-review/preview']);
 await expect(page.getByRole('button', {name: 'Revisit this quest'})).toBeDisabled();
});

test('a finished review in a preview is ready, and nothing is saved', async ({page}) => {
 await mockApi(page);
 await page.goto('/preview?lesson=py.final-brief&card=5');
 await fill(page, Object.fromEntries(Object.entries(recorded.good).map(([k, v]) => [k, {done: true, evidence: v}])));
 await form(page).getByRole('button', {name: 'Check my review'}).click();
 await expect(form(page).getByRole('status')).toHaveText('Every part is ready to record. In a preview nothing is saved.');
 await expect(page.getByText('Preview badge: not saved.')).toBeVisible();
});

test('a student records a finished review, and it is labelled self-reported', async ({page}) => {
 const posted = await mockApi(page, 'student');
 await page.goto('/learn/py.final-brief');
 await page.getByRole('button', {name: 'Continue →'}).click();
 await page.getByRole('button', {name: 'Continue →'}).click();
 await page.getByRole('button', {name: /Lockpick|hint that costs/}).first().click();
 await page.getByRole('button', {name: 'Continue →'}).click();
 await page.getByRole('button', {name: 'Start my challenge'}).click();
 await expect(page.getByText('They are kept as self-reported: nothing checked the work itself.')).toBeVisible();
 await fill(page, Object.fromEntries(Object.entries(recorded.good).map(([k, v]) => [k, {done: true, evidence: v}])));
 await form(page).getByRole('button', {name: 'Record my review'}).click();
 await expect(form(page).getByRole('status')).toContainText('kept as self-reported, in your words');
 await expect(page.getByText('Your review is saved, as self-reported.')).toBeVisible();
 expect(posted).toEqual([{path: '/api/self-review/py.final-brief', body: null}, {path: '/api/self-review', body: expect.objectContaining({lesson_id: 'py.final-brief'})}]);
});

test('coming back, a student reads the brief they recorded; a preview never asks for one', async ({page}) => {
 const posted = await mockApi(page, 'student', true);
 await page.goto('/learn/py.final-brief');
 for (const _ of [0, 1]) await page.getByRole('button', {name: 'Continue →'}).click();
 await page.getByRole('button', {name: /Lockpick|hint that costs/}).first().click();
 await page.getByRole('button', {name: 'Continue →'}).click();
 await page.getByRole('button', {name: 'Start my challenge'}).click();
 await expect(page.getByText('This is the review you recorded on')).toBeVisible();
 for (const [id, text] of Object.entries(recorded.good)) await expect(page.locator(`#review-${id}`)).toHaveValue(text);
 await expect(form(page).getByRole('checkbox', {checked: true})).toHaveCount(Object.keys(recorded.good).length);
 expect(posted).toEqual([{path: '/api/self-review/py.final-brief', body: null}]);
 const previewed = await mockApi(page);
 await page.goto('/preview?lesson=py.final-brief&card=5');
 await expect(page.locator('#review-choice')).toHaveValue('');
 expect(previewed).toEqual([]);
});

test.describe('axe', () => {
 test.use({bypassCSP: true});
 const AXE = path.join(__dirname, '..', 'node_modules', 'axe-core', 'axe.min.js');
 for (const size of [{name: 'desktop', width: 1280, height: 900}, {name: 'phone', width: 375, height: 812}]) {
  test(`a review with notes, ${size.name}: no WCAG A or AA findings, no sideways scroll`, async ({page}) => {
   await page.setViewportSize(size);
   await mockApi(page);
   await page.goto('/preview?lesson=py.final-brief&card=5');
   await fill(page, recorded.short);
   await form(page).getByRole('button', {name: 'Check my review'}).click();
   await expect(form(page).getByRole('status')).not.toBeEmpty();
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
