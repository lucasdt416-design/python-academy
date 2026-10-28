import {test, expect, Page} from '@playwright/test';
// The API's real answers for Python unit 2 (catalog, the unit's lessons, check plans, and judge answers
// for recorded requests), checked against the API by backend/tests/test_unit2_lessons.py. Python runs
// for real in Pyodide here, so each test also proves the browser reports what the recording expects.
import recorded from './fixtures/unit2-api.json';

/* EDU-04 part 1: py.arithmetic, py.int-float and py.convert-input, end to end. */

type Scenario = (typeof recorded.scenarios)[number];
const scenario = (name: string) => recorded.scenarios.find(s => s.name === name)!;
const LESSONS = [
 {id: 'py.arithmetic', key: 'arithmetic', title: 'Count the treasure', badge: 'Treasure counter'},
 {id: 'py.int-float', key: 'int-float', title: 'Average the scores', badge: 'Score keeper'},
 {id: 'py.convert-input', key: 'convert-input', title: 'Score the riddle', badge: 'Riddle scorer'},
];
// Hidden cases' expected output: never in anything the page receives or shows.
const HIDDEN_EXPECTED = ['142\\n6', '9\\n0', '97.5', '10.0\\n10', '370', '130', '4\\n-4'];

/* partial: serve unit 2 as it was released in part 1, with its first three lessons and more to come
 * (complete: false), or, with 'old-api', as an API from before the complete field would. */
