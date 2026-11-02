'use client';
import {type ReactNode, useEffect, useRef, useState} from 'react';
import {type Catalog,type Course,type Unit,unitNumber} from './catalog-data';
import CodeEditor,{goToLine} from './code-editor';
import {type ErrorHint,type Explanation,HINT_TEXT,type HintStep,OUTLINE_AFTER,RESULTS,type Result,STATE_LABELS,type Sample,checkLine,explain,nextHint,parseError,pythonMessage} from './feedback';

type Lesson = {id:string;title:string;concept:string;badge:string;description:string;learnTitle:string;learn:string;detail:string;example:string;exampleOutput:string;exampleNote:string;question:string;options:string[];answer:number;why:string;guided:string;starter:string;challenge:string;hints:string[];inputs:string[];exampleInputs:string[];errorHints?:ErrorHint[];similarExample?:Sample|null;otherWays?:Sample[];course?:string;unit?:string;check?:string};
/** A browser check (ENG-03): what GET /api/checks/<lesson> gives, and what public/check-runner.js reports per case. Hidden cases come without expected output. */
type Plan={time_limit_ms:number;output_limit:number;cases:{id:string;visibility:'visible'|'hidden';description:string;inputs:string[];test_should?:'pass'|'fail'}[]};
type CaseReport={id:string;status:string;output:string;errorType:string|null;line:number|null;message:string|null;shown?:string};
type Place={course:Course;unit:Unit};
/** The released unit holding this lesson, or the first released unit when there is none (the lesson page's default). */
function findUnit(catalog:Catalog,lessonId:string|null):Place|null{
 const units=catalog.courses.flatMap(course=>course.units.filter(u=>u.status==='released').map(unit=>({course,unit})));
 return units.find(p=>p.unit.lessons.some(l=>l.id===lessonId))??units[0]??null;
}
/** What the Output panel shows after a browser check: each visible case's output. Hidden cases are not shown. */
function caseOutput(plan:Plan,reports:CaseReport[]){
 const stopped:Record<string,string>={timeout:`(stopped: still running after ${plan.time_limit_ms/1000} seconds)`,not_run:'(not run)',unavailable:'(Python could not start)',error:'(Python stopped)',no_function:'(that function is not defined)',bad_signature:'(that function takes different arguments)',not_comparable:'(this check cannot compare the returned value)'};
 return plan.cases.filter(c=>c.visibility==='visible').map(c=>{const r=reports.find(x=>x.id===c.id);if(c.test_should&&(r?.status==='ok'||r?.status==='error'))return `With ${c.description}:\n${r.status==='ok'?'(your tests all passed)':'(a test stopped here)'}`;const printed=(r?.output??'').replace(/\n$/,'');return `With ${c.description}:\n${[printed,r?.shown!=null?`Returned: ${r.shown}`:'',r?.status==='output_limit'?'(stopped: too much output)':r&&r.status!=='ok'?stopped[r.status]??'':''].filter(Boolean).join('\n')||'(nothing printed)'}`;}).join('\n\n');
}
const stages=['Discover','See it work','Predict','Try it','Your challenge'];
/** What the last run showed: a check result, a run with no check, or a Python error explained (app/feedback.ts).
 * tag: the Python error type or check rule it was about, so the hint tagged for it is offered first. */
type Report={state:Result|'ran';text:string;explanation?:Explanation;python?:string;tag?:string|null};
/** Code between backticks in a message, shown as code. */
function withCode(text:string):ReactNode[]{return text.split('`').map((part,i)=>i%2?<code key={i}>{part}</code>:part);}
async function api(path:string,data?:unknown){
 const response=await fetch('/api/'+path,{method:data===undefined?'GET':'POST',headers:data===undefined?{}:{'Content-Type':'application/json'},body:data===undefined?undefined:JSON.stringify(data)});
 const result=await response.json();if(!response.ok)throw Error(typeof result.detail==='string'?result.detail:'Your practice could not be checked. Please try again.');return result;
}

