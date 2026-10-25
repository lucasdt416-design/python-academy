const backend = process.env.BACKEND_URL || (process.env.BACKEND_HOSTPORT ? `http://${process.env.BACKEND_HOSTPORT}` : 'http://localhost:8000');

// Security headers (backlog SEC-04). The page policy is in Report-Only mode: browsers log what it
// would block (DevTools console) but block nothing. To enforce it, follow handoff 06 section 4:
// send PAGE_POLICY + "; frame-ancestors 'none'" as Content-Security-Policy instead.
// 'unsafe-inline' scripts: Next.js puts its page data in inline <script> tags whose contents
// change per page, so hashes cannot list them; nonces would need a request-time proxy (follow-up).
export const PAGE_POLICY = ["default-src 'self'", "script-src 'self' 'unsafe-inline'", "style-src 'self'", "img-src 'self'", "font-src 'self'", "connect-src 'self'", "worker-src 'self'", "object-src 'none'", "base-uri 'none'", "form-action 'self'"].join('; ');
// Pyodide runs in this worker, which has its own enforced policy: it may load Pyodide from the CDN
// and compile it ('unsafe-eval' covers WebAssembly), and nothing else.
export const WORKER_POLICY = "default-src 'none'; script-src 'unsafe-eval' https://cdn.jsdelivr.net; connect-src https://cdn.jsdelivr.net";

export default {
  async rewrites() { return [ {source:'/health',destination:`${backend}/health`}, {source:'/api/:path*',destination:`${backend}/api/:path*`}, {source:'/auth/:path*',destination:`${backend}/auth/:path*`} ]; },
  async headers() { return [
    {source:'/:path*',headers:[
      {key:'Strict-Transport-Security',value:'max-age=31536000; includeSubDomains'},
      {key:'X-Content-Type-Options',value:'nosniff'},
      {key:'Referrer-Policy',value:'no-referrer'},
      {key:'X-Frame-Options',value:'DENY'},
      // frame-ancestors is ignored in Report-Only policies, so it is enforced on its own now.
      {key:'Content-Security-Policy',value:"frame-ancestors 'none'"},
      {key:'Content-Security-Policy-Report-Only',value:PAGE_POLICY},
    ]},
    // Listed last so it replaces the page headers above for the worker (Next.js: the last match wins).
    {source:'/python-worker.js',headers:[{key:'Content-Security-Policy',value:WORKER_POLICY},{key:'Content-Security-Policy-Report-Only',value:WORKER_POLICY}]},
  ]; }
};
