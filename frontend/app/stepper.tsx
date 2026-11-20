'use client';
// "Watch it run": step through a program one line at a time. The worker (public/python-worker.js,
// runTrace) runs it once and records every line of the learner's own code as it is about to run; this
// replays that recording. Nothing runs again while you step, and nothing here is sent anywhere.
import {Fragment, useEffect, useRef, useState} from 'react';
import {type PyNode, type Vars, show} from './scene-kit';

type Step = {line: number; event: 'line' | 'return' | 'exception'; fn: string; depth: number; vars: Vars; out: number; ret?: PyNode; exc?: string};
type Trace = {steps: Step[]; output: string; stopped: 'steps' | 'output' | null; error: string | null; line: number | null};

const fnName = (fn: string) => fn === '<module>' ? 'the main program' : `${fn}()`;
const valueOf = (v: PyNode | undefined) => v ? show(v, true) : '';
/** What changed between two steps in the same place, in words: "total changed from 4 to 8; x is new: 3". */
function changes(before: Vars, after: Vars): {name: string; was?: string; now: string}[] {
 return Object.entries(after).filter(([, v]) => v.t !== 'function' && v.t !== 'module' && v.t !== 'class')
  .map(([name, v]) => ({name, was: name in before ? valueOf(before[name]) : undefined, now: valueOf(v)}))
  .filter(c => c.was !== c.now);
}

/** One sentence for step i: what the line before it did, or the call or return that brought us here. */
export function narrate(trace: Trace, i: number, lines: string[]): string {
 const step = trace.steps[i], prev = trace.steps[i - 1], code = (n: number) => (lines[n - 1] ?? '').trim();
 const printed = prev ? trace.output.slice(prev.out, step.out).replace(/\n$/, '') : '';
 const said = printed ? ` It printed ${JSON.stringify(printed.length > 60 ? printed.slice(0, 59) + '…' : printed)}.` : '';
 if (!prev) return `The program is about to start, at line ${step.line}: ${code(step.line)}`;
 if (step.event === 'return' && step.fn === '<module>') return `Line ${prev.line} ran.${said} That is the end of the program.`;
 if (step.event === 'return') return `${fnName(step.fn)} finishes on line ${step.line} and gives back ${valueOf(step.ret) || 'None'}.${said}`;
 if (step.event === 'exception') return `Line ${step.line} raised ${step.exc}.${said}`;
 if (step.depth > prev.depth) {
  const handed = Object.entries(step.vars).map(([n, v]) => `${n} = ${valueOf(v)}`).join(', ');
  return `Line ${prev.line} called ${fnName(step.fn)}${handed ? `, which starts with ${handed}` : ''}. Next is line ${step.line}.${said}`;
 }
 if (step.depth < prev.depth) return `Back in ${fnName(step.fn)}, at line ${step.line}.${said}`;
 const changed = changes(prev.vars, step.vars);
 const what = changed.length ? ' ' + changed.map(c => c.was === undefined ? `${c.name} is now ${c.now}` : `${c.name} changed from ${c.was} to ${c.now}`).join('; ') + '.' : ' No name changed.';
 return `Line ${prev.line} ran.${what}${said} Next is line ${step.line}.`;
}

