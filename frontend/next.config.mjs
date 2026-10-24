const backend = process.env.BACKEND_URL || 'http://localhost:8000';
export default {
  async rewrites() { return [ {source:'/health',destination:`${backend}/health`}, {source:'/api/:path*',destination:`${backend}/api/:path*`}, {source:'/auth/:path*',destination:`${backend}/auth/:path*`} ]; },
  async headers() { return [{source:'/python-worker.js',headers:[{key:'Content-Security-Policy',value:"default-src 'none'; script-src 'unsafe-eval' https://cdn.jsdelivr.net; connect-src https://cdn.jsdelivr.net"}]},{source:'/:path*',headers:[{key:'X-Content-Type-Options',value:'nosniff'},{key:'Referrer-Policy',value:'no-referrer'},{key:'X-Frame-Options',value:'DENY'}]}]; }
};
