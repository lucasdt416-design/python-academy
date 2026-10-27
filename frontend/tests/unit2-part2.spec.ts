import {test, expect, Page} from '@playwright/test';
// The API's real answers for Python unit 2, part 2, checked against the API by
// backend/tests/test_unit2_part2.py; part 1's are used too, to finish the whole unit. Python runs for
// real in Pyodide here, so each test also proves the browser reports what the recording expects.
import recorded from './fixtures/unit2-part2-api.json';
import part1 from './fixtures/unit2-api.json';

/* EDU-04 part 2: py.compare, py.boolean-logic and py.elif end to end, and the unit's ending. */

type Scenario = (typeof recorded.scenarios)[number];
const SCENARIOS = [...recorded.scenarios, ...part1.scenarios] as unknown as Scenario[];
const scenario = (name: string) => SCENARIOS.find(s => s.name === name)!;
const UNIT = recorded.units['py.u02'];
const LESSONS = [
 {id: 'py.compare', key: 'compare', title: 'Too high or too low?', badge: 'Riddle judge'},
 {id: 'py.boolean-logic', key: 'boolean', title: 'Close enough?', badge: 'Close call'},
 {id: 'py.elif', key: 'elif', title: 'The riddle keeper\'s verdict', badge: 'Fair verdict'},
];

