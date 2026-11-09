import {test, expect, Page} from '@playwright/test';
// Visual redesign (docs/design/prototype/index.html): lesson pictures, the quest ticket, worked-example
// markers and the home page playground. The API answers are the recorded real ones used by the unit specs.
import u1 from './fixtures/lesson-units-api.json';
import u2 from './fixtures/unit2-api.json';
import u2b from './fixtures/unit2-part2-api.json';
import u3a from './fixtures/unit3-api.json';
import u3 from './fixtures/unit3-part2-api.json';

// Every released lesson and the picture made for it. Written out here, not imported, so a wrong
// entry in app/lesson-art.tsx fails the test.
const PICTURES: Record<string, string> = {
 hello: 'art-hello', variables: 'art-variables', input: 'art-input', choices: 'art-choices', adventure: 'art-adventure',
 'py.arithmetic': 'art-arithmetic', 'py.int-float': 'art-int-float', 'py.convert-input': 'art-convert', 'py.compare': 'art-compare', 'py.boolean-logic': 'art-logic', 'py.elif': 'art-elif',
 'py.while-loops': 'art-while', 'py.loop-termination': 'art-three-tries', 'py.for-range': 'art-for-range', 'py.accumulate': 'art-accumulate', 'py.nested-loops': 'art-nested',
};
const units: Record<string, unknown> = {...u1.units, ...u2b.units, ...u3.units};
const plans: Record<string, unknown> = {...u2.plans, ...u2b.plans, ...u3a.plans, ...u3.plans};

async function mockApi(page: Page, override: Record<string, unknown> = {}) {
 const requests: string[] = [];
 await page.route('**/api/**', async route => {
  const path = new URL(route.request().url()).pathname; requests.push(path);
  let status = 200, json: unknown = {};
  const unit = /^\/api\/units\/([^/]+)\/lessons$/.exec(path)?.[1], plan = /^\/api\/checks\/(.+)$/.exec(path)?.[1];
  if (path in override) json = override[path];
  else if (path === '/api/catalog') json = u3.catalog;
  else if (unit && unit in units) json = units[unit];
  else if (plan && plan in plans) json = plans[plan];
  else if (path === '/api/me') { status = 401; json = {detail: 'Sign in to continue'}; }
  else { status = 404; json = {detail: 'Not Found'}; }
  await route.fulfill({status, contentType: 'application/json', body: JSON.stringify(json)});
 });
 return requests;
}
const violations = new WeakMap<Page, string[]>();
test.beforeEach(async ({page}) => {
 const found: string[] = []; violations.set(page, found);
 await page.exposeFunction('reportCspViolation', (v: string) => found.push(v));
 await page.addInitScript(() => document.addEventListener('securitypolicyviolation', e => (window as unknown as {reportCspViolation: (v: string) => void}).reportCspViolation(`${e.effectiveDirective} blocked ${e.blockedURI || 'inline'}`)));
});
test.afterEach(async ({page}) => { expect(violations.get(page)).toEqual([]); });

test('each of the 16 lessons shows its own picture, on the course page and its lesson page', async ({page}) => {
 await mockApi(page);
 await page.goto('/courses/py');
 const rows = page.locator('a.row');
 await expect(rows).toHaveCount(16);
 const seen: Record<string, string | null> = {};
 for (const row of await rows.all()) {
  const id = new URL(await row.getAttribute('href') ?? '', 'http://x').searchParams.get('lesson')!;
  const art = row.locator('svg.art');
  seen[id] = await art.getAttribute('data-art');
  // A real drawing, not an empty frame.
  expect(await art.locator('path, rect, circle, ellipse, text').count(), id).toBeGreaterThan(5);
 }
 expect(seen).toEqual(PICTURES);
 for (const [id, art] of [['hello', 'art-hello'], ['py.compare', 'art-compare'], ['py.nested-loops', 'art-nested']]) {
  await page.goto(`/preview?lesson=${id}`);
  const picture = page.locator('.lhead svg.art');
  await expect(picture).toHaveAttribute('data-art', art);
  await expect(picture).toHaveAttribute('role', 'img');
  expect((await picture.getAttribute('aria-label'))!.length).toBeGreaterThan(10);
 }
});

test('a lesson without a picture of its own gets the plain one', async ({page}) => {
 await mockApi(page, {'/api/catalog': u1.catalog});
 await page.goto('/preview?lesson=fixture.double');
 await expect(page.getByRole('heading', {level: 1, name: 'Double a number'})).toBeVisible();
 const picture = page.locator('.lhead svg.art');
 await expect(picture).toHaveAttribute('data-art', 'fallback');
 await expect(picture).toHaveAttribute('aria-label', 'Green hills under a small py sign');
 await expect(page.locator('.unit-lesson svg.art')).toHaveAttribute('data-art', 'fallback');
 await expect(page.locator('.story-world')).toHaveCount(0);
});

