"""Real browser regressions with controlled media/recognition failure injection.

MAMBA_BROWSER=webkit python3 tests/test_game_browser.py -v
MAMBA_GAME_HTML=game/B1_11_CONSOLIDADA.html ... reproduces failures on the baseline.
No requests to Floot or Supabase: external requests are blocked by each context.
"""
from functools import partial
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import os
import copy
import json
import threading
import unittest
import uuid

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / os.environ.get('MAMBA_GAME_HTML', 'game/index.html')
HOOK = """
window.mamba = {
  get game(){return game;}, get host(){return host;}, get online(){return online;},
  LETTERS, QUESTION_POOL, ACTIVE_QUESTION_POOL, STATIC_AUDIO, NEW_VOICE_AUDIO,
  resetGame, resetQuestionDraw, makePlayer, currentItem, currentItemFor,
  submitAnswer, doPass, startTimer, pauseTimer, effectiveTimeMs, handleTimeUp,
  setTurnState, turnPrompt, syncUI, hostSpeak, cancelHostSpeech, deviceSpeak,
  startSuddenDeath, submitSudden, startRecognition, onlineState, onlineHydrate,
  roomInviteUrl, toggleGamePause,
  unlockAudio, primeAV,
  createOnlineRoom, joinOnlineRoom, fetchRoom, handleRoom, onlineSyncNow,
};
"""


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def do_GET(self):
        if self.path.split('?')[0] == '/index.html':
            html = TARGET.read_text().replace('\n})();', '\n' + HOOK + '\n})();')
            data = html.encode()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        else:
            super().do_GET()

    def do_POST(self):
        if self.path != '/__room':
            self.send_error(404)
            return
        payload = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        with self.server.room_lock:
            room = self.server.room
            action = payload['action']
            result = {}
            if action == 'create':
                self.server.room = {'code':'TEST01', 'version':1, 'host_name':payload['name'], 'guest_name':None,
                                    'game_state':payload['game_state'], 'status':'waiting'}
                self.server.tokens = {'host':str(uuid.uuid4())}
                result = {'code':'TEST01', 'token':self.server.tokens['host']}
            elif not room or payload.get('code') != room['code']:
                result = {'error':'room_not_found'}
            elif action == 'join':
                if room['guest_name']:
                    result = {'error':'room_full'}
                else:
                    room['guest_name'] = payload['name']
                    room['version'] += 1
                    self.server.tokens['guest'] = str(uuid.uuid4())
                    result = {'code':room['code'], 'token':self.server.tokens['guest']}
            elif action == 'get':
                result = {'room':room}
            elif self.server.tokens.get(payload.get('role')) != payload.get('token'):
                result = {'error':'unauthorized'}
            elif action == 'resume':
                result = {'room':room}
            elif action == 'sync':
                if payload['version'] != room['version']:
                    result = {'error':'version_conflict'}
                else:
                    room['game_state'] = payload['game_state']
                    room['status'] = payload['status']
                    room['version'] += 1
                    result = {'version':room['version']}
            data = json.dumps(copy.deepcopy(result)).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)


class GameBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(ROOT / 'game')))
        cls.server.room_lock = threading.Lock()
        cls.server.room = None
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f'http://127.0.0.1:{cls.server.server_port}/index.html'
        cls.pw = sync_playwright().start()
        engine = os.environ.get('MAMBA_BROWSER', 'chromium')
        executable = os.environ.get('MAMBA_CHROMIUM', '/usr/bin/chromium' if Path('/usr/bin/chromium').exists() else '')
        cls.browser = getattr(cls.pw, engine).launch(
            **({'executable_path': executable} if engine == 'chromium' and executable else {}))

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def setUp(self):
        self.context = self.browser.new_context()
        self.context.route('**/*', lambda r: r.continue_() if r.request.url.startswith(('http://127.0.0.1:', 'blob:http://127.0.0.1:')) else r.abort())
        self.context.add_init_script(path=str(ROOT / 'tests/browser_fakes.js'))
        self.page = self.context.new_page()
        self.errors = []
        self.page.on('pageerror', lambda e: self.errors.append(str(e)))
        instant = datetime(2026, 10, 12, tzinfo=timezone.utc)
        self.page.clock.install(time=instant)
        self.page.clock.pause_at(instant)
        self.page.goto(self.url, wait_until='domcontentloaded')
        self.page.locator('#handsFree').uncheck()
        self.page.evaluate('mamba.host.unlocked = true')

    def tearDown(self):
        self.context.close()
        self.assertEqual(self.errors, [], 'Unexpected JavaScript error')

    def advance(self, ms=200):
        # Give fetch promises a chance to settle between simulated time slices.
        for _ in range(max(1, ms // 200)):
            self.page.clock.fast_forward(min(200, ms))
            self.page.wait_for_timeout(5)

    def boot(self, speech=False):
        if not speech:
            self.page.locator('.options-menu-wrap').evaluate('(el)=>el.open=true')
            self.page.locator('#soundBtn').click()
        self.page.evaluate('void mamba.resetGame()')
        self.advance()
        self.page.wait_for_function('mamba.game !== null')

    def state(self, expression):
        return self.page.evaluate(expression)

    def test_missing_mp3_and_tts_allow_text_answer(self):
        self.page.evaluate("audioMode='reject'; ttsMode='error'")
        self.boot(speech=True)
        self.advance(1000)
        self.assertEqual(self.state('mamba.game.turnState'), 'ANSWERING')
        self.assertTrue(self.page.locator('#sendTextBtn').is_enabled())
        answer = self.state('mamba.currentItem().answer')
        self.page.locator('#textAnswer').fill(answer)
        self.page.locator('#sendTextBtn').click()
        self.advance(1000)
        self.assertEqual(self.state('mamba.game.players[0].correct'), 1)

    def test_tts_never_starts_has_deadline(self):
        self.boot()
        self.page.evaluate("ttsMode='hang'; window.speechResult=null; void mamba.deviceSpeak('Definición breve.').then(r=>speechResult=r)")
        self.advance(11000)
        self.assertEqual(self.state('speechResult && speechResult.status'), 'failed')

    def test_pause_suspends_tts_deadline_and_playback(self):
        self.boot()
        self.page.evaluate("ttsMode='stall'; window.speechResult=null; mamba.setTurnState('READING'); void mamba.deviceSpeak('Definición breve.').then(r=>speechResult=r)")
        self.advance()
        self.page.locator('#pauseGame').click()
        self.assertTrue(self.state('speechSynthesis.paused'))
        self.advance(31000)
        self.assertIsNone(self.state('speechResult'))
        self.page.locator('#pauseGame').click()
        self.assertFalse(self.state('speechSynthesis.paused'))
        self.page.evaluate('speechSynthesis.utterance.onend()')
        self.assertEqual(self.state('speechResult.status'), 'completed')

    def test_all_letters_are_playable_without_changing_existing_questions(self):
        self.boot()
        self.assertEqual(self.state('mamba.game.players.map(p=>p.items.filter(q=>q.state!=="disabled").length)'), [27, 27])
        for letter in ('K', 'W'):
            answers = self.state(f'mamba.game.players.map(p=>p.items.find(q=>q.letter==="{letter}").answer)')
            self.assertEqual(len(set(answers)), 2)
        self.assertEqual(self.state('mamba.ACTIVE_QUESTION_POOL.length'), 208)

    def test_clock_only_runs_for_answering_owner_and_pause_preserves_time(self):
        self.boot()
        self.advance(1000)
        first = self.state('mamba.effectiveTimeMs(0)')
        self.assertLess(first, 150000)
        self.assertEqual(self.state('mamba.effectiveTimeMs(1)'), 150000)
        self.page.locator('#pauseGame').click()
        paused = self.state('mamba.effectiveTimeMs(0)')
        self.advance(2000)
        self.assertEqual(self.state('mamba.effectiveTimeMs(0)'), paused)
        self.page.locator('#pauseGame').click()
        self.page.evaluate("mamba.setTurnState('READING')")
        reading = self.state('mamba.effectiveTimeMs(0)')
        self.advance(2000)
        self.assertEqual(self.state('mamba.effectiveTimeMs(0)'), reading)

    def test_clock_is_not_affected_by_wall_clock_adjustment(self):
        self.boot()
        before = self.state('mamba.effectiveTimeMs(0)')
        self.page.evaluate('Date.now = () => 0')
        self.advance(1000)
        after = self.state('mamba.effectiveTimeMs(0)')
        self.assertGreater(before - after, 900)
        self.assertLess(before - after, 1500)

    def test_expired_answer_is_rejected_before_next_interval_tick(self):
        self.boot()
        self.page.evaluate('mamba.game.players[0].timeMs=0; mamba.submitAnswer(mamba.currentItem().answer)')
        self.assertEqual(self.state('mamba.game.players[0].correct'), 0)
        self.assertTrue(self.state('mamba.game.players[0].timedOut'))
        self.assertEqual(self.state('mamba.game.active'), 1)

    def test_recognition_that_never_ends_cannot_freeze_validation(self):
        self.boot()
        self.page.evaluate('recognitionHangs=true; mamba.startRecognition()')
        self.advance()
        self.page.evaluate('lastRecognition.onspeechend()')
        self.advance(2000)
        self.assertEqual(self.state('mamba.game.turnState'), 'ANSWERING')
        self.assertTrue(self.page.locator('#sendTextBtn').is_enabled())
        # A late final result from the abandoned session must not score.
        self.page.evaluate("lastRecognition.onresult({resultIndex:0,results:[Object.assign([{transcript:mamba.currentItem().answer}],{isFinal:true})]})")
        self.assertEqual(self.state('mamba.game.players[0].correct'), 0)

    def test_correct_wrong_pass_pending_and_restart(self):
        self.boot()
        self.page.locator('#textAnswer').fill(self.state('mamba.currentItem().answer'))
        self.page.locator('#sendTextBtn').click()
        self.advance()
        self.assertEqual(self.state('mamba.game.players[0].correct'), 1)
        self.assertEqual(self.state('mamba.currentItem().letter'), 'B')
        self.page.locator('#textAnswer').fill('respuesta incorrecta de prueba')
        self.page.locator('#sendTextBtn').click()
        self.advance()
        self.assertEqual(self.state('mamba.game.active'), 1)
        self.assertEqual(self.state('mamba.game.players[0].wrong'), 1)
        self.page.locator('#passBtn').click()
        self.advance()
        self.assertEqual(self.state('mamba.game.players[1].items[0].state'), 'pending')
        self.assertEqual(self.state('mamba.game.active'), 0)
        self.page.evaluate('void mamba.resetGame()')
        self.advance()
        self.assertEqual(self.state('mamba.game.players.map(p=>p.correct+p.wrong)'), [0, 0])

    def test_unlock_without_play_resolution_cannot_block_start(self):
        self.page.evaluate("audioMode='hang'; mamba.host.unlocked=false; window.unlockResult=null; void mamba.unlockAudio().then(r=>unlockResult=r)")
        self.advance(11000)
        self.assertIs(self.state('unlockResult'), False)
        self.assertEqual(self.state('mamba.host.audio.volume'), 1)

    def test_unanswered_mic_permission_does_not_block_text_game(self):
        self.page.locator('#handsFree').check()
        self.page.evaluate("void(navigator.mediaDevices.getUserMedia=()=>new Promise(resolve=>window.releaseMic=resolve)); window.micResult=null; void mamba.primeAV().then(r=>micResult=r)")
        self.advance(6000)
        self.assertIs(self.state('micResult'), False)
        self.page.evaluate('window.trackStopped=false; releaseMic({getTracks:()=>[{stop:()=>window.trackStopped=true}]})')
        self.assertTrue(self.state('trackStopped'))

    def test_mp3_start_and_stall_have_bounded_fallback(self):
        self.boot(speech=True)
        self.advance(1000)
        for mode in ('hang', 'stall'):
            with self.subTest(mode=mode):
                self.page.evaluate("audioMode=" + json.dumps(mode) + "; ttsMode='error'; window.speechResult=null; void mamba.hostSpeak('Facu.').then(r=>speechResult=r)")
                self.advance(12000)
                self.assertEqual(self.state('speechResult && speechResult.status'), 'failed')

    def test_missing_tts_allows_answers(self):
        self.page.evaluate("audioMode='reject'; Object.defineProperty(window,'speechSynthesis',{value:undefined})")
        self.boot(speech=True)
        self.advance(1000)
        self.assertTrue(self.page.locator('#sendTextBtn').is_enabled())

    def test_throwing_voice_enumeration_allows_answers(self):
        self.page.evaluate("audioMode='reject'; void(speechSynthesis.getVoices=()=>{throw new Error('voices unavailable')})")
        self.boot(speech=True)
        self.advance(1000)
        self.assertTrue(self.page.locator('#sendTextBtn').is_enabled())

    def test_cancelled_tts_cannot_complete_a_new_turn(self):
        self.boot()
        self.page.evaluate("ttsMode='stall'; window.speechResult=null; void mamba.deviceSpeak('Definición vieja.').then(r=>speechResult=r)")
        self.advance()
        self.page.evaluate('window.oldEnd = speechSynthesis.utterance.onend; void mamba.resetGame()')
        self.advance()
        self.assertEqual(self.state('speechResult.status'), 'cancelled')
        self.page.evaluate('oldEnd()')
        self.assertEqual(self.state('mamba.game.turnState'), 'ANSWERING')
        self.assertEqual(self.state('mamba.game.players.map(p=>p.correct)'), [0, 0])

    def test_sudden_death_keeps_score_when_feedback_audio_fails(self):
        self.boot(speech=True)
        self.page.evaluate("audioMode='reject'; ttsMode='error'; mamba.startSuddenDeath()")
        self.advance(2000)
        self.assertEqual(self.state('mamba.game.turnState'), 'ANSWERING')
        self.assertFalse(self.page.locator('#passBtn').is_enabled())
        self.assertIsNone(self.state('mamba.game.timerId'))
        self.page.locator('#textAnswer').fill(self.state('mamba.game.suddenQuestion.answer'))
        self.page.locator('#sendTextBtn').click()
        self.advance(2000)
        self.assertEqual(self.state('mamba.game.suddenScores'), [1, 0])
        self.assertEqual(self.state('mamba.game.active'), 1)
        self.page.locator('#textAnswer').fill('respuesta incorrecta')
        self.page.locator('#sendTextBtn').click()
        self.advance(2000)
        self.assertTrue(self.state('mamba.game.over'))
        self.assertIn('Mamba', self.page.locator('#winnerText').inner_text())
        self.page.locator('#playAgainBtn').click()
        self.advance(2000)
        self.assertFalse(self.state('mamba.game.suddenDeath'))
        self.assertEqual(self.state('mamba.game.suddenScores'), [0, 0])

    def test_pause_during_sudden_validation_does_not_accept_answer_twice(self):
        self.boot()
        self.page.evaluate('mamba.startSuddenDeath()')
        self.advance()
        self.page.locator('.options-menu-wrap').evaluate('(el)=>el.open=true')
        self.page.locator('#soundBtn').click()
        self.page.evaluate("ttsMode='stall'; audioMode='reject'; void mamba.submitSudden(mamba.game.suddenQuestion.answer)")
        self.advance()
        self.assertEqual(self.state('mamba.game.turnState'), 'VALIDATING')
        self.page.locator('#pauseGame').click()
        self.page.locator('#pauseGame').click()
        self.assertEqual(self.state('mamba.game.turnState'), 'VALIDATING')
        self.assertFalse(self.page.locator('#sendTextBtn').is_enabled())
        self.page.evaluate('speechSynthesis.utterance.onend()')
        self.advance()
        self.assertEqual(self.state('mamba.game.suddenScores'), [1, 0])

    def test_pass_by_voice_and_stale_result_after_handoff(self):
        self.boot()
        self.page.evaluate('mamba.startRecognition()')
        self.advance()
        self.page.evaluate("window.oldRecognition=lastRecognition; lastRecognition.onresult({resultIndex:0,results:[Object.assign([{transcript:'pasapalabra'}],{isFinal:true})]})")
        self.advance()
        self.assertEqual(self.state('mamba.game.active'), 1)
        self.assertEqual(self.state('mamba.game.players[0].items[0].state'), 'pending')
        self.page.evaluate("oldRecognition.onresult({resultIndex:0,results:[Object.assign([{transcript:mamba.currentItem().answer}],{isFinal:true})]})")
        self.assertEqual(self.state('mamba.game.players.map(p=>p.correct)'), [0, 0])

    def test_sudden_recognition_uses_correct_final_alternative(self):
        self.boot()
        self.page.evaluate('mamba.startSuddenDeath()')
        self.advance()
        self.page.evaluate('mamba.startRecognition()')
        self.advance()
        self.page.evaluate("lastRecognition.onresult({resultIndex:0,results:[Object.assign([{transcript:'incorrecta'},{transcript:mamba.game.suddenQuestion.answer}],{isFinal:true})]})")
        self.advance()
        self.assertEqual(self.state('mamba.game.suddenScores'), [1, 0])
        self.assertEqual(self.state('mamba.game.active'), 1)

    def test_expired_validation_recovers_to_timeout_not_frozen_clock(self):
        self.boot()
        self.page.evaluate('mamba.startRecognition()')
        self.advance()
        self.page.evaluate('mamba.game.players[0].timeMs=0; lastRecognition.onspeechend()')
        self.advance(2000)
        self.assertTrue(self.state('mamba.game.players[0].timedOut'))
        self.assertEqual(self.state('mamba.game.active'), 1)

    def test_end_by_timeout_and_fresh_restart(self):
        self.boot()
        self.page.evaluate('mamba.game.players[0].correct=1; mamba.game.players.forEach(p=>p.timeMs=0)')
        self.advance(1000)
        self.assertTrue(self.state('mamba.game.over'))
        self.assertTrue(self.page.locator('#endScreen').is_visible())
        self.assertIsNone(self.state('mamba.game.timerId'))
        self.page.locator('#playAgainBtn').click()
        self.advance()
        self.assertFalse(self.state('mamba.game.over'))
        self.assertEqual(self.state('mamba.game.players.map(p=>p.timedOut)'), [False, False])

    def test_invitation_stays_on_candidate_origin(self):
        self.assertEqual(self.state("mamba.roomInviteUrl('ABC123')"), self.url + '?sala=ABC123')
        self.page.goto(self.url + '?sala=ABC123', wait_until='domcontentloaded')
        self.assertEqual(self.page.locator('#roomCodeInput').input_value(), 'ABC123')

    def test_question_rotation_keeps_kw_different_across_players_and_rounds(self):
        self.boot()
        first = self.state('mamba.game.players.map(p=>p.items.filter(q=>["K","W"].includes(q.letter)).map(q=>q.answer))')
        self.page.evaluate('void mamba.resetGame()')
        self.advance()
        second = self.state('mamba.game.players.map(p=>p.items.filter(q=>["K","W"].includes(q.letter)).map(q=>q.answer))')
        self.assertEqual(first[0], second[1])
        self.assertEqual(first[1], second[0])

    def test_thirty_local_restarts_keep_full_coverage(self):
        self.boot()
        for _ in range(30):
            self.page.evaluate('void mamba.resetGame()')
            self.advance()
            self.assertEqual(self.state('mamba.game.players.map(p=>p.items.filter(q=>q.state!=="disabled").length)'), [27, 27])
            self.assertEqual(self.state('mamba.game.players.map(p=>p.correct+p.wrong)'), [0, 0])
            self.assertEqual(self.state('mamba.game.turnState'), 'ANSWERING')

    def test_old_timer_callback_cannot_expire_a_new_game(self):
        self.page.evaluate('window.clockCallbacks=[]; window.registerInterval=setInterval.bind(window); void(window.setInterval=(fn,ms)=>{if(ms===200)clockCallbacks.push(fn);return registerInterval(fn,ms)})')
        self.boot()
        self.page.evaluate('window.oldTick=clockCallbacks[0]; void mamba.resetGame()')
        self.advance()
        self.page.evaluate('mamba.game.players[0].timeMs=0; oldTick()')
        self.assertFalse(self.state('mamba.game.players[0].timedOut'))

    def test_overlapping_resets_cannot_restore_an_older_game(self):
        self.page.evaluate('mamba.host.unlocked=false; window.pendingUnlocks=[]; void(mamba.host.audio.play=()=>new Promise(resolve=>pendingUnlocks.push(resolve)))')
        self.page.evaluate('void mamba.resetGame(); void mamba.resetGame()')
        self.advance()
        self.assertIsNone(self.state('mamba.game'))
        self.page.evaluate('pendingUnlocks[1]()')
        self.advance()
        match = self.state('mamba.game.matchId')
        self.page.evaluate('pendingUnlocks[0]()')
        self.advance()
        self.assertEqual(self.state('mamba.game.matchId'), match)

    def test_full_roscos_include_kw_and_complete_sudden_death(self):
        self.boot()
        seen = [[], []]
        for _ in range(54):
            owner = self.state('mamba.game.active')
            seen[owner].append(self.state('mamba.currentItem().letter'))
            self.page.locator('#textAnswer').fill(self.state('mamba.currentItem().answer'))
            self.page.locator('#sendTextBtn').click()
            self.advance()
        letters = self.state('mamba.LETTERS')
        self.assertEqual(seen, [letters, letters])
        self.assertEqual(self.state('mamba.game.players.map(p=>p.correct)'), [27, 27])
        self.assertTrue(self.state('mamba.game.suddenDeath'))
        for answer in [self.state('mamba.game.suddenQuestion.answer'), 'incorrecta']:
            self.page.locator('#textAnswer').fill(answer)
            self.page.locator('#sendTextBtn').click()
            self.advance()
        self.assertTrue(self.state('mamba.game.over'))
        self.assertIn('Mamba', self.page.locator('#winnerText').inner_text())

    def test_mp3_native_playback_and_menu_game_screenshots(self):
        # Separate context: actual HTMLMediaElement, no fake TTS/audio, no clock.
        with self.browser.new_context() as context:
            context.route('**/*', lambda r: r.continue_() if r.request.url.startswith(('http://127.0.0.1:', 'blob:http://127.0.0.1:')) else r.abort())
            page = context.new_page()
            errors = []
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.goto(self.url, wait_until='domcontentloaded')
            engine = os.environ.get('MAMBA_BROWSER', 'chromium')
            output = ROOT / 'artifacts' / engine
            output.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(output / 'menu.png'))
            page.locator('#handsFree').uncheck()
            page.locator('#startBtn').click()
            page.wait_for_function('mamba.game && mamba.game.countingDown')
            page.evaluate("""() => {
              const q=mamba.ACTIVE_QUESTION_POOL.find(q=>q[0]==='A'&&mamba.NEW_VOICE_AUDIO.has(mamba.STATIC_AUDIO[q[0]+': '+q[2]]));
              Object.assign(mamba.game.players[0].items[0], {letter:q[0],answer:q[1],clue:q[2],aliases:q[3]||[],rule:q[4]||'EMPIEZA'});
              mamba.syncUI();
            }""")
            page.wait_for_function('mamba.host.audio.currentTime > 0.05 && mamba.game.turnState === "READING"', timeout=20000)
            self.assertEqual(page.evaluate('mamba.effectiveTimeMs(0)'), 150000)
            page.screenshot(path=str(output / 'primera-partida.png'))
            page.wait_for_function('mamba.game.turnState === "ANSWERING"', timeout=30000)
            self.assertFalse(page.evaluate('mamba.game.audioFailed'))
            self.assertTrue(page.locator('#sendTextBtn').is_enabled())
            self.assertEqual(errors, [])

    def test_online_two_isolated_sessions_handoff_and_timer_contract(self):
        self.context.close()
        contexts = []
        pages = []
        for _ in range(2):
            context = self.browser.new_context()
            contexts.append(context)
            context.route('**/*', lambda r: r.continue_() if r.request.url.startswith(('http://127.0.0.1:', 'blob:http://127.0.0.1:')) else r.abort())
            context.add_init_script(path=str(ROOT / 'tests/browser_fakes.js'))
            context.add_init_script(path=str(ROOT / 'tests/online_fake.js'))
            page = context.new_page()
            page.on('pageerror', lambda e: self.errors.append(str(e)))
            instant = datetime(2026, 10, 12, tzinfo=timezone.utc)
            page.clock.install(time=instant)
            page.clock.pause_at(instant)
            page.goto(self.url, wait_until='domcontentloaded')
            page.locator('#handsFree').uncheck()
            page.evaluate("mamba.host.unlocked=true; audioMode='reject'; ttsMode='error'")
            pages.append(page)
        host, guest = pages

        def pump(milliseconds=2000):
            for _ in range(milliseconds // 200):
                for page in pages:
                    page.clock.fast_forward(200)
                    page.wait_for_timeout(5)

        try:
            host.locator('#onlinePanel').evaluate('(el)=>el.hidden=false')
            host.locator('#onlineName').fill('Host de prueba')
            host.evaluate('void mamba.createOnlineRoom()')
            pump()
            self.assertEqual(host.evaluate('mamba.online.code'), 'TEST01')
            guest.locator('#showJoinBtn').click()
            guest.locator('#onlineName').fill('Guest de prueba')
            guest.locator('#roomCodeInput').fill('TEST01')
            guest.evaluate('void mamba.joinOnlineRoom()')
            pump(4000)
            self.assertEqual([p.evaluate('mamba.game.turnState') for p in pages], ['ANSWERING', 'ANSWERING'])
            self.assertTrue(host.locator('#sendTextBtn').is_enabled())
            self.assertFalse(guest.locator('#sendTextBtn').is_enabled())
            self.assertIsNotNone(host.evaluate('mamba.onlineState().timerEndsAt'))
            host.locator('#passBtn').click()
            pump(4000)
            self.assertEqual([p.evaluate('mamba.game.active') for p in pages], [1, 1])
            self.assertTrue(guest.locator('#sendTextBtn').is_enabled())
            self.assertFalse(host.locator('#sendTextBtn').is_enabled())
            self.assertIsNone(host.evaluate('mamba.game.timerId'))
            self.assertEqual(host.evaluate('mamba.game.players[0].items[0].state'), 'pending')
            frozen = guest.evaluate('mamba.game.players[0].timeMs')
            guest.locator('#textAnswer').fill(guest.evaluate('mamba.currentItem().answer'))
            guest.locator('#sendTextBtn').click()
            pump(4000)
            self.assertEqual([p.evaluate('mamba.game.players[1].correct') for p in pages], [1, 1])
            self.assertEqual(guest.evaluate('mamba.game.players[0].timeMs'), frozen)
            self.assertEqual(guest.evaluate('mamba.currentItem().letter'), 'B')
        finally:
            for context in contexts:
                context.close()


if __name__ == '__main__':
    # One process per engine keeps launch failures and test counts explicit.
    unittest.main()
