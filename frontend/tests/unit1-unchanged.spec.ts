import fs from 'node:fs';
import path from 'node:path';
import {test, expect, Page} from '@playwright/test';
import lessons from '../../backend/tests/fixtures/legacy_lessons_v1.json';
import catalog from '../../backend/tests/fixtures/catalog_v1.json';
import api from './fixtures/lesson-units-api.json';

/* UI-05: unit 1 must look and behave exactly as before lessons were loaded per unit. The snapshot
 * was recorded from main at 3263342 (before UI-05) with WRITE_UNIT1_SNAPSHOT=1, and every card,
 * hint and result text of every unit 1 lesson must still match it. The API answers are the real
 * ones (backend/tests/test_lesson_units.py checks lesson-units-api.json against the API). */
const SNAPSHOT = path.join(__dirname, 'fixtures', 'unit1-page.snapshot.json');
const WRITE = process.env.WRITE_UNIT1_SNAPSHOT === '1';
const CHECKED = {passed: false, result: 'needs_work', feedback: 'A fixed check answer, the same before and after UI-05.', rule: null, assessment: 'browser_practice'};

async function mockApi(page: Page) {
 await page.route('**/api/**', async route => {
  const p = new URL(route.request().url()).pathname;
  const body = p === '/api/lessons' ? lessons : p === '/api/catalog' ? catalog : p === '/api/units/py.u01/lessons' ? api.units['py.u01'] : p === '/api/check' ? CHECKED : {};
  await route.fulfill({contentType: 'application/json', body: JSON.stringify(body)});
 });
}
// WebKit reports a <progress> bar as two extra blank lines, which Chromium does not, so runs of blank
// lines count as one, on the page and in the snapshot. Every line of text must still match exactly.
const lines = (value: string) => value.replace(/\n{3,}/g, '\n\n');
const text = (page: Page) => page.locator('section.adventure').innerText();
const normal = (texts: Record<string, string>) => Object.fromEntries(Object.entries(texts).map(([key, value]) => [key, lines(value)]));

test('every unit 1 card, hint and result reads exactly as before UI-05', async ({page}) => {
 test.setTimeout(300000);
 await mockApi(page);
 const seen: Record<string, string> = {};
 for (const lesson of lessons) {
  for (let card = 1; card <= 5; card++) {
   await page.goto(`/preview?lesson=${lesson.id}&card=${card}`);
   await expect(page.getByText(`Card ${card} of 5`)).toBeVisible();
   seen[`${lesson.id} card ${card}`] = await text(page);
  }
  // Card 5: the hint ladder, step by step, then a run that the (mocked) check answers.
  for (let step = 1; step <= 4; step++) {
   await page.locator('.hint-ladder button').click();
   seen[`${lesson.id} hint ${step}`] = await page.locator('.hint-ladder').innerText();
  }
  await page.getByLabel('Your Python code').fill(lesson.example);
  await page.getByRole('button', {name: 'Run & check challenge'}).click();
  await expect(page.locator('#code-feedback')).not.toBeEmpty({timeout: 25000});
  seen[`${lesson.id} challenge result`] = await page.locator('.editor-panel').innerText();
  // Card 4: a run with no check.
  await page.goto(`/preview?lesson=${lesson.id}&card=4`);
  await page.getByRole('button', {name: 'Run Python →'}).click();
  await expect(page.locator('#code-feedback')).not.toBeEmpty({timeout: 25000});
  seen[`${lesson.id} try it result`] = await page.locator('.editor-panel').innerText();
 }
 if (WRITE) fs.writeFileSync(SNAPSHOT, JSON.stringify(seen, null, 1) + '\n');
 expect(normal(seen)).toEqual(normal(JSON.parse(fs.readFileSync(SNAPSHOT, 'utf8'))));
});
