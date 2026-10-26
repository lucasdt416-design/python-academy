import {WORKER_POLICY} from './csp.mjs';

const backend = process.env.BACKEND_URL || (process.env.BACKEND_HOSTPORT ? `http://${process.env.BACKEND_HOSTPORT}` : 'http://localhost:8000');

// Security headers (backlog SEC-04). The page Content-Security-Policy is set per request in
// proxy.ts (SEC-09), in Report-Only mode; handoff 08 section 5 has the switch to enforce mode.

export default {
  async rewrites() { return [ {source:'/health',destination:`${backend}/health`}, {source:'/api/:path*',destination:`${backend}/api/:path*`}, {source:'/auth/:path*',destination:`${backend}/auth/:path*`} ]; },
  async headers() { return [
    {source:'/:path*',headers:[
      {key:'Strict-Transport-Security',value:'max-age=31536000; includeSubDomains'},
      {key:'X-Content-Type-Options',value:'nosniff'},
      {key:'Referrer-Policy',value:'no-referrer'},
      {key:'X-Frame-Options',value:'DENY'},
      // frame-ancestors is ignored in Report-Only policies, so it is enforced on its own now.
      // The page policies themselves come from proxy.ts, because they need a nonce per request.
      {key:'Content-Security-Policy',value:"frame-ancestors 'none'"},
    ]},
    // Listed last so it replaces the page headers above for the worker (Next.js: the last match wins).
    {source:'/python-worker.js',headers:[{key:'Content-Security-Policy',value:WORKER_POLICY},{key:'Content-Security-Policy-Report-Only',value:WORKER_POLICY}]},
  ]; }
};
