// Dummy values only in this local test process; no real credentials or backend.
Deno.env.set('SUPABASE_URL', 'https://abcdefghijklmnopqrst.supabase.co');
Deno.env.set('SUPABASE_SERVICE_ROLE_KEY', 'local-test-placeholder');
Deno.env.set('MAMBA_CANDIDATE_ORIGIN', 'https://facundocapello-blip.github.io');
const {handleRoomRequest} = await import('./index.ts');
const origin = 'https://facundocapello-blip.github.io';
function assert(condition: unknown, message: string) { if (!condition) throw new Error(message); }
function request(body: string, method='POST', source=origin) {
  return new Request('https://staging.test/functions/v1/multiplayer-room', {method,headers:{Origin:source},...(method==='POST'?{body}:{})});
}

Deno.test('reject unapproved browser origin before RPC', async () => {
  const response = await handleRoomRequest(request('{}', 'POST', 'https://other.test'));
  assert(response.status===403, 'Origin must be rejected');
});
Deno.test('CORS preflight only permits explicit candidate origin', async () => {
  const response = await handleRoomRequest(request('', 'OPTIONS'));
  assert(response.status===204, 'Preflight status');
  assert(response.headers.get('Access-Control-Allow-Origin')===origin, 'No wildcard origin');
});
Deno.test('reject GET and malformed JSON', async () => {
  assert((await handleRoomRequest(request('', 'GET'))).status===405, 'Only POST');
  assert((await handleRoomRequest(request('{'))).status===400, 'Bad JSON');
});
Deno.test('cap incoming request size', async () => {
  assert((await handleRoomRequest(request(' '.repeat(131073)))).status===413, 'Body limit');
});
Deno.test('forward valid action to the staging RPC and return result', async () => {
  const original = globalThis.fetch;
  globalThis.fetch = async (url, options) => {
    assert(String(url)==='https://abcdefghijklmnopqrst.supabase.co/rest/v1/rpc/mamba_staging_action', 'Staging only');
    assert(JSON.parse(String(options?.body)).payload.action==='create', 'RPC envelope');
    return new Response(JSON.stringify({code:'ABC123',token:'local-fake-token'}), {headers:{'Content-Type':'application/json'}});
  };
  try {
    const response = await handleRoomRequest(request(JSON.stringify({action:'create',name:'Test'})));
    assert(response.status===200, 'Success');
    assert((await response.json()).code==='ABC123', 'Response preserved');
  } finally { globalThis.fetch = original; }
});
Deno.test('upstream failure does not expose service credentials or details', async () => {
  const original = globalThis.fetch;
  globalThis.fetch = async () => new Response('private upstream error', {status:500});
  try {
    const response = await handleRoomRequest(request('{"action":"get"}'));
    assert(response.status===503, 'Unavailability');
    assert((await response.text())==='{"error":"staging_unavailable"}', 'Sanitized response');
  } finally { globalThis.fetch = original; }
});
