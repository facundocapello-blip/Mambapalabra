#!/usr/bin/env python3
"""Package isolated B1.13 staging candidate without changing B1.12 artifacts."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
STAGING="qbzrqinnhrgeqvgtifrt"
PROD="mcrnstwmubtiiacyiaeu"
def main():
    html=(ROOT/"index.html").read_bytes()
    source=html.decode("utf-8")
    assert 'B1.13-ROSCO-PROTAGONISTA-STAGING' in source
    assert STAGING in source and PROD not in source
    assert "sb_secret_" not in source and "service_role" not in source
    assert 'await hostSpeak(wrongLead)' in source
    assert 'toUpperCase(),3000' in source
    assets=json.loads((ROOT/"ASSETS_SHA256.json").read_text())
    mp3=[p for p in assets if p.endswith(".mp3")]
    assert len(mp3)==188
    for rel,digest in assets.items():
        f=ROOT/rel
        assert f.is_file() and hashlib.sha256(f.read_bytes()).hexdigest()==digest,rel
    meta={
      "candidate":"B1.13","source_branch":"feature/b113-rosco-audio-ux",
      "asset_prefix":"/Mambapalabra/","mp3":len(mp3),
      "online":"staging","staging_project":STAGING,
      "index_sha256":hashlib.sha256(html).hexdigest(),
      "revision":"Rosco protagonista, relojes circulares, audio incorrecto en origen, feedback 3s"
    }
    dist=ROOT/"dist"
    dist.mkdir(exist_ok=True)
    output=dist/"MAMBAPALABRA_B1_13_STAGING.zip"
    with ZipFile(output,"w",ZIP_DEFLATED,compresslevel=6) as z:
        z.writestr("CANDIDATE.json",json.dumps(meta,ensure_ascii=False,indent=2)+"\n")
        for rel in ["index.html","ASSETS_SHA256.json",".nojekyll",*assets]:
            z.write(ROOT/rel,rel)
    print(json.dumps({"zip":str(output),"sha256":meta["index_sha256"],"mp3":len(mp3)}))
if __name__=="__main__":
    main()
