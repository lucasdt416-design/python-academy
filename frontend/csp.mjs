// Content-Security-Policy values (backlog SEC-04 and SEC-09), shared by next.config.mjs and proxy.ts.

// Handoff 06 policy. 'unsafe-inline' lets Next.js's inline scripts run, but also any injected one.
export const PAGE_POLICY = ["default-src 'self'", "script-src 'self' 'unsafe-inline'", "style-src 'self'", "img-src 'self'", "font-src 'self'", "connect-src 'self'", "worker-src 'self'", "object-src 'none'", "base-uri 'none'", "form-action 'self'"].join('; ');

// SEC-09: the same policy, except that inline scripts run only if they carry this request's nonce.
// proxy.ts makes a new nonce for every page request and Next.js adds it to its own scripts.
export function noncePolicy(nonce) {
  return PAGE_POLICY.replace("script-src 'self' 'unsafe-inline'", `script-src 'self' 'nonce-${nonce}'`);
}

// Pyodide runs in this worker, which has its own enforced policy: it may load Pyodide from the CDN
// and compile it ('unsafe-eval' covers WebAssembly), and nothing else.
export const WORKER_POLICY = "default-src 'none'; script-src 'unsafe-eval' https://cdn.jsdelivr.net; connect-src https://cdn.jsdelivr.net";
