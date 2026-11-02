/* Dedicated worker; learner code runs locally, never on the application server. */
importScripts('https://cdn.jsdelivr.net/pyodide/v0.27.7/full/pyodide.js');
// Replaces input() with the player replies typed on the page, in order.
const REPLIES = `
import json as __academy_json
import builtins as __academy_builtins
__academy_replies = iter(__academy_json.loads(__academy_input_json))
def __academy_input(prompt=''):
    try:
        return next(__academy_replies)
    except StopIteration:
        raise EOFError('Add a player reply for each input() call, in order.')
__academy_builtins.input = __academy_input
`;
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
 if (cases.some(c => c.call)) await py.runPythonAsync(CALLER, {filename: '<academy>'});
 self.postMessage({type:'ready'});
 for (const {id, inputs} of cases) {
  output = ''; capped = false;
  // Text an earlier case left in Python's output buffer (one stopped at the output limit leaves some)
  // belongs to that case: flush it out here and drop it, so it never shows up in this case's output.
  try { py.runPython('import sys\nsys.stdout.flush()'); } catch {}
  output = ''; capped = false;
  self.postMessage({type:'start', id});
  const namespace = py.toPy({__name__: '__main__'});
  let report;
  try {
   py.globals.set('__academy_input_json', JSON.stringify(inputs || []));
   // Its own file name, so errors inside it are not reported as lines of the learner's code.
   await py.runPythonAsync(REPLIES, {filename: '<academy>'});
   await py.runPythonAsync(code, {globals: namespace});
   let called = null;
   if (calls.get(id)) {
    // Only what the call itself prints is compared: a correct program may print other things first.
    await py.runPythonAsync('import sys\nsys.stdout.flush()');
    output = '';
    py.globals.set('__academy_namespace', namespace);
    py.globals.set('__academy_call_json', JSON.stringify(calls.get(id)));
    called = JSON.parse(await py.runPythonAsync(`__academy_call(__academy_namespace, __academy_call_json, ${outputLimit})`, {filename: '<academy>'}));
   }
   await py.runPythonAsync('import sys\nsys.stdout.flush()');
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
