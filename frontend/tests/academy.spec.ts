import {test, expect, Page} from '@playwright/test';
// Same JSON that /api/lessons serves; backend tests assert they are identical.
import lessons from '../../backend/tests/fixtures/legacy_lessons_v1.json';
import catalog from '../../backend/tests/fixtures/catalog_v1.json';
async function mockApi(page:Page,initialRole:string|null,done:string[]=[]){
 let role=initialRole;const completed:string[]=[...done];
 await page.route('**/api/**',async route=>{
  const path=new URL(route.request().url()).pathname;let body:unknown={},status=200;
  if(path==='/api/lessons')body=lessons;
  else if(path==='/api/catalog')body=catalog;
  else if(path==='/api/awards')body={xp:completed.length*100,completed,badges:[]};
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
 await expect(page.getByRole('heading',{name:'Your first course is ready.'})).toBeVisible();await expect(page.getByRole('link',{name:/^Start/})).toHaveAttribute('href','/learn/hello');
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
 await mockApi(page,'student');await page.goto('/learn/hello');
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
 await page.getByRole('link',{name:/Launch your adventure/}).click();await expect(page.getByRole('heading',{name:'Connect the pieces into a game'})).toBeVisible();expect(requests).toEqual([]);
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
test('checker service errors keep the draft, award nothing, and allow a retry',async({page})=>{
 await mockApi(page,null);await page.route('**/api/check',route=>route.fulfill({contentType:'application/json',body:JSON.stringify({passed:false,result:'service_error',feedback:'Unable to assess this right now. Your code is unchanged; please try again in a moment.',assessment:'browser_practice'})}));
 const code='print("A forest.")\nprint("A dragon!")';await page.goto('/preview?lesson=hello&card=5');await page.getByLabel('Your Python code').fill(code);await page.getByRole('button',{name:'Run & check challenge'}).click();
 await expect(page.getByRole('status').filter({hasText:'Unable to assess this right now'})).toBeVisible({timeout:25000});await expect(page.getByText(/badge earned!/)).toHaveCount(0);
 await expect(page.getByLabel('Your Python code')).toHaveValue(code);await expect(page.getByRole('button',{name:'Run & check challenge'})).toBeEnabled();await expect(page.getByText('0 XP',{exact:true})).toBeVisible();
});
test('mobile classroom fits, collapses the unit menu, and respects reduced motion',async({page})=>{
 await page.setViewportSize({width:375,height:812});await page.emulateMedia({reducedMotion:'reduce'});await mockApi(page,null);await page.goto('/preview?lesson=adventure&card=4');
 await expect(page.getByLabel('Your Python code')).toBeVisible();expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
 const toggle=page.getByRole('button',{name:/Lesson 5 of 5/});await expect(toggle).toHaveAttribute('aria-expanded','false');await expect(page.getByRole('link',{name:/Launch your adventure/})).toBeHidden();
 await toggle.click();await expect(toggle).toHaveAttribute('aria-expanded','true');const current=page.getByRole('link',{name:/Launch your adventure/});await expect(current).toHaveAttribute('aria-current','page');
 const box=await current.boundingBox();expect(box!.x).toBeGreaterThanOrEqual(0);expect(box!.x+box!.width).toBeLessThanOrEqual(375);
 await page.getByRole('link',{name:/Open the story/}).click();await expect(toggle).toHaveCount(0);await expect(page.getByRole('button',{name:/Lesson 1 of 5/})).toHaveAttribute('aria-expanded','false');
 expect(await page.locator('.world-spark').evaluateAll(elements=>elements.every(el=>getComputedStyle(el).animationName==='none'))).toBe(true);
});
test('catalog shows every course, with coming-soon courses labelled and not startable',async({page})=>{
 await mockApi(page,null);await page.goto('/courses');
 const courses=page.getByRole('list',{name:'Courses'}).getByRole('listitem');await expect(courses).toHaveCount(catalog.courses.length);
 const python=page.getByRole('article',{name:'Python Foundations'});await expect(python.getByText('Available',{exact:true})).toBeVisible();await expect(python.getByText('5 lessons ready to try')).toBeVisible();
 await expect(page.getByText('Coming soon',{exact:true})).toHaveCount(catalog.courses.length-1);
 await expect(page.getByRole('article',{name:'Hackathon Ready'}).getByText('Builds on Python Foundations units 1–7.')).toBeVisible();
 await page.getByRole('link',{name:'Hackathon Ready'}).click();await expect(page).toHaveURL('/courses/hack');
 await expect(page.getByText('This course is coming soon and cannot be started yet.')).toBeVisible();await expect(page.getByRole('link',{name:/^(Start|Continue)/})).toHaveCount(0);
 await expect(page.getByRole('list',{name:'Units'}).getByRole('listitem')).toHaveCount(7);await expect(page.locator('.unit-card a')).toHaveCount(0);
});
test('course page shows unit progress and continues where the student left off',async({page})=>{
 await mockApi(page,'student',['hello']);await page.goto('/courses/py');
 await expect(page.getByRole('heading',{level:1,name:'Python Foundations'})).toBeVisible();await expect(page.getByText('1 of 5 available lessons complete')).toBeVisible();
 const unit=page.getByRole('article',{name:'Build Your Own Adventure'});
 await expect(unit.getByRole('link',{name:/Open the story.*Completed/})).toHaveAttribute('href','/learn/hello');
 await expect(unit.getByRole('link',{name:/Create your hero.*Up next/})).toBeVisible();await expect(unit.getByRole('link',{name:/Choose a path.*Not started/})).toBeVisible();
 await expect(page.getByRole('article',{name:'Numbers and decisions'}).getByText('Coming soon')).toBeVisible();
 await page.getByRole('link',{name:/Continue: Create your hero/}).click();await expect(page).toHaveURL('/learn/variables');
 await expect(page.getByRole('heading',{name:'Remember a detail with a variable'})).toBeVisible();
});
test('lesson sidebar shows done, current, and not started, and works from the keyboard',async({page})=>{
 await mockApi(page,'student',['hello']);await page.goto('/learn/choices');
 const nav=page.getByRole('navigation',{name:'Lessons in this unit'});await expect(nav.getByText('1 of 5 lessons complete')).toBeVisible();
 await expect(nav.getByRole('link',{name:/Open the story.*Completed/})).toBeVisible();await expect(nav.getByRole('link',{name:/Choose a path.*Current lesson/})).toHaveAttribute('aria-current','page');
 await expect(nav.getByRole('link',{name:/Launch your adventure.*Not started/})).toBeVisible();
 await expect(page.getByRole('navigation',{name:'Breadcrumb'}).getByRole('link',{name:'Python Foundations'})).toHaveAttribute('href','/courses/py');
 await nav.getByRole('link',{name:/Create your hero/}).focus();await page.keyboard.press('Enter');
 await expect(page).toHaveURL('/learn/variables');await expect(nav.getByRole('link',{name:/Create your hero/})).toHaveAttribute('aria-current','page');
 await expect(page.getByRole('heading',{name:'Remember a detail with a variable'})).toBeFocused();
});
test('student home offers the next lesson and shows XP',async({page})=>{
 await mockApi(page,'student',['hello','variables']);await page.goto('/');
 await expect(page.getByRole('heading',{name:'Welcome back. Keep building.'})).toBeVisible();
 const next=page.getByRole('region',{name:'Meet the player'});await expect(next.getByText('200 XP')).toBeVisible();
 await expect(next.getByRole('link',{name:/Continue/})).toHaveAttribute('href','/learn/input');
 await expect(page.getByRole('article',{name:'Python Foundations'}).getByText('2 of 5 lessons complete')).toBeVisible();
});
