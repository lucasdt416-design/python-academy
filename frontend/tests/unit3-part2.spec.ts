import {test, expect, Page} from '@playwright/test';
// The API's real answers for Python unit 3, part 2, checked against the API by
// backend/tests/test_unit3_part2.py; part 1's are used too, to finish the whole unit. Python runs for
// real in Pyodide here, so each test also proves the browser reports what the recording expects.
import recorded from './fixtures/unit3-part2-api.json';
import part1 from './fixtures/unit3-api.json';
import goals from '../../backend/tests/fixtures/goals_v1.json';

/* EDU-03 part 2: py.accumulate and py.nested-loops end to end, and the unit's ending. */

type Scenario = (typeof recorded.scenarios)[number];
const SCENARIOS = [...recorded.scenarios, ...part1.scenarios] as unknown as Scenario[];
const scenario = (name: string) => SCENARIOS.find(s => s.name === name)!;
const UNIT = recorded.units['py.u03'];
const LESSONS = [
 {id: 'py.accumulate', key: 'accumulate', title: 'Keep the score', badge: 'Tally keeper'},
 {id: 'py.nested-loops', key: 'nested', title: 'Rooms on the map', badge: 'Map reader'},
];

async function mockApi(page: Page, {student = false}: {student?: boolean} = {}) {
 const posted: Record<string, unknown>[] = [], answers: {path: string; text: string}[] = [];
 const everything = recorded.catalog.courses.flatMap(c => c.units.filter(u => u.status === 'released').flatMap(u => u.lessons.map(l => l.id)));
 await page.route('**/api/**', async route => {
  const path = new URL(route.request().url()).pathname;
  let status = 200, json: unknown = {};
  const unit = /^\/api\/units\/([^/]+)\/lessons$/.exec(path)?.[1], plan = /^\/api\/checks\/(.+)$/.exec(path)?.[1];
  if (path === '/api/catalog') json = recorded.catalog;
  else if (path === '/api/me') ({status, json} = student ? {status: 200, json: {id: 1, email: 'test@example.com', role: 'student'}} : {status: 401, json: {detail: 'Sign in to continue'}});
  else if (path === '/api/awards') json = {xp: everything.length * 100, completed: everything, badges: []};
  else if (path === '/api/recommendation') json = recorded.recommendation;
  else if (path === '/api/goal') json = {goal: 'scratch', chosen: true, asked: true};
  else if (path === '/api/goals') json = goals;
  else if (path === '/api/progress') json = everything;
  else if (path === '/api/history' || path === '/api/family') json = [];
  else if (unit === 'py.u03') json = UNIT;
  else if (unit) { status = 404; json = {detail: 'Not Found'}; }
  else if (plan) json = ({...part1.plans, ...recorded.plans} as Record<string, unknown>)[plan];
  else if (path === '/api/check') {
   const body = route.request().postDataJSON(); posted.push(body);
   const match = SCENARIOS.find(s => JSON.stringify(s.request) === JSON.stringify(body));
   ({status = 200, json} = match ? {json: match.response} : {status: 500, json: {detail: 'not a recorded request'}});
  }
  const text = JSON.stringify(json); answers.push({path, text});
  await route.fulfill({status, contentType: 'application/json', body: text});
 });
 return {posted, answers};
}
const violations = new WeakMap<Page, string[]>();
test.beforeEach(async ({page}) => {
 const found: string[] = []; violations.set(page, found);
 await page.exposeFunction('reportCspViolation', (v: string) => found.push(v));
 await page.addInitScript(() => document.addEventListener('securitypolicyviolation', e => (window as unknown as {reportCspViolation: (v: string) => void}).reportCspViolation(`${e.effectiveDirective} blocked ${e.blockedURI || 'inline'}`)));
});
test.afterEach(async ({page}) => { expect(violations.get(page)).toEqual([]); });

const result = (page: Page) => page.locator('#code-feedback');
const hints = (page: Page) => page.getByRole('region', {name: 'Hints'});
async function runScenario(page: Page, s: Scenario, goto = true) {
 if (goto) await page.goto(`/preview?lesson=${s.request.lesson_id}&card=5`);
 await page.getByLabel('Your Python code').fill(s.request.code);
 await page.getByRole('button', {name: 'Run & check challenge'}).click();
 await expect(page.getByRole('button', {name: 'Run & check challenge'})).toBeEnabled({timeout: 45000});
}
async function toNextLesson(page: Page, index: number) {
 const next = UNIT[index];
 await page.getByRole('button', {name: 'Next quest →'}).click();
 await page.getByRole('button', {name: 'Continue →'}).click();
 await page.getByRole('button', {name: 'Continue →'}).click();
 await page.getByRole('group', {name: next.question}).getByRole('button', {name: next.options[next.answer], exact: true}).click();
 await page.getByRole('button', {name: 'Continue →'}).click();
 await page.getByRole('button', {name: 'Start my challenge'}).click();
}

