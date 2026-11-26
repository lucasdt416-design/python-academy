'use client';
// The projects page (/projects, E1): a learner's own projects, and the starters a new one can begin from.
// Projects are kept with the learner's account and seen only by them (backend app/projects.py).
import {useEffect, useState} from 'react';

export type ProjectSummary = {id: number; title: string; starter: string; files: number; updated: string; revision: number};
export type Starter = {id: string; title: string; about: string; final: boolean; files: string[]};

export async function call(path: string, method = 'GET', data?: unknown) {
 const r = await fetch('/api/' + path, {method, headers: data === undefined ? {} : {'Content-Type': 'application/json'}, body: data === undefined ? undefined : JSON.stringify(data)});
 const body = await r.json().catch(() => ({}));
 if (!r.ok) { const e = Error(typeof body.detail === 'string' ? body.detail : 'Something went wrong. Please try again.') as Error & {status?: number}; e.status = r.status; throw e; }
 return body;
}

/** "just now", "5 minutes ago", "yesterday", or the date. */
export function ago(iso: string, now = Date.now()) {
 const s = Math.max(0, (now - new Date(iso).getTime()) / 1000);
 if (s < 60) return 'just now';
 if (s < 3600) { const m = Math.floor(s / 60); return `${m} ${m === 1 ? 'minute' : 'minutes'} ago`; }
 if (s < 86400) { const h = Math.floor(s / 3600); return `${h} ${h === 1 ? 'hour' : 'hours'} ago`; }
 if (s < 172800) return 'yesterday';
 return new Date(iso).toLocaleDateString(undefined, {day: 'numeric', month: 'short', year: 'numeric'});
}

function StarterRow({s, busy, onStart}: {s: Starter; busy: boolean; onStart: () => void}) {
 return <li className="starter">
  <div><h3>{s.title}</h3><p>{s.about}</p><p className="muted">Starts with {s.files.map((f, i) => <span key={f}>{i ? ', ' : ''}<code>{f}</code></span>)}</p></div>
  <button type="button" className="btn small" disabled={busy} onClick={onStart}>Start {s.title === 'Empty project' ? 'an empty project' : s.title}</button>
 </li>;
}

export default function Projects() {
 const [list, setList] = useState<ProjectSummary[] | null>(null), [most, setMost] = useState(20), [starters, setStarters] = useState<Starter[]>([]);
 const [error, setError] = useState(''), [busy, setBusy] = useState(false), [confirming, setConfirming] = useState<number | null>(null);
 useEffect(() => {
  call('projects').then(b => { setList(b.projects); setMost(b.most); }).catch(e => setError((e as Error).message));
  call('project-starters').then(setStarters).catch(() => {});
 }, []);
 async function start(id: string) {
  setBusy(true); setError('');
  try { const made = await call('projects', 'POST', {starter: id}); location.assign(`/projects/${made.id}`); }
  catch (e) { setError((e as Error).message); setBusy(false); }
 }
 async function remove(id: number) {
  setBusy(true); setError('');
  try { await call(`projects/${id}`, 'DELETE'); setList(l => (l ?? []).filter(p => p.id !== id)); setConfirming(null); }
  catch (e) { setError((e as Error).message); } finally { setBusy(false); }
 }
 const finals = starters.filter(s => s.final), others = starters.filter(s => !s.final);
 return <section className="projects" aria-labelledby="projects-title">
  <h1 id="projects-title">Projects</h1>
  <p className="lead">Build something of your own, in as many files as it needs. Your code runs in this browser, and the files are saved to your account, where only you can see them.</p>
  {error && <p className="notice" role="alert">{error}</p>}
  {list === null ? !error && <p role="status">Loading your projects…</p> : list.length > 0 && <>
   <h2>Yours</h2>
   <ul className="project-list">{list.map(p => <li key={p.id}>
    <div><a href={`/projects/${p.id}`} className="project-name">{p.title}</a><p className="muted">{p.files} {p.files === 1 ? 'file' : 'files'} · changed {ago(p.updated)}</p></div>
    {confirming === p.id
     ? <div className="project-confirm" role="group" aria-label={`Delete ${p.title}?`}><span>Delete it and all its files? This can’t be undone.</span><button type="button" className="btn small danger" disabled={busy} onClick={() => remove(p.id)}>Delete</button><button type="button" className="btn small" onClick={() => setConfirming(null)}>Keep it</button></div>
     : <button type="button" className="btn small quiet" onClick={() => setConfirming(p.id)} aria-label={`Delete ${p.title}`}>Delete</button>}
   </li>)}</ul>
   {list.length >= most && <p className="muted">You have {most} projects, the most an account keeps. Delete one to start another.</p>}
  </>}
  {starters.length > 0 && <>
   <h2>Start a project</h2>
   <ul className="starter-list">{others.map(s => <StarterRow key={s.id} s={s} busy={busy || (list?.length ?? 0) >= most} onStart={() => start(s.id)}/>)}</ul>
   {finals.length > 0 && <>
    <h3 className="starter-group">Final projects for Python Foundations</h3>
    <p className="muted">Each comes with its data file and empty versions of the functions it is built on. The lesson <a href="/learn/py.final-brief">Choose your project</a> helps you pick one and plan it.</p>
    <ul className="starter-list">{finals.map(s => <StarterRow key={s.id} s={s} busy={busy || (list?.length ?? 0) >= most} onStart={() => start(s.id)}/>)}</ul>
   </>}
  </>}
 </section>;
}
