/* Dedicated worker; learner code runs locally, never on the application server. */
importScripts('https://cdn.jsdelivr.net/pyodide/v0.27.7/full/pyodide.js');
self.onmessage = async ({data}) => {
 try {
  let output = '';
  const py = await loadPyodide({stdout:s=>{output+=s+'\n';if(output.length>20000)throw Error('Output exceeded 20,000 characters.');}});
  py.globals.set('__academy_input_json', JSON.stringify(data.inputs || []));
  await py.runPythonAsync(`
import json as __academy_json
import builtins as __academy_builtins
__academy_replies = iter(__academy_json.loads(__academy_input_json))
def __academy_input(prompt=''):
    try:
        return next(__academy_replies)
    except StopIteration:
        raise EOFError('Add a player reply for each input() call, in order.')
__academy_builtins.input = __academy_input
`);
  await py.runPythonAsync(data.code);
  self.postMessage({output});
 } catch(e) {self.postMessage({error:String(e)});}
};