function World({chapter}:{chapter:number}){
 return <svg className="story-world" viewBox="0 0 640 230" role="img" aria-label={['A moonlit castle beyond rolling hills','A backpack and lantern for your hero','A welcoming message above the castle','Two paths through an enchanted valley','A floating island ready for your adventure'][chapter]}>
  <defs><linearGradient id="sky" x2="0" y2="1"><stop stopColor="#dce8f4"/><stop offset="1" stopColor="#f5ead9"/></linearGradient></defs>
  <rect width="640" height="230" rx="20" fill="url(#sky)"/>
  <circle className="world-moon" cx="510" cy="48" r="24" fill="#fff8d5"/>
  <path d="M0 155Q95 85 210 151T430 130T640 145V230H0" fill="#acc8bc"/>
  <path d="M0 190Q100 135 230 180T460 165T640 180V230H0" fill="#739f91"/>
  <path d="M285 230Q370 185 320 148" fill="none" stroke="#eedcbb" strokeWidth="22"/>
  {chapter>=3&&<path d="M305 213Q420 210 465 154" fill="none" stroke="#eedcbb" strokeWidth="16"/>}
  <g fill="#4b686d"><rect x="264" y="82" width="102" height="76" rx="3"/><rect x="248" y="65" width="30" height="99"/><rect x="352" y="65" width="30" height="99"/></g>
  <g fill="#82668e"><path d="M242 66L263 35L284 66Z"/><path d="M346 66L367 35L388 66Z"/></g>
  <path d="M300 158V127Q315 103 330 127V158" fill="#f9d697"/>
  <g fill="#f9d697"><rect x="257" y="82" width="10" height="15" rx="4"/><rect x="361" y="82" width="10" height="15" rx="4"/></g>
  <g className="world-spark" fill="#ffffff"><path d="M153 48l3 8 8 3-8 3-3 8-3-8-8-3 8-3Z"/><path d="M440 78l2 6 6 2-6 2-2 6-2-6-6-2 6-2Z"/></g>
  {chapter===1&&<g><rect x="105" y="139" width="43" height="48" rx="12" fill="#b57851"/><path d="M115 140v-9q11-17 23 0v9" fill="none" stroke="#725341" strokeWidth="5"/><rect x="165" y="151" width="22" height="30" rx="5" fill="#ffe29b" stroke="#725341" strokeWidth="4"/></g>}
  {chapter===2&&<g><rect x="91" y="88" width="105" height="42" rx="15" fill="white"/><path d="M164 128l11 14v-16" fill="white"/><text x="114" y="115" fill="#385c50" fontSize="17" fontFamily="monospace">Hello!</text></g>}
  {chapter===4&&<g className="world-spark"><path d="M440 122l57-15 39 17-48 17Z" fill="#e4d0ae"/><path d="M440 122l48 19 48-17-43 41Z" fill="#859d94"/><path d="M478 112v-40l27 12-27 9" fill="#97749d" stroke="#715779" strokeWidth="3"/></g>}
 </svg>;
}