// The cards

for (const lesson of LESSONS) {
 test(`${lesson.title}: every card shows, and a prediction must be right to continue`, async ({page}) => {
  await mockApi(page);
  const data = UNIT.find(l => l.id === lesson.id)!;
  await page.goto(`/preview?lesson=${lesson.id}`);
  await expect(page.getByRole('heading', {level: 2, name: data.learnTitle})).toBeVisible();
  await expect(page.getByText(data.learn)).toBeVisible();
  await page.getByRole('button', {name: 'Continue →'}).click();
  await expect(page.locator('.teaching-panel .example-code')).toHaveText(data.example);
  await expect(page.locator('.teaching-panel pre.output')).toHaveText(data.exampleOutput);
  await page.getByRole('button', {name: 'Continue →'}).click();
  const prediction = page.getByRole('group', {name: data.question});
  const wrong = data.options.findIndex((_, i) => i !== data.answer);
  await prediction.getByRole('button', {name: data.options[wrong], exact: true}).click();
  await expect(page.getByRole('status').filter({hasText: 'Let’s look again.'})).toContainText(data.why);
  await expect(page.getByRole('button', {name: 'Continue →'})).toBeDisabled();
  await prediction.getByRole('button', {name: data.options[data.answer], exact: true}).click();
  await page.getByRole('button', {name: 'Continue →'}).click();
  await expect(page.getByText(data.guided)).toBeVisible();
  await page.getByRole('button', {name: 'Run Python →'}).click();
  await expect(result(page)).toContainText('Ran · not checked', {timeout: 45000});
  await expect(page.locator('.execution-output')).toHaveText(data.exampleOutput);
  await page.getByRole('button', {name: 'Start my challenge'}).click();
  await expect(page.getByText(data.challenge)).toBeVisible();
  await expect(page.getByLabel('Your Python code')).toHaveValue(data.starter);
 });

 test(`${lesson.title}: a correct program passes, with the badge and other ways`, async ({page}) => {
  const s = scenario(`${lesson.key} passed`);
  const {posted} = await mockApi(page);
  await runScenario(page, s);
  await expect(result(page)).toContainText('Check passed');
  await expect(page.getByText(`${lesson.badge} badge earned!`)).toBeVisible();
  await expect(page.getByRole('region', {name: 'Other ways to do it'})).toBeVisible();
  expect(posted).toEqual([s.request]);
  expect(Object.keys((posted[0].runs as object[])[0]).sort()).toEqual(['error_type', 'id', 'line', 'output', 'status']);
 });

 test(`${lesson.title}: an endless loop is stopped at 3 seconds, explained, and is not a pass`, async ({page}) => {
  const s = scenario(`${lesson.key} endless loop`);
  const {posted} = await mockApi(page);
  const started = Date.now();
  await runScenario(page, s);
  expect(Date.now() - started).toBeLessThan(40000);
  await expect(result(page)).toContainText('Your program kept running');
  await expect(page.locator('.execution-output')).toContainText('(stopped: still running after 3 seconds)');
  expect(posted).toEqual([s.request]);
  await expect(page.getByText(/badge earned!/)).toHaveCount(0);
 });

 test(`${lesson.title}: a module the browser does not have is "Not checked"`, async ({page}) => {
  const s = scenario(`${lesson.key} unsupported`);
  const {posted} = await mockApi(page);
  await runScenario(page, s);
  await expect(result(page)).toHaveText('Not checked' + s.response.feedback);
  expect(posted).toEqual([s.request]);
 });
}

test('Keep the score, Try it: the total inside the loop shows what the card predicted', async ({page}) => {
 await mockApi(page);
 const data = UNIT.find(l => l.id === 'py.accumulate')!;
 await page.goto('/preview?lesson=py.accumulate&card=4');
 await page.getByLabel('Your Python code').fill(data.example.replace('total = 0\n', '').replace('    coins = int', '    total = 0\n    coins = int'));
 await page.getByRole('button', {name: 'Run Python →'}).click();
 await expect(result(page)).toContainText('Ran · not checked', {timeout: 45000});
 await expect(page.locator('.execution-output')).toHaveText('8\n2.6666666666666665');
});

