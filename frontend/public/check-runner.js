/* Browser behaviour checks (ENG-03, docs/plan/browser-checks.md).
 * Runs the learner's code against each case of a check plan from GET /api/checks/<lesson id>, in a
 * fresh Pyodide worker, and stops the worker if a case runs longer than the plan allows. It returns
 * one report per case, which forSubmission() turns into the `runs` of POST /api/check or
 * /api/attempts. It decides nothing: the API compares the output with the expected output, which
 * for hidden cases only the API has. Python's own error message stays in the browser.
 */
export const LOAD_LIMIT_MS = 30000;

export function runCases(code, plan, {workerUrl = '/python-worker.js', loadLimitMs = LOAD_LIMIT_MS} = {}) {
 return new Promise(resolve => {
  const reports = new Map(plan.cases.map(c => [c.id, {id: c.id, status: 'not_run', output: '', errorType: null, line: null, message: null}]));
  const worker = new Worker(workerUrl);
  let timer = null, current = null, finished = false;
  const finish = () => {
   if (finished) return;
   finished = true; clearTimeout(timer); worker.terminate();
   resolve(plan.cases.map(c => reports.get(c.id)));
  };
  const unavailable = () => { for (const report of reports.values()) report.status = 'unavailable'; finish(); };
  // Loading Python can take a while on a slow connection; the per-case limit starts after it.
  timer = setTimeout(unavailable, loadLimitMs);
  worker.onerror = unavailable;
  worker.onmessage = ({data}) => {
   if (finished) return;
   if (data.type === 'unavailable') unavailable();
   else if (data.type === 'ready') clearTimeout(timer);
   else if (data.type === 'start') {
    current = data.id; clearTimeout(timer);
    // A loop that never ends blocks the worker, so only terminating it can stop the program.
    timer = setTimeout(() => { reports.get(current).status = 'timeout'; finish(); }, plan.time_limit_ms);
   } else if (data.type === 'case') {
    clearTimeout(timer);
    reports.set(data.id, {id: data.id, status: data.status, output: String(data.output || '').slice(0, plan.output_limit),
     errorType: data.errorType ?? null, line: data.line ?? null, message: data.message ?? null,
     // A function-call case (ENG-06): the value as JSON for the API, and as Python shows it for the page.
     ...(data.returned != null ? {returned: data.returned, shown: data.shown} : {})});
   } else if (data.type === 'done') finish();
  };
  worker.postMessage({mode: 'cases', code, cases: plan.cases.map(({id, inputs, call, files, seed}) => ({id, inputs, ...(call ? {call} : {}), ...(files ? {files} : {}), ...(seed ? {seed} : {})})), outputLimit: plan.output_limit});
 });
}

/** The reports as the API accepts them: no error message, which can echo the learner's own text. */
export function forSubmission(reports) {
 return reports.map(({id, status, output, errorType, line, returned}) => ({id, status, output, error_type: errorType, line, ...(returned != null ? {returned} : {})}));
}
