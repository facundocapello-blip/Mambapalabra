"""Smoke test exported/local or deployed HTTPS candidate using iPhone dimensions."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import hashlib
import json
import os
from pathlib import Path
import re
import threading
import unittest
from urllib.request import urlopen
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
EXPORT = Path(os.environ.get('MAMBA_EXPORT', '/workspace/candidate-pages-b111'))


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, *_): pass
    def do_GET(self):
        self.path = self.path.removeprefix('/Mambapalabra')
        super().do_GET()


class CandidateMobileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pw = sync_playwright().start()
        cls.engine = os.environ.get('MAMBA_BROWSER', 'chromium')
        executable = os.environ.get('MAMBA_CHROMIUM', '/usr/bin/chromium' if Path('/usr/bin/chromium').exists() else '')
        cls.browser = getattr(cls.pw, cls.engine).launch(**({'executable_path':executable} if cls.engine == 'chromium' and executable else {}))
        cls.url = os.environ.get('MAMBA_CANDIDATE_URL')
        cls.server = None
        if not cls.url:
            cls.server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(EXPORT)))
            threading.Thread(target=cls.server.serve_forever, daemon=True).start()
            cls.url = f'http://127.0.0.1:{cls.server.server_port}/Mambapalabra/'
        source = (ROOT / 'game/index.html').read_text()
        cls.questions = []
        for name in ('QUESTION_POOL', 'YOUTUBE_QUESTION_POOL'):
            value = re.search(r'const '+name+r'\s*=([^\n]+)', source)[1]
            cls.questions.extend(json.loads(value.rstrip(';')))

    @classmethod
    def tearDownClass(cls):
        cls.browser.close(); cls.pw.stop()
        if cls.server: cls.server.shutdown(); cls.server.server_close()

    def test_iphone_portrait_and_landscape_controls(self):
        for viewport in ({'width':390,'height':844}, {'width':844,'height':390}):
            with self.subTest(viewport=viewport), self.browser.new_context(
                viewport=viewport, is_mobile=True, has_touch=True, device_scale_factor=3) as context:
                page = context.new_page()
                errors, production_requests = [], []
                page.on('pageerror', lambda e: errors.append(str(e)))
                page.on('request', lambda r: production_requests.append(r.url) if 'mcrnstwmubtiiacyiaeu' in r.url or 'floot.app' in r.url else None)
                response = page.goto(self.url, wait_until='networkidle')
                self.assertEqual(response.status, 200)
                self.assertFalse(page.locator('#createOnlineBtn').is_enabled())
                self.assertEqual(page.evaluate('window.mamba === undefined'), True)
                self.assertTrue(page.locator('.lobby-logo img').evaluate('(img)=>img.complete && img.naturalWidth > 0'))
                self.assertLessEqual(page.evaluate('document.documentElement.scrollWidth'), viewport['width'])
                page.locator('#handsFree').uncheck()
                page.locator('summary[aria-label="Opciones"]').tap()
                page.locator('#soundBtn').tap()
                page.locator('summary[aria-label="Opciones"]').tap()
                page.locator('#startBtn').tap()
                page.locator('#game').wait_for(state='visible')
                page.locator('#startCountdown').wait_for(state='hidden')
                page.wait_for_function('!document.querySelector("#sendTextBtn").disabled', timeout=20000)
                clue = page.locator('#questionText').inner_text()
                answer = next(q[1] for q in self.questions if q[2] == clue)
                page.locator('#textAnswer').fill(answer)
                page.locator('#sendTextBtn').tap()
                page.wait_for_function('document.querySelector("#scoreMamba").textContent === "1"')
                page.wait_for_function('!document.querySelector("#passBtn").disabled')
                page.locator('#passBtn').tap()
                page.wait_for_function('document.querySelector("#cardFacu").classList.contains("active")')
                page.wait_for_function('!document.querySelector("#sendTextBtn").disabled')
                page.locator('#textAnswer').fill('respuesta de prueba incorrecta')
                page.locator('#sendTextBtn').tap()
                page.wait_for_function('document.querySelector("#wrongFacu").textContent === "1"')
                page.wait_for_function('!document.querySelector("#pauseGame").disabled')
                page.locator('#pauseGame').tap()
                timer = page.locator('#railTimer').inner_text()
                page.wait_for_timeout(1200)
                self.assertEqual(page.locator('#railTimer').inner_text(), timer)
                self.assertFalse(page.locator('#sendTextBtn').is_enabled())
                page.locator('#pauseGame').tap()
                page.wait_for_function('!document.querySelector("#sendTextBtn").disabled')
                for selector in ('#micBtn','#passBtn','#sendTextBtn','#pauseGame'):
                    bounds = page.locator(selector).bounding_box()
                    self.assertGreaterEqual(bounds['height'], 44)
                output = ROOT / 'artifacts/mobile'
                output.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(output / f'{self.engine}-{viewport["width"]}.png'), full_page=True)
                page.locator('summary[aria-label="Opciones"]').tap()
                page.once('dialog', lambda dialog: dialog.accept())
                page.locator('#restartBtn').tap()
                page.wait_for_function('document.querySelector("#scoreMamba").textContent === "0"')
                page.wait_for_function('!document.querySelector("#sendTextBtn").disabled')
                self.assertEqual(errors, [])
                self.assertEqual(production_requests, [])

    def test_all_original_mp3_are_served_under_candidate_prefix(self):
        manifest = json.loads((ROOT / 'game/ASSETS_SHA256.json').read_text())
        for name, expected in manifest.items():
            with self.subTest(name=name), urlopen(self.url + name, timeout=30) as response:
                self.assertEqual(response.status, 200)
                self.assertEqual(hashlib.sha256(response.read()).hexdigest(), expected)


if __name__ == '__main__': unittest.main()
