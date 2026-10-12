#!/usr/bin/env python3
"""Verify preserved resources and package the candidate without network or deploy."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def verified_assets():
    game = ROOT / 'game'
    assets = json.loads((game / 'ASSETS_SHA256.json').read_text())
    mp3 = [name for name in assets if name.startswith('new-audio/') and name.endswith('.mp3')]
    if len(mp3) != 188:
        raise ValueError(f'Expected 188 original MP3 files, got {len(mp3)}')
    for name, expected in assets.items():
        relative = Path(name)
        if relative.is_absolute() or '..' in relative.parts:
            raise ValueError(f'Unsafe resource path: {name}')
        actual = hashlib.sha256((game / relative).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f'Resource changed: {name}')
    return assets


def package(output):
    assets = verified_assets()
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for name in ['index.html', 'ASSETS_SHA256.json', *assets]:
            archive.write(ROOT / 'game' / name, name)
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'artifacts/MAMBAPALABRA_B111_ESTABILIZACION.zip')
    args = parser.parse_args()
    output = package(args.output)
    print(f'{output}: {hashlib.sha256(output.read_bytes()).hexdigest()} (188 original MP3)')
