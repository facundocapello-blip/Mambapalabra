"""Observational online-audio test on deployed B1.12 with 2 independent browsers.

Records native media events and speechSynthesis calls; does not mock microphone/audio,
change game logic or touch production. Inconclusive on real iPhone speakers.
"""
import os
from playwright.sync_api import sync_playwright

URL="https://facundocapello-blip.github.io/Mambapalabra/?qa=guest-sound-b112"
STAGING="qbzrqinnhrgeqvgtifrt"
PRODUCTION="mcrnstwmubtiiacyiaeu"
TRACK=r"""
(() => {
  window.__audioAudit={plays:[],playing:[],failed:[],utterances:[]};
  const orig=HTMLMediaElement.prototype.play;
  HTMLMediaElement.prototype.play=function(...args) {
    const url=this.currentSrc||this.src||"";
    if(url.includes("new-audio"))window.__audioAudit.plays.push(url.split("/").pop());
    const result=orig.apply(this,args);
    if(result?.catch)result.catch(err=>window.__audioAudit.failed.push(String(err?.name||err)));
    return result;
  };
  document.addEventListener("playing",e=>{
    const url=e.target?.currentSrc||e.target?.src||"";
    if(url.includes("new-audio"))window.__audioAudit.playing.push(url.split("/").pop());
  },true);
  try {
    const original=window.speechSynthesis.speak.bind(window.speechSynthesis);
    window.speechSynthesis.speak=(utterance)=>{
       if((utterance.text||"").trim()) window.__audioAudit.utterances.push(utterance.text);
       return original(utterance);
    };
  } catch (_) {}
})();
"""

def run():
    browser_name=os.environ.get("MAMBA_BROWSER","chromium")
    with sync_playwright() as pw:
        browser=getattr(pw,browser_name).launch()
        contexts=[browser.new_context(viewport={"width":390,"height":844},is_mobile=True,has_touch=True) for _ in range(2)]
        for context in contexts:context.add_init_script(TRACK)
        host,guest=[context.new_page() for context in contexts]
        errors=[];illegal=[]
        for page in (host,guest):
            page.on("pageerror",lambda e: errors.append(str(e)))
            page.on("request",lambda req:illegal.append(req.url) if PRODUCTION in req.url or "floot.app" in req.url else None)
        try:
            host.goto(URL,wait_until="domcontentloaded",timeout=45000)
            host.locator("#createOnlineBtn").click()
            host.wait_for_function('document.querySelector("#roomCode").textContent.trim().length===6',timeout=45000)
            code=host.locator("#roomCode").inner_text().strip()
            guest.goto(URL+"&sala="+code,wait_until="domcontentloaded",timeout=45000)
            if guest.locator("#joinRow").is_hidden():guest.locator("#showJoinBtn").click()
            guest.locator("#onlineName").fill("QA-GUEST-VOICE")
            guest.locator("#roomCodeInput").fill(code)
            guest.locator("#joinOnlineBtn").click()
            host.locator("#game").wait_for(state="visible",timeout=75000)
            guest.locator("#game").wait_for(state="visible",timeout=75000)
            host.wait_for_function('!document.querySelector("#sendTextBtn").disabled',timeout=90000)
            assert guest.locator("#sendTextBtn").is_disabled(),"Guest must not answer host turn"
            host_audit=host.evaluate("window.__audioAudit")
            assert host_audit["plays"] or host_audit["utterances"],"Host speech was never attempted"
            guest_before=guest.evaluate("({playing:window.__audioAudit.playing.length,utterances:window.__audioAudit.utterances.length})")
            host.locator("#textAnswer").fill("QA-RESPUESTA-INCORRECTA")
            host.locator("#sendTextBtn").click()
            guest.wait_for_function('!document.querySelector("#sendTextBtn").disabled',timeout=90000)
            assert host.locator("#sendTextBtn").is_disabled(),"Host kept answer control after handoff"
            audit=guest.evaluate("window.__audioAudit")
            played=audit["playing"][guest_before["playing"]:]
            utterances=audit["utterances"][guest_before["utterances"]:]
            assert played or utterances, "Guest was not sent any narration on its first turn"
            assert not errors, "Browser errors: "+str(errors[:2])
            assert not illegal, "Unexpected production request"
            print(f"PASS {browser_name}: host/guest audio attempt, turn handoff, guest play events={len(played)}, guest TTS utterances={len(utterances)}, permission gates OK")
            print("NOTE: browser sound events do not prove real iPhone speaker output.")
        except Exception:
            for label,page in (("host",host),("guest",guest)):
                try:
                    status=page.locator("#onlineError").inner_text()
                    controls=page.evaluate("({state:document.querySelector('#transcript')?.textContent,disabled:document.querySelector('#sendTextBtn')?.disabled,audio:window.__audioAudit})")
                    print("DIAGNOSTICS "+label+" "+str({"status":status,"ui":controls})[:2200])
                except Exception: pass
            raise
        finally:
            for context in contexts:context.close()
            browser.close()
if __name__=="__main__":run()
