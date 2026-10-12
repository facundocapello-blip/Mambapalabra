"""Real isolated PostgreSQL staging contract tests; never calls Supabase.

Requires the local Docker container from staging/README.md.
"""
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import subprocess
import unittest

CONTAINER = os.environ.get('MAMBA_PG_CONTAINER', 'mamba-b111-staging-pg')


def sql(query, check=True):
    result = subprocess.run(['docker','exec','-i',CONTAINER,'psql','-U','postgres','-tA','-v','ON_ERROR_STOP=1'],
                            input=query, text=True, capture_output=True)
    if check and result.returncode:
        raise RuntimeError(result.stderr)
    return result


def action(payload):
    encoded = json.dumps(payload).encode().hex()
    query = "SELECT public.mamba_staging_action(convert_from(decode('" + encoded + "','hex'),'utf8')::jsonb);"
    return json.loads(sql(query).stdout)


class PostgreSQLStagingTests(unittest.TestCase):
    def create(self):
        return action({'action':'create','name':'Host de prueba','game_state':{'settings':{'seconds':150}}})

    def test_concurrent_join_has_exactly_one_winner(self):
        room = self.create()
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda name:action({'action':'join','code':room['code'],'name':name}), ['Guest A','Guest B']))
        self.assertEqual(sum('token' in result for result in results), 1)
        self.assertEqual(sum(result.get('error')=='room_full' for result in results), 1)
        state = action({'action':'get','code':room['code']})['room']
        self.assertEqual(state['version'], 2)
        self.assertNotIn('token', json.dumps(state))

    def test_version_owner_idempotency_and_token_checks(self):
        host = self.create()
        guest = action({'action':'join','code':host['code'],'name':'Guest'})
        state = {'players':[{'name':'Host'},{'name':'Guest'}], 'active':0, 'turnState':'ANSWERING', 'opId':'host:1'}
        payload = {'action':'sync','code':host['code'],'role':'host','token':host['token'],'version':2,'game_state':state,'status':'playing'}
        self.assertEqual(action(payload)['version'], 3)
        self.assertEqual(action(payload)['version'], 3)  # retry, no duplicate write
        payload['game_state'] = dict(state, opId='host:2')
        self.assertEqual(action(payload)['error'], 'version_conflict')
        payload['version'] = 3
        payload['role'] = 'guest'; payload['token'] = guest['token']
        self.assertEqual(action(payload)['error'], 'not_turn_owner')
        payload['role'] = 'host'; payload['token'] = 'not-a-token'
        self.assertEqual(action(payload)['error'], 'unauthorized')
        payload['token'] = host['token']; payload['game_state']['active'] = 1
        self.assertEqual(action(payload)['version'], 4)
        payload['version'] = 4; payload['game_state']['opId'] = 'host:3'
        self.assertEqual(action(payload)['error'], 'not_turn_owner')
        payload['role'] = 'guest'; payload['token'] = guest['token']; payload['game_state']['opId'] = 'guest:1'
        self.assertEqual(action(payload)['version'], 5)

    def test_expired_room_and_unauthorized_resume(self):
        room = self.create()
        self.assertEqual(action({'action':'resume','code':room['code'],'role':'host','token':'wrong'})['error'], 'unauthorized')
        self.assertIn('room', action({'action':'resume','code':room['code'],'role':'host','token':room['token']}))
        sql("UPDATE public.multiplayer_rooms SET expires_at=now()-interval '1 second' WHERE code='"+room['code']+"';")
        self.assertEqual(action({'action':'get','code':room['code']})['error'], 'room_not_found')

    def test_anonymous_clients_cannot_write_or_read_private_tokens(self):
        self.assertNotEqual(sql('SET ROLE anon; SELECT * FROM mamba_private.room_tokens;', check=False).returncode, 0)
        self.assertNotEqual(sql("SET ROLE anon; DELETE FROM public.multiplayer_rooms;", check=False).returncode, 0)
        self.assertNotEqual(sql("SET ROLE anon; SELECT public.mamba_staging_action('{}');", check=False).returncode, 0)


class PostgreSQLOnlineBrowserTests(unittest.TestCase):
    def test_two_browser_sessions_use_real_postgresql(self):
        import test_game_browser as browser_tests
        original = browser_tests.Handler.do_POST

        def post(handler):
            if handler.path != '/__room': handler.send_error(404); return
            payload = json.loads(handler.rfile.read(int(handler.headers['Content-Length'])))
            data = json.dumps(action(payload)).encode()
            handler.send_response(200); handler.send_header('Content-Type','application/json')
            handler.send_header('Content-Length',str(len(data))); handler.end_headers(); handler.wfile.write(data)

        browser_tests.Handler.do_POST = post
        suite = browser_tests.GameBrowserTests
        suite.setUpClass()
        case = suite('test_online_two_isolated_sessions_handoff_and_timer_contract')
        case.network_wait_ms = 50
        try:
            case.setUp()
            case.test_online_two_isolated_sessions_handoff_and_timer_contract()
        finally:
            case.tearDown(); suite.tearDownClass(); browser_tests.Handler.do_POST = original


if __name__ == '__main__': unittest.main()