const NEEDS_WORK = [
 {name: 'accumulate needs_work', button: 'Show a hint about this check', label: 'About this check', hint: 'With rounds of 10, 0 and 5, the lines are 15, 1 and 5.0. If your total says 5, it goes back to 0 on every turn: its start line belongs above the loop.'},
 {name: 'accumulate counter from 1', button: 'Show a hint about this check', label: 'About this check', hint: 'With one round of 10 points, the lines are 10, 0 and 10.0. A total or a counter that starts above 0 is already wrong here, and // gives 10 where / gives 10.0.'},
 {name: 'accumulate out of replies', button: 'Show a hint about this error', label: 'About this error', hint: 'Your loop asked for more points than there were rounds. range(rounds) already runs exactly once per round.'},
 {name: 'nested needs_work', button: 'Show a hint about this check', label: 'About this check', hint: 'With 2 rows of 3 columns, the coins go 1, 2, 3, then 2, 4, 6, and the total is 18. If you see 1, 2, 2, 4, 3, 6, the two loops are the wrong way round. If only the first row printed, the inner counter did not start again.'},
 {name: 'nested inner not reset', button: 'Show a hint about this check', label: 'About this check', hint: 'With 2 rows of 3 columns, the coins go 1, 2, 3, then 2, 4, 6, and the total is 18. If you see 1, 2, 2, 4, 3, 6, the two loops are the wrong way round. If only the first row printed, the inner counter did not start again.'},
];
for (const {name, button, label, hint} of NEEDS_WORK) {
 test(`${name}: the judge says what happened, and the hint tagged for it comes first`, async ({page}) => {
  const s = scenario(name);
  const {posted} = await mockApi(page);
  await runScenario(page, s);
  await expect(result(page)).toHaveText('Not yet' + s.response.feedback);
  await expect(page.getByText(/badge earned!/)).toHaveCount(0);
  await expect(hints(page).getByRole('button')).toHaveText(button);
  await hints(page).getByRole('button').click();
  await expect(hints(page).getByRole('listitem')).toHaveText([`${label}. ${hint}`]);
  await expect(hints(page).getByRole('button')).toHaveText('Show a nudge');
  expect(posted).toEqual([s.request]);
 });
}

test('nested prints for ever: the output limit stops it, and it is not a pass', async ({page}) => {
 const s = scenario('nested prints for ever');
 const {posted} = await mockApi(page);
 await runScenario(page, s);
 await expect(result(page)).toContainText('Too much output');
 await expect(page.locator('.execution-output')).toContainText('(stopped: too much output)');
 expect(posted).toEqual([s.request]);
 await expect(page.getByText(/badge earned!/)).toHaveCount(0);
});

const ERRORS = [
 {name: 'accumulate zero division', title: 'Division by zero', where: 'Line 11', line: 11, python: 'ZeroDivisionError: division by zero', secret: 'division by zero',
  hint: 'The average divides by the number of rounds played, and that is always at least 1. Check which number comes after the /.'},
 {name: 'nested indentation error', title: 'The lines inside this for loop need indenting', where: 'Line 4', line: 4, python: "IndentationError: expected an indented block after 'for' statement on line 3", secret: 'expected an indented block',
  hint: 'Each loop\'s block goes four spaces further in than its for line: four for the inner for line, and eight for the lines inside it.'},
];
for (const e of ERRORS) {
 test(`${e.name}: the friendly explanation, the line, and Python's message kept in the browser`, async ({page}) => {
  const s = scenario(e.name);
  const {posted} = await mockApi(page);
  await runScenario(page, s);
  await expect(result(page)).toContainText('Python stopped');
  await expect(result(page)).toContainText(e.title);
  await expect(result(page)).toContainText(e.where);
  await expect(page.locator('.code-gutter .gutter-line.error')).toHaveText(`▶${e.line}`);
  await page.getByText('Show Python’s message').click();
  await expect(page.locator('.python-message')).toContainText(e.python);
  await hints(page).getByRole('button', {name: 'Show a hint about this error'}).click();
  await expect(hints(page).getByRole('listitem')).toHaveText([`About this error. ${e.hint}`]);
  expect(JSON.stringify(posted)).not.toContain(e.secret);
  expect(posted).toEqual([s.request]);
  await expect(page.getByText(/badge earned!/)).toHaveCount(0);
 });
}