export default function Stepper({code, inputs, files, modules, onClose}: {code: string; inputs: string[]; files?: Record<string, string>; modules?: Record<string, string>; onClose: () => void}) {
 const [trace, setTrace] = useState<Trace | null>(null), [problem, setProblem] = useState(''), [at, setAt] = useState(0), [playing, setPlaying] = useState(false);
 const heading = useRef<HTMLHeadingElement>(null);
 useEffect(() => {
  const w = new Worker('/python-worker.js');
  const timer = setTimeout(() => { w.terminate(); setProblem('It took longer than 15 seconds to record. Try a shorter run, or fewer loop turns.'); }, 15000);
  w.onmessage = ({data}) => { clearTimeout(timer); w.terminate(); if (data.trace) setTrace(data.trace); else setProblem('Python could not start. Check your connection and try again.'); };
  w.onerror = () => { clearTimeout(timer); w.terminate(); setProblem('Python could not start. Check your connection and try again.'); };
  w.postMessage({mode: 'trace', code, inputs, files, modules});
  requestAnimationFrame(() => heading.current?.focus());
  return () => { clearTimeout(timer); w.terminate(); };
 // Recorded once, when opened: the page closes this panel when the code changes.
 }, []);// eslint-disable-line react-hooks/exhaustive-deps
 const last = trace ? Math.max(0, trace.steps.length - 1) : 0;
 useEffect(() => {
  if (!playing) return;
  if (at >= last) { setPlaying(false); return; }
  const t = setTimeout(() => setAt(a => Math.min(last, a + 1)), 650);
  return () => clearTimeout(t);
 }, [playing, at, last]);
 const lines = code.split('\n');
 const step = trace?.steps[at], prev = trace?.steps[at - 1];
 const changed = step && prev && step.depth === prev.depth ? new Set(changes(prev.vars, step.vars).map(c => c.name)) : new Set<string>();
 const shownVars = step ? Object.entries(step.vars).filter(([, v]) => v.t !== 'module' && v.t !== 'class') : [];
 return <section className="stepper" aria-labelledby="stepper-title">
  <div className="stepper-head">
   <h3 id="stepper-title" ref={heading} tabIndex={-1}>Watch it run</h3>
   {trace && <span className="muted">Step {at + 1} of {trace.steps.length}</span>}
   <button type="button" className="btn small" onClick={onClose}>Close</button>
  </div>
  {!trace && !problem && <p role="status">Recording each step…</p>}
  {problem && <p className="notice" role="alert">{problem}</p>}
  {trace && trace.steps.length === 0 && <p className="notice">{trace.error ? `Python could not read this program (${trace.error}${trace.line ? ` on line ${trace.line}` : ''}), so there are no steps to show. Fix it and try again.` : 'This program has no lines to step through.'}</p>}
  {trace && step && <>
   <div className="stepper-controls" role="group" aria-label="Step controls">
    <button type="button" className="btn small" onClick={() => { setPlaying(false); setAt(0); }} disabled={at === 0}>First</button>
    <button type="button" className="btn small" onClick={() => { setPlaying(false); setAt(a => Math.max(0, a - 1)); }} disabled={at === 0}>← Back</button>
    <button type="button" className="btn small primary" onClick={() => { setPlaying(false); setAt(a => Math.min(last, a + 1)); }} disabled={at === last}>Next →</button>
    <button type="button" className="btn small" onClick={() => { setPlaying(false); setAt(last); }} disabled={at === last}>Last</button>
    <button type="button" className="btn small" aria-pressed={playing} onClick={() => setPlaying(p => !p)} disabled={at === last && !playing}>{playing ? 'Pause' : 'Play'}</button>
    <label className="stepper-slider"><span className="visually-hidden">Step</span><input type="range" min={0} max={last} value={at} onChange={e => { setPlaying(false); setAt(Number(e.target.value)); }}/></label>
   </div>
   <p className="stepper-say" aria-live="polite">{narrate(trace, at, lines)}</p>
   <div className="stepper-body">
    <pre className="stepper-code" tabIndex={0} aria-label="Your program, with the next line marked"><code>{lines.map((text, i) => {
     const n = i + 1, next = n === step.line, ran = prev && n === prev.line && !next;
     return <Fragment key={n}><span className={'stepper-line' + (next ? ' next' : '') + (ran ? ' ran' : '')} aria-current={next ? 'step' : undefined}><span className="stepper-gutter" aria-hidden="true">{next ? '▶' : ran ? '✓' : ''}</span><span className="stepper-no" aria-hidden="true">{n}</span>{text || ' '}</span></Fragment>;
    })}</code></pre>
    <div className="stepper-side">
     <h4>{step.depth > 1 ? `Inside ${fnName(step.fn)}` : 'Names right now'}</h4>
     {step.depth > 1 && <p className="stepper-stack muted">{Array.from({length: step.depth - 1}, () => '↳ ').join('')}called from the main program</p>}
     {shownVars.length ? <table className="stepper-vars"><tbody>{shownVars.map(([name, v]) => <tr key={name} className={changed.has(name) ? 'changed' : undefined}>
      <th scope="row">{name}</th><td><code>{valueOf(v)}</code>{changed.has(name) && prev && name in prev.vars ? <span className="was"> was {valueOf(prev.vars[name])}</span> : changed.has(name) ? <span className="was"> new</span> : null}</td></tr>)}</tbody></table>
      : <p className="muted">No names yet.</p>}
     {step.event === 'return' && <p className="stepper-return">Gives back <code>{valueOf(step.ret) || 'None'}</code></p>}
     <h4>Printed so far</h4>
     <pre className="output stepper-output">{trace.output.slice(0, step.out) || ' '}</pre>
    </div>
   </div>
   {at === last && <p className="muted" role="status">{trace.error ? `Python stopped here with ${trace.error}${trace.line ? ` on line ${trace.line}` : ''}.` : trace.stopped === 'steps' ? `Stopped recording after ${trace.steps.length} steps. A loop that runs this long may never end: check that something changes each time round.` : trace.stopped === 'output' ? 'Stopped: the program printed too much.' : 'The program finished.'}</p>}
  </>}
 </section>;
}
