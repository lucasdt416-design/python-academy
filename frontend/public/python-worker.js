/* Dedicated worker; learner code runs locally, never on the application server. */
importScripts('https://cdn.jsdelivr.net/pyodide/v0.27.7/full/pyodide.js');
// ENG-07, docs/plan/browser-checks.md section 9. The only list of modules a learner's program may import.
// To add one, say why in a handoff and check what it exposes: this list is also what stops a learner
// reaching os, js or pyodide by accident.
const ALLOWED_MODULES = ['math', 'random', 'datetime', 'json', 'csv', 're'];
// What the worker itself needs, loaded before the import guard goes on. Runs once per worker.
const SETUP = `
import builtins as __academy_builtins
import json as __academy_json
import random as __academy_random
import sys as __academy_sys

def __academy_flush():
    __academy_sys.stdout.flush()
`;
// The import guard. A module's own code imports what it needs as usual: random needs os, for example.
// Only the learner's program is limited. This is a guide for learners and not a sandbox, because Python
// cannot sandbox itself (random._os is one way round it). The real boundary is this worker, with no
// network and its Content-Security-Policy.
const GUARD = `
__academy_allowed = frozenset(__academy_json.loads(__academy_allowed_json))
# C code imports this one using the caller's globals, so datetime.strptime() looks like the learner's import.
__academy_internal = frozenset({'_strptime'})
__academy_real_import = __academy_builtins.__import__

def __academy_import(name, globals=None, locals=None, fromlist=(), level=0):
    owner = __academy_sys.modules.get((globals or {}).get('__name__'))
    from_a_module = owner is not None and owner.__name__ != '__main__' and vars(owner) is globals
    if not from_a_module and (level != 0 or name.partition('.')[0] not in __academy_allowed | __academy_internal):
        raise ModuleNotFoundError(f"The module {name!r} is not available here.", name=name)
    return __academy_real_import(name, globals, locals, fromlist, level)

__academy_builtins.__import__ = __academy_import
`;
async function guardImports(py, extra = '') {
 await py.runPythonAsync(SETUP + extra, {filename: '<academy>'});
 py.globals.set('__academy_allowed_json', JSON.stringify(ALLOWED_MODULES));
 await py.runPythonAsync(GUARD, {filename: '<academy>'});
}
// Replaces input() with the player replies typed on the page, in order.
const REPLIES = `
__academy_replies = iter(__academy_json.loads(__academy_input_json))
def __academy_input(prompt=''):
    try:
        return next(__academy_replies)
    except StopIteration:
        raise EOFError('Add a player reply for each input() call, in order.')
__academy_builtins.input = __academy_input
`;
// Files (ENG-08, docs/plan/browser-checks.md section 9). A program finds only the files it was given, in
// Pyodide's in-memory filesystem, and anything it wrote before is gone. Nothing here is ever saved.
const HOME = '/home/pyodide';
function emptyFolder(FS, folder) {
 for (const name of FS.readdir(folder)) {
  if (name === '.' || name === '..') continue;
  const path = `${folder}/${name}`;
  if (FS.isDir(FS.lstat(path).mode)) { emptyFolder(FS, path); FS.rmdir(path); } else FS.unlink(path);
 }
}
function freshFiles({FS}, files) {
 FS.mkdirTree(HOME);
 FS.chdir(HOME);
 for (const folder of [HOME, '/tmp']) emptyFolder(FS, folder);
 for (const [path, text] of Object.entries(files || {})) {
  const parts = path.split('/');
  if (parts.length > 1) FS.mkdirTree(`${HOME}/${parts.slice(0, -1).join('/')}`);
  FS.writeFile(`${HOME}/${path}`, text);
 }
}
// No network for learner code. Called once Pyodide has loaded, so nothing else needs these. The
// worker's Content-Security-Policy also only allows connections to the Pyodide CDN.
function noNetwork() {
 for (const name of ['fetch', 'XMLHttpRequest', 'WebSocket', 'EventSource', 'importScripts', 'caches']) {
  try { Object.defineProperty(self, name, {value: undefined, configurable: false}); } catch { self[name] = undefined; }
 }
}
self.onmessage = async ({data}) => {
 if (data.mode === 'cases') return runCases(data);
 let output = '', capped = false;
 try {
  // Python reports the stop as "OSError: [Errno 29] I/O error", so the flag says why it happened.
  const py = await loadPyodide({stdout:s=>{output+=s+'\n';if(output.length>20000){capped=true;throw Error('Output exceeded 20,000 characters.');}}});
  noNetwork();
  await guardImports(py);
  freshFiles(py, data.files);
  py.globals.set('__academy_input_json', JSON.stringify(data.inputs || []));
  // Its own file name, so an error inside it is not reported as a line of the learner's code.
  await py.runPythonAsync(REPLIES, {filename: '<academy>'});
  await py.runPythonAsync(data.code);
  self.postMessage({output});
 } catch(e) {
  // The page explains the error (app/feedback.ts); the output printed before it stays visible.
  self.postMessage({error:String(e), errorType:e.type || null, output, outputLimit:capped});
 }
};

