// Isolated staging adapter. Never deploy with the production project ref.
const projectUrl = Deno.env.get('SUPABASE_URL') ?? '';
const serviceKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? '';
const allowedOrigin = Deno.env.get('MAMBA_CANDIDATE_ORIGIN') ?? '';
if (!projectUrl || projectUrl.includes('mcrnstwmubtiiacyiaeu') || !serviceKey || !allowedOrigin) {
  throw new Error('Configure a separate staging project and explicit candidate origin');
}
const headers = {'Content-Type':'application/json', 'Access-Control-Allow-Origin':allowedOrigin,
  'Access-Control-Allow-Headers':'authorization, x-client-info, apikey, content-type',
  'Access-Control-Allow-Methods':'POST, OPTIONS', 'Vary':'Origin'};
export async function handleRoomRequest(request: Request): Promise<Response> {
  if (request.headers.get('origin') !== allowedOrigin) return new Response(JSON.stringify({error:'origin_not_allowed'}), {status:403, headers});
  if (request.method === 'OPTIONS') return new Response(null, {status:204, headers});
  if (request.method !== 'POST') return new Response(JSON.stringify({error:'method_not_allowed'}), {status:405, headers});
  try {
    const body = await request.text();
    if (new TextEncoder().encode(body).length > 131072) return new Response(JSON.stringify({error:'payload_too_large'}), {status:413, headers});
    const payload = JSON.parse(body);
    const response = await fetch(projectUrl + '/rest/v1/rpc/mamba_staging_action', {
      method:'POST', headers:{'Content-Type':'application/json', 'apikey':serviceKey, 'Authorization':'Bearer '+serviceKey},
      body:JSON.stringify({payload}), signal:AbortSignal.timeout(10000),
    });
    if (!response.ok) return new Response(JSON.stringify({error:'staging_unavailable'}), {status:503, headers});
    return new Response(JSON.stringify(await response.json()), {headers});
  } catch {
    return new Response(JSON.stringify({error:'invalid_request'}), {status:400, headers});
  }
}
if (import.meta.main) Deno.serve(handleRoomRequest);