export default function Adventure({preview,onSaved,lessonId}:{preview:boolean;onSaved:()=>void;lessonId?:string}){
 const [lessons,setLessons]=useState<Lesson[]>([]),[selected,setSelected]=useState(0),[stage,setStage]=useState(0),[code,setCode]=useState(''),[output,setOutput]=useState(''),[report,setReport]=useState<Report|null>(null),[errorLine,setErrorLine]=useState<number|null>(null),[error,setError]=useState(''),[prediction,setPrediction]=useState<number|null>(null),[shownHints,setShownHints]=useState<HintStep[]>([]),[failedRuns,setFailedRuns]=useState(0),[replies,setReplies]=useState<string[]>([]),[done,setDone]=useState<string[]>([]),[running,setRunning]=useState(false),[passed,setPassed]=useState(false),[drafts,setDrafts]=useState<Record<string,string>>({}),[place,setPlace]=useState<Place|null>(null),[menuOpen,setMenuOpen]=useState(false);
 const worker=useRef<Worker|null>(null),timer=useRef<ReturnType<typeof setTimeout>|null>(null),heading=useRef<HTMLHeadingElement>(null),editor=useRef<HTMLTextAreaElement>(null),version=useRef(0);
 const lesson=lessons[selected];
 useEffect(()=>{
  let active=true;
  const query=new URLSearchParams(location.search),wanted=lessonId??query.get('lesson');
  // Lessons come one unit at a time (UI-05): the catalog says which unit holds the lesson. If the
  // catalog or that route is unavailable (for example an older API during a deploy), unit 1 comes
  // from /api/lessons as before.
  (async()=>{
   let items:Lesson[],where:Place|null=null;
   try{where=findUnit(await api('catalog') as Catalog,wanted);if(!where)throw Error();items=await api(`units/${where.unit.id}/lessons`);if(!Array.isArray(items)||!items.length)throw Error();}
   catch{items=await api('lessons');where=null;api('catalog').then((catalog:Catalog)=>{if(active)setPlace(findUnit(catalog,items[0].id));}).catch(()=>{});}
   if(!active)return;
   setLessons(items);if(where)setPlace(where);const index=Math.max(0,items.findIndex(l=>l.id===wanted));setSelected(index);setCode(items[index].example);setReplies(items[index].exampleInputs);if(preview){const target=Number(query.get('card'));if(target>=1&&target<=5)setStage(target-1);if(target===5)setCode(items[index].starter);}
  })().catch(()=>{if(active)setError('Lessons could not load. Please reload to try again.');});
  if(!preview)api('progress').then(x=>{if(active)setDone(x)}).catch(()=>setError('Saved progress could not load. Your lessons are still available.'));
  return()=>{active=false;worker.current?.terminate();if(timer.current)clearTimeout(timer.current);version.current++;};
 },[preview,lessonId]);
 function stop(){worker.current?.terminate();worker.current=null;if(timer.current)clearTimeout(timer.current);timer.current=null;setRunning(false);version.current++;}
 function focusCard(){requestAnimationFrame(()=>heading.current?.focus());}
 function address(index:number,card:number){window.history.replaceState({},'',preview?`/preview?lesson=${lessons[index].id}&card=${card+1}`:`/learn/${lessons[index].id}`);}
 function clear(){setReport(null);setErrorLine(null);}
 function move(card:number){stop();setStage(card);clear();setError('');setOutput('');setShownHints([]);setFailedRuns(0);setPassed(false);if(card===4)setCode(drafts[lesson.id+':4']??lesson.starter);else if(card===3)setCode(drafts[lesson.id+':3']??lesson.example);address(selected,card);focusCard();}
 function choose(index:number){stop();setMenuOpen(false);setSelected(index);setStage(0);setCode(lessons[index].example);setReplies(lessons[index].exampleInputs);setOutput('');setError('');clear();setShownHints([]);setFailedRuns(0);setPrediction(null);setPassed(false);address(index,0);focusCard();}
 function edit(value:string){
  // A check result is about the code that was checked, so it goes. A Python error stays until the next
  // run, but its highlight goes once that line changes (lesson-feedback.md section 5).
  if(report?.state!=='execution_error')setReport(null);
  if(errorLine&&(code.split('\n')[errorLine-1]!==value.split('\n')[errorLine-1]||code.split('\n').length!==value.split('\n').length))setErrorLine(null);
  setCode(value);setPassed(false);setDrafts(old=>({...old,[lesson.id+':'+stage]:value}));
 }
 function stopped(explanation:Explanation,python?:string,tag?:string|null){setReport({state:'execution_error',text:explanation.text,explanation,python,tag});setErrorLine(explanation.line);}
 // Runs on the challenge card that Python stopped or the check did not pass, in a row (decision 25).
 function failed(challenge:boolean){if(challenge)setFailedRuns(n=>n+1);}
 async function run(){
  stop();setRunning(true);clear();setError('');setOutput('Starting Python…');setPassed(false);
  const runVersion=version.current,runCode=code,runInputs=[...replies],runLesson=lesson.id,challenge=stage===4,context={code:runCode,unit:place?unitNumber(place.unit):1};
  if(challenge&&lesson.check==='browser-tests')return runChecks(runVersion,runCode,runLesson,context);
  const w=new Worker('/python-worker.js');worker.current=w;
  timer.current=setTimeout(()=>{if(version.current!==runVersion)return;stop();setOutput('Execution stopped after 15 seconds.');stopped(explain({stop:'timeout'},context));failed(challenge);},15000);
  w.onerror=()=>{if(version.current!==runVersion)return;stop();setOutput('Python could not start. Check your connection and try again.');};
  w.onmessage=async({data})=>{
   if(version.current!==runVersion)return;
   w.terminate();worker.current=null;if(timer.current)clearTimeout(timer.current);timer.current=null;
   // What printed before an error stays visible; the error itself is explained below the output.
   setOutput(data.output||(data.error?'(Nothing printed before Python stopped.)':'(No output yet.)'));
   if(data.error){setRunning(false);const error=data.outputLimit?null:parseError(data.error,data.errorType);stopped(explain(error??{stop:'output_limit'},context),pythonMessage(data.error),error?.type);failed(challenge);return;}
   // A run is not a check: printing something must never look like a pass.
   if(!challenge){setRunning(false);setReport({state:'ran',text:'Your code ran. This card has no check: compare the output with the task, then try another change.'});return;}
   try{
    const result=await api(preview?'check':'attempts',{lesson_id:runLesson,code:runCode,output:data.output,inputs:runInputs});
    if(version.current!==runVersion)return;
    show(result,runLesson);
   }catch(e){if(version.current===runVersion)setError((e as Error).message);}
   finally{if(version.current===runVersion)setRunning(false);}
  };
  w.postMessage({code:runCode,inputs:runInputs});
 }
 /** Shows a check result. Only the result state counts as a pass; an unknown state is shown as the
  * check being unavailable. A Python error explained in the browser replaces the check's own words. */
 function show(result:any,runLesson:string,python?:{explanation:Explanation;message?:string}|null){
  const state:Result=RESULTS.includes(result.result)?result.result:'service_error',ok=state==='passed'&&result.passed===true;
  const tag=state==='needs_work'?result.rule??result.failed?.error_type??null:state==='execution_error'?result.failed?.error_type??null:null;
  if(state==='execution_error'&&python)stopped(python.explanation,python.message,tag);
  else{setReport({state,tag,text:state===result.result?result.feedback:'Unable to assess this right now. Your code is unchanged; please try again in a moment.'});setErrorLine(checkLine(result));}
  setPassed(ok);
  if(ok)setFailedRuns(0);else if(state==='needs_work'||state==='execution_error')failed(true);
  if(ok)setDone(old=>old.includes(runLesson)?old:[...old,runLesson]);
  if(!preview)onSaved();
 }
 /** A challenge with a browser check (ENG-03, docs/plan/browser-checks.md): the cases run here, in a
  * fresh worker per run (public/check-runner.js), and only the reported output, status, error type
  * and line go to the API, which compares them with the expected output. Python's message stays here. */
 async function runChecks(runVersion:number,runCode:string,runLesson:string,context:{code:string;unit:number}){
  setOutput('Running the test cases…');
  try{
   const plan:Plan=await api(`checks/${runLesson}`);
   const runner=await import(/* webpackIgnore: true */ /* turbopackIgnore: true */ '/check-runner.js' as string);
   const reports:CaseReport[]=await runner.runCases(runCode,plan);
   if(version.current!==runVersion)return;
   setOutput(caseOutput(plan,reports));
   const result=await api(preview?'check':'attempts',{lesson_id:runLesson,code:runCode,output:reports[0]?.output??'',inputs:[],runs:runner.forSubmission(reports)});
   if(version.current!==runVersion)return;
   const failedCase=result.failed,report=reports.find(r=>r.id===failedCase?.id)??reports.find(r=>r.status==='error'),limits={seconds:plan.time_limit_ms/1000,limit:plan.output_limit.toLocaleString('en-US')};
   const python=failedCase?.reason==='timeout'?{explanation:explain({stop:'timeout'},context,limits)}
    :failedCase?.reason==='output_limit'?{explanation:explain({stop:'output_limit'},context,limits)}
    :failedCase?.reason==='error'?{explanation:explain({type:failedCase.error_type,line:failedCase.line,message:report?.message??''},context),message:report?.message??undefined}:null;
   show(result,runLesson,python);
  }catch(e){if(version.current===runVersion)setError((e as Error).message);}
  finally{if(version.current===runVersion)setRunning(false);}
 }
 if(!lesson)return <section className="card" role="status">{error||'Preparing your adventure…'}</section>;
 const completed=lessons.filter(l=>done.includes(l.id)).length;
 // aria-disabled, not disabled, on the last hint button, so keyboard focus is not lost when it changes.
 // The hint button gets a gentle outline after OUTLINE_AFTER failed runs: no popup, no movement.
 const next=nextHint(lesson.hints,lesson.errorHints??[],report?.tag??null,shownHints.map(h=>h.key),lesson.similarExample),outlined=failedRuns>=OUTLINE_AFTER&&next!==null,otherWays=lesson.otherWays??[];
 // Unit 1 keeps its own words and pictures; later units use their catalog title and summary.
 const unitOne=!place||place.unit.id==='py.u01',checked=stage===4&&lesson.check==='browser-tests';
 return <section className="adventure" aria-label={unitOne?'Build Your Own Adventure':place.unit.title}>
  {place&&<nav className="breadcrumb" aria-label="Breadcrumb"><ol><li><a href="/courses">Courses</a></li><li><a href={`/courses/${place.course.id}`}>{place.course.title}</a></li><li aria-current="page">Unit {unitNumber(place.unit)}: {place.unit.title}</li></ol></nav>}
  <div className="chapter-heading"><div>{unitOne?<><p className="eyebrow">UNIT 01 · BUILD SOMETHING THAT IS YOURS</p><h1>Build Your Own <span>Adventure.</span></h1><p>Five small quests. One story only you could make.</p></>:<><p className="eyebrow">UNIT {String(unitNumber(place.unit)).padStart(2,'0')} · {place.course.title.toUpperCase()}</p><h1>{place.unit.title}</h1><p>{place.unit.summary}</p></>}</div><div className="xp"><strong>{completed*100} XP</strong><span>{completed} of {lessons.length} badges earned{preview?' · preview session':''}</span></div></div>
  {preview&&<div className="preview-banner" role="note"><strong>Content preview</strong><span>Jump to any lesson or card. Practice and badges stay in this session; they are not saved.</span><a href="/">Return to your account</a></div>}
  <div className="lesson-layout">
  <nav className="unit-nav" aria-label="Lessons in this unit">
   <button className="unit-nav-toggle" aria-expanded={menuOpen} aria-controls="unit-lessons" onClick={()=>setMenuOpen(open=>!open)}><span><strong>Lesson {selected+1} of {lessons.length}</strong> · {completed} complete</span><span aria-hidden="true">{menuOpen?'▴':'▾'}</span></button>
   <div id="unit-lessons" className={menuOpen?'unit-nav-body open':'unit-nav-body'}>
    <p className="eyebrow">UNIT {place?unitNumber(place.unit):1}</p><p className="unit-nav-title">{place?.unit.title??'Build Your Own Adventure'}</p>
    <progress className="meter" value={completed} max={lessons.length} aria-label="Unit progress"/><p className="unit-nav-count">{completed} of {lessons.length} lessons complete</p>
    <ol className="unit-lessons">{lessons.map((item,index)=>{const finished=done.includes(item.id),current=index===selected;return <li key={item.id}><a href={preview?`/preview?lesson=${item.id}`:`/learn/${item.id}`} className={'unit-lesson'+(finished?' done':'')+(current?' current':'')} aria-current={current?'page':undefined} onClick={event=>{event.preventDefault();choose(index);}}><span className="unit-lesson-mark" aria-hidden="true">{finished?'✓':index+1}</span><span className="unit-lesson-text">{item.title}<small>{item.concept}</small></span><span className="visually-hidden">{finished?'Completed':current?'Current lesson':'Not started'}</span></a></li>;})}</ol>
    {place&&<a className="unit-nav-course" href={`/courses/${place.course.id}`}>All units in {place.course.title}</a>}
   </div>
  </nav>
  <div className="lesson-main">
  <div className="card-progress"><span>Quest {selected+1} of {lessons.length} · {lesson.badge}</span><span>Card {stage+1} of 5</span></div>
  <div className="stage-track" aria-label="Card progress">{stages.map((name,i)=>preview?<button key={name} aria-current={stage===i?'step':undefined} className={stage===i?'current':''} onClick={()=>move(i)}>{i+1}. {name}</button>:<span key={name} aria-current={stage===i?'step':undefined} className={stage===i?'current':''}>{i+1}. {name}</span>)}</div>
  <article className={'quest-card '+(stage>=3?'with-editor':'')} aria-label="Current learning card">
   <div className="teaching-panel">
    <p className="eyebrow">{stages[stage].toUpperCase()} · {lesson.concept}</p>
    <h2 ref={heading} tabIndex={-1}>{stage===0?lesson.learnTitle:stage===1?'Watch the story take shape':stage===2?'What do you think happens?':stage===3?'Make one small change':'Make it your own'}</h2>
    {stage===0&&<>{unitOne&&<World chapter={selected}/>}<p className="lead">{lesson.learn}</p><p>{lesson.detail}</p></>}
    {stage===1&&<><p>Read this working example, one line at a time.</p><pre className="example-code"><code>{lesson.example}</code></pre>{lesson.inputs.length>0&&<p className="reply-note">Player replies: {lesson.exampleInputs.join(' → ')}</p>}<h3>What appears on screen</h3><pre className="output">{lesson.exampleOutput}</pre><p>{lesson.exampleNote}</p></>}
    {stage===2&&<><pre className="example-code"><code>{lesson.example}</code></pre><fieldset className="prediction"><legend>{lesson.question}</legend>{lesson.options.map((option,index)=><button key={option} aria-pressed={prediction===index} onClick={()=>setPrediction(index)}>{option}</button>)}</fieldset>{prediction!==null&&<p className="feedback" role="status">{prediction===lesson.answer?'That’s it! ':'Let’s look again. '}{lesson.why}</p>}</>}
    {stage===3&&<>{unitOne&&<World chapter={selected}/>}<p className="lead">{lesson.guided}</p><p>The working example is in your editor. Experiment freely—you can always reset it.</p></>}
    {stage===4&&<><p className="lead">{lesson.challenge}</p><p className="reward-note">Complete the challenge to earn the {lesson.badge} badge and 100 XP.</p><p className="muted">Hints are beside your code. Take them one at a time, only if you want them.</p></>}
   </div>
   {stage>=3&&<section className="editor-panel" aria-label="Python playground"><div className="editor-top"><span>story.py</span><span>Python playground</span></div><label htmlFor="code">Your Python code</label><CodeEditor code={code} onChange={edit} disabled={running} errorLine={errorLine} describedBy={report?'editor-help code-feedback':'editor-help'} editor={editor}/><p id="editor-help" className="muted">Tab inserts four spaces. Shift + Tab leaves the editor.</p>
    {checked&&<p className="reply-note">This challenge runs your program with its own replies, including some you cannot see, and checks what it prints.</p>}
    {lesson.inputs.length>0&&!checked&&<fieldset className="player-replies"><legend>Player replies</legend><p>input() reads these in order. Prompts ask for your replies; only print() messages appear in Output.</p>{lesson.inputs.map((label,i)=><label key={label} htmlFor={'reply-'+i}>{label}<input id={'reply-'+i} maxLength={500} disabled={running} value={replies[i]??''} onChange={e=>{setReplies(old=>old.map((v,j)=>j===i?e.target.value:v));setPassed(false);if(report?.state!=='execution_error')setReport(null);}}/></label>)}</fieldset>}
    <div className="actions"><button className="primary" disabled={running} onClick={run}>{running?'Running…':stage===4?'Run & check challenge':'Run Python →'}</button>{running&&<button onClick={()=>{stop();setOutput('Execution stopped.');}}>Stop</button>}<button disabled={running} onClick={()=>{edit(stage===4?lesson.starter:lesson.example);setOutput('');clear();}}>Reset code</button></div><h3>Output</h3><pre className="output execution-output" aria-live="polite">{output||'Your story will appear here.'}</pre>
    <div id="code-feedback" className={'result'+(report?' '+report.state.replace('_','-'):'')} role="status">{report&&<><p className="result-state">{STATE_LABELS[report.state]}</p>{report.explanation?<><p className="result-title">{withCode(report.explanation.title)}</p>{report.explanation.where&&<p className="result-where">{report.explanation.where}</p>}<p>{withCode(report.explanation.text)}</p></>:<p>{report.text}</p>}</>}</div>
    {report&&(errorLine||report.python)&&<div className="result-actions">{errorLine&&<button onClick={()=>editor.current&&goToLine(editor.current,errorLine)}>Go to line {errorLine}</button>}{report.python&&<details><summary>Show Python’s message</summary><pre className="python-message">{report.python}</pre></details>}</div>}
    {stage===4&&<section className="hint-ladder" aria-labelledby="hints-title"><h3 id="hints-title">Hints</h3><ol aria-live="polite">{shownHints.map(hint=><li className="hint" key={hint.key}><strong>{hint.label}.</strong> {hint.text}{hint.code&&<pre className="example-code"><code>{hint.code}</code></pre>}</li>)}</ol><button className={outlined?'suggested':undefined} aria-disabled={!next} aria-describedby={outlined?'hint-suggested':undefined} onClick={()=>{if(next)setShownHints(old=>[...old,next]);}}>{next?next.button:HINT_TEXT.done}</button>{outlined&&<p id="hint-suggested" className="visually-hidden">{HINT_TEXT.suggested}</p>}{!next&&<p className="muted">{HINT_TEXT.noAnswer}</p>}</section>}
    {passed&&stage===4&&otherWays.length>0&&<section className="other-ways" aria-labelledby="other-ways-title"><h3 id="other-ways-title">{HINT_TEXT.otherWays}</h3><p className="muted">{HINT_TEXT.otherWaysIntro}</p>{otherWays.map(way=><figure key={way.code}><pre className="example-code"><code>{way.code}</code></pre><figcaption>{way.note}</figcaption></figure>)}</section>}
    {error&&<p className="notice" role="alert">{error}</p>}<p className="muted">Python runs in your browser. Challenge checks cover the syntax taught in this chapter; badges mark practice, not mastery.</p>
   </section>}
   {passed&&stage===4&&<div className="badge-earned" role="status"><span className="badge-icon" aria-hidden="true">✦</span><div><strong>{lesson.badge} badge earned!</strong><p>{done.includes(lesson.id)?'100 XP for this quest. Repeating it does not add extra XP.':''}{preview?' Preview badge: not saved.':' Your practice is saved.'}</p></div></div>}
   <div className="card-controls"><button disabled={stage===0||running} onClick={()=>move(stage-1)}>← Back</button><span>{stage===4?'Your story. Your pace.':'One idea at a time.'}</span>{stage<4?<button className="primary" disabled={running||(stage===2&&prediction!==lesson.answer)} onClick={()=>move(stage+1)}>{stage===3?'Start my challenge':'Continue →'}</button>:<button className="primary" disabled={!passed||running} onClick={()=>selected<lessons.length-1?choose(selected+1):move(0)}>{selected<lessons.length-1?'Next quest →':'Revisit this quest'}</button>}</div>
  </article>
  {completed===lessons.length&&(unitOne?<section className="chapter-complete"><h2>You made an adventure.</h2><p>Five badges. Four Python skills. Keep remixing your story, or invite someone to play it.</p></section>:place.unit.complete===true?<section className="chapter-complete"><h2>Unit complete.</h2><p>You finished every lesson in {place.unit.title}. <a href={`/courses/${place.course.id}`}>See the course</a> for what comes next.</p></section>
   :<section className="chapter-complete"><h2>You finished every lesson released so far.</h2><p>That is all of {place.unit.title} for now. <a href={`/courses/${place.course.id}`}>See the course</a> for what comes next.</p></section>)}
  </div>
  </div>
 </section>;
}
