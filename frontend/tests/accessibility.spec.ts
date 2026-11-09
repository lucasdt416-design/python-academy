import {test, expect, Page} from '@playwright/test';
import path from 'node:path';
import lessons from '../../backend/tests/fixtures/legacy_lessons_v1.json';
import catalog from '../../backend/tests/fixtures/catalog_v1.json';
import goals from '../../backend/tests/fixtures/goals_v1.json';

/* QA-01a: the accessibility audit. axe-core checks each page against WCAG 2.0, 2.1 and 2.2, levels A
 * and AA, at a desktop and a phone width, and every finding fails the test. axe finds about a third
 * of real problems, so this sits beside the keyboard tests (keyboard.spec.ts) and the manual sheet
 * for real screen readers (docs/plan/screen-reader-test-sheet.md), never instead of them. */

const AXE = path.join(__dirname, '..', 'node_modules', 'axe-core', 'axe.min.js');
const TAGS = ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa'];
const WIDTHS = [{name: 'desktop', width: 1280, height: 900}, {name: 'phone', width: 375, height: 812}];

async function mockApi(page: Page, role: string | null) {
 await page.route('**/api/**', route => {
  const path = new URL(route.request().url()).pathname;
  let body: unknown = {}, status = 200;
  if (path === '/api/me') { status = role ? 200 : 401; body = role ? {id: 1, email: 'test@example.com', role} : {detail: 'Sign in to continue'}; }
  else if (path === '/api/lessons') body = lessons;
  else if (path === '/api/catalog') body = catalog;
  else if (path === '/api/goals') body = goals;
  else if (path === '/api/goal') body = {goal: 'scratch', chosen: true, asked: true};
  else if (path === '/api/awards') body = {xp: 100, completed: ['hello'], badges: []};
  else if (path === '/api/progress') body = ['hello'];
  else if (path === '/api/history' || path === '/api/family') body = [];
  else if (path === '/api/recommendation') body = {kind: 'continue', reason: "You're partway through Python Foundations.", course: 'py', unit: 'py.u01', lesson: 'variables', options: [], notes: [], rules_version: 1};
  else if (path === '/api/check' || path === '/api/attempts') body = {passed: true, result: 'passed', feedback: 'Your adventure works.', assessment: 'browser_checked', xp: 100};
  return route.fulfill({status, contentType: 'application/json', body: JSON.stringify(body)});
 });
}

/** Runs axe and returns one line per finding, naming the rule and the first few elements. */
async function audit(page: Page) {
 await page.addScriptTag({path: AXE});
 const found = await page.evaluate(async tags => {
  const axe = (window as unknown as {axe: {run: (c: Document, o: object) => Promise<{violations: {id: string; nodes: {target: string[]}[]}[]}>}}).axe;
  const result = await axe.run(document, {runOnly: {type: 'tag', values: tags}});
  return result.violations.map(v => `${v.id}: ${v.nodes.slice(0, 3).map(n => n.target.join(' ')).join(', ')}`);
 }, TAGS);
 return found;
}

const PAGES: {name: string; role: string | null; url: string; ready: (page: Page) => Promise<void>}[] = [
 {name: 'welcome, signed out', role: null, url: '/', ready: p => expect(p.getByRole('link', {name: /Continue with Google/})).toBeVisible()},
 {name: 'student home', role: 'student', url: '/', ready: p => expect(p.getByRole('heading', {name: /Welcome back/})).toBeVisible()},
 {name: 'course page', role: 'student', url: '/courses/py', ready: p => expect(p.getByRole('heading').first()).toBeVisible()},
 ...[1, 2, 3, 4, 5].map(card => ({name: `lesson card ${card}`, role: 'student', url: `/preview?lesson=hello&card=${card}`, ready: (p: Page) => expect(p.getByText(`Card ${card} of 5`)).toBeVisible()})),
];

for (const size of WIDTHS) {
 for (const target of PAGES) {
  test(`${target.name}, ${size.name}: no WCAG A or AA findings`, async ({page}) => {
   await page.setViewportSize(size);
   // Scanning mid-animation reports colours that a learner never sees once it settles (handoff 32).
   await page.emulateMedia({reducedMotion: 'reduce'});
   await mockApi(page, target.role);
   await page.goto(target.url);
   await target.ready(page);
   expect(await audit(page)).toEqual([]);
  });
 }
}

test('a challenge result, pass and error, has no WCAG A or AA findings', async ({page}) => {
 test.setTimeout(120000);
 await page.emulateMedia({reducedMotion: 'reduce'});
 await mockApi(page, 'student');
 await page.goto('/preview?lesson=hello&card=5');
 const editor = page.getByLabel('Your Python code');
 await editor.fill('print("A cave.")\nprint("A dragon yawns.")');
 await page.getByRole('button', {name: 'Run & check challenge'}).click();
 await expect(page.locator('.execution-output')).toContainText('A dragon yawns.', {timeout: 60000});
 expect(await audit(page)).toEqual([]);
 await editor.fill('print("A cave."\n');
 await page.getByRole('button', {name: 'Run & check challenge'}).click();
 await expect(page.getByRole('button', {name: /Go to line/})).toBeVisible({timeout: 60000});
 expect(await audit(page)).toEqual([]);
});

test('the audit really finds problems: a button with no name fails it', async ({page}) => {
 await mockApi(page, null);
 await page.goto('/');
 await page.evaluate(() => document.body.append(Object.assign(document.createElement('button'), {className: 'nameless'})));
 expect((await audit(page)).join('\n')).toContain('button-name');
});
