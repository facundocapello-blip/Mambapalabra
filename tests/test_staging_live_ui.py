"""End-to-end HTTPS test with two INDEPENDENT browser contexts against live STAGING only."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright
URL="https://facundocapello-blip.github.io/Mambapalabra/"
STAGING="qbzrqinnhrgeqvgtifrt"
PRODUCTION="mcrnstwmubtiiacyiaeu"
def run():
    with sync_playwright() as pw:
        browser=getattr(pw,os.environ.get("MAMBA_BROWSER","chromium")).launch()
        ctx1=browser.new_context(viewport={"width":390,"height":844},is_mobile=True,has_touch=True)
        ctx2=browser.new_context(viewport={"width":390,"height":844},is_mobile=True,has_touch=True)
        p1,p2=ctx1.new_page(),ctx2.new_page()
        illegal=[];backend=[];errors=[]
        for p in [p1,p2]:
            p.on("request",lambda req: (illegal.append(req.url) if PRODUCTION in req.url or "floot.app" in req.url else (backend.append(req.url) if STAGING in req.url else None)))
            p.on("pageerror",lambda e: errors.append(str(e)))
        try:
            p1.goto(URL+"?online-staging-check=1",wait_until="domcontentloaded",timeout=35000)
            p1.wait_for_function('window.supabase && document.querySelector("#createOnlineBtn") && !document.querySelector("#createOnlineBtn").disabled',timeout=60000)
            assert p1.locator("#handsFree").count()==0
            p1.locator('summary[aria-label="Opciones"]').click()
            p1.locator("#soundBtn").click()
            p1.locator('summary[aria-label="Opciones"]').click()
            p1.locator("#createOnlineBtn").click()
            p1.wait_for_function('document.querySelector("#roomCode").textContent.trim().length===6',timeout=35000)
            code=p1.locator("#roomCode").inner_text().strip()
            assert len(code)==6, "room not created"
            p2.goto(URL+"?sala="+code,wait_until="domcontentloaded",timeout=35000)
            p2.wait_for_function('window.supabase && document.querySelector("#showJoinBtn")',timeout=35000)
            assert p2.locator("#handsFree").count()==0
            p2.locator('summary[aria-label="Opciones"]').click()
            p2.locator("#soundBtn").click()
            p2.locator('summary[aria-label="Opciones"]').click()
            if p2.locator("#joinRow").is_hidden():p2.locator("#showJoinBtn").click()
            p2.locator("#onlineName").fill("QA-GUEST")
            p2.locator("#roomCodeInput").fill(code)
            p2.locator("#joinOnlineBtn").click()
            p1.locator("#game").wait_for(state="visible",timeout=60000)
            p2.locator("#game").wait_for(state="visible",timeout=60000)
            p1.wait_for_function('!document.querySelector("#sendTextBtn").disabled',timeout=30000)
            assert p2.locator("#sendTextBtn").is_disabled(),"Guest allowed to answer host turn"
            # Ambas pantallas muestran simultáneamente los segundos de AMBOS jugadores.
            for view in (p1,p2):
                assert view.locator("#orbTimer1").is_visible() and view.locator("#orbTimer2").is_visible()
                assert view.locator("#orbTimer2").inner_text()=="150","Guest's idle clock already decremented"
                assert view.locator("#orbName1").inner_text() and view.locator("#orbName2").inner_text()
            assert p1.locator("#orbP1").evaluate("(el)=>el.classList.contains('active-turn')")

            # Wrong answer must transfer authority without touching the other clock.
            p1.locator("#textAnswer").fill("RESPUESTA-INCORRECTA-PRUEBA")
            p1.locator("#sendTextBtn").click()
            p2.wait_for_function('!document.querySelector("#sendTextBtn").disabled',timeout=60000)
            assert p2.locator("#orbP2").evaluate("(el)=>el.classList.contains('active-turn')"),"Guest timer did not become active"
            assert p1.locator("#orbTimer1").is_visible() and p2.locator("#orbTimer2").is_visible()

            p1.wait_for_function('document.querySelector("#sendTextBtn").disabled',timeout=30000)
            Path("artifacts/online-staging").mkdir(parents=True,exist_ok=True)
            p1.screenshot(path="artifacts/online-staging/host.png")
            p2.screenshot(path="artifacts/online-staging/guest.png")
            assert not illegal, "Production request observed!"
            assert len(backend)>=3, "No request to real staging"
            assert not errors, "JavaScript error(s): "+str(errors[:2])
            print("PASS: HTTPS live staging, two isolated sessions, create/join, both games, handoff, write permission and no production requests")
        except Exception:
            print("FAIL DETAIL: host status="+p1.locator("#onlineError").inner_text() if p1.locator("#onlineError").count() else "no host error")
            print("FAIL DETAIL: guest status="+p2.locator("#onlineError").inner_text() if p2.locator("#onlineError").count() else "no guest error")
            raise
        finally:
            ctx1.close();ctx2.close();browser.close()
if __name__=="__main__":run()