async function mockApi(page: Page) {
 const posted: Record<string, unknown>[] = [], answers: {path: string; text: string}[] = [];
 await page.route('**/api/**', async route => {
  const path = new URL(route.request().url()).pathname;
  let status = 200, json: unknown = {};
  const unit = /^\/api\/units\/([^/]+)\/lessons$/.exec(path)?.[1], plan = /^\/api\/checks\/(.+)$/.exec(path)?.[1];
  if (path === '/api/catalog') json = recorded.catalog;
  else if (path === '/api/me') { status = 401; json = {detail: 'Sign in to continue'}; }
  else if (unit === 'py.u02') json = UNIT;
  else if (unit) { status = 404; json = {detail: 'Not Found'}; }
  else if (plan) json = ({...part1.plans, ...recorded.plans} as Record<string, unknown>)[plan];
  else if (path === '/api/check') {
   const body = route.request().postDataJSON(); posted.push(body);
   // The recorded answer only for exactly the recorded request (same code and the same reports).
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
  await expect(page.getByText(`Quest ${UNIT.indexOf(data) + 1} of 6 · ${lesson.badge}`)).toBeVisible();
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
  await expect(page.getByText(`Complete the challenge to earn the ${lesson.badge} badge and 100 XP.`)).toBeVisible();
  await expect(page.getByLabel('Your Python code')).toHaveValue(data.starter);
 });
}

// Each challenge, end to end with real Python

for (const lesson of LESSONS) {
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
}

const NEEDS_WORK = [
 {name: 'compare needs_work', hint: 'When the guess equals the secret, it is neither too high nor too low: False, False, True. If your first line says True, you may have used >= where > belongs.'},
 {name: 'boolean needs_work', hint: 'A guess of 53 is 3 away from 50, so it is not close. If your first line says True, check whether you joined the two limits with or: or is True when either side is, and here one side always is.'},
 // Separate ifs where elif is taught: the exactly right guess prints three scores.
 {name: 'elif needs_work', hint: 'An exactly right guess scores 10, printed once. Separate if statements can all run; in an if and elif chain only the first match does. Put the exact check first.',
  output: 'With a secret of 40 and a guess of 40:\n10\n5\n1'},
];
for (const {name, hint, output} of NEEDS_WORK) {
 test(`${name}: the judge names the case, and the hint tagged for it comes first`, async ({page}) => {
  const s = scenario(name);
  const {posted} = await mockApi(page);
  await runScenario(page, s);
  await expect(result(page)).toHaveText('Not yet' + s.response.feedback);
  await expect(page.getByText(/badge earned!/)).toHaveCount(0);
  if (output) await expect(page.locator('.execution-output')).toContainText(output);
  await expect(hints(page).getByRole('button')).toHaveText('Show a hint about this check');
  await hints(page).getByRole('button').click();
  await expect(hints(page).getByRole('listitem')).toHaveText([`About this check. ${hint}`]);
  await expect(hints(page).getByRole('button')).toHaveText('Show a nudge');
  expect(posted).toEqual([s.request]);
 });
}

const ERRORS = [
 {name: 'compare name error', title: 'Python does not know gues', text: 'Did you mean guess? Names must be spelled exactly the same each time.', where: 'Line 3', line: 3,
  python: "NameError: name 'gues' is not defined", secret: 'is not defined', hint: 'Use the names from the starter, secret and guess, spelled exactly the same.'},
 {name: 'boolean syntax error', title: 'Python cannot read line 3', text: 'Check the quotes, parentheses and colons on line 3 and the line before it.', where: 'On or just before line 3', line: 3,
  python: 'SyntaxError', secret: 'invalid syntax', hint: 'Each side of and and or needs a whole comparison, like guess >= 1 and guess <= 100. Writing guess >= 1 and <= 100 makes Python stop.'},
 {name: 'elif indentation error', title: 'The lines inside this if need indenting', text: 'Lines that belong to an if or else start with four spaces. Indent line 4.', where: 'Line 4', line: 4,
  python: "IndentationError: expected an indented block after 'if' statement on line 3", secret: 'expected an indented block', hint: 'The line under each if, elif and else starts with four spaces. Press Tab at the start of the line to add them.'},
];
for (const e of ERRORS) {
 test(`${e.name}: the friendly explanation, the line, and Python's message kept in the browser`, async ({page}) => {
  const s = scenario(e.name);
  const {posted} = await mockApi(page);
  await runScenario(page, s);
  await expect(result(page)).toContainText('Python stopped');
  await expect(result(page)).toContainText(e.title);
  await expect(result(page)).toContainText(e.text);
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

for (const lesson of LESSONS) {
 test(`${lesson.title}: an endless loop is stopped at 3 seconds and is not a pass`, async ({page}) => {
  const s = scenario(`${lesson.key} endless loop`);
  const {posted} = await mockApi(page);
  const started = Date.now();
  await runScenario(page, s);
  expect(Date.now() - started).toBeLessThan(40000);
  await expect(result(page)).toContainText('Your program kept running');
  await expect(result(page)).toContainText('It did not finish within 3 seconds');
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
  await expect(page.getByText(/badge earned!/)).toHaveCount(0);
 });
}

// Hidden cases

test('a hidden case that fails is named by its description only, with its tagged hint', async ({page}) => {
 const s = scenario('compare hidden');
 await mockApi(page);
 await runScenario(page, s);
 await expect(result(page)).toContainText('a large secret (a hidden test case)');
 await expect(page.locator('.execution-output')).not.toContainText('large secret');
 const shown = await page.locator('body').innerText();
 for (const value of ['1000', '999']) expect(shown).not.toContain(value);
 await hints(page).getByRole('button', {name: 'Show a hint about this check'}).click();
 await expect(hints(page).getByRole('listitem')).toHaveText(['About this check. Compare guess with secret, not with numbers typed into the code, so your program works for every secret.']);
});

test('no check plan or answer the page receives holds a hidden case\'s expected output', async ({page}) => {
 const {answers} = await mockApi(page);
 for (const name of ['compare passed', 'boolean needs_work', 'elif needs_work']) await runScenario(page, scenario(name));
 const plans = answers.filter(a => a.path.startsWith('/api/checks/')).map(a => JSON.parse(a.text));
 expect(plans).toHaveLength(3);
 for (const plan of plans) for (const c of plan.cases) expect('expected' in c).toBe(c.visibility === 'visible');
 for (const a of answers.filter(a => a.path === '/api/check')) {
  const failed = JSON.parse(a.text).failed;
  if (failed?.visibility === 'hidden') expect(failed).not.toHaveProperty('expected_line');
 }
});

// The unit, complete

test('after the sixth lesson the unit is complete, and the page says so', async ({page}) => {
 await mockApi(page);
 const all = ['arithmetic', 'int-float', 'convert-input', 'compare', 'boolean', 'elif'];
 for (const [i, key] of all.entries()) {
  if (i > 0) await toNextLesson(page, i);
  await runScenario(page, scenario(`${key} passed`), i === 0);
  await expect(page.getByText(/badge earned!/)).toBeVisible();
 }
 await expect(page.getByText('600 XP')).toBeVisible();
 await expect(page.getByText('6 of 6 badges earned · preview session')).toBeVisible();
 const done = page.locator('.chapter-complete');
 await expect(done.getByRole('heading')).toHaveText('Unit complete.');
 await expect(done).toContainText('You finished every lesson in Numbers and decisions. See the course for what comes next.');
 await expect(done).not.toContainText('released so far');
 await expect(done.getByRole('link', {name: 'See the course'})).toHaveAttribute('href', '/courses/py');
 await expect(page.getByRole('button', {name: 'Next quest →'})).toHaveCount(0);
 await page.getByRole('button', {name: 'Revisit this quest'}).click();
 await expect(page.getByText('Card 1 of 5')).toBeVisible();
});

test('the elif challenge fits a phone, with no sideways scrolling, and nothing moves with reduced motion', async ({page}) => {
 await page.setViewportSize({width: 375, height: 812});
 await page.emulateMedia({reducedMotion: 'reduce'});
 await mockApi(page);
 await page.goto('/preview?lesson=py.boolean-logic&card=2');
 await expect(page.locator('.teaching-panel .example-code')).toBeVisible();
 expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
 await runScenario(page, scenario('elif needs_work'));
 expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
 expect(await page.locator('.result, .result *').evaluateAll(els => els.every(el => getComputedStyle(el).animationName === 'none'))).toBe(true);
});
