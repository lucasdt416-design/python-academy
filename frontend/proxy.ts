import {NextResponse, type NextRequest} from 'next/server';
import {PAGE_POLICY, noncePolicy} from './csp.mjs';

// Report-Only while false: browsers log what the policy would block but block nothing. Set to true
// to enforce it (handoff 08 section 5). `next dev` always stays Report-Only, because the development
// server injects inline styles and uses eval.
const ENFORCE = false;

// Runs before every page request (backlog SEC-09). See config.matcher for what it skips.
export function proxy(request: NextRequest) {
  // 128 random bits per request, so an injected script cannot guess the nonce.
  const nonce = btoa(String.fromCharCode(...crypto.getRandomValues(new Uint8Array(16))));
  const policy = noncePolicy(nonce);
  // Next.js reads the nonce from the request's Content-Security-Policy header (that one first,
  // else the Report-Only one) and adds it to its scripts. Set ours and drop any the caller sent.
  const headers = new Headers(request.headers);
  headers.set('content-security-policy', policy);
  headers.delete('content-security-policy-report-only');
  const response = NextResponse.next({request: {headers}});
  if (ENFORCE && process.env.NODE_ENV !== 'development') {
    response.headers.set('Content-Security-Policy', `${policy}; frame-ancestors 'none'`);
  } else {
    // Both policies, as two policies in one header: handoff 06's and this nonce policy.
    response.headers.set('Content-Security-Policy-Report-Only', `${PAGE_POLICY}, ${policy}`);
  }
  return response;
}

export const config = {
  matcher: [{
    // Pages only: not the API, sign-in, health check, built files or the Python worker, which
    // keeps its own policy from next.config.mjs.
    source: '/((?!api/|auth/|health|_next/|python-worker\\.js|favicon\\.ico).*)',
    // Link prefetches fetch data, not HTML, so they need no nonce.
    missing: [{type: 'header', key: 'next-router-prefetch'}, {type: 'header', key: 'purpose', value: 'prefetch'}],
  }],
};
