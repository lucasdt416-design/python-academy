import {test, expect, Page} from '@playwright/test';
import path from 'path';
// The Practice Arena (app/arena.tsx) and "A likely cause" (app/adventure.tsx, /api/insights). The arena
// answers come from backend/tests/test_review.py, which proves they are the real API's.
import recorded from './fixtures/arena-api.json';
import units from './fixtures/units-4-11-api.json';
import goals from '../../backend/tests/fixtures/goals_v1.json';

type Result = {correct: boolean; why: string; back_in_days: number; answer?: number; lines?: string[]};
const RESULTS = recorded.results as unknown as Record<string, {right: Result; wrong: Result; answer: number | null; lines: string[] | null}>;

async function mockApi(page: Page, {role = 'student' as string | null, session = recorded.session as unknown, insights = [] as unknown[]} = {}) {
 const posted: {path: string; body: Record<string, unknown>}[] = [];
 await page.route('**/api/**', async route => {
  const req = route.request(), where = new URL(req.url()).pathname;
  let status = 200, json: unknown = {};
  const unit = /^\/api\/units\/([^/]+)\/lessons$/.exec(where)?.[1], plan = /^\/api\/checks\/(.+)$/.exec(where)?.[1];
  if (where === '/api/me') ({status, json} = role ? {status: 200, json: {id: 1, email: 'learner@example.com', role}} : {status: 401, json: {detail: 'Sign in to continue'}});
  else if (where === '/api/catalog') json = units.catalog;
  else if (where === '/api/goals') json = goals;
  else if (where === '/api/goal') json = {goal: 'scratch', chosen: true, asked: true};
  else if (where === '/api/awards') json = {xp: 300, completed: [], badges: []};
  else if (where === '/api/progress' || where === '/api/history' || where === '/api/family') json = [];
  else if (where === '/api/recommendation') json = {kind: 'continue', reason: "You're partway through Python Foundations.", course: 'py', unit: 'py.u04', lesson: 'py.sets', options: [], notes: [], rules_version: 2};
  else if (unit) json = (units.units as Record<string, unknown>)[unit];
  else if (plan) json = (units.plans as Record<string, unknown>)[plan];
  else if (where === '/api/review') json = session;
  else if (where === '/api/review/answer') {
   const body = req.postDataJSON(); posted.push({path: where, body});
   const r = RESULTS[body.card_id];
   const right = r.lines ? JSON.stringify(body.lines) === JSON.stringify(r.lines) : body.choice === r.answer;
   json = right ? r.right : r.wrong;
  } else if (where === '/api/insights') { posted.push({path: where, body: req.postDataJSON()}); json = {insights}; }
  else if (where === '/api/check') json = {passed: false, result: 'needs_work', feedback: 'For three items, line 1 should be "3".', rule: 'py.lists.case.three', assessment: 'browser_tests', cases: [], failed: {reason: 'wrong_output'}};
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

const cards = recorded.session.cards;
const card = (page: Page) => page.getByRole('article');
const option = (i: number, n: number) => (cards[i] as unknown as {options: string[]}).options[n];
async function answerRight(page: Page, i: number) {
 await card(page).getByRole('button', {name: option(i, RESULTS[cards[i].id].answer!), exact: true}).click();
}

test('a whole session: every right answer lands a hit, and the creature is tamed', async ({page}) => {
 const posted = await mockApi(page);
 await page.goto('/');
 await page.getByRole('navigation', {name: 'Main'}).getByRole('link', {name: 'Practice'}).click();
 await expect(page.getByRole('heading', {level: 1, name: 'Tame the Packrat'})).toBeVisible();
 for (let i = 0; i < cards.length; i++) {
  await expect(card(page).getByText(`· ${i + 1} of 5`)).toBeVisible();
  await answerRight(page, i);
  await expect(page.getByRole('status').filter({hasText: 'A hit!'})).toContainText(RESULTS[cards[i].id].right.why);
  await page.getByRole('button', {name: i === cards.length - 1 ? 'Finish' : 'Next question'}).click();
 }
 await expect(page.getByRole('heading', {name: 'You tamed the Packrat!'})).toBeVisible();
 await expect(page.getByRole('img', {name: 'The Packrat, tamed'})).toBeVisible();
 // Only the card id and the choice are sent; answers come back from the server.
 expect(posted.map(p => Object.keys(p.body).sort())).toEqual(Array(5).fill(['card_id', 'choice']));
});

test('a wrong answer explains why, comes back once at the end, and can still win the round', async ({page}) => {
 const posted = await mockApi(page);
 await page.goto('/practice');
 const first = RESULTS[cards[0].id];
 await card(page).getByRole('button', {name: option(0, (first.answer! + 1) % 3), exact: true}).click();
 await expect(page.getByRole('status').filter({hasText: 'Not this time.'})).toContainText(first.wrong.why);
 await expect(card(page).locator('.tile.right')).toHaveCount(1);
 await page.getByRole('button', {name: 'Next question'}).click();
 for (let i = 1; i < cards.length; i++) { await answerRight(page, i); await page.getByRole('button', {name: 'Next question'}).click(); }
 await expect(card(page).getByText('second try')).toBeVisible();
 await answerRight(page, 0);
 await page.getByRole('button', {name: 'Finish'}).click();
 await expect(page.getByRole('heading', {name: 'You tamed the Packrat!'})).toBeVisible();
 // The second try is checked on the page: the schedule keeps the first answer.
 expect(posted.filter(p => p.body.card_id === cards[0].id)).toHaveLength(1);
});

test('an arrange-the-lines card is solved with the move buttons, from the keyboard', async ({page}) => {
 const order = recorded.order_card;
 await mockApi(page, {session: {...recorded.session, cards: [order]}});
 await page.goto('/practice');
 await expect(card(page).getByText('Arrange the lines')).toBeVisible();
 const want = RESULTS[order.id].lines!;
 // Bubble the lines into the right order using only the buttons.
 for (let target = 0; target < want.length; target++) {
  const now = await card(page).locator('.order-lines code').allTextContents();
  for (let at = now.indexOf(want[target]); at > target; at--) {
   await card(page).getByRole('button', {name: `Move up: ${want[target].trim()}`}).focus();
   await page.keyboard.press('Enter');
  }
 }
 await card(page).getByRole('button', {name: 'Check the order'}).click();
 await expect(page.getByRole('status').filter({hasText: 'A hit!'})).toBeVisible();
});

test('before any lesson is finished, the arena says how to unlock it', async ({page}) => {
 await mockApi(page, {session: {...recorded.session, cards: [], unlocked: false, creature: null}});
 await page.goto('/practice');
 await expect(page.getByText("Finish a lesson's challenge, and questions about it will appear here")).toBeVisible();
 await expect(page.getByRole('heading', {name: 'Your collection'})).toBeVisible();
 await expect(page.getByText('Not met yet')).toHaveCount(14);
});

test('signed out, the arena asks you to sign in; parents see no Practice link', async ({page}) => {
 await mockApi(page, {role: null});
 await page.goto('/practice');
 await expect(page.getByRole('link', {name: 'Sign in with Google'})).toBeVisible();
 await page.unrouteAll();
 await mockApi(page, {role: 'parent'});
 await page.goto('/');
 await expect(page.getByRole('link', {name: 'Practice'})).toHaveCount(0);
});

// A likely cause

test('after a check does not pass, a likely cause is offered with its line, and never as a verdict', async ({page}) => {
 const insight = {id: 'reset-in-loop', line: 3, text: '`pack` starts again on line 3, inside the loop, so it forgets every earlier turn. Give it its starting value once, above the loop.'};
 const posted = await mockApi(page, {role: null, insights: [insight]});
 await page.goto('/preview?lesson=py.lists&card=5');
 const code = 'count = int(input())\nfor n in range(count):\n    pack = []\n    pack.append(input())\nwanted = input()\nprint(len(pack))\nprint(wanted in pack)\nprint(pack)';
 await page.getByLabel('Your Python code').fill(code);
 await page.getByRole('button', {name: 'Run & check challenge'}).click();
 const cause = page.getByRole('region', {name: 'A likely cause'});
 await expect(cause).toContainText('starts again on line 3', {timeout: 45000});
 await expect(cause).toContainText('It may be wrong; the check decides.');
 await cause.getByRole('button', {name: 'Go to line 3'}).click();
 await expect(page.getByLabel('Your Python code')).toBeFocused();
 expect(posted.find(p => p.path === '/api/insights')?.body).toEqual({lesson_id: 'py.lists', code});
 // Editing clears it, like the result it belongs to.
 await page.getByLabel('Your Python code').press('End');
 await page.getByRole('button', {name: 'Reset code'}).click();
 await expect(cause).toHaveCount(0);
});

test.describe('axe', () => {
 test.use({bypassCSP: true});
 const AXE = path.join(__dirname, '..', 'node_modules', 'axe-core', 'axe.min.js');
 for (const size of [{name: 'desktop', width: 1280, height: 900}, {name: 'phone', width: 375, height: 812}]) {
  test(`arena with a card answered, ${size.name}: no WCAG A or AA findings, no sideways scroll`, async ({page}) => {
   await page.setViewportSize(size);
   await mockApi(page);
   await page.goto('/practice');
   await answerRight(page, 0);
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
