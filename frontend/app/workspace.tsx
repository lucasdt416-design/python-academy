'use client';
// The project workspace (/projects/<id>, E1, docs/plan/courses/py-final-project.md section 3).
//
// A project's files, one open in the editor at a time. Run plays main.py as live play does (each reply
// re-runs it from the start), with the other .py files importable and every other file there to open.
// Changes save to the account a moment after typing stops. With "Keep files my program writes" on, the
// files a finished run made or changed are added to the project, so a save file is there next time.
import {useCallback, useEffect, useRef, useState} from 'react';
import CodeEditor, {goToLine} from './code-editor';
import LivePlay, {type Written} from './live-play';
import {ago, call} from './projects';

type Project = {id: number; title: string; starter: string; files: Record<string, string>; keep_written: boolean; updated: string; revision: number};
type Saving = {state: 'saved' | 'waiting' | 'saving' | 'failed' | 'stale'; message?: string};
type Snapshot = {program: string; modules: Record<string, string>; files: Record<string, string>; key: number};

const MAIN = 'main.py', SAVE_AFTER_MS = 1200, MAX_FILES = 20;
const NAME = /^[a-z][a-z0-9_-]{0,30}\.(py|txt|csv|json|md|html|css)$/;

/** What is wrong with a new file name, or ''. The server checks the same, and names Python's own modules too. */
export function nameProblem(name: string, taken: string[]): string {
 if (!name) return 'Type a name, like helpers.py or notes.txt.';
 if (!NAME.test(name)) return 'Use lowercase letters, digits, _ or -, start with a letter, and end with .py, .txt, .csv, .json, .md, .html or .css.';
 if (name.endsWith('.py') && name.includes('-')) return `Python can’t import a name with - in it. Try ${name.replace(/-/g, '_')}.`;
 if (taken.includes(name)) return `There is already a file called ${name}.`;
 return '';
}

/** The file and line an error came from: the last frame in the learner's own files. main.py runs as "<exec>". */
export function errorPlace(raw: string): {file: string; line: number} | null {
 const frames = [...raw.matchAll(/File "(<exec>|\/home\/pyodide\/([a-z][a-z0-9_]*\.py))", line (\d+)/g)];
 const last = frames.pop();
 return last ? {file: last[1] === '<exec>' ? MAIN : last[2], line: Number(last[3])} : null;
}

function runOf(files: Record<string, string>, key: number): Snapshot {
 const modules: Record<string, string> = {}, data: Record<string, string> = {};
 for (const [name, text] of Object.entries(files)) if (name !== MAIN) (name.endsWith('.py') ? modules : data)[name] = text;
 return {program: files[MAIN] ?? '', modules, files: data, key};
}

function list(names: string[]) { return names.length < 2 ? names.join('') : names.slice(0, -1).join(', ') + ' and ' + names[names.length - 1]; }