const HIDDEN = [
 {name: 'accumulate hidden', text: 'a longer game (a hidden test case)', hint: 'Check a longer game: use the number of rounds in range() and in the average, and / rather than //, which throws away the part after the point.', secrets: ['3.4']},
 {name: 'nested hidden', text: 'a map with more rows (a hidden test case)', hint: 'Check a map with more rows than the examples: the outer range() has to follow the rows reply.', secrets: ['60']},
];
for (const h of HIDDEN) {
 test(`${h.name}: a hidden case that fails is named by its description only, with its tagged hint`, async ({page}) => {
  await mockApi(page);
  await runScenario(page, scenario(h.name));
  await expect(result(page)).toContainText(h.text);
  const shown = await result(page).innerText();
  for (const value of h.secrets) expect(shown).not.toContain(value);
  await hints(page).getByRole('button', {name: 'Show a hint about this check'}).click();
  await expect(hints(page).getByRole('listitem')).toHaveText([`About this check. ${h.hint}`]);
 });
}

test('no check plan the page receives holds a hidden case\'s expected output', async ({page}) => {
 const {answers} = await mockApi(page);
 for (const name of ['accumulate passed', 'nested needs_work']) await runScenario(page, scenario(name));
 const plans = answers.filter(a => a.path.startsWith('/api/checks/')).map(a => JSON.parse(a.text));
 expect(plans).toHaveLength(2);
 for (const plan of plans) for (const c of plan.cases) expect('expected' in c).toBe(c.visibility === 'visible');
});

// The unit, complete

test('after the fifth lesson the unit is complete, and the page says so', async ({page}) => {
 await mockApi(page);
 for (const [i, key] of ['while', 'termination', 'for', 'accumulate', 'nested'].entries()) {
  if (i > 0) await toNextLesson(page, i);
  await runScenario(page, scenario(`${key} passed`), i === 0);
  await expect(page.getByText(/badge earned!/)).toBeVisible();
 }
 await expect(page.getByText('500 XP')).toBeVisible();
 await expect(page.getByText('5 of 5 badges earned · preview session')).toBeVisible();
 const done = page.locator('.chapter-complete');
 await expect(done.getByRole('heading')).toHaveText('Unit complete.');
 await expect(done).toContainText('You finished every lesson in Repeat and explore. See the course for what comes next.');
 await expect(done).not.toContainText('released so far');
 await expect(done.getByRole('link', {name: 'See the course'})).toHaveAttribute('href', '/courses/py');
 await expect(page.getByRole('button', {name: 'Next quest →'})).toHaveCount(0);
});

test('the student home after unit 3 says unit 4 is next and not written yet, with nothing to start', async ({page}) => {
 await mockApi(page, {student: true});
 await page.goto('/');
 const card = page.getByRole('region', {name: 'More lessons are on the way'});
 await expect(card.getByText("You've finished everything available on your path so far.")).toBeVisible();
 await expect(card.getByText('Python Foundations unit 4, Keep track of a world, is next on your path. Its lessons are not written yet.')).toBeVisible();
 await expect(card).not.toContainText('Repeat and explore');
 await expect(card.getByRole('link', {name: /^(Start|Continue)/})).toHaveCount(0);
});

test('the catalog and course page show unit 3 as whole, with its true summary and five lessons', async ({page}) => {
 await mockApi(page);
 await page.goto('/courses');
 await expect(page.getByText('3 of 12 units open')).toBeVisible();
 await page.goto('/courses/py');
 const unit = page.getByRole('article', {name: 'Repeat and explore'});
 await expect(unit.getByText('while and for loops that always finish, running totals, and loops inside loops.')).toBeVisible();
 await expect(unit.getByRole('link')).toHaveCount(5);
 await expect(page.getByRole('article', {name: 'Keep track of a world'}).getByText('Coming soon')).toBeVisible();
});

test('the nested loops challenge fits a phone, with no sideways scrolling, and nothing moves with reduced motion', async ({page}) => {
 await page.setViewportSize({width: 375, height: 812});
 await page.emulateMedia({reducedMotion: 'reduce'});
 await mockApi(page);
 await page.goto('/preview?lesson=py.accumulate&card=4');
 await expect(page.getByLabel('Reply 1')).toBeVisible();
 expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
 await runScenario(page, scenario('nested needs_work'));
 expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
 expect(await page.locator('.result, .result *').evaluateAll(els => els.every(el => getComputedStyle(el).animationName === 'none'))).toBe(true);
});
