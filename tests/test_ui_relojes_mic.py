"""Regresión: dos relojes visibles + micrófono exclusivamente manual."""
import json, os, re, threading, unittest
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
class Handler(SimpleHTTPRequestHandler):
    def log_message(self,*args): pass
    def do_GET(self):
        self.path=self.path.removeprefix('/Mambapalabra')
        return super().do_GET()

class UICandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(ROOT)))
        threading.Thread(target=cls.server.serve_forever,daemon=True).start()
        cls.url=f'http://127.0.0.1:{cls.server.server_port}/Mambapalabra/'
        cls.pw=sync_playwright().start()
        cls.browser=getattr(cls.pw,os.getenv('MAMBA_BROWSER','chromium')).launch()
        cls.questions=[]
        # The candidate is the precise public HTML, not a reconstructed game.
        source=(ROOT/'index.html').read_text()
        for name in ('QUESTION_POOL','YOUTUBE_QUESTION_POOL'):
            literal=re.search(r'const '+name+r'\s*=([^\n]+)',source)
            assert literal, name
            cls.questions.extend(json.loads(literal[1].rstrip(';')))
    @classmethod
    def tearDownClass(cls):
        cls.browser.close();cls.pw.stop()
        cls.server.shutdown();cls.server.server_close()
    def make_page(self):
        ctx=self.browser.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,device_scale_factor=3)
        ctx.add_init_script("""(() => {
          window.__micStarts=0;
          window.__permissionRequests=0;
          class FakeSpeechRecognition {
            constructor(){window.__lastRecognition=this;}
            start(){window.__micStarts++;setTimeout(()=>this.onstart?.(),0);}
            stop(){setTimeout(()=>this.onend?.(),0);}
            abort(){setTimeout(()=>this.onend?.(),0);}
          }
          window.SpeechRecognition=FakeSpeechRecognition;
          window.webkitSpeechRecognition=FakeSpeechRecognition;
          if(navigator.mediaDevices)navigator.mediaDevices.getUserMedia=() => {
            window.__permissionRequests++;return Promise.reject(new Error('Do not request microphone before RESPONDER'));
          };
        })();""")
        page=ctx.new_page()
        errors=[];page.on('pageerror',lambda e: errors.append(str(e)))
        page.goto(self.url,wait_until='domcontentloaded')
        return ctx,page,errors
    def begin(self,page):
        self.assertEqual(page.locator('#handsFree').count(),0)
        page.locator('summary[aria-label="Opciones"]').tap()
        page.locator('#soundBtn').tap() # disable narrator only for deterministic timing
        page.locator('summary[aria-label="Opciones"]').tap()
        page.locator('#startBtn').tap()
        page.locator('#game').wait_for(state='visible',timeout=25000)
        page.wait_for_function('!document.querySelector("#sendTextBtn").disabled',timeout=30000)
    def test_two_independent_seconds_and_complete_local_flow(self):
        ctx,page,errors=self.make_page()
        try:
            self.begin(page)
            self.assertEqual(page.locator('#orbName1').inner_text(),'Mamba')
            self.assertEqual(page.locator('#orbName2').inner_text(),'Facu')
            self.assertEqual(page.locator('#orbTimer1').inner_text(),'150')
            self.assertEqual(page.locator('#orbTimer2').inner_text(),'150')
            self.assertEqual(page.evaluate('window.__micStarts'),0)
            self.assertEqual(page.evaluate('window.__permissionRequests'),0)
            page.wait_for_timeout(1600)
            t1=int(page.locator('#orbTimer1').inner_text())
            self.assertLess(t1,150)
            self.assertEqual(page.locator('#orbTimer2').inner_text(),'150')
            # A correct answer advances the letter and does not open the mic.
            clue=page.locator('#questionText').inner_text()
            match=next(q for q in self.questions if q[2]==clue)
            page.locator('#textAnswer').fill(match[1])
            page.locator('#sendTextBtn').tap()
            page.wait_for_function('document.querySelector("#scoreMamba").textContent === "1"',timeout=20000)
            page.wait_for_function('!document.querySelector("#sendTextBtn").disabled',timeout=30000)
            self.assertEqual(page.evaluate('window.__micStarts'),0)
            page.locator('#textAnswer').fill('RESPUESTA INCORRECTA PRUEBA')
            page.locator('#sendTextBtn').tap()
            page.wait_for_function('document.querySelector("#cardFacu").classList.contains("active")',timeout=30000)
            page.wait_for_function('!document.querySelector("#sendTextBtn").disabled',timeout=30000)
            first=int(page.locator('#orbTimer1').inner_text())
            page.wait_for_timeout(1400)
            self.assertEqual(int(page.locator('#orbTimer1').inner_text()),first)
            self.assertLess(int(page.locator('#orbTimer2').inner_text()),150)
            self.assertEqual(page.evaluate('window.__micStarts'),0)
            page.locator('#pauseGame').tap()
            frozen=[page.locator(f'#orbTimer{i}').inner_text() for i in (1,2)]
            page.wait_for_timeout(1200)
            self.assertEqual([page.locator(f'#orbTimer{i}').inner_text() for i in (1,2)],frozen)
            page.locator('#pauseGame').tap()
            page.wait_for_function('!document.querySelector("#passBtn").disabled',timeout=20000)
            page.locator('#passBtn').tap()
            page.wait_for_function('!document.querySelector("#sendTextBtn").disabled',timeout=20000)
            self.assertEqual(page.evaluate('window.__micStarts'),0)
            page.locator('summary[aria-label="Opciones"]').tap()
            page.once('dialog',lambda dialog:dialog.accept())
            page.locator('#restartBtn').tap()
            page.wait_for_function('document.querySelector("#scoreMamba").textContent === "0"',timeout=25000)
            page.wait_for_function('!document.querySelector("#sendTextBtn").disabled',timeout=30000)
            self.assertEqual(page.evaluate('window.__micStarts'),0)
            self.assertEqual(page.evaluate('window.__permissionRequests'),0)
            self.assertEqual(page.locator('#orbTimer2').inner_text(),'150')
            self.assertEqual(errors,[])
        finally:ctx.close()
    def test_manual_respond_starts_microphone_once(self):
        ctx,page,errors=self.make_page()
        try:
            self.begin(page)
            self.assertEqual(page.evaluate('window.__micStarts'),0)
            self.assertEqual(page.evaluate('window.__permissionRequests'),0)
            page.locator('#micBtn').tap()
            page.wait_for_function('window.__micStarts===1',timeout=10000)
            page.wait_for_function('document.querySelector("#micBtn").textContent==="ESCUCHANDO"',timeout=10000)
            page.evaluate('window.__lastRecognition.onend()')
            page.wait_for_function('document.querySelector("#micBtn").textContent==="RESPONDER"',timeout=10000)
            self.assertEqual(page.evaluate('window.__micStarts'),1)
            self.assertEqual(page.evaluate('window.__permissionRequests'),0)
            self.assertEqual(errors,[])
        finally:ctx.close()

if __name__=='__main__':unittest.main()