export default function Workspace({id}: {id: string}) {
 const [project, setProject] = useState<Project | null>(null), [error, setError] = useState(''), [open, setOpen] = useState(MAIN);
 const [saving, setSaving] = useState<Saving>({state: 'saved'}), [run, setRun] = useState<Snapshot | null>(null), [place, setPlace] = useState<{file: string; line: number} | null>(null);
 const [adding, setAdding] = useState<null | {name: string; problem: string}>(null), [renaming, setRenaming] = useState<null | {name: string; problem: string}>(null), [deleting, setDeleting] = useState(false);
 const [kept, setKept] = useState<null | {kept: string[]; notKept: string[]; skipped: string[]}>(null), [changedSinceRun, setChangedSinceRun] = useState(false);
 const editor = useRef<HTMLTextAreaElement>(null), latest = useRef<Project | null>(null), revision = useRef(0), timer = useRef<ReturnType<typeof setTimeout> | null>(null), inFlight = useRef(false), again = useRef(false), dirty = useRef(false), stale = useRef(false);

 useEffect(() => {
  call(`projects/${id}`).then((p: Project) => { setProject(p); latest.current = p; revision.current = p.revision; document.title = `${p.title} · Python Academy`; })
   .catch(e => setError((e as Error).message));
 }, [id]);
 // A tab closed with changes not yet saved asks first.
 useEffect(() => {
  const warn = (e: BeforeUnloadEvent) => { if (dirty.current || inFlight.current) e.preventDefault(); };
  addEventListener('beforeunload', warn); return () => removeEventListener('beforeunload', warn);
 }, []);

 const save = useCallback(async () => {
  if (timer.current) { clearTimeout(timer.current); timer.current = null; }
  const p = latest.current;
  if (!p || stale.current) return;
  if (inFlight.current) { again.current = true; return; }
  inFlight.current = true; dirty.current = false; setSaving({state: 'saving'});
  try {
   const saved: Project = await call(`projects/${p.id}`, 'PUT', {revision: revision.current, title: p.title, files: p.files, keep_written: p.keep_written});
   revision.current = saved.revision;
   setProject(cur => cur && {...cur, updated: saved.updated, revision: saved.revision});
   setSaving(dirty.current ? {state: 'waiting'} : {state: 'saved'});
  } catch (e) {
   const status = (e as {status?: number}).status;
   dirty.current = true;
   stale.current = status === 409;
   setSaving({state: status === 409 ? 'stale' : 'failed', message: status === 422 || status === 409 || status === 429 ? (e as Error).message : 'Not saved yet: the connection dropped. Your work is still here.'});
   again.current = false;
  } finally {
   inFlight.current = false;
   if (again.current) { again.current = false; void save(); }
  }
 }, []);

 /** Every change goes through here: it updates the page at once and saves a moment later. */
 function change(next: (p: Project) => Project, now = false) {
  const p = latest.current;
  if (!p || stale.current) return;
  const updated = next(p);
  latest.current = updated; setProject(updated); dirty.current = true;
  setSaving(s => s.state === 'failed' ? s : {state: 'waiting'});
  if (timer.current) clearTimeout(timer.current);
  if (now) void save(); else timer.current = setTimeout(() => void save(), SAVE_AFTER_MS);
 }
 const edit = (text: string) => { change(p => ({...p, files: {...p.files, [open]: text}})); if (run) setChangedSinceRun(true); setPlace(pl => pl?.file === open ? null : pl); };

 function choose(name: string, line?: number) {
  setOpen(name); setAdding(null); setRenaming(null); setDeleting(false);
  requestAnimationFrame(() => { if (editor.current) { if (line) goToLine(editor.current, line); else editor.current.scrollTop = 0; } });
 }
 function startRun() {
  const p = latest.current; if (!p) return;
  setKept(null); setPlace(null); setChangedSinceRun(false);
  setRun(r => runOf(p.files, (r?.key ?? 0) + 1));
 }
 // Functional updates only: LivePlay calls these from the run that was started, perhaps several renders ago.
 const finished = useCallback(({written, skipped}: Written) => {
  const names = Object.keys(written);
  if (!names.length && !skipped.length) return;
  const p = latest.current; if (!p) return;
  if (!p.keep_written) { setKept({kept: [], notKept: names, skipped}); return; }
  const fresh = names.filter(n => !(n in p.files)), room = MAX_FILES - Object.keys(p.files).length;
  const fits = names.filter(n => n in p.files || fresh.indexOf(n) < room);
  setKept({kept: fits, notKept: names.filter(n => !fits.includes(n)), skipped});
  if (fits.length) change(cur => ({...cur, files: {...cur.files, ...Object.fromEntries(fits.map(n => [n, written[n]]))}}), true);
 // change() and save() read only refs, so the first render's copies stay correct.
 }, []);// eslint-disable-line react-hooks/exhaustive-deps
 const failed = useCallback((raw: string | null) => setPlace(raw ? errorPlace(raw) : null), []);
 const where = useCallback((raw: string) => { const at = errorPlace(raw); return at ? `${at.file}, line ${at.line}` : null; }, []);

 if (error) return <section className="workspace"><p className="notice" role="alert">{error}</p><p><a href="/projects">Back to your projects</a></p></section>;
 if (!project) return <p role="status">Opening your project…</p>;
 const names = Object.keys(project.files), text = project.files[open] ?? '';
 const status = saving.state === 'saved' ? `Saved ${ago(project.updated)}` : saving.state === 'saving' ? 'Saving…' : saving.state === 'waiting' ? 'Changes not saved yet' : saving.message ?? '';

 function addFile(e: React.FormEvent) {
  e.preventDefault(); if (!adding) return;
  const name = adding.name.trim(), problem = nameProblem(name, names);
  if (problem) { setAdding({name, problem}); return; }
  setAdding(null);
  change(p => ({...p, files: {...p.files, [name]: ''}}), true);
  choose(name);
 }
 function renameFile(e: React.FormEvent) {
  e.preventDefault(); if (!renaming) return;
  const name = renaming.name.trim();
  if (name === open) { setRenaming(null); return; }
  const problem = nameProblem(name, names);
  if (problem) { setRenaming({name, problem}); return; }
  const from = open;
  change(p => ({...p, files: Object.fromEntries(Object.entries(p.files).map(([n, t]) => [n === from ? name : n, t]))}), true);
  setRenaming(null); setOpen(name);
 }
 function deleteFile() {
  const gone = open;
  change(p => { const files = {...p.files}; delete files[gone]; return {...p, files}; }, true);
  setDeleting(false); setOpen(MAIN);
 }

 return <section className="workspace" aria-labelledby="ws-title">
  <div className="ws-head">
   <a href="/projects" className="ws-back">Projects</a>
   <label htmlFor="ws-title" className="visually-hidden">Project name</label>
   <input id="ws-title" className="ws-title" maxLength={60} value={project.title} disabled={saving.state === 'stale'} onChange={e => change(p => ({...p, title: e.target.value}))}/>
   <p className={'ws-status' + (saving.state === 'failed' || saving.state === 'stale' ? ' bad' : '')} role="status">{status}{saving.state === 'failed' && <button type="button" className="btn small" onClick={() => void save()}>Try again</button>}{saving.state === 'stale' && <button type="button" className="btn small" onClick={() => location.reload()}>Reload</button>}</p>
  </div>
  <div className="ws-body">
   <nav className="ws-files" aria-label="Files">
    <h2 className="ws-label">Files</h2>
    <ul>{names.map(n => <li key={n}><button type="button" className={'ws-file' + (n === open ? ' on' : '')} aria-current={n === open ? 'true' : undefined} onClick={() => choose(n)}>{n}</button></li>)}</ul>
    {adding
     ? <form className="ws-name-form" onSubmit={addFile}><label htmlFor="ws-new">New file name</label><input id="ws-new" autoFocus value={adding.name} placeholder="helpers.py" autoComplete="off" spellCheck={false} aria-invalid={!!adding.problem} aria-describedby={adding.problem ? 'ws-new-problem' : undefined} onChange={e => setAdding({name: e.target.value.toLowerCase(), problem: ''})} onKeyDown={e => { if (e.key === 'Escape') setAdding(null); }}/>{adding.problem && <p id="ws-new-problem" className="ws-problem">{adding.problem}</p>}<div className="ws-row"><button className="btn small primary">Add</button><button type="button" className="btn small" onClick={() => setAdding(null)}>Cancel</button></div></form>
     : <button type="button" className="btn small" disabled={names.length >= MAX_FILES || saving.state === 'stale'} onClick={() => setAdding({name: '', problem: ''})}>New file</button>}
    {names.length >= MAX_FILES && <p className="muted">{MAX_FILES} files is the most a project holds.</p>}
    <label className="ws-keep"><input type="checkbox" checked={project.keep_written} disabled={saving.state === 'stale'} onChange={e => { const on = e.target.checked; change(p => ({...p, keep_written: on}), true); }}/> Keep files my program writes</label>
    <p className="muted ws-keep-note">{project.keep_written ? 'When a run finishes, text files it made or changed are saved here, so the next run can read them.' : 'Files your program writes are gone after each run.'}</p>
   </nav>
   <div className="ws-main">
    <div className="ws-file-bar">
     {renaming
      ? <form className="ws-name-form inline" onSubmit={renameFile}><label htmlFor="ws-rename" className="visually-hidden">New name for {open}</label><input id="ws-rename" autoFocus value={renaming.name} autoComplete="off" spellCheck={false} aria-invalid={!!renaming.problem} aria-describedby={renaming.problem ? 'ws-rename-problem' : undefined} onChange={e => setRenaming({name: e.target.value.toLowerCase(), problem: ''})} onKeyDown={e => { if (e.key === 'Escape') setRenaming(null); }}/><button className="btn small primary">Rename</button><button type="button" className="btn small" onClick={() => setRenaming(null)}>Cancel</button>{renaming.problem && <p id="ws-rename-problem" className="ws-problem">{renaming.problem}</p>}</form>
      : deleting
      ? <div className="ws-confirm" role="group" aria-label={`Delete ${open}?`}><span>Delete <code>{open}</code>? This can’t be undone.</span><button type="button" className="btn small danger" onClick={deleteFile}>Delete</button><button type="button" className="btn small" onClick={() => setDeleting(false)}>Keep it</button></div>
      : <><label htmlFor="code" className="ws-open"><span className="visually-hidden">Editing </span>{open}</label>
        {open === MAIN ? <span className="muted">Runs when you press Run</span> : <><button type="button" className="btn small quiet" disabled={saving.state === 'stale'} onClick={() => setRenaming({name: open, problem: ''})}>Rename</button><button type="button" className="btn small quiet" disabled={saving.state === 'stale'} onClick={() => setDeleting(true)}>Delete</button></>}
        <button type="button" className="btn primary ws-run" onClick={startRun}>{run ? 'Run again' : 'Run'}</button></>}
    </div>
    <CodeEditor code={text} onChange={edit} disabled={saving.state === 'stale'} errorLine={place?.file === open ? place.line : null} describedBy="ws-status-note" editor={editor}/>
    <p id="ws-status-note" className="visually-hidden">{open === MAIN ? 'main.py runs when you press Run.' : open.endsWith('.py') ? `main.py can use this file with import ${open.slice(0, -3)}.` : `Your program can open this file with open("${open}").`}</p>
    {open !== MAIN && <p className="muted ws-hint">{open.endsWith('.py') ? <>Use it from <code>main.py</code> with <code>import {open.slice(0, -3)}</code>.</> : <>Your program can read it with <code>open(&quot;{open}&quot;)</code>.</>}</p>}
    {run && <>
     {changedSinceRun && <p className="muted ws-stale-run">You changed the code since this run. Run again to see the change.</p>}
     <LivePlay key={run.key} heading="Output" program={run.program} files={run.files} modules={run.modules} unit={12} collect onFinished={finished} onError={failed} locate={where}/>
     {place && names.includes(place.file) && !(place.file === open && !changedSinceRun) && <p className="ws-place"><button type="button" className="btn small" onClick={() => choose(place.file, place.line)}>Show {place.file}, line {place.line}</button></p>}
     {kept && <div className="ws-kept" role="status">
      {kept.kept.length > 0 && <p>Kept what your program wrote: {list(kept.kept)}.</p>}
      {kept.notKept.length > 0 && (project.keep_written
       ? <p>Not kept, because a project holds {MAX_FILES} files: {list(kept.notKept)}.</p>
       : <p>Your program wrote {list(kept.notKept)}. {kept.notKept.length === 1 ? 'It is' : 'They are'} gone now. Turn on <strong>Keep files my program writes</strong> to keep {kept.notKept.length === 1 ? 'it' : 'them'}.</p>)}
      {kept.skipped.length > 0 && <p className="muted">Not kept, because only text files ending .txt, .csv, .json, .md, .html or .css, at the top of the project and up to 50,000 characters, can be: {list(kept.skipped)}.</p>}
     </div>}
    </>}
   </div>
  </div>
 </section>;
}
