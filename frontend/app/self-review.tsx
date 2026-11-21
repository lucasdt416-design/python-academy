'use client';
// ENG-09: a challenge the learner reviews themselves (backend/app/self_review.py). Each part of a short
// rubric is ticked and answered in the learner's own words. The API looks only at the writing (enough
// words, not the question copied back, nothing the text policy refuses) and, signed in, keeps a finished
// review as self-reported evidence. Drafts never leave the page.
import {useState} from 'react';

export type Criterion = {id: string; text: string; ask: string; min_words: number};
export type SelfReview = {kind: 'rubric' | 'reflection' | 'local-tutorial'; criteria: Criterion[]};
type Answer = {done: boolean; evidence: string};
type Result = {recorded: boolean; result: string; problems: Record<string, string>; feedback: string};

const count = (text: string) => (text.match(/[A-Za-z0-9']+/g) ?? []).length;

export default function SelfReviewPanel({lessonId, review, preview, onRecorded}: {lessonId: string; review: SelfReview; preview: boolean; onRecorded: () => void}) {
 const [answers, setAnswers] = useState<Record<string, Answer>>({});
 const [result, setResult] = useState<Result | null>(null), [sending, setSending] = useState(false), [error, setError] = useState('');
 const set = (id: string, change: Partial<Answer>) => setAnswers(old => ({...old, [id]: {done: false, evidence: '', ...old[id], ...change}}));
 async function send() {
  setSending(true); setError('');
  try {
   const r = await fetch(preview ? '/api/self-review/preview' : '/api/self-review', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({lesson_id: lessonId, answers})});
   const body = await r.json();
   if (!r.ok) throw Error(typeof body.detail === 'string' ? body.detail : 'Your review could not be sent. What you wrote is still here.');
   setResult(body);
   if (body.recorded || body.result === 'ready') onRecorded();
  } catch (e) { setError(e instanceof Error ? e.message : 'Your review could not be sent. What you wrote is still here.'); }
  finally { setSending(false); }
 }
 const problems = result?.problems ?? {};
 return <section className="self-review" aria-labelledby="self-review-title">
  <h3 id="self-review-title">Your review</h3>
  <p className="muted">Tick each part when it is done, and say what you did in your own words. Nothing checks the work itself, so this is kept as <strong>your own review</strong>{preview ? '; in a preview nothing is saved' : ''}.</p>
  <ol className="review-parts">{review.criteria.map(c => {
   const a = answers[c.id] ?? {done: false, evidence: ''}, words = count(a.evidence), note = problems[c.id];
   return <li key={c.id} className={note ? 'needs' : result?.recorded ? 'ok' : undefined}>
    <label className="review-tick"><input type="checkbox" checked={a.done} onChange={e => set(c.id, {done: e.target.checked})}/>{c.text}</label>
    <label className="review-ask" htmlFor={`review-${c.id}`}>{c.ask}</label>
    <textarea id={`review-${c.id}`} rows={2} maxLength={2000} value={a.evidence} aria-describedby={`count-${c.id}${note ? ` note-${c.id}` : ''}`} onChange={e => set(c.id, {evidence: e.target.value})}/>
    <p id={`count-${c.id}`} className="review-count">{words} {words === 1 ? 'word' : 'words'} · at least {c.min_words}</p>
    {note && <p id={`note-${c.id}`} className="review-note">{note}</p>}
   </li>;
  })}</ol>
  <div className="actions"><button className="primary" disabled={sending} onClick={send}>{sending ? 'Sending…' : preview ? 'Check my review' : 'Record my review'}</button></div>
  <div className={'result' + (result ? (result.recorded || result.result === 'ready' ? ' passed' : ' needs-work') : '')} role="status">{result && <p>{result.feedback}</p>}</div>
  {error && <p className="notice" role="alert">{error}</p>}
 </section>;
}
