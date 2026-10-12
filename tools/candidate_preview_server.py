#!/usr/bin/env python3
"""Serve only the exported candidate, with MP3 byte ranges for mobile Safari."""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import mimetypes
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit


def handler(root, prefix='/Mambapalabra/'):
    root = Path(root).resolve()

    class CandidateHandler(BaseHTTPRequestHandler):
        def log_message(self, *_): pass
        def do_HEAD(self): self.serve(False)
        def do_GET(self): self.serve(True)
        def serve(self, send_body):
            path = unquote(urlsplit(self.path).path)
            if path == '/':
                self.send_response(302); self.send_header('Location',prefix); self.end_headers(); return
            if not path.startswith(prefix): self.send_error(404); return
            relative = path[len(prefix):] or 'index.html'
            if '..' in Path(relative).parts or '\x00' in relative: self.send_error(404); return
            target = (root / relative).resolve()
            if not target.is_relative_to(root) or not target.is_file(): self.send_error(404); return
            size = target.stat().st_size
            start, end, status = 0, size-1, 200
            requested_range = self.headers.get('Range')
            if requested_range:
                match = re.fullmatch(r'bytes=(\d*)-(\d*)', requested_range)
                if not match or not any(match.groups()): self.send_error(416); return
                first, last = match.groups()
                if first:
                    start = int(first); end = min(int(last),size-1) if last else size-1
                else:
                    start = max(0,size-int(last))
                if start<0 or start> end or start>=size:
                    self.send_response(416); self.send_header('Content-Range',f'bytes */{size}'); self.end_headers(); return
                status = 206
            self.send_response(status)
            self.send_header('Content-Type',mimetypes.guess_type(str(target))[0] or 'application/octet-stream')
            self.send_header('Content-Length',str(max(0,end-start+1)))
            self.send_header('Accept-Ranges','bytes')
            self.send_header('X-Content-Type-Options','nosniff')
            self.send_header('Cache-Control','no-store' if target.suffix=='.html' else 'public, max-age=3600')
            if status==206: self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
            self.end_headers()
            if send_body:
                with target.open('rb') as source:
                    source.seek(start); self.wfile.write(source.read(max(0,end-start+1)))
    return CandidateHandler


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',required=True,type=Path)
    parser.add_argument('--port',type=int,default=8765)
    args=parser.parse_args()
    ThreadingHTTPServer(('127.0.0.1',args.port),handler(args.root)).serve_forever()
