#!/usr/bin/env python3
"""Verifica integridad y produce ZIP COMPLETO de la candidata B1.12.
No publica ni cambia ningún servicio. Nunca incluye claves privadas.
"""
import hashlib
import json
import re
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
VERSION = "B1.12"
STAGING = "qbzrqinnhrgeqvgtifrt"
PRODUCTION = "mcrnstwmubtiiacyiaeu"

def main():
    html = (ROOT / "index.html").read_bytes()
    source = html.decode("utf-8")
    metadata = json.loads((ROOT / "CANDIDATE.json").read_text())
    assert metadata["candidate"] == VERSION
    assert metadata["online"] == "staging"
    assert metadata["staging_project"] == STAGING
    assert metadata["index_sha256"] == hashlib.sha256(html).hexdigest(), "HASH HTML / MANIFIESTO NO COINCIDEN"
    assert 'mambapalabra-version" content="B1.12-DOS-RELOJES-STAGING"' in source
    assert 'id="orbTimer1"' in source and 'id="orbTimer2"' in source
    assert 'id="orbName1"' in source and 'id="orbName2"' in source
    assert 'id="handsFree"' not in source
    assert "autoStartRecognition" not in source
    assert STAGING in source and PRODUCTION not in source
    assert "sb_secret_" not in source and "service_role" not in source
    assert 'id="createOnlineBtn" type="button" disabled' not in source
    assert re.search(r"<script src=.*supabase.min.js",source)
    assets = json.loads((ROOT / "ASSETS_SHA256.json").read_text())
    mp3 = [p for p in assets if p.endswith(".mp3")]
    assert len(mp3) == 188, f"Expected 188 MP3; got {len(mp3)}"
    for rel, expected in assets.items():
        path = ROOT / rel
        assert path.is_file(), f"Missing asset: {rel}"
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, f"Changed asset: {rel}"
    dist = ROOT / "dist"
    dist.mkdir(exist_ok=True)
    output = dist / "MAMBAPALABRA_B1_12_STAGING.zip"
    files = ["index.html", "CANDIDATE.json", "ASSETS_SHA256.json", ".nojekyll"] + list(assets)
    assert len(files) == len(set(files))
    with ZipFile(output, "w", compression=ZIP_DEFLATED, compresslevel=6) as archive:
        for rel in sorted(files):
            archive.write(ROOT / rel, rel)
    print(json.dumps({"version": VERSION, "online": "staging",
       "html_sha256": metadata["index_sha256"], "mp3_verified": len(mp3),
       "total_files": len(files), "zip": str(output), "zip_bytes": output.stat().st_size}))
if __name__ == "__main__":
    main()
