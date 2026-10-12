#!/usr/bin/env python3
"""Export a separate HTTPS candidate without pointing online at production."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
PRODUCTION_PROJECT = 'mcrnstwmubtiiacyiaeu'
spec = importlib.util.spec_from_file_location('package_candidate', ROOT / 'tools/package_candidate.py')
packager = importlib.util.module_from_spec(spec)
spec.loader.exec_module(packager)


def replace_once(text, old, new):
    if text.count(old) != 1:
        raise ValueError(f'Expected one export anchor: {old[:70]}')
    return text.replace(old, new, 1)


def export(output, prefix, staging_url='', staging_key=''):
    if not re.fullmatch(r'/[A-Za-z0-9_/-]*/', prefix):
        raise ValueError('Use an absolute directory prefix ending in /')
    if bool(staging_url) != bool(staging_key):
        raise ValueError('Staging URL and publishable key are required together')
    if staging_url:
        parsed = urlparse(staging_url)
        if parsed.scheme != 'https' or not re.fullmatch(r'[a-z0-9]{20}\.supabase\.co', parsed.netloc):
            raise ValueError('Use a separate Supabase HTTPS project URL')
        if parsed.netloc.split('.')[0] == PRODUCTION_PROJECT:
            raise ValueError('Production Supabase is forbidden for this candidate')
        if not staging_key.startswith('sb_publishable_'):
            raise ValueError('Only a publishable key may be included in public HTML')
    assets = packager.verified_assets()
    output = Path(output)
    if output.exists() and any(output.iterdir()):
        raise ValueError('Export directory must be empty; preserve existing deployments')
    output.mkdir(parents=True, exist_ok=True)
    for name in assets:
        target = output / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / 'game' / name, target)
    html = (ROOT / 'game/index.html').read_text()
    html = html.replace('/new-audio/', prefix + 'new-audio/').replace('/_cdn/', prefix + '_cdn/')
    html = re.sub(r'const SUPABASE_URL="[^"]*";', 'const SUPABASE_URL=' + json.dumps(staging_url) + ';', html, count=1)
    html = re.sub(r'const SUPABASE_KEY="[^"]*";', 'const SUPABASE_KEY=' + json.dumps(staging_key) + ';', html, count=1)
    html = replace_once(html,
        'const sb=(window.supabase&&window.supabase.createClient)?window.supabase.createClient(SUPABASE_URL,SUPABASE_KEY):null;',
        'const sb=(SUPABASE_URL&&SUPABASE_KEY&&window.supabase&&window.supabase.createClient)?window.supabase.createClient(SUPABASE_URL,SUPABASE_KEY):null;')
    html = replace_once(html, '<div class="local-section"><h2>Juego local</h2>',
        '<p role="status">Candidata B1.11 · pruebas en iPhone</p>\n<div class="local-section"><h2>Juego local</h2>')
    if not staging_url:
        html = replace_once(html, '<div class="online-section"><h2>Online</h2><p>Cada jugador desde su dispositivo</p>',
            '<div class="online-section"><h2>Online</h2><p>Las salas estarán disponibles cuando terminemos de preparar el entorno de prueba.</p>')
        html = replace_once(html, '<button id="createOnlineBtn" type="button">', '<button id="createOnlineBtn" type="button" disabled>')
        html = replace_once(html, '<button id="showJoinBtn" type="button">', '<button id="showJoinBtn" type="button" disabled>')
        html = replace_once(html, '<button id="joinOnlineBtn" type="button">', '<button id="joinOnlineBtn" type="button" disabled>')
        html = re.sub(r'<script src="https://cdn\.jsdelivr\.net/[^\"]+"></script>', '', html, count=1)
    if PRODUCTION_PROJECT in html:
        raise ValueError('Export still contains the production project')
    (output / 'index.html').write_text(html)
    (output / '.nojekyll').write_text('')
    (output / 'ASSETS_SHA256.json').write_text(json.dumps(assets, indent=2) + '\n')
    metadata = {'candidate':'B1.11', 'source_commit':'65aa00153fb744004f890900640363cbbe524ebd',
                'asset_prefix':prefix, 'mp3':188, 'online':'staging' if staging_url else 'disabled',
                'index_sha256':hashlib.sha256(html.encode()).hexdigest()}
    (output / 'CANDIDATE.json').write_text(json.dumps(metadata, indent=2) + '\n')
    return metadata


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--prefix', default='/Mambapalabra/')
    parser.add_argument('--staging-url', default='')
    parser.add_argument('--staging-key-file', type=Path)
    args = parser.parse_args()
    metadata = export(args.output, args.prefix, args.staging_url,
                      args.staging_key_file.read_text().strip() if args.staging_key_file else '')
    print(json.dumps(metadata, indent=2))
