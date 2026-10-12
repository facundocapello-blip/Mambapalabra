#!/usr/bin/env python3
"""Compila el HTML editable B1.11 replicando las 5 sustituciones verificadas de Floot.
No cambia producción; mantiene todos los recursos originales dentro de ZIP fuente.
"""
from pathlib import Path
import io
import urllib.request
import zipfile

SOURCE_URL = "https://mambapalabra-b1-candidata.floot.app/_cdn/static/b280c36c-b922-47d1-9a6d-ef7327c9b517-mambapalabra-b1-10-visual.zip"

DEVICE = '''  function deviceSpeak(text,opts={},seq=host.seq){
    if(!window.speechSynthesis||!window.SpeechSynthesisUtterance)return Promise.resolve({status:SPEECH_RESULT.FAILED,started:false});
    return new Promise(resolve=>{
      let done=false,started=false,timer;
      const finish=status=>{if(done)return;done=true;clearTimeout(timer);if(host.cancelPlayback===cancel)host.cancelPlayback=null;utterance.onend=null;utterance.onerror=null;if(seq===host.seq){host.speaking=false;updateMusic();}resolve({status,started});};
      const cancel=()=>finish(SPEECH_RESULT.CANCELLED);
      const utterance=new SpeechSynthesisUtterance(text);
      utterance.lang="es-AR";utterance.rate=.92;
      const voices=window.speechSynthesis.getVoices();
      utterance.voice=voices.find(v=>/^es[-_]AR/i.test(v.lang))||voices.find(v=>/^es/i.test(v.lang))||null;
      host.cancelPlayback=cancel;host.speaking=true;updateMusic();
      setVoiceStatus("fish","Voz en español del dispositivo.");
      utterance.onstart=()=>{if(seq!==host.seq)return cancel();started=true;if(opts.onStart)opts.onStart();};
      utterance.onend=()=>finish(seq===host.seq?SPEECH_RESULT.COMPLETED:SPEECH_RESULT.CANCELLED);
      utterance.onerror=()=>finish(seq===host.seq?SPEECH_RESULT.FAILED:SPEECH_RESULT.CANCELLED);
      timer=setTimeout(()=>{finish(SPEECH_RESULT.FAILED);if(seq===host.seq)window.speechSynthesis.cancel();},Math.max(30000,text.length*180));
      try{window.speechSynthesis.speak(utterance);}catch(e){finish(SPEECH_RESULT.FAILED);}
    });
  }
'''
OLD_NO_MP3='    if(!paths.length){if(YOUTUBE_QUESTION_POOL.some(q=>((q[4]==="CONTIENE"?"Contiene ":"")+q[0]+": "+q[2])===text))setVoiceStatus("text","Definición sin audio: leé la pregunta en pantalla.");if(opts.onStart)opts.onStart();return {status:SPEECH_RESULT.COMPLETED,started:false};}'
OLD_MP3_ERROR='if(result.status===SPEECH_RESULT.FAILED)setVoiceStatus("error","No pude cargar el audio del conductor. Tocá REPETIR.");'

def replace_once(text, original, new, label):
    n=text.count(original)
    if n!=1: raise RuntimeError(f"Ancla {label}: se esperaba 1, hay {n}. No se construye.")
    return text.replace(original,new,1)

def consolidate(html):
    html=replace_once(html, '  async function hostSpeak(text,opts={}){', DEVICE+'  async function hostSpeak(text,opts={}){', 'insertar TTS')
    html=replace_once(html, OLD_NO_MP3, '    if(!paths.length)return deviceSpeak(text,opts,seq);', 'sin MP3')
    html=replace_once(html, OLD_MP3_ERROR, 'if(result.status===SPEECH_RESULT.FAILED)return deviceSpeak(text,opts,seq);', 'MP3 fallido')
    html=replace_once(html, '  async function primeAV(){', '  async function primeAV(){\n    try{const u=new SpeechSynthesisUtterance(" ");u.lang="es-AR";window.speechSynthesis.speak(u);}catch(e){}', 'prime AV')
    html=replace_once(html, 'B1.10-CANDIDATA-TV', 'B1.11-VOZ-COMPLETA', 'versión')
    return html

def main():
    source=Path('game/B1_10_ORIGINAL_FLOOT.html')
    if not source.exists():
        print('Descargando código original desde Floot...')
        with urllib.request.urlopen(SOURCE_URL,timeout=90) as resp:
            blob=resp.read()
        with zipfile.ZipFile(io.BytesIO(blob)) as archive:
            clips=[name for name in archive.namelist() if name.startswith('new-audio/') and name.endswith('.mp3')]
            if len(clips)!=188: raise RuntimeError(f'ZIP inesperado: {len(clips)} MP3')
            source.parent.mkdir(parents=True,exist_ok=True)
            source.write_bytes(archive.read('index.html'))
    compiled=consolidate(source.read_text(encoding='utf8'))
    out=Path('game/B1_11_CONSOLIDADA.html')
    if out.exists() and out.read_text(encoding='utf8')!=compiled: raise RuntimeError('Ya existe una B1.11 distinta; no sobrescribir.')
    out.write_text(compiled,encoding='utf8')
    print(f'Consolidada B1.11: {out}, {len(compiled)} caracteres; audio en ZIP fuente.')
    print('ADVERTENCIA: en hosting directo preservar rutas de audio /new-audio y enlace ?sala antes de publicar.')
if __name__=='__main__': main()
