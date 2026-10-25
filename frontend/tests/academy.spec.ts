import {test, expect, Page} from '@playwright/test';
import lessons from '../../backend/app/curriculum.json';
async function mockApi(page:Page,initialRole:string|null){
 let role=initialRole;const completed:string[]=[];
 await page.route('**/api/**',async route=>{
  const path=new URL(route.request().url()).pathname;let body:unknown={},status=200;
  if(path==='/api/lessons')body=lessons;
  else if(path==='/api/me'){status=role?200:401;body=role?{id:1,email:'test@example.com',role}:{detail:'Sign in to continue'};}
  else if(path==='/api/history'||path==='/api/family')body=[];
  else if(path==='/api/progress')body=completed;
  else if(path==='/api/enroll'){role=route.request().postDataJSON().invitation?'student':'parent';body={role};}
  else if(path==='/api/invitations')body={url:'https://academy.example/?invite=test'};
  else if(path==='/api/logout')role=null;
  else if(path==='/api/check'||path==='/api/attempts'){
   const data=route.request().postDataJSON();if(path==='/api/attempts'&&!completed.includes(data.lesson_id))completed.push(data.lesson_id);
   body={passed:true,feedback:'Your adventure works with different player replies.'};
  }
  await route.fulfill({status,contentType:'application/json',body:JSON.stringify(body)});
 });
}
test('welcome provides Google sign-in and keyboard skip navigation',async({page})=>{
 await mockApi(page,null);await page.goto('/');
 await expect(page.getByRole('link',{name:/Continue with Google/})).toHaveAttribute('href','/auth/google');
 await page.keyboard.press('Tab');await expect(page.getByRole('link',{name:/Skip/})).toBeFocused();
});
test('invitation survives redirect and enrolls a student',async({page})=>{
 await mockApi(page,'pending');await page.goto('/?invite=private-token');await page.reload();
 await page.getByLabel('Date of birth').fill('2010-01-01');
 const request=page.waitForRequest(r=>r.url().endsWith('/api/enroll'));
 await page.getByRole('button',{name:'Complete registration'}).click();
 expect((await request).postDataJSON().invitation).toBe('private-token');
 await expect(page.getByRole('heading',{name:'Your story starts with one instruction'})).toBeVisible();
 expect(await page.evaluate(()=>sessionStorage.getItem('academy-invite'))).toBeNull();
});
test('parent creates an invitation, previews lessons, and returns to family',async({page})=>{
 await mockApi(page,'parent');await page.goto('/');
 await page.getByLabel('Student’s Google email').fill('learner@example.com');await page.getByRole('button',{name:'Create invitation'}).click();
 await expect(page.getByLabel('Invitation link')).toHaveValue('https://academy.example/?invite=test');
 await page.getByRole('link',{name:/Try the lessons/}).click();
 await expect(page.getByRole('article',{name:'Current learning card'})).toHaveCount(1);
 await page.getByRole('link',{name:'Return to your account'}).click();
 await expect(page.getByRole('heading',{name:'Help their curiosity grow.'})).toBeVisible();
 await page.getByRole('button',{name:'Sign out'}).click();await expect(page.getByRole('link',{name:/Continue with Google/})).toBeVisible();
});
test('student sees one card at a time and predicts before coding',async({page})=>{
 await mockApi(page,'student');await page.goto('/');
 await expect(page.getByRole('article',{name:'Current learning card'})).toHaveCount(1);
 await expect(page.getByLabel('Your Python code')).toHaveCount(0);await expect(page.getByText('Card 1 of 5')).toBeVisible();
 await page.getByRole('button',{name:'Continue →',exact:true}).click();
 await expect(page.getByRole('heading',{name:'Watch the story take shape'})).toBeVisible();
 await expect(page.getByRole('heading',{name:'Your story starts with one instruction'})).toHaveCount(0);
 await page.getByRole('button',{name:'Continue →',exact:true}).click();
 await expect(page.getByRole('button',{name:'Continue →',exact:true})).toBeDisabled();
 await page.getByRole('button',{name:'The dragon message',exact:true}).click();await expect(page.getByText(/Let’s look again/)).toBeVisible();
 await expect(page.getByRole('button',{name:'Continue →',exact:true})).toBeDisabled();
 await page.getByRole('button',{name:'The castle message',exact:true}).click();await page.getByRole('button',{name:'Continue →',exact:true}).click();
 await expect(page.getByLabel('Your Python code')).toHaveValue(lessons[0].example);
 await expect(page.getByRole('heading',{name:'Make one small change'})).toBeFocused();
 await page.getByRole('button',{name:'Start my challenge'}).click();await expect(page.getByLabel('Your Python code')).toHaveValue(lessons[0].starter);
 await expect(page.getByRole('button',{name:'Next quest →'})).toBeDisabled();
});
test('preview jumps to any card without private API requests',async({page})=>{
 const requests:string[]=[];page.on('request',r=>{if(/\/api\/(me|history|family|attempts|progress)$/.test(new URL(r.url()).pathname))requests.push(r.url());});
 await mockApi(page,null);await page.goto('/preview?lesson=choices&card=5');
 await expect(page.getByText('Card 5 of 5')).toBeVisible();await expect(page.getByLabel('Your Python code')).toHaveValue(lessons[3].starter);
 await page.getByRole('button',{name:'1. Discover',exact:true}).click();await expect(page.getByLabel('Your Python code')).toHaveCount(0);
 await page.getByRole('button',{name:/Launch your adventure/}).click();await expect(page.getByRole('heading',{name:'Connect the pieces into a game'})).toBeVisible();expect(requests).toEqual([]);
});
test('drafts survive card navigation and hints are gradual',async({page})=>{
 await mockApi(page,null);await page.goto('/preview?lesson=variables&card=5');
 const editor=page.getByLabel('Your Python code');await editor.fill('hero = "Kai"');await page.getByRole('button',{name:'Show next hint'}).click();
 await expect(page.getByText(/Hint 1\./)).toBeVisible();await expect(page.getByText(/Hint 2\./)).toHaveCount(0);
 await page.getByRole('button',{name:'4. Try it',exact:true}).click();await page.getByRole('button',{name:'5. Your challenge',exact:true}).click();
 await expect(editor).toHaveValue('hero = "Kai"');await editor.fill('');await editor.press('Tab');await expect(editor).toHaveValue('    ');await editor.press('Shift+Tab');await expect(editor).not.toBeFocused();
});
// Actual Python runs in Pyodide. Account/check API responses are mocked here; backend checks have separate tests.
for(const lesson of lessons){test(`real Python executes ${lesson.id} with player replies`,async({page})=>{
 await mockApi(page,null);await page.goto(`/preview?lesson=${lesson.id}&card=5`);await page.getByLabel('Your Python code').fill(lesson.example);
 const request=page.waitForRequest(r=>r.url().endsWith('/api/check'));await page.getByRole('button',{name:'Run & check challenge'}).click();
 await expect(page.locator('.execution-output')).toHaveText(lesson.exampleOutput,{timeout:25000});expect((await request).postDataJSON().inputs).toEqual(lesson.exampleInputs);
 await expect(page.getByText(lesson.badge+' badge earned!',{exact:true})).toBeVisible();await expect(page.getByText('100 XP',{exact:true})).toBeVisible();
 await page.getByRole('button',{name:'Run & check challenge'}).click();await expect(page.getByRole('button',{name:'Run & check challenge'})).toBeEnabled({timeout:25000});await expect(page.getByText('100 XP',{exact:true})).toBeVisible();
});}
test('different player replies change the actual Python story',async({page})=>{
 await mockApi(page,null);await page.goto('/preview?lesson=adventure&card=5');await page.getByLabel('Your Python code').fill(lessons[4].example);
 await page.getByLabel('Player name',{exact:true}).fill('Kai');await page.getByLabel('Path: left or right').fill('right');await page.getByRole('button',{name:'Run & check challenge'}).click();
 await expect(page.locator('.execution-output')).toContainText('Welcome aboard, Kai',{timeout:25000});await expect(page.locator('.execution-output')).toContainText('sky garden');
});
test('Python errors and endless loops stay recoverable',async({page})=>{
 await mockApi(page,null);await page.goto('/preview?lesson=hello&card=5');await page.getByLabel('Your Python code').fill('print(');await page.getByRole('button',{name:'Run & check challenge'}).click();
 await expect(page.locator('.execution-output')).toContainText('SyntaxError',{timeout:25000});await page.getByLabel('Your Python code').fill('while True:\n    pass');await page.getByRole('button',{name:'Run & check challenge'}).click();
 await page.getByRole('button',{name:'Stop',exact:true}).click();await expect(page.locator('.execution-output')).toHaveText('Execution stopped.');await page.getByRole('button',{name:'Run & check challenge'}).click();
 await expect(page.locator('.execution-output')).toContainText('Execution stopped after 15 seconds',{timeout:20000});await expect(page.getByRole('button',{name:'Run & check challenge'})).toBeEnabled();
});
test('mobile classroom fits and respects reduced motion',async({page})=>{
 await page.setViewportSize({width:375,height:812});await page.emulateMedia({reducedMotion:'reduce'});await mockApi(page,null);await page.goto('/preview?lesson=adventure&card=4');
 await expect(page.getByLabel('Your Python code')).toBeVisible();expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
 const active=await page.locator('.quest.active').boundingBox();expect(active!.x).toBeGreaterThanOrEqual(0);expect(active!.x+active!.width).toBeLessThanOrEqual(375);
 expect(await page.locator('.world-spark').evaluateAll(elements=>elements.every(el=>getComputedStyle(el).animationName==='none'))).toBe(true);
});
