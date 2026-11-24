import {test, expect, Page} from '@playwright/test';
import path from 'path';
// Live play (E2, app/live-play.tsx, the worker's live runs) with real Pyodide. Each reply re-runs the
// program from the start with every reply so far; random keeps one seed per game; nothing is sent.
import recorded from './fixtures/units-4-11-api.json';
import goals from '../../backend/tests/fixtures/goals_v1.json';

const UNITS = recorded.units as unknown as Record<string, unknown>;
async function mockApi(page: Page) {
 const requests: string[] = [];
 await page.route('**/api/**', async route => {
  const where = new URL(route.request().url()).pathname;
  requests.push(where);
  let status = 200, json: unknown = {};
  const unit = /^\/api\/units\/([^/]+)\/lessons$/.exec(where)?.[1];
  if (where === '/api/catalog') json = recorded.catalog;
  else if (where === '/api/me') ({status, json} = {status: 401, json: {detail: 'Sign in to continue'}});
  else if (where === '/api/goals') json = goals;
  else if (unit) json = UNITS[unit];
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

const panel = (page: Page) => page.getByRole('region', {name: 'Play it live'});
const screen = (page: Page) => panel(page).locator('.live-screen');
const replyBox = (page: Page) => panel(page).getByRole('textbox');
async function open(page: Page, code?: string) {
 await page.goto('/preview?lesson=py.validate-input&card=4');
 if (code !== undefined) await page.getByLabel('Your Python code').fill(code);
 await page.getByRole('button', {name: 'Play it live'}).click();
}
async function reply(page: Page, text: string, count: number) {
 await expect(replyBox(page)).toBeEnabled({timeout: 45000});
 await replyBox(page).fill(text);
 await panel(page).getByRole('button', {name: 'Reply'}).click();
 await expect(panel(page).getByText(`${count} ${count === 1 ? 'reply' : 'replies'}`)).toBeVisible();
}

test('a program asks, the player answers each question as it comes, and it plays to the end', async ({page}) => {
 const requests = await mockApi(page);
 await open(page);
 await expect(panel(page).getByText('Your program asks: Door?')).toBeVisible({timeout: 45000});
 // While playing, the typed-in replies and the empty Output give way to the game.
 await expect(page.getByRole('group', {name: 'Player replies'})).toHaveCount(0);
 await expect(page.getByText('Your story will appear here.')).toHaveCount(0);
 await reply(page, 'four', 1);
 await expect(screen(page)).toHaveText('Door? four\nType a number.\n');
 await reply(page, '7', 2);
 await reply(page, '2', 3);
 await expect(panel(page).getByText('The program finished. Start over to play again.')).toBeVisible({timeout: 45000});
 await expect(screen(page)).toHaveText('Door? four\nType a number.\nDoor? 7\nThere are only 3 doors.\nDoor? 2\nYou open door 2\n');
 await expect(replyBox(page)).toHaveCount(0);
 expect(requests.filter(p => !['/api/catalog', '/api/me', '/api/goals'].includes(p) && !p.startsWith('/api/units/'))).toEqual([]);
 await panel(page).getByRole('button', {name: 'Start over'}).click();
 await expect(panel(page).getByText('0 replies')).toBeVisible();
 await expect(screen(page)).not.toContainText('You open door');
});

test('random numbers stay the same for the whole game, so a re-run carries on where it was', async ({page}) => {
 await mockApi(page);
 await open(page, 'import random\nsecret = random.randint(1, 1000000)\nprint("rolled", secret)\nwhile True:\n    guess = input("Guess? ")\n    print("you said", guess, "roll", random.randint(1, 1000000))\n');
 await expect(replyBox(page)).toBeEnabled({timeout: 45000});
 const first = await screen(page).textContent();
 await reply(page, 'a', 1);
 await expect(screen(page)).toContainText('you said a');
 await reply(page, 'b', 2);
 await expect(screen(page)).toContainText('you said b');
 const after = (await screen(page).textContent()) ?? '';
 expect(after.startsWith(first ?? 'missing')).toBe(true);
 expect(after.split('\n').filter(l => l.startsWith('you said'))).toHaveLength(2);
});

test('except Exception cannot swallow the wait, and an error is explained in the unit\'s words', async ({page}) => {
 await mockApi(page);
 await open(page, 'try:\n    n = input("How many? ")\nexcept Exception:\n    print("caught")\nprint(int(n) * 2)\n');
 await expect(panel(page).getByText('Your program asks: How many?')).toBeVisible({timeout: 45000});
 await expect(screen(page)).not.toContainText('caught');
 await reply(page, 'lots', 1);
 await expect(panel(page).locator('.result')).toContainText('Line 5', {timeout: 45000});
 await expect(screen(page)).toHaveText('How many? lots\n');
});

test('the button is offered only for a program that calls input(), and changing the code closes the game', async ({page}) => {
 await mockApi(page);
 await page.goto('/preview?lesson=py.validate-input&card=4');
 await page.getByLabel('Your Python code').fill('print("no questions here")');
 await expect(page.getByRole('button', {name: 'Play it live'})).toHaveCount(0);
 await page.getByLabel('Your Python code').fill('name = input("Name? ")\nprint("Hi", name)');
 await page.getByRole('button', {name: 'Play it live'}).click();
 await expect(replyBox(page)).toBeEnabled({timeout: 45000});
 await page.getByLabel('Your Python code').fill('name = input("Your name? ")\nprint("Hi", name)');
 await expect(panel(page)).toHaveCount(0);
});

test.describe('axe', () => {
 test.use({bypassCSP: true});
 const AXE = path.join(__dirname, '..', 'node_modules', 'axe-core', 'axe.min.js');
 for (const size of [{name: 'desktop', width: 1280, height: 900}, {name: 'phone', width: 375, height: 812}]) {
  test(`a game in progress, ${size.name}: no WCAG A or AA findings, no sideways scroll`, async ({page}) => {
   await page.setViewportSize(size);
   await mockApi(page);
   await open(page);
   await reply(page, 'four', 1);
   await expect(replyBox(page)).toBeEnabled({timeout: 45000});
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
