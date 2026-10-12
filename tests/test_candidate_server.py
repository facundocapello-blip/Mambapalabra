from functools import partial
import importlib.util
from http.server import ThreadingHTTPServer
from pathlib import Path
import tempfile
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('candidate_server',ROOT/'tools/candidate_preview_server.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


class CandidateServerTests(unittest.TestCase):
    def setUp(self):
        self.directory=tempfile.TemporaryDirectory()
        root=Path(self.directory.name)
        (root/'index.html').write_text('<h1>Candidata</h1>')
        (root/'new-audio').mkdir();(root/'new-audio/test.mp3').write_bytes(b'ID3audio-test')
        self.server=ThreadingHTTPServer(('127.0.0.1',0),module.handler(root))
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
        self.url=f'http://127.0.0.1:{self.server.server_port}/Mambapalabra/'
    def tearDown(self):
        self.server.shutdown();self.server.server_close();self.thread.join();self.directory.cleanup()
    def test_mp3_range_and_head(self):
        with urlopen(Request(self.url+'new-audio/test.mp3',headers={'Range':'bytes=0-1'})) as response:
            self.assertEqual(response.status,206);self.assertEqual(response.read(),b'ID')
            self.assertEqual(response.headers['Content-Range'],'bytes 0-1/13')
            self.assertEqual(response.headers['Content-Type'],'audio/mpeg')
        with urlopen(Request(self.url+'new-audio/test.mp3',method='HEAD')) as response:
            self.assertEqual(response.status,200);self.assertEqual(response.read(),b'')
            self.assertEqual(response.headers['Accept-Ranges'],'bytes')
    def test_out_of_range_and_suffix(self):
        with self.assertRaises(HTTPError) as raised:
            urlopen(Request(self.url+'new-audio/test.mp3',headers={'Range':'bytes=99-100'}))
        self.assertEqual(raised.exception.code,416)
        with urlopen(Request(self.url+'new-audio/test.mp3',headers={'Range':'bytes=-4'})) as response:
            self.assertEqual(response.read(),b'test')
    def test_no_directory_listing_or_paths_outside_export(self):
        for path in ('%2e%2e/README.md','new-audio/','/etc/passwd'):
            with self.subTest(path=path),self.assertRaises(HTTPError) as raised:
                urlopen(self.url+path)
            self.assertEqual(raised.exception.code,404)
