import {test, expect, Page} from '@playwright/test';
// The API's real answers for Python unit 3, part 1 (catalog, the unit's lessons, check plans and judge
// answers), checked against the API by backend/tests/test_unit3_lessons.py. Part 2 and the unit's ending
// are in unit3-part2.spec.ts. Python runs for real in Pyodide here.
import recorded from './fixtures/unit3-api.json';
import goals from '../../backend/tests/fixtures/goals_v1.json';

/* EDU-03 part 1: py.while-loops, py.loop-termination and py.for-range. */

type Scenario = (typeof recorded.scenarios)[number];
const scenario = (name: string) => recorded.scenarios.find(s => s.name === name)!;
const UNIT = recorded.units['py.u03'];
const LESSONS = [
 {id: 'py.while-loops', key: 'while', title: 'Keep guessing', badge: 'Patient guesser'},
 {id: 'py.loop-termination', key: 'termination', title: 'Three tries', badge: 'Loop closer'},
 {id: 'py.for-range', key: 'for', title: 'Step by step', badge: 'Step counter'},
];

/* Unit 3 as it was released in part 1, with three lessons and more to come. The real catalog has it complete now. */
function partialCatalog() {
 const catalog = JSON.parse(JSON.stringify(recorded.catalog));
 const unit = catalog.courses[0].units[2];
 unit.lessons = unit.lessons.slice(0, 3);
 unit.complete = false;
 return catalog;
}
async function mockApi(page: Page, {student = false, partial = false}: {student?: boolean; partial?: boolean} = {}) {
 const posted: Record<string, unknown>[] = [], answers: {path: string; text: string}[] = [];
 const everything = recorded.catalog.courses.flatMap(c => c.units.filter(u => u.status === 'released').flatMap(u => u.lessons.map(l => l.id)));
 await page.route('**/api/**', async route => {
  const path = new URL(route.request().url()).pathname;
  let status = 200, json: unknown = {};
  const unit = /^\/api\/units\/([^/]+)\/lessons$/.exec(path)?.[1], plan = /^\/api\/checks\/(.+)$/.exec(path)?.[1];
  if (path === '/api/catalog') json = partial ? partialCatalog() : recorded.catalog;
  else if (path === '/api/me') ({status, json} = student ? {status: 200, json: {id: 1, email: 'test@example.com', role: 'student'}} : {status: 401, json: {detail: 'Sign in to continue'}});
  else if (path === '/api/awards') json = {xp: everything.length * 100, completed: everything, badges: []};
  else if (path === '/api/goal') json = {goal: 'scratch', chosen: true, asked: true};
  else if (path === '/api/goals') json = goals;
  else if (path === '/api/progress') json = everything;
  else if (path === '/api/history' || path === '/api/family') json = [];
  else if (unit === 'py.u03') json = partial ? UNIT.slice(0, 3) : UNIT;
  else if (unit) { status = 404; json = {detail: 'Not Found'}; }
  else if (plan) json = (recorded.plans as Record<string, unknown>)[plan];
  else if (path === '/api/check') {
   const body = route.request().postDataJSON(); posted.push(body);
   const match = recorded.scenarios.find(s => JSON.stringify(s.request) === JSON.stringify(body));
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
async function tryIt(page: Page, code: string) {
 await page.getByLabel('Your Python code').fill(code);
 await page.getByRole('button', {name: 'Run Python →'}).click();
 await expect(page.getByRole('button', {name: 'Run Python →'})).toBeEnabled({timeout: 45000});
}

// The unit and its cards

test('unit 3 loads on its own: its heading, its five lessons, and no unit 1 pictures', async ({page}) => {
 await mockApi(page);
 await page.goto('/preview?lesson=py.while-loops');
 // Visual redesign: the page heading is the lesson's title; the unit's title heads the lesson list.
 await expect(page.getByRole('heading', {level: 1, name: 'Keep guessing'})).toBeVisible();
 await expect(page.getByText('unit 3 · lesson 1 of 5')).toBeVisible();
 await expect(page.getByRole('region', {name: 'Repeat and explore'})).toBeVisible();
 await expect(page.getByRole('navigation', {name: 'Lessons in this unit'}).getByRole('listitem')).toHaveText([/Keep guessing/, /Three tries/, /Step by step/, /Keep the score/, /Rooms on the map/]);
 await expect(page.getByText('Quest 1 of 5 · Patient guesser')).toBeVisible();
 await expect(page.locator('.story-world')).toHaveCount(0);
});

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
}

// The "Try it" cards: running out of replies, and a loop that never ends, are both safe

test('Keep guessing, Try it: when the replies run out, the page says so in plain words', async ({page}) => {
 await mockApi(page);
 await page.goto('/preview?lesson=py.while-loops&card=4');
 await page.getByLabel('Reply 3').fill('comet');
 await page.getByRole('button', {name: 'Run Python →'}).click();
 await expect(result(page)).toContainText('Python stopped', {timeout: 45000});
 await expect(result(page)).toContainText('Not enough player replies');
 await expect(result(page)).toContainText('Your program asked for input more times than there are player replies.');
 // What printed before the replies ran out stays.
 await expect(page.locator('.execution-output')).toHaveText('The door stays shut.\nThe door stays shut.\nThe door stays shut.');
});

test('Three tries, Try it: deleting the countdown line stops at once with "Too much output", and the page stays usable', async ({page}) => {
 await mockApi(page);
 await page.goto('/preview?lesson=py.loop-termination&card=4');
 const data = UNIT.find(l => l.id === 'py.loop-termination')!;
 const started = Date.now();
 await tryIt(page, data.example.replace('    count = count - 1\n', ''));
 expect(Date.now() - started).toBeLessThan(30000);
 await expect(result(page)).toContainText('Too much output');
 await expect(result(page)).toContainText('Print less, or check for a loop that never ends.');
 await page.getByRole('button', {name: 'Reset code'}).click();
 await expect(page.getByLabel('Your Python code')).toHaveValue(data.example);
});

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
 {name: 'while needs_work', button: 'Show a hint about this check', label: 'About this check', hint: 'With a secret of 7 and guesses of 9, 3 and 7, the lines are True, then False. If only True printed, your program checked once with if; a while loop checks again after every guess.'},
 // A loop that keeps asking after the right guess runs out of replies: the hint for that comes first.
 {name: 'while out of replies', button: 'Show a hint about this error', label: 'About this error', hint: 'Your loop asked for another guess after the last reply. Check that it stops as soon as the guess is right: that is when its condition should become False.'},
 {name: 'termination needs_work', button: 'Show a hint about this check', label: 'About this check', hint: 'Only the first three guesses count, so the lines are 3 and False, even though a fourth reply would be right. If your program printed 4 and True, the loop needs a limit on tries.'},
 {name: 'for needs_work', button: 'Show a hint about this check', label: 'About this check', hint: 'With a top step of 8, the hero lands on 2, 4, 6 and 8. If 8 is missing, the stop of your range() is 8: make it one bigger.'},
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

test('while prints for ever: the output limit stops it, and it is not a pass', async ({page}) => {
 const s = scenario('while prints for ever');
 const {posted} = await mockApi(page);
 await runScenario(page, s);
 await expect(result(page)).toContainText('Too much output');
 await expect(result(page)).toContainText('more than 10,000 characters');
 await expect(page.locator('.execution-output')).toContainText('(stopped: too much output)');
 expect(posted).toEqual([s.request]);
 await expect(page.getByText(/badge earned!/)).toHaveCount(0);
});

const ERRORS = [
 {name: 'while name error', title: 'Python does not know gues', text: 'Did you mean guess? Names must be spelled exactly the same each time.', where: 'Line 3', line: 3,
  python: "NameError: name 'gues' is not defined", secret: 'is not defined', hint: 'Use the names from the starter, secret and guess, and spell them the same inside the loop.'},
 {name: 'termination indentation error', title: 'The lines inside this while loop need indenting', text: 'Lines that belong to a loop start with four spaces, so Python knows they repeat. Indent line 5.', where: 'Line 5', line: 5,
  python: "IndentationError: expected an indented block after 'while' statement on line 4", secret: 'expected an indented block', hint: null},
 {name: 'for type error', title: 'Text and numbers cannot be joined with +', text: 'To add numbers, turn the text into a number with int(...).', where: 'Line 2', line: 2,
  python: 'TypeError: can only concatenate str (not "int") to str', secret: 'can only concatenate', hint: 'range() needs whole numbers. Turn the reply into a number with int(...) before you use it.'},
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
  if (e.hint) {
   await hints(page).getByRole('button', {name: 'Show a hint about this error'}).click();
   await expect(hints(page).getByRole('listitem')).toHaveText([`About this error. ${e.hint}`]);
  }
  expect(JSON.stringify(posted)).not.toContain(e.secret);
  expect(posted).toEqual([s.request]);
  await expect(page.getByText(/badge earned!/)).toHaveCount(0);
 });
}

for (const lesson of LESSONS) {
 test(`${lesson.title}: an endless loop is stopped at 3 seconds, explained, and is not a pass`, async ({page}) => {
  const s = scenario(`${lesson.key} endless loop`);
  const {posted} = await mockApi(page);
  const started = Date.now();
  await runScenario(page, s);
  expect(Date.now() - started).toBeLessThan(40000);
  await expect(result(page)).toContainText('Your program kept running');
  await expect(result(page)).toContainText('It did not finish within 3 seconds, usually because a loop never ends. Check that something inside the loop changes, so that the loop can stop.');
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

test('a hidden case that fails is named by its description only, with its tagged hint', async ({page}) => {
 await mockApi(page);
 await runScenario(page, scenario('for hidden'));
 await expect(result(page)).toContainText('a taller staircase (a hidden test case)');
 await expect(page.locator('.execution-output')).not.toContainText('taller staircase');
 await hints(page).getByRole('button', {name: 'Show a hint about this check'}).click();
 await expect(hints(page).getByRole('listitem')).toHaveText(['About this check. Use the reply in your range(), not numbers typed into the code, so it works for every staircase.']);
});

test('no check plan the page receives holds a hidden case\'s expected output', async ({page}) => {
 const {answers} = await mockApi(page);
 for (const name of ['while passed', 'termination needs_work', 'for passed']) await runScenario(page, scenario(name));
 const plans = answers.filter(a => a.path.startsWith('/api/checks/')).map(a => JSON.parse(a.text));
 expect(plans).toHaveLength(3);
 for (const plan of plans) for (const c of plan.cases) expect('expected' in c).toBe(c.visibility === 'visible');
});

// A unit still being written, as unit 3 was after part 1

test('after the third lesson of a unit still being written, the page says the rest is still to come', async ({page}) => {
 await mockApi(page, {partial: true});
 for (const [i, lesson] of LESSONS.entries()) {
  if (i > 0) {
   const next = UNIT[i];
   await page.getByRole('button', {name: 'Next quest →'}).click();
   await page.getByRole('button', {name: 'Continue →'}).click();
   await page.getByRole('button', {name: 'Continue →'}).click();
   await page.getByRole('group', {name: next.question}).getByRole('button', {name: next.options[next.answer], exact: true}).click();
   await page.getByRole('button', {name: 'Continue →'}).click();
   await page.getByRole('button', {name: 'Start my challenge'}).click();
  }
  await runScenario(page, scenario(`${lesson.key} passed`), i === 0);
  await expect(page.getByText(`${lesson.badge} badge earned!`)).toBeVisible();
 }
 await expect(page.getByText('3 of 3 badges earned · preview session')).toBeVisible();
 const done = page.locator('.chapter-complete');
 await expect(done.getByRole('heading')).toHaveText('You finished every lesson released so far.');
 await expect(done).toContainText('That is all of Repeat and explore for now. See the course for what comes next.');
 await expect(done).not.toContainText('Unit complete');
});

test('the catalog and course page show unit 3 as open, with its five lessons', async ({page}) => {
 await mockApi(page);
 await page.goto('/courses');
 await expect(page.getByText('3 of 12 units open')).toBeVisible();
 await page.goto('/courses/py');
 const unit = page.getByRole('article', {name: 'Repeat and explore'});
 await expect(unit.getByRole('link')).toHaveText([/Keep guessing.*Try it/, /Three tries.*Try it/, /Step by step.*Try it/, /Keep the score.*Try it/, /Rooms on the map.*Try it/]);
 await expect(page.getByRole('article', {name: 'Keep track of a world'}).getByText('Coming soon')).toBeVisible();
});

test('unit 3 fits a phone, with no sideways scrolling, and nothing moves with reduced motion', async ({page}) => {
 await page.setViewportSize({width: 375, height: 812});
 await page.emulateMedia({reducedMotion: 'reduce'});
 await mockApi(page);
 await page.goto('/preview?lesson=py.while-loops&card=4');
 await expect(page.getByLabel('Reply 1')).toBeVisible();
 expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
 await runScenario(page, scenario('termination needs_work'));
 expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
 expect(await page.locator('.result, .result *').evaluateAll(els => els.every(el => getComputedStyle(el).animationName === 'none'))).toBe(true);
});
