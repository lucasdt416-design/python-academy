'use client';
// The Practice Arena (/practice): spaced review as a short battle. Five cards from lessons you have
// finished; each right answer lands a hit on the unit's creature. A wrong answer shows why and the card
// comes back once at the end, so every session can still be won. Nothing here changes XP or progress.
// Cards and answers: backend/app/review.py.
import {Fragment, useEffect, useState} from 'react';

type Card = {id: string; lesson: string; kind: 'predict' | 'trace' | 'order' | 'bug'; prompt: string; code?: string; options?: string[]; lines?: string[]; expected?: string; inputs?: string[]};
type Creature = {unit: string; name: string; about: string};
type Session = {cards: Card[]; due: number; ahead: boolean; unlocked: boolean; creature: Creature | null; tamed: string[]; creatures: Creature[]};
type Result = {correct: boolean; why: string; back_in_days: number; answer?: number; lines?: string[]};
const KIND: Record<Card['kind'], string> = {predict: 'Predict', trace: 'Trace', order: 'Arrange the lines', bug: 'Spot the bug'};

/** A creature for each unit, built from a few shapes so each one is different. */
const LOOKS: Record<string, {body: string; tone: string; extra: string}> = {
 'py.u01': {body: 'M-30 20q-6-44 30-50q36 6 30 50z', tone: 'outfit-plum', extra: 'M-8 -30l-6-14M8 -30l6-14'},
 'py.u02': {body: 'M-34 10q0-36 34-36t34 36q-12 14-34 14t-34-14z', tone: 'outfit-slate', extra: 'M-34 0l-18-14 10 20M34 0l18-14-10 20'},
 'py.u03': {body: 'M-26 22q-10-40 26-46q36 6 26 46z', tone: 'outfit-amber', extra: 'M-16 -22l-8-14 14 6M16 -22l8-14-14 6'},
 'py.u04': {body: 'M-32 22q-4-30 10-40q22-12 44 0q12 10 10 40z', tone: 'outfit-moss', extra: 'M30 10q20 0 22 12'},
 'py.u05': {body: 'M-24 20q-4-38 24-44q28 6 24 44z', tone: 'outfit-clay', extra: 'M-24 -6l-22-10 8 18M24 -6l22-10-8 18'},
 'py.u06': {body: 'M-34 22q-6-46 34-48q40 2 34 48z', tone: 'outfit-clay', extra: 'M-20 -22a8 8 0 1 1 2 0M20 -22a8 8 0 1 0-2 0'},
 'py.u07': {body: 'M-30 22q-2-36 30-40q32 4 30 40z', tone: 'outfit-amber', extra: 'M-20 -14l-10 18M20 -14l10 18'},
 'py.u08': {body: 'M-36 20q0-30 36-30t36 30z', tone: 'outfit-moss', extra: 'M-26 10h52M-14 -4h28'},
 'py.u09': {body: 'M-36 20q-2-16 12-20q12-4 12-18q0-12 12-12t12 12q0 14 12 18q14 4 12 20z', tone: 'outfit-plum', extra: ''},
 'py.u10': {body: 'M-26 22q-6-34 26-42q32 8 26 42z', tone: 'outfit-clay', extra: 'M-14 -16l-8-18 16 8M14 -16l8-18-16 8'},
 'py.u11': {body: 'M-32 22q-6-30 6-42q12-12 26-12q30 0 30 28v26z', tone: 'outfit-slate', extra: 'M-6 -32l4-10 4 10M8 -30l4-10 4 10'},
 'cs.u01': {body: 'M-10 22q-4-30 10-44q14 14 10 44z', tone: 'outfit-plum', extra: 'M-10 0q-34-30-40 6q10 18 40 4M10 0q34-30 40 6q-10 18-40 4M-4 -22l-6-12M4 -22l6-12'},
 'cs.u03': {body: 'M-28 24q-8-44 28-50q36 6 28 50z', tone: 'outfit-moss', extra: 'M-22 -22l-6-14 14 8M22 -22l6-14-14 8M-6 6l6 6 6-6'},
};
export function CreaturePicture({unit, hurt = 0, tamed = false, label}: {unit: string; hurt?: number; tamed?: boolean; label?: string}) {
 const look = LOOKS[unit] ?? LOOKS['py.u01'];
 return <svg viewBox="-60 -60 120 100" className={'creature' + (tamed ? ' tamed' : '') + (hurt ? ' hurt' : '')} role={label ? 'img' : undefined} aria-label={label} aria-hidden={label ? undefined : true}>
  <ellipse className="creature-shadow" cx="0" cy="24" rx="40" ry="6"/>
  <g key={hurt} className={hurt ? 'creature-hit' : undefined}>
   <path className={look.tone + ' s-ink'} d={look.body}/>
   {look.extra && <path className="s-ink" d={look.extra}/>}
   <circle className="f-white s-ink-s" cx="-10" cy="-6" r="7"/><circle className="f-white s-ink-s" cx="10" cy="-6" r="7"/>
   <circle className="f-ink" cx={tamed ? -9 : -11} cy="-5" r="3"/><circle className="f-ink" cx={tamed ? 11 : 9} cy="-5" r="3"/>
   <path className="s-ink-s" d={tamed ? 'M-8 8q8 6 16 0' : 'M-8 10q8-4 16 0'}/>
  </g>
 </svg>;
}

