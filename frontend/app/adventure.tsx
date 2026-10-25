'use client';
import {useEffect, useRef, useState} from 'react';

type Lesson = {id:string;title:string;concept:string;badge:string;description:string;learnTitle:string;learn:string;detail:string;example:string;exampleOutput:string;exampleNote:string;question:string;options:string[];answer:number;why:string;guided:string;starter:string;challenge:string;hints:string[];inputs:string[];exampleInputs:string[]};
const stages=['Discover','See it work','Predict','Try it','Your challenge'];
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

export default function Adventure({preview,onSaved}:{preview:boolean;onSaved:()=>void}){
 const [lessons,setLessons]=useState<Lesson[]>([]),[selected,setSelected]=useState(0),[stage,setStage]=useState(0),[code,setCode]=useState(''),[output,setOutput]=useState(''),[feedback,setFeedback]=useState(''),[error,setError]=useState(''),[prediction,setPrediction]=useState<number|null>(null),[hints,setHints]=useState(0),[replies,setReplies]=useState<string[]>([]),[done,setDone]=useState<string[]>([]),[running,setRunning]=useState(false),[passed,setPassed]=useState(false),[drafts,setDrafts]=useState<Record<string,string>>({});
 const worker=useRef<Worker|null>(null),timer=useRef<ReturnType<typeof setTimeout>|null>(null),heading=useRef<HTMLHeadingElement>(null),questMap=useRef<HTMLElement>(null),version=useRef(0);
 const lesson=lessons[selected];
 useEffect(()=>{const nav=questMap.current,active=nav?.children[selected] as HTMLElement|undefined;if(nav&&active&&nav.scrollWidth>nav.clientWidth)nav.scrollLeft+=active.getBoundingClientRect().left-nav.getBoundingClientRect().left-(nav.clientWidth-active.clientWidth)/2;},[selected,lessons]);
 useEffect(()=>{
  let active=true;
  api('lessons').then((items:Lesson[])=>{if(!active)return;setLessons(items);const query=new URLSearchParams(location.search);const index=Math.max(0,items.findIndex(l=>l.id===query.get('lesson')));setSelected(index);setCode(items[index].example);setReplies(items[index].exampleInputs);if(preview){const target=Number(query.get('card'));if(target>=1&&target<=5)setStage(target-1);if(target===5)setCode(items[index].starter);}}).catch(()=>setError('Lessons could not load. Please reload to try again.'));
  if(!preview)api('progress').then(x=>{if(active)setDone(x)}).catch(()=>setError('Saved progress could not load. Your lessons are still available.'));
  return()=>{active=false;worker.current?.terminate();if(timer.current)clearTimeout(timer.current);version.current++;};
 },[preview]);
 function stop(){worker.current?.terminate();worker.current=null;if(timer.current)clearTimeout(timer.current);timer.current=null;setRunning(false);version.current++;}
 function focusCard(){requestAnimationFrame(()=>heading.current?.focus());}
 function address(index:number,card:number){if(preview)window.history.replaceState({},'',`/preview?lesson=${lessons[index].id}&card=${card+1}`);}
 function move(card:number){stop();setStage(card);setFeedback('');setError('');setOutput('');setHints(0);setPassed(false);if(card===4)setCode(drafts[lesson.id+':4']??lesson.starter);else if(card===3)setCode(drafts[lesson.id+':3']??lesson.example);address(selected,card);focusCard();}
 function choose(index:number){stop();setSelected(index);setStage(0);setCode(lessons[index].example);setReplies(lessons[index].exampleInputs);setOutput('');setError('');setFeedback('');setHints(0);setPrediction(null);setPassed(false);address(index,0);focusCard();}
 function edit(value:string){setCode(value);setPassed(false);setFeedback('');setDrafts(old=>({...old,[lesson.id+':'+stage]:value}));}
 async function run(){
  stop();setRunning(true);setFeedback('');setError('');setOutput('Starting Python…');setPassed(false);
  const runVersion=version.current,runCode=code,runInputs=[...replies],runLesson=lesson.id,challenge=stage===4;
  const w=new Worker('/python-worker.js');worker.current=w;
  timer.current=setTimeout(()=>{if(version.current!==runVersion)return;stop();setOutput('Execution stopped after 15 seconds. Check for an endless loop and try again.');},15000);
  w.onerror=()=>{if(version.current!==runVersion)return;stop();setOutput('Python could not start. Check your connection and try again.');};
  w.onmessage=async({data})=>{
   if(version.current!==runVersion)return;
   w.terminate();worker.current=null;if(timer.current)clearTimeout(timer.current);timer.current=null;
   setOutput(data.error||data.output||'(No output yet.)');
   if(data.error){setRunning(false);setFeedback(/SyntaxError|IndentationError/.test(data.error)?'Check matching quotes and parentheses. If you used if/else, check colons and four-space indentation.':/NameError/.test(data.error)?'Check the variable or function name. Python is case-sensitive: print is lowercase, and a variable must be defined before use.':'Read the error above, make one change, and try again.');return;}
   if(!challenge){setRunning(false);setFeedback('Your code ran. Compare the result with the task, then try another change.');return;}
   try{
    const result=await api(preview?'check':'attempts',{lesson_id:runLesson,code:runCode,output:data.output,inputs:runInputs});
    if(version.current!==runVersion)return;
    setFeedback(result.feedback);setPassed(result.passed);
    if(result.passed)setDone(old=>old.includes(runLesson)?old:[...old,runLesson]);
    if(!preview)onSaved();
   }catch(e){if(version.current===runVersion)setError((e as Error).message);}
   finally{if(version.current===runVersion)setRunning(false);}
  };
  w.postMessage({code:runCode,inputs:runInputs});
 }
 if(!lesson)return <section className="card" role="status">{error||'Preparing your adventure…'}</section>;
 const completed=lessons.filter(l=>done.includes(l.id)).length;
 return <section className="adventure" aria-label="Build Your Own Adventure">
  <div className="chapter-heading"><div><p className="eyebrow">CHAPTER 01 · BUILD SOMETHING THAT IS YOURS</p><h1>Build Your Own <span>Adventure.</span></h1><p>Five small quests. One story only you could make.</p></div><div className="xp"><strong>{completed*100} XP</strong><span>{completed} of 5 badges earned{preview?' · preview session':''}</span></div></div>
  {preview&&<aside className="preview-banner"><strong>Content preview</strong><span>Jump to any lesson or card. Practice and badges stay in this session; they are not saved.</span><a href="/">Return to your account</a></aside>}
  <nav ref={questMap} className="quest-map" aria-label="Lessons">{lessons.map((item,index)=><button key={item.id} className={selected===index?'quest active':'quest'} aria-current={selected===index?'step':undefined} onClick={()=>choose(index)}><span className="quest-number" aria-hidden="true">{done.includes(item.id)?'✓':String(index+1).padStart(2,'0')}</span><span>{item.title}<small>{item.concept}</small>{done.includes(item.id)&&<small>Badge earned</small>}</span></button>)}</nav>
  <div className="card-progress"><span>Quest {selected+1} of 5 · {lesson.badge}</span><span>Card {stage+1} of 5</span></div>
  <div className="stage-track" aria-label="Card progress">{stages.map((name,i)=>preview?<button key={name} aria-current={stage===i?'step':undefined} className={stage===i?'current':''} onClick={()=>move(i)}>{i+1}. {name}</button>:<span key={name} aria-current={stage===i?'step':undefined} className={stage===i?'current':''}>{i+1}. {name}</span>)}</div>
  <article className={'quest-card '+(stage>=3?'with-editor':'')} aria-label="Current learning card">
   <div className="teaching-panel">
    <p className="eyebrow">{stages[stage].toUpperCase()} · {lesson.concept}</p>
    <h2 ref={heading} tabIndex={-1}>{stage===0?lesson.learnTitle:stage===1?'Watch the story take shape':stage===2?'What do you think happens?':stage===3?'Make one small change':'Make it your own'}</h2>
    {stage===0&&<><World chapter={selected}/><p className="lead">{lesson.learn}</p><p>{lesson.detail}</p></>}
    {stage===1&&<><p>Read this working example, one line at a time.</p><pre className="example-code"><code>{lesson.example}</code></pre>{lesson.inputs.length>0&&<p className="reply-note">Player replies: {lesson.exampleInputs.join(' → ')}</p>}<h3>What appears on screen</h3><pre className="output">{lesson.exampleOutput}</pre><p>{lesson.exampleNote}</p></>}
    {stage===2&&<><pre className="example-code"><code>{lesson.example}</code></pre><fieldset className="prediction"><legend>{lesson.question}</legend>{lesson.options.map((option,index)=><button key={option} aria-pressed={prediction===index} onClick={()=>setPrediction(index)}>{option}</button>)}</fieldset>{prediction!==null&&<p className="feedback" role="status">{prediction===lesson.answer?'That’s it! ':'Let’s look again. '}{lesson.why}</p>}</>}
    {stage===3&&<><World chapter={selected}/><p className="lead">{lesson.guided}</p><p>The working example is in your editor. Experiment freely—you can always reset it.</p></>}
    {stage===4&&<><p className="lead">{lesson.challenge}</p><p className="reward-note">Complete the challenge to earn the {lesson.badge} badge and 100 XP.</p><button onClick={()=>setHints(x=>Math.min(3,x+1))} disabled={hints===3}>{hints===3?'All hints shown':'Show next hint'}</button><div aria-live="polite">{lesson.hints.slice(0,hints).map((hint,i)=><p className="hint" key={hint}><strong>Hint {i+1}.</strong> {hint}</p>)}</div></>}
   </div>
   {stage>=3&&<section className="editor-panel" aria-label="Python playground"><div className="editor-top"><span>story.py</span><span>Python playground</span></div><label htmlFor="code">Your Python code</label><textarea id="code" spellCheck={false} rows={11} value={code} disabled={running} aria-describedby="editor-help" onChange={e=>edit(e.target.value)} onKeyDown={e=>{if(e.key==='Tab'&&!e.shiftKey){e.preventDefault();const target=e.currentTarget,start=target.selectionStart,end=target.selectionEnd;edit(code.slice(0,start)+'    '+code.slice(end));requestAnimationFrame(()=>{target.selectionStart=target.selectionEnd=start+4;});}}}/><p id="editor-help" className="muted">Tab inserts four spaces. Shift + Tab leaves the editor.</p>
    {lesson.inputs.length>0&&<fieldset className="player-replies"><legend>Player replies</legend><p>input() reads these in order. Prompts ask for your replies; only print() messages appear in Output.</p>{lesson.inputs.map((label,i)=><label key={label} htmlFor={'reply-'+i}>{label}<input id={'reply-'+i} maxLength={500} disabled={running} value={replies[i]??''} onChange={e=>{setReplies(old=>old.map((v,j)=>j===i?e.target.value:v));setPassed(false);setFeedback('');}}/></label>)}</fieldset>}
    <div className="actions"><button className="primary" disabled={running} onClick={run}>{running?'Running…':stage===4?'Run & check challenge':'Run Python →'}</button>{running&&<button onClick={()=>{stop();setOutput('Execution stopped.');}}>Stop</button>}<button disabled={running} onClick={()=>{edit(stage===4?lesson.starter:lesson.example);setOutput('');setFeedback('');}}>Reset code</button></div><h3>Output</h3><pre className="output execution-output" aria-live="polite">{output||'Your story will appear here.'}</pre>{feedback&&<p className="feedback" role="status">{feedback}</p>}{error&&<p className="notice" role="alert">{error}</p>}<p className="muted">Python runs in your browser. Challenge checks cover the syntax taught in this chapter; badges mark practice, not mastery.</p>
   </section>}
   {passed&&stage===4&&<div className="badge-earned" role="status"><span className="badge-icon" aria-hidden="true">✦</span><div><strong>{lesson.badge} badge earned!</strong><p>{done.includes(lesson.id)?'100 XP for this quest. Repeating it does not add extra XP.':''}{preview?' Preview badge: not saved.':' Your practice is saved.'}</p></div></div>}
   <div className="card-controls"><button disabled={stage===0||running} onClick={()=>move(stage-1)}>← Back</button><span>{stage===4?'Your story. Your pace.':'One idea at a time.'}</span>{stage<4?<button className="primary" disabled={running||(stage===2&&prediction!==lesson.answer)} onClick={()=>move(stage+1)}>{stage===3?'Start my challenge':'Continue →'}</button>:<button className="primary" disabled={!passed||running} onClick={()=>selected<lessons.length-1?choose(selected+1):move(0)}>{selected<lessons.length-1?'Next quest →':'Revisit this quest'}</button>}</div>
  </article>
  {completed===5&&<section className="chapter-complete"><h2>You made an adventure.</h2><p>Five badges. Four Python skills. Keep remixing your story, or invite someone to play it.</p></section>}
 </section>;
}