// Browser behaviour checks (ENG-03, docs/plan/browser-checks.md). Runs the code once per check case
// with that case's replies, in a fresh namespace, and reports what it printed or how it stopped.
// The page (public/check-runner.js) stops this worker when a case runs too long; the API compares
// the output with the expected output.
// Python's message ends with "<Type>: <details>"; the learner's code is the file "<exec>".
const lastLine = message => [...String(message).matchAll(/File "<exec>", line (\d+)/g)].map(m => Number(m[1])).pop() ?? null;
const lastText = message => String(message).trim().split('\n').pop();
// Function-call cases (ENG-06, docs/plan/browser-checks.md section 8). Calls a function the learner's
// program defined, and describes what happened. An error inside the function is not caught here, so it
// reaches the page like any other Python error, with the line in the learner's code.
const CALLER = `
import inspect as __academy_inspect
import json as __academy_json_module
import re as __academy_re

def __academy_plain(value, depth=0):
    if depth > 20:
        raise ValueError('too deep')
    kind = type(value)
    if value is None or kind in (bool, int, str):
        return value
    if kind is float:
        if value != value or value in (float('inf'), float('-inf')):
            raise ValueError('not finite')
        return value
    if kind in (list, tuple):
        return [__academy_plain(item, depth + 1) for item in value]
    if kind is dict and all(type(key) is str for key in value):
        return {key: __academy_plain(item, depth + 1) for key, item in value.items()}
    raise ValueError('not plain')

def __academy_call(namespace, call_json, limit):
    call = __academy_json_module.loads(call_json)
    function = namespace.get(call['function'])
    if not callable(function):
        return __academy_json_module.dumps({'status': 'no_function'})
    args, kwargs = call.get('args', []), call.get('kwargs', {})
    try:
        signature = __academy_inspect.signature(function)
    except (TypeError, ValueError):
        signature = None
    if signature is not None:
        try:
            signature.bind(*args, **kwargs)
        except TypeError:
            return __academy_json_module.dumps({'status': 'bad_signature'})
    value = function(*args, **kwargs)
    kind = type(value).__name__
    try:
        text = __academy_json_module.dumps(__academy_plain(value), allow_nan=False)
        if len(text) > limit:
            raise ValueError('too long')
    except (TypeError, ValueError, RecursionError):
        name = kind if __academy_re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]{0,79}', kind) else 'unknown'
        return __academy_json_module.dumps({'status': 'not_comparable', 'errorType': name})
    return __academy_json_module.dumps({'status': 'ok', 'returned': text, 'shown': repr(value)[:200]})
`;
async function runCases({code, cases, outputLimit}) {
 const calls = new Map(cases.map(c => [c.id, c.call]));
 const given = new Map(cases.map(c => [c.id, c.files]));
 const references = new Map(cases.map(c => [c.id, c.reference]));
 let py;
 try { py = await loadPyodide(); } catch { self.postMessage({type:'unavailable'}); return; }
 noNetwork();
 let output = '', capped = false;
 // write (not batched) also delivers a last line that has no newline.
 const decoder = new TextDecoder();
 py.setStdout({write: bytes => {
  output += decoder.decode(bytes, {stream: true});
  if (output.length > outputLimit) { capped = true; output = output.slice(0, outputLimit); throw new Error('Output limit reached.'); }
  return bytes.length;
 }});
 await guardImports(py, cases.some(c => c.call) ? CALLER : '');
 self.postMessage({type:'ready'});
 for (const {id, inputs, seed} of cases) {
  output = ''; capped = false;
  // Text an earlier case left in Python's output buffer (one stopped at the output limit leaves some)
  // belongs to that case: flush it out here and drop it, so it never shows up in this case's output.
  try { py.runPython('__academy_flush()'); } catch {}
  output = ''; capped = false;
  self.postMessage({type:'start', id});
  const namespace = py.toPy({__name__: '__main__'});
  let report;
  try {
   freshFiles(py, given.get(id));
   py.globals.set('__academy_input_json', JSON.stringify(inputs || []));
   // Its own file name, so errors inside it are not reported as lines of the learner's code.
   await py.runPythonAsync(REPLIES, {filename: '<academy>'});
   // The same random numbers every run, so a check can expect them (0 unless the case sets one).
   await py.runPythonAsync(`__academy_random.seed(${Number(seed) || 0})`, {filename: '<academy>'});
   // ENG-10: the code under test, loaded first in the same namespace. Its own file name, so a line
   // number reported to the learner is always one of theirs.
   if (references.get(id) != null) await py.runPythonAsync(references.get(id), {globals: namespace, filename: '<reference>'});
   await py.runPythonAsync(code, {globals: namespace});
   let called = null;
   if (calls.get(id)) {
    // Only what the call itself prints is compared: a correct program may print other things first.
    await py.runPythonAsync('__academy_flush()', {filename: '<academy>'});
    output = '';
    py.globals.set('__academy_namespace', namespace);
    py.globals.set('__academy_call_json', JSON.stringify(calls.get(id)));
    called = JSON.parse(await py.runPythonAsync(`__academy_call(__academy_namespace, __academy_call_json, ${outputLimit})`, {filename: '<academy>'}));
   }
   await py.runPythonAsync('__academy_flush()', {filename: '<academy>'});
   report = capped ? {status: 'output_limit'} : {status: 'ok', ...called};
  } catch (e) {
   report = capped ? {status: 'output_limit'} : {status: 'error', errorType: e.type || e.name || null, line: lastLine(e.message), message: lastText(e.message)};
  } finally {
   namespace.destroy();
  }
  self.postMessage({type: 'case', id, output, ...report});
 }
 self.postMessage({type: 'done'});
}