async function getSession(): Promise<Session> {
 const r = await fetch('/api/review');
 const body = await r.json();
 if (!r.ok) throw Error(typeof body.detail === 'string' ? body.detail : 'The arena could not load. Please try again.');
 return body;
}

function OrderCard({card, done, onAnswer}: {card: Card; done: Result | null; onAnswer: (lines: string[]) => void}) {
 const [lines, setLines] = useState(card.lines ?? []);
 useEffect(() => setLines(card.lines ?? []), [card.id, card.lines]);
 const move = (i: number, by: number) => setLines(old => { const next = old.slice(), j = i + by; [next[i], next[j]] = [next[j], next[i]]; return next; });
 return <>
  <p className="muted">It should print:</p><pre className="output arena-expected">{card.expected}</pre>
  {card.inputs?.length ? <p className="muted">Replies typed: {card.inputs.join(', ')}</p> : null}
  <ol className="order-lines">{lines.map((line, i) => <li key={line} className={done ? (done.lines?.[i] === line ? 'ok' : 'off') : undefined}>
   <code>{line}</code>
   {!done && <span className="order-buttons"><button type="button" className="btn small" disabled={i === 0} onClick={() => move(i, -1)} aria-label={`Move up: ${line.trim()}`}>↑</button><button type="button" className="btn small" disabled={i === lines.length - 1} onClick={() => move(i, 1)} aria-label={`Move down: ${line.trim()}`}>↓</button></span>}
  </li>)}</ol>
  {!done && <button type="button" className="primary" onClick={() => onAnswer(lines)}>Check the order</button>}
  {done && !done.correct && done.lines && <><p className="muted">The order that works:</p><pre className="example-code">{done.lines.join('\n')}</pre></>}
 </>;
}

