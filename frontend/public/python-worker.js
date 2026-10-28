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
async function runCases({code, cases, outputLimit}) {
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
   await py.runPythonAsync('import sys\nsys.stdout.flush()');
   report = {status: capped ? 'output_limit' : 'ok'};
  } catch (e) {
   report = capped ? {status: 'output_limit'} : {status: 'error', errorType: e.type || e.name || null, line: lastLine(e.message), message: lastText(e.message)};
  } finally {
   namespace.destroy();
  }
  self.postMessage({type: 'case', id, output, ...report});
 }
 self.postMessage({type: 'done'});
}
