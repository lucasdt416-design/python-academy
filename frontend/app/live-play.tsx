'use client';
// Live play (E2, docs/plan/courses/py-final-project.md section 3): play a program that asks questions,
// typing each reply when it asks, instead of typing every reply before the run.
//
// Nothing new runs anywhere else: each reply re-runs the program from the start, in a fresh worker
// (public/python-worker.js, live: true), with every reply so far. Random numbers use one seed for the
// whole game, so every re-run plays out the same way, and the usual 15-second and output limits apply
// to each run. Nothing here is sent to the API.
import {useEffect, useRef, useState} from 'react';
import {explain, parseError, type Explanation} from './feedback';

const MAX_REPLIES = 100;
type Turn = {output: string; waiting: string | null; finished: boolean; error: Explanation | null};

function code(text: string) { return text.split('`').map((part, i) => i % 2 ? <code key={i}>{part}</code> : part); }

export default function LivePlay({program, files, modules, unit}: {program: string; files?: Record<string, string>; modules?: Record<string, string>; unit: number}) {
 const [replies, setReplies] = useState<string[]>([]), [turn, setTurn] = useState<Turn | null>(null), [running, setRunning] = useState(true), [problem, setProblem] = useState(''), [draft, setDraft] = useState('');
 const [seed, setSeed] = useState(() => Math.floor(Math.random() * 1_000_000));
 const spare = useRef<Worker | null>(null), heading = useRef<HTMLHeadingElement>(null), field = useRef<HTMLInputElement>(null);
 // A worker loads and checks Python while the player is still typing, so a reply doesn't wait for that.
 const take = () => { const w = spare.current ?? new Worker('/python-worker.js'); spare.current = null; return w; };
 const warm = () => { if (!spare.current) { spare.current = new Worker('/python-worker.js'); spare.current.postMessage({mode: 'warm'}); } };

 useEffect(() => {
  setRunning(true); setProblem('');
  const w = take();
  const timer = setTimeout(() => { w.terminate(); setRunning(false); setTurn(t => ({output: t?.output ?? '', waiting: null, finished: false, error: explain({stop: 'timeout'}, {code: program, unit})})); }, 15000);
  w.onerror = () => { clearTimeout(timer); w.terminate(); setRunning(false); setProblem('Python could not start. Check your connection and try again.'); };
  w.onmessage = ({data}) => {
   clearTimeout(timer); w.terminate(); setRunning(false);
   const error = data.error ? explain(data.outputLimit ? {stop: 'output_limit'} : parseError(data.error, data.errorType), {code: program, unit}) : null;
   setTurn({output: data.output ?? '', waiting: typeof data.waiting === 'string' ? data.waiting : null, finished: data.finished === true, error});
   if (typeof data.waiting === 'string') { warm(); requestAnimationFrame(() => field.current?.focus()); }
  };
  w.postMessage({code: program, inputs: replies, files, modules, live: true, seed});
  return () => { clearTimeout(timer); w.terminate(); };
 // A new run for each reply, and when the game starts over; the page closes this panel when the code changes.
 }, [replies, seed]);// eslint-disable-line react-hooks/exhaustive-deps
 useEffect(() => { requestAnimationFrame(() => heading.current?.focus()); return () => spare.current?.terminate(); }, []);

 const send = (e: React.FormEvent) => { e.preventDefault(); if (running || turn?.waiting == null) return; setReplies(r => [...r, draft]); setDraft(''); };
 const restart = () => { setReplies([]); setDraft(''); setTurn(null); setSeed(Math.floor(Math.random() * 1_000_000)); };
 const full = replies.length >= MAX_REPLIES;
 return <section className="live-play" aria-labelledby="live-title">
  <div className="stepper-head">
   <h3 id="live-title" ref={heading} tabIndex={-1}>Play it live</h3>
   <span className="muted">{replies.length} {replies.length === 1 ? 'reply' : 'replies'}</span>
   <button type="button" className="btn small" onClick={restart} disabled={running && !turn}>Start over</button>
  </div>
  <p className="muted live-how">Type each reply when your program asks. Each reply reruns it from the start with every reply so far (random numbers stay the same), so it picks up where it left off.</p>
  <pre className="output live-screen" aria-live="polite" aria-busy={running}>{turn?.output || (running ? 'Starting Python…' : '(Nothing printed yet.)')}</pre>
  {problem && <p className="notice" role="alert">{problem}</p>}
  {turn?.waiting != null && !full && <form className="live-reply" onSubmit={send}>
   <label htmlFor="live-reply">{turn.waiting.trim() ? <>Your program asks: <span className="live-prompt">{turn.waiting}</span></> : 'Your program is waiting for a reply'}</label>
   <div className="live-row"><input id="live-reply" ref={field} maxLength={500} autoComplete="off" value={draft} disabled={running} onChange={e => setDraft(e.target.value)}/><button className="primary" disabled={running}>{running ? 'Running…' : 'Reply'}</button></div>
  </form>}
  <div role="status">
   {full && turn?.waiting != null && <p className="notice">That is {MAX_REPLIES} replies, the most one game can take here. Start over to play again.</p>}
   {turn?.finished && <p className="live-end">The program finished. Start over to play again.</p>}
   {turn?.error && <div className="result execution-error"><p className="result-title">{code(turn.error.title)}</p>{turn.error.where && <p className="result-where">{turn.error.where}</p>}<p>{code(turn.error.text)}</p></div>}
  </div>
 </section>;
}