export default function Arena() {
 const [session, setSession] = useState<Session | null>(null), [error, setError] = useState('');
 const [queue, setQueue] = useState<Card[]>([]), [retry, setRetry] = useState<Set<string>>(new Set()), [hits, setHits] = useState(0), [done, setDone] = useState<Result | null>(null), [choice, setChoice] = useState<number | null>(null);
 const [known, setKnown] = useState<Record<string, Result>>({}), [busy, setBusy] = useState(false);
 useEffect(() => { getSession().then(s => { setSession(s); setQueue(s.cards); }).catch(e => setError((e as Error).message)); }, []);
 if (error) return <p className="notice" role="alert">{error}</p>;
 if (!session) return <p role="status">Opening the arena…</p>;
 const card = queue[0], total = session.cards.length, creature = session.creature;
 async function answer(payload: {choice?: number; lines?: string[]}) {
  if (!card) return;
  setBusy(true);
  try {
   let result: Result;
   if (retry.has(card.id) && known[card.id]) {
    // The second try at a card is checked here, against the answer already shown; the schedule
    // stays as the first answer set it.
    const k = known[card.id];
    result = {...k, correct: card.kind === 'order' ? JSON.stringify(payload.lines) === JSON.stringify(k.lines) : payload.choice === k.answer};
   } else {
    const r = await fetch('/api/review/answer', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({card_id: card.id, ...payload})});
    const body = await r.json();
    if (!r.ok) throw Error(typeof body.detail === 'string' ? body.detail : 'That answer could not be checked. Please try again.');
    result = body;
    setKnown(old => ({...old, [card.id]: body}));
   }
   setDone(result);
   if (result.correct) setHits(h => h + 1);
  } catch (e) { setError((e as Error).message); } finally { setBusy(false); }
 }
 function next() {
  if (!card) return;
  const wrong = done && !done.correct && !retry.has(card.id);
  setQueue(q => wrong ? [...q.slice(1), card] : q.slice(1));
  if (wrong) setRetry(r => new Set(r).add(card.id));
  setDone(null); setChoice(null);
 }
 const won = total > 0 && hits >= total;
 return <section className="arena" aria-labelledby="arena-title">
  <div className="arena-head">
   <div><p className="kicker">practice arena</p><h1 id="arena-title">{creature ? `Tame the ${creature.name}` : 'The arena'}</h1>
    {creature && <p className="lead">{`${creature.about[0].toUpperCase()}${creature.about.slice(1)}. Answer its questions about lessons you have finished.`}</p>}</div>
   {creature && <div className="arena-creature"><CreaturePicture unit={creature.unit} hurt={hits} tamed={won} label={`The ${creature.name}${won ? ', tamed' : ''}`}/>
    <progress className="meter" value={total - hits} max={total || 1} aria-label={`${creature.name}: ${total - hits} of ${total} questions left`}/></div>}
  </div>
  {!session.unlocked && <p className="notice">Finish a lesson's challenge, and questions about it will appear here, spaced out over days so they stick.</p>}
  {session.unlocked && total === 0 && <p className="notice">Nothing to review right now. Come back tomorrow.</p>}
  {session.ahead && total > 0 && <p className="muted">Nothing is due today, so these are early practice.</p>}
  {card && <article className={'arena-card kind-' + card.kind} aria-labelledby="card-prompt">
   <p className="kicker">{KIND[card.kind]}{retry.has(card.id) ? ' · second try' : ''} · {Math.min(total, hits + 1)} of {total}</p>
   <h2 id="card-prompt">{card.prompt}</h2>
   {card.code && <pre className="example-code" tabIndex={0}><code>{card.kind === 'bug' ? card.code.split('\n').map((l, i) => <Fragment key={i}>{`${String(i + 1).padStart(2)}  ${l}`}{'\n'}</Fragment>) : card.code}</code></pre>}
   {card.kind === 'order' ? <OrderCard card={card} done={done} onAnswer={lines => answer({lines})}/> :
    <fieldset className="prediction"><legend className="visually-hidden">{card.prompt}</legend>
     {(card.options ?? []).map((option, i) => <button key={option} type="button" disabled={!!done || busy} aria-pressed={choice === i}
      className={'tile' + (done ? (i === done.answer ? ' right' : i === choice ? ' wrong' : '') : '')} onClick={() => { setChoice(i); answer({choice: i}); }}>
      <span className="ltr" aria-hidden="true">{'ABCDEFGH'[i]}</span><span><code>{option}</code></span></button>)}
    </fieldset>}
   {done && <div className={'feedback arena-feedback ' + (done.correct ? 'right' : 'wrong')} role="status">
    <p><strong>{done.correct ? 'A hit!' : 'Not this time.'}</strong> {done.why}</p>
    <p className="muted">{done.correct ? `This one comes back in ${done.back_in_days} ${done.back_in_days === 1 ? 'day' : 'days'}.` : retry.has(card.id) ? 'It comes back tomorrow.' : 'You get one more try at it at the end, and it comes back tomorrow.'}</p>
    <button type="button" className="primary" onClick={next}>{queue.length > 1 || (!done.correct && !retry.has(card.id)) ? 'Next question' : 'Finish'}</button>
   </div>}
  </article>}
  {!card && total > 0 && <div className="arena-end" role="status">
   <h2>{won ? `You tamed the ${creature?.name}!` : 'Well fought.'}</h2>
   <p>{won ? 'Every question answered. These cards come back over the next days, a little further apart each time they are right.' : 'The cards you missed come back tomorrow.'}</p>
   <a className="btn" href="/practice">Another round</a>
  </div>}
  <section aria-labelledby="collection-title" className="collection">
   <h2 id="collection-title">Your collection</h2>
   <p className="muted">A creature joins when its unit's questions have been answered right five times. It is a record of practice, not a grade.</p>
   <ul>{session.creatures.map(c => { const has = session.tamed.includes(c.unit); return <li key={c.unit} className={has ? 'has' : 'missing'}>
    {has ? <CreaturePicture unit={c.unit} tamed/> : <span className="creature-unknown" aria-hidden="true">?</span>}
    <span>{has ? c.name : 'Not met yet'}<small>Unit {Number(c.unit.split('.u')[1])}</small></span></li>; })}</ul>
  </section>
 </section>;
}