function partialCatalog(kind: 'more-coming' | 'old-api') {
 const catalog = JSON.parse(JSON.stringify(recorded.catalog));
 const unit = catalog.courses[0].units[1];
 unit.lessons = unit.lessons.slice(0, 3);
 if (kind === 'old-api') for (const c of catalog.courses) for (const u of c.units) delete u.complete;
 else unit.complete = false;
 return catalog;
}
async function mockApi(page: Page, {partial}: {partial?: 'more-coming' | 'old-api'} = {}) {
 const requests: string[] = [], posted: Record<string, unknown>[] = [], answers: string[] = [];
 await page.route('**/api/**', async route => {
  const path = new URL(route.request().url()).pathname;
  requests.push(path);
  let status = 200, json: unknown = {};
  const unit = /^\/api\/units\/([^/]+)\/lessons$/.exec(path)?.[1], plan = /^\/api\/checks\/(.+)$/.exec(path)?.[1];
  if (path === '/api/catalog') json = partial ? partialCatalog(partial) : recorded.catalog;
  else if (unit === 'py.u02' && partial) json = recorded.units['py.u02'].slice(0, 3);
  else if (path === '/api/me') { status = 401; json = {detail: 'Sign in to continue'}; }
  else if (unit && unit in recorded.units) json = recorded.units[unit as keyof typeof recorded.units];
  else if (unit) { status = 404; json = {detail: 'Not Found'}; }
  else if (plan) json = recorded.plans[plan as keyof typeof recorded.plans];
  else if (path === '/api/check') {
   const body = route.request().postDataJSON(); posted.push(body);
   // The recorded answer only for exactly the recorded request (same code and the same reports).
   const match = recorded.scenarios.find(s => JSON.stringify(s.request) === JSON.stringify(body));
   ({status = 200, json} = match ? {json: match.response} : {status: 500, json: {detail: 'not a recorded request'}});
  }
  const text = JSON.stringify(json); answers.push(text);
  await route.fulfill({status, contentType: 'application/json', body: text});
 });
 return {requests, posted, answers};
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

// The unit and its cards

test('unit 2 loads on its own: its heading, its three lessons, and no unit 1 pictures', async ({page}) => {
 const {requests} = await mockApi(page);
 await page.goto('/preview?lesson=py.arithmetic');
 await expect(page.getByRole('heading', {level: 1, name: 'Numbers and decisions'})).toBeVisible();
 await expect(page.getByText('UNIT 02 · PYTHON FOUNDATIONS')).toBeVisible();
 await expect(page.getByText('Arithmetic, whole numbers and decimals, numbers from input(), comparisons, Boolean logic and elif.')).toBeVisible();
 const nav = page.getByRole('navigation', {name: 'Lessons in this unit'});
 await expect(nav.getByRole('listitem')).toHaveText([/Count the treasure/, /Average the scores/, /Score the riddle/, /Too high or too low\?/, /Close enough\?/, /The riddle keeper's verdict/]);
 await expect(page.getByText('Quest 1 of 6 · Treasure counter')).toBeVisible();
 await expect(page.locator('.story-world')).toHaveCount(0);
 expect(requests.filter(p => p.startsWith('/api/units/'))).toEqual(['/api/units/py.u02/lessons']);
 expect(requests).not.toContain('/api/lessons');
});

for (const lesson of LESSONS) {
 test(`${lesson.title}: every card shows, and a prediction must be right to continue`, async ({page}) => {
  await mockApi(page);
  const data = recorded.units['py.u02'].find(l => l.id === lesson.id)!;
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
  await expect(page.getByRole('status').filter({hasText: 'That’s it!'})).toBeVisible();
  await page.getByRole('button', {name: 'Continue →'}).click();
  await expect(page.getByText(data.guided)).toBeVisible();
  // "Try it" runs the worked example for real, with its replies, and says it is not a check.
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
  // Only what the ENG-03 contract allows: per case id, status, output, error type and line.
  expect(Object.keys((posted[0].runs as object[])[0]).sort()).toEqual(['error_type', 'id', 'line', 'output', 'status']);
 });
}

const NEEDS_WORK = [
 {name: 'arithmetic needs_work', hint: 'Compare your first line with 3. A decimal point, like 3.4, means / was used: // keeps only the whole coins. Words on the line? Print just the number.',
  output: 'With 17 coins and 5 friends:\n3.4\n2\n\nWith 20 coins and 4 friends:\n5.0\n0\n\nWith 3 coins and 5 friends:\n0.6\n3'},
 {name: 'int-float needs_work', hint: 'The average of 7 and 8 is 7.5. If your first line says 11.0, Python divided only the second score: put the addition inside parentheses.'},
 {name: 'int-float negative', hint: 'With -3 and 2, the average is -0.5. int() cuts off the decimal part, so the second line is 0. The // operator rounds down instead, which gives -1 for negative numbers.'},
 {name: 'convert-input needs_work', hint: 'With an empty points reply, the riddle is worth 0, so both lines show the score unchanged.'},
];
for (const {name, hint, output} of NEEDS_WORK) {
 test(`${name}: the judge names the case, and the hint tagged for it comes first`, async ({page}) => {
  const s = scenario(name);
  const {posted} = await mockApi(page);
  await runScenario(page, s);
  await expect(result(page)).toHaveText('Not yet' + s.response.feedback);
  await expect(page.getByText(/badge earned!/)).toHaveCount(0);
  if (output) await expect(page.locator('.execution-output')).toHaveText(output);
  await expect(hints(page).getByRole('button')).toHaveText('Show a hint about this check');
  await hints(page).getByRole('button').click();
  await expect(hints(page).getByRole('listitem')).toHaveText([`About this check. ${hint}`]);
  // Then the ladder from its first step; never an answer button.
  await expect(hints(page).getByRole('button')).toHaveText('Show a nudge');
  expect(posted).toEqual([s.request]);
 });
}

// secret: part of Python's message, which must never be sent to the API.
const ERRORS = [
 {name: 'arithmetic name error', secret: 'is not defined', title: 'Python does not know coin', text: 'Did you mean coins? Names must be spelled exactly the same each time.', line: 3,
  python: "NameError: name 'coin' is not defined. Did you mean: 'coins'?", hint: 'Use the names the starter made, coins and friends, spelled exactly the same in your print() lines.'},
 {name: 'int-float type error', secret: 'can only concatenate', title: 'Text and numbers cannot be joined with +', text: 'On line 3, one side of + is text and the other is a number. To add numbers, turn the text into a number with int(...).', line: 3,
  python: 'TypeError: can only concatenate str (not "float") to str', hint: 'Print each number on its own, like print(total). Joining a number to text with + needs str(), and this check wants only the numbers.'},
 {name: 'convert-input value error', secret: 'invalid literal', title: 'That text is not a whole number', text: 'int() only turns text like "7" into a number. Check what was typed.', line: 2,
  python: "ValueError: invalid literal for int() with base 10: ''", hint: 'One test leaves the points reply empty, and int() can\'t turn empty text into a number. Check whether the reply is "" before you call int().'},
];
for (const e of ERRORS) {
 test(`${e.name}: the friendly explanation in unit 2's words, the line, and Python's message kept in the browser`, async ({page}) => {
  const s = scenario(e.name);
  const {posted} = await mockApi(page);
  await runScenario(page, s);
  await expect(result(page)).toContainText('Python stopped');
  await expect(result(page)).toContainText(e.title);
  await expect(result(page)).toContainText(e.text);
  await expect(result(page)).toContainText(`Line ${e.line}`);
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

test('a hidden case that fails is named by its description only', async ({page}) => {
 const s = scenario('arithmetic hidden');
 await mockApi(page);
 await runScenario(page, s);
 await expect(result(page)).toContainText('a big chest (a hidden test case)');
 // The Output panel shows the visible cases only.
 await expect(page.locator('.execution-output')).not.toContainText('big chest');
 const shown = await page.locator('body').innerText();
 for (const value of ['142', '1000']) expect(shown).not.toContain(value);
 await hints(page).getByRole('button', {name: 'Show a hint about this check'}).click();
 await expect(hints(page).getByRole('listitem')).toHaveText(['About this check. Your program needs to work for any chest. Use coins and friends in your calculations, not numbers typed into the code.']);
});

test('no answer the page receives holds a hidden expected output', async ({page}) => {
 const {answers} = await mockApi(page);
 for (const name of ['arithmetic passed', 'int-float negative', 'convert-input needs_work']) await runScenario(page, scenario(name));
 await page.goto('/courses/py');
 await expect(page.getByRole('heading', {name: 'Numbers and decisions'})).toBeVisible();
 expect(answers.length).toBeGreaterThan(10);
 for (const answer of answers) for (const value of HIDDEN_EXPECTED) expect(answer).not.toContain(value);
});

// A unit still being written (as unit 2 was after part 1). The real catalog has none now; the
// complete unit's ending is in unit2-part2.spec.ts.

for (const partial of ['more-coming', 'old-api'] as const) test(`after the last released lesson of a unit still being written (${partial}), the page says the rest is still to come`, async ({page}) => {
 await mockApi(page, {partial});
 for (const [i, lesson] of LESSONS.entries()) {
  await runScenario(page, scenario(`${lesson.key} passed`), i === 0);
  await expect(page.getByText(`${lesson.badge} badge earned!`)).toBeVisible();
  if (i === 2) break;
  // On to the next lesson, card by card, as a learner would.
  const next = recorded.units['py.u02'][i + 1];
  await page.getByRole('button', {name: 'Next quest →'}).click();
  await page.getByRole('button', {name: 'Continue →'}).click();
  await page.getByRole('button', {name: 'Continue →'}).click();
  await page.getByRole('group', {name: next.question}).getByRole('button', {name: next.options[next.answer], exact: true}).click();
  await page.getByRole('button', {name: 'Continue →'}).click();
  await page.getByRole('button', {name: 'Start my challenge'}).click();
 }
 await expect(page.getByText('300 XP')).toBeVisible();
 await expect(page.getByText('3 of 3 badges earned · preview session')).toBeVisible();
 const done = page.locator('.chapter-complete');
 await expect(done.getByRole('heading')).toHaveText('You finished every lesson released so far.');
 await expect(done).toContainText('That is all of Numbers and decisions for now. See the course for what comes next.');
 await expect(done).not.toContainText('Unit complete');
 await expect(done.getByRole('link', {name: 'See the course'})).toHaveAttribute('href', '/courses/py');
 // The last released lesson has no "Next quest": it offers to revisit, and nothing breaks.
 await expect(page.getByRole('button', {name: 'Next quest →'})).toHaveCount(0);
 await page.getByRole('button', {name: 'Revisit this quest'}).click();
 await expect(page.getByText('Card 1 of 5')).toBeVisible();
});

test('the catalog and course page show unit 2 as open, with its six lessons', async ({page}) => {
 await mockApi(page);
 await page.goto('/courses');
 await expect(page.getByText('2 of 12 units open')).toBeVisible();
 await page.goto('/courses/py');
 const unit = page.getByRole('article', {name: 'Numbers and decisions'});
 await expect(unit.getByRole('link')).toHaveText([/Count the treasure.*Try it/, /Average the scores.*Try it/, /Score the riddle.*Try it/, /Too high or too low\?.*Try it/, /Close enough\?.*Try it/, /The riddle keeper's verdict.*Try it/]);
 await expect(unit.getByText('Coming soon')).toHaveCount(0);
 await expect(page.getByRole('article', {name: 'Repeat and explore'}).getByText('Coming soon')).toBeVisible();
});

test('unit 2 fits a phone, with no sideways scrolling, and nothing moves with reduced motion', async ({page}) => {
 await page.setViewportSize({width: 375, height: 812});
 await page.emulateMedia({reducedMotion: 'reduce'});
 await mockApi(page);
 await page.goto('/preview?lesson=py.int-float&card=2');
 await expect(page.locator('.teaching-panel .example-code')).toBeVisible();
 expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
 await runScenario(page, scenario('int-float needs_work'));
 await expect(page.getByText('This challenge runs your program with its own replies')).toBeVisible();
 expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
 expect(await page.locator('.result, .result *').evaluateAll(els => els.every(el => getComputedStyle(el).animationName === 'none'))).toBe(true);
});