const ticket = (page: Page) => page.getByRole('region', {name: 'Done when your program gives'});
for (const [id, visible, hidden] of [['py.arithmetic', 3, 2], ['py.compare', 4, 2], ['py.while-loops', 3, 2]] as const)
 test(`the challenge's quest ticket for ${id} shows its ${visible} visible cases and ${hidden} locked`, async ({page}) => {
  await mockApi(page);
  await page.goto(`/preview?lesson=${id}&card=5`);
  const plan = plans[id] as {cases: {visibility: string; description: string; expected?: string}[]};
  const shown = plan.cases.filter(c => c.visibility === 'visible');
  expect(shown).toHaveLength(visible);
  await expect(ticket(page).locator('li.case-visible')).toHaveCount(visible);
  await expect(ticket(page).locator('li.case-visible')).toHaveText(shown.map(c => new RegExp(c.description.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'))));
  await expect(ticket(page).locator('li.case-hidden')).toHaveText(`${hidden} more cases you can’t see`);
  // Hidden cases are only counted: their descriptions are not shown.
  for (const c of plan.cases.filter(c => c.visibility === 'hidden')) await expect(ticket(page)).not.toContainText(c.description);
 });

test('the ticket never shows a hidden case\'s expected output, even if a plan held one', async ({page}) => {
 const plan = JSON.parse(JSON.stringify(plans['py.arithmetic']));
 plan.cases[3].expected = 'HIDDEN-EXPECTED-142';
 await mockApi(page, {'/api/checks/py.arithmetic': plan});
 await page.goto('/preview?lesson=py.arithmetic&card=5');
 await expect(ticket(page).locator('li.case-hidden')).toHaveText('2 more cases you can’t see');
 await expect(page.locator('body')).not.toContainText('HIDDEN-EXPECTED-142');
});

test('a challenge without a browser check has no ticket, and no plan is asked for', async ({page}) => {
 const requests = await mockApi(page);
 await page.goto('/preview?lesson=hello&card=5');
 await expect(page.getByText('Card 5 of 5')).toBeVisible();
 await expect(ticket(page)).toHaveCount(0);
 expect(requests.filter(p => p.startsWith('/api/checks/'))).toEqual([]);
});

test('worked-example markers pair each print() line with its output line, and leave the text exact', async ({page}) => {
 await mockApi(page);
 await page.goto('/preview?lesson=py.arithmetic&card=2');
 const lesson = (units['py.u02'] as {id: string; example: string; exampleOutput: string}[]).find(l => l.id === 'py.arithmetic')!;
 const code = page.locator('.teaching-panel .example-code'), output = page.locator('.teaching-panel pre.output');
 await expect(code).toHaveText(lesson.example);
 await expect(output).toHaveText(lesson.exampleOutput);
 const codeMarks = await code.locator('[data-mark]').evaluateAll(els => els.map(e => [e.textContent, e.getAttribute('data-mark')]));
 expect(codeMarks).toEqual([['print(score)', '1'], ['print(coins // 5)', '2'], ['print(coins % 5)', '3']]);
 expect(await output.locator('[data-mark]').evaluateAll(els => els.map(e => [e.textContent, e.getAttribute('data-mark')]))).toEqual([['53', '1'], ['2', '2'], ['3', '3']]);
 // A loop's output can't be paired line by line, so it gets no markers.
 await page.goto('/preview?lesson=py.while-loops&card=2');
 await expect(page.locator('.teaching-panel .example-code')).toBeVisible();
 await expect(page.locator('.teaching-panel [data-mark]')).toHaveCount(0);
});

test('the home page playground previews // and % like Python, and never loads Python', async ({page}) => {
 const requests: string[] = [];
 page.on('request', r => requests.push(r.url()));
 await mockApi(page);
 await page.goto('/');
 const play = page.getByRole('region', {name: /count_the_treasure\.py/});
 await expect(play.getByText('Preview', {exact: true})).toBeVisible();
 const out = play.getByTestId('pg-out');
 await expect(out).toHaveText('3\n2');
 await play.getByLabel('coins').fill('-7');
 await expect(out).toHaveText('-2\n3');  // Python: -7 // 5 is -2 and -7 % 5 is 3
 await play.getByLabel('friends').fill('0');
 await expect(out).toContainText('ZeroDivisionError');
 await play.getByLabel('friends').fill('2.5');
 await expect(out).toHaveText('Type a whole number in each box.');
 await page.waitForLoadState('networkidle');
 expect(requests.filter(u => /pyodide|python-worker|check-runner/.test(u))).toEqual([]);
});

test('the sign-in line states the real account rules', async ({page}) => {
 await mockApi(page);
 await page.goto('/');
 await expect(page.getByText('Learners 13 and up sign in through a parent\'s invitation. Anyone over 25 can start a family account. Accounts for learners 16 and up on their own are planned, not open yet.')).toBeVisible();
 await expect(page.getByRole('link', {name: /Sign in with Google/})).toHaveAttribute('href', '/auth/google');
 await expect(page.getByText('Design prototype')).toHaveCount(0);
});

for (const width of [390, 1280])
 test(`no page scrolls sideways at ${width} px, and cards do not move with reduced motion`, async ({page}) => {
  await page.setViewportSize({width, height: 900});
  await page.emulateMedia({reducedMotion: 'reduce'});
  await mockApi(page);
  for (const url of ['/', '/courses', '/courses/py', '/preview?lesson=py.arithmetic&card=2', '/preview?lesson=py.compare&card=5', '/preview?lesson=hello&card=4']) {
   await page.goto(url);
   await page.waitForLoadState('networkidle');
   expect(await page.evaluate(() => document.documentElement.scrollWidth), url).toBeLessThanOrEqual(width);
   for (const name of await page.locator('.quest-card, .badge-earned').evaluateAll(els => els.map(e => getComputedStyle(e).animationName))) expect(name, url).toBe('none');
  }
 });
