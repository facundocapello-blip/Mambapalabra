#!/usr/bin/env python3
"""Descarga el código ORIGINAL B1.10 de Floot para Codex. No publica ni modifica producción."""
import hashlib
import io
import json
from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile

URL="https://mambapalabra-b1-candidata.floot.app/_cdn/static/b280c36c-b922-47d1-9a6d-ef7327c9b517-mambapalabra-b1-10-visual.zip"
with urlopen(URL,timeout=90) as response:
    data=response.read()
with ZipFile(io.BytesIO(data)) as z:
    files=z.namelist()
    audios=[x for x in files if x.startswith("new-audio/") and x.endswith(".mp3")]
    if "index.html" not in files or len(audios)!=188:
        raise SystemExit(f"Paquete inesperado: index.html={('index.html' in files)}; MP3={len(audios)}")
    html=z.read("index.html")
Path("game").mkdir(exist_ok=True)
Path("game/B1_10_ORIGINAL_FLOOT.html").write_bytes(html)
meta={"origen":URL,"version_origen":"B1.10 (NO es B1.11 hasta consolidar 5 reemplazos)",
      "archivos_en_zip":len(files),"mp3":len(audios),
      "zip_sha256":hashlib.sha256(data).hexdigest(),
      "html_sha256":hashlib.sha256(html).hexdigest()}
Path("game/ORIGEN.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2)+"\n")
print(json.dumps(meta,ensure_ascii=False))
