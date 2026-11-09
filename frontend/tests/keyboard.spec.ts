import {test, expect, Page, Locator} from '@playwright/test';
import lessons from '../../backend/tests/fixtures/legacy_lessons_v1.json';
import catalog from '../../backend/tests/fixtures/catalog_v1.json';
import goals from '../../backend/tests/fixtures/goals_v1.json';

/* QA-01a. These tests use the keyboard only: no click(), fill() or focus() anywhere in this file.
 * That matters. Tests that call focus() jump over whatever blocks a keyboard user, which is how the
 * editor stopped anyone tabbing to the Run button without any test noticing. Python is real. */

async function mockApi(page: Page) {
 await page.route('**/api/**', route => {
  const path = new URL(route.request().url()).pathname;
  let body: unknown = {};
  if (path === '/api/me') body = {id: 1, email: 'test@example.com', role: 'student'};
  else if (path === '/api/lessons') body = lessons;
  else if (path === '/api/catalog') body = catalog;
  else if (path === '/api/goals') body = goals;
  else if (path === '/api/goal') body = {goal: 'scratch', chosen: true, asked: true};
  else if (path === '/api/awards') body = {xp: 0, completed: [], badges: []};
  else if (path === '/api/history' || path === '/api/family' || path === '/api/progress') body = [];
  else if (path === '/api/recommendation') body = {kind: 'start', reason: 'Start here.', course: null, unit: null, lesson: null};
  else if (path === '/api/check' || path === '/api/attempts') body = {passed: true, result: 'passed', feedback: 'Your adventure works.', assessment: 'browser_checked', xp: 100};
  return route.fulfill({contentType: 'application/json', body: JSON.stringify(body)});
 });
}

const editor = (page: Page) => page.getByLabel('Your Python code');
const focused = (target: Locator) => target.evaluate(el => el === document.activeElement);

/** Presses Tab until target has focus, leaving the editor the way a learner must. Fails if it never gets there. */
async function tabTo(page: Page, target: Locator, most = 40) {
 const stops: string[] = [];
 for (let i = 0; i < most; i++) {
  if (await target.count() && await focused(target)) return;
  const inEditor = await editor(page).count() && await focused(editor(page));
  if (inEditor) await page.keyboard.press('Escape');
  await page.keyboard.press('Tab');
  stops.push(await page.evaluate(() => (document.activeElement as HTMLElement).tagName + ' ' + (document.activeElement as HTMLElement).innerText?.slice(0, 30)));
 }
 throw new Error(`Tab never reached the target. Stops: ${stops.join(' | ')}`);
}

async function press(page: Page, name: string | RegExp) {
 await tabTo(page, page.getByRole('button', {name, exact: typeof name === 'string'}));
 await page.keyboard.press('Enter');
}

test.beforeEach(async ({page}) => { await mockApi(page); });

test('the skip link is the first stop, and moves focus past the navigation', async ({page}) => {
 await page.goto('/learn/hello');
 await page.keyboard.press('Tab');
 await expect(page.getByRole('link', {name: /Skip/})).toBeFocused();
 await page.keyboard.press('Enter');
 await page.keyboard.press('Tab');
 const inNavigation = await page.evaluate(() => !!document.activeElement?.closest('nav'));
 expect(inNavigation).toBe(false);
});

test('a whole lesson works from the keyboard: cards, prediction, code, run and next', async ({page}) => {
 test.setTimeout(120000);
 await page.goto('/learn/hello');
 await expect(page.getByText('Card 1 of 5')).toBeVisible();
 await press(page, 'Continue →');
 await expect(page.getByRole('heading', {name: 'Watch the story take shape'})).toBeVisible();
 await press(page, 'Continue →');
 await press(page, 'The castle message');
 await press(page, 'Continue →');
 await expect(editor(page)).toHaveValue(lessons[0].example);
 await press(page, 'Start my challenge');
 await expect(editor(page)).toHaveValue(lessons[0].starter);

 await tabTo(page, editor(page));
 await page.keyboard.press('ControlOrMeta+a');
 await page.keyboard.type('print("You wake up in a cave.")\nprint("A dragon yawns.")');
 await press(page, 'Run & check challenge');
 await expect(page.locator('.execution-output')).toContainText('A dragon yawns.', {timeout: 60000});
 const next = page.getByRole('button', {name: 'Next quest →'});
 await expect(next).toBeEnabled();
 await press(page, 'Next quest →');
 await expect(page).toHaveURL('/learn/variables');
});

