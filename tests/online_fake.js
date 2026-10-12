// A local protocol double, not a production/staging backend certification.
window.supabase = {createClient: () => ({
  functions: {invoke: async (_name, {body}) => {
    const response = await fetch('/__room', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(body)});
    const data = await response.json();
    return {data, error:null};
  }},
  removeChannel: async () => {},
  channel: () => ({on() { return this; }, subscribe(callback) { setTimeout(()=>callback('SUBSCRIBED'), 1); return this; }}),
})};
