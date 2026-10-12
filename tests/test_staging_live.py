#!/usr/bin/env python3
"""Read/operate only dedicated MAMBAPALABRA-STAGING; no production URL, no secrets in logs."""
import json, os, urllib.request, uuid
PRODUCTION="mcrnstwmubtiiacyiaeu"
PROJECT="qbzrqinnhrgeqvgtifrt"
ORIGIN="https://facundocapello-blip.github.io"
URL="https://"+PROJECT+".supabase.co/functions/v1/multiplayer-room"
assert PRODUCTION not in URL and PROJECT in URL
def action(payload):
    req=urllib.request.Request(URL,data=json.dumps(payload).encode(),headers={
        "Origin":ORIGIN,"Content-Type":"application/json"},method="POST")
    with urllib.request.urlopen(req,timeout=30) as response:
        if response.status!=200:raise AssertionError("HTTP "+str(response.status))
        return json.load(response)
def test():
    created=action({"action":"create","name":"QA-LIVE","game_state":{"settings":{"seconds":150}}})
    assert len(created.get("code",""))==6 and created.get("token"),"create: "+str(created.get("error","unknown"))
    room=created["code"]
    joined=action({"action":"join","code":room,"name":"QA-GUEST"})
    assert joined.get("token") and joined.get("code")==room,"join: "+str(joined.get("error","unknown"))
    invalid=action({"action":"sync","code":room,"role":"guest","token":"no-token","version":2,"game_state":{},"status":"playing"})
    assert invalid.get("error")=="unauthorized","invalid token not rejected"
    state={"players":[{"name":"QA-LIVE"},{"name":"QA-GUEST"}],"active":0,"turnState":"ANSWERING","opId":str(uuid.uuid4())}
    p={"action":"sync","code":room,"role":"guest","token":joined["token"],"version":2,"game_state":state,"status":"playing"}
    assert action(p).get("error")=="not_turn_owner","guest changed host turn"
    p["role"]="host";p["token"]=created["token"]
    ok=action(p)
    assert ok.get("version")==3,"valid host sync: "+str(ok.get("error","unknown"))
    assert action(p).get("version")==3,"idempotent retry failed"
    room_data=action({"action":"get","code":room}).get("room")
    assert room_data and room_data.get("version")==3 and room_data.get("game_state",{}).get("opId")==state["opId"],"get mismatch"
    print("LIVE STAGING SMOKE PASS: create / join / reject token / reject turn / sync / retry / get")
if __name__=="__main__":test()