test('in the editor: Tab types spaces, Esc then Tab moves on, and the code is untouched', async ({page}) => {
 await page.goto('/preview?lesson=hello&card=5');
 await expect(editor(page)).toBeVisible();
 await tabTo(page, editor(page));
 const start = await editor(page).inputValue();

 await page.keyboard.press('Tab');
 await expect(editor(page)).toBeFocused();
 await expect(editor(page)).toHaveValue('    ' + start);

 await page.keyboard.press('Escape');
 await page.keyboard.press('Tab');
 await expect(page.getByRole('button', {name: 'Run & check challenge'})).toBeFocused();
 await expect(editor(page)).toHaveValue('    ' + start);
});

test('Esc only lasts for the next key, and coming back to the editor starts afresh', async ({page}) => {
 await page.goto('/preview?lesson=hello&card=5');
 await expect(editor(page)).toBeVisible();
 await tabTo(page, editor(page));
 await page.keyboard.press('ControlOrMeta+a');
 await page.keyboard.press('Backspace');

 // A key after Esc cancels it, so an accidental Esc cannot throw a learner out of the editor mid-line.
 await page.keyboard.press('Escape');
 await page.keyboard.type('x');
 await page.keyboard.press('Tab');
 await expect(editor(page)).toBeFocused();
 await expect(editor(page)).toHaveValue('x    ');

 // Leave, come back with Shift + Tab, and Tab types spaces again.
 await page.keyboard.press('Escape');
 await page.keyboard.press('Tab');
 await expect(editor(page)).not.toBeFocused();
 await page.keyboard.press('Shift+Tab');
 await expect(editor(page)).toBeFocused();
 await page.keyboard.press('Tab');
 await expect(editor(page)).toBeFocused();
});

test('Shift + Tab still goes back out of the editor, without Esc', async ({page}) => {
 await page.goto('/preview?lesson=hello&card=5');
 await expect(editor(page)).toBeVisible();
 await tabTo(page, editor(page));
 const start = await editor(page).inputValue();
 await page.keyboard.press('Shift+Tab');
 await expect(editor(page)).not.toBeFocused();
 await expect(editor(page)).toHaveValue(start);
});

test('the page tells learners how to leave the editor', async ({page}) => {
 await page.goto('/preview?lesson=hello&card=5');
 const described = await editor(page).evaluate(el => (el.getAttribute('aria-describedby') ?? '').split(/\s+/).map(id => document.getElementById(id)?.textContent ?? '').join(' '));
 expect(described).toContain('press Esc and then Tab');
});

test('every stop on a lesson page shows where the focus is, and nothing forces its own tab order', async ({page}) => {
 await page.goto('/preview?lesson=hello&card=5');
 await expect(editor(page)).toBeVisible();
 expect(await page.locator('[tabindex]:not([tabindex="0"]):not([tabindex="-1"])').count()).toBe(0);
 const missing: string[] = [];
 for (let i = 0; i < 30; i++) {
  if (await focused(editor(page))) await page.keyboard.press('Escape');
  await page.keyboard.press('Tab');
  const stop = await page.evaluate(() => {
   const el = document.activeElement as HTMLElement;
   if (el === document.body) return null;
   // The editor's ring is on the box around it, so that it also goes round the line numbers.
   const style = getComputedStyle(el.id === 'code' ? el.closest('.code-editor')! : el);
   const shown = (style.outlineStyle !== 'none' && parseFloat(style.outlineWidth) > 0) || style.boxShadow !== 'none';
   return {shown, name: el.tagName + ' ' + (el.innerText ?? '').slice(0, 30)};
  });
  if (!stop) break;
  if (!stop.shown) missing.push(stop.name);
 }
 expect(missing).toEqual([]);
});
