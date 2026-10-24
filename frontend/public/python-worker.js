/* Dedicated worker: no server-side execution and no application cookies passed in. */
importScripts('https://cdn.jsdelivr.net/pyodide/v0.27.7/full/pyodide.js');
self.onmessage = async ({data}) => {
 try {
  let output = '';
  const py = await loadPyodide({stdout:s=>{output+=s+'\n';if(output.length>20000)throw Error('Output exceeded 20,000 characters.');}});
  await py.runPythonAsync(data.code);
  self.postMessage({output});
 } catch(e) {self.postMessage({error:String(e)});}
};
