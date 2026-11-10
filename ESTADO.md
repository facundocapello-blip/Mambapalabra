# ESTADO — Mambapalabra

Actualizado: 2026-11-10

## Publicado
- `https://facundocapello-blip.github.io/Mambapalabra/` — rama `production`, HTTP 200 verificado 10/11 (index 259 KB, audio-map 60 KB).
- Refactor 10/11: `index.html` 376 KB → 255 KB (-32%). `audio-map.json` fuera del HTML, con fetch y fallback. Código muerto (PIPER_AUDIO_MAP, RESERVE) eliminado.
- Versión visible en el lobby: **B1.13.1-UX1 · RC6**.
- Último commit: `ece420e` (= `origin/production`, 10/11). Encima de `275c793` (merge del refactor `d2764e4`).

## Abierto
- Probar en iPhone real: checklist en `~/work/mambapalabra-prueba-iphone.md`.
- Letras flojas: K tiene 6 palabras y W 7 (las demás, 10–20). Si se emparejan, las nuevas salen sin voz.
- PWA: falta service worker para que sea instalable y funcione offline. El manifest ya está.
- Accesibilidad: los `letter-chip` del rosco son `<div>` sin `role` ni `aria-label`; un lector de pantalla no sigue el progreso.

## Trampas
- GitHub Pages cachea 10 minutos: usar `?v=N` antes de decir que algo no se publicó.
- No renombrar ni mover nada de `fish-bank/`, `fish-audio/`, `new-audio/`: el mapa de audio los referencia.
- El modo Online está deshabilitado a propósito (el Supabase al que apuntaba no existe).
- `main` no tiene el juego. Publicar desde `main` deja el sitio roto.
- `index.html.bak-pre-refactor` es backup local y está en `.gitignore`.

## Verificar
- `powershell -NoProfile -File qa/smoke.ps1` — HTTP, build B1.13 y 10 assets al azar contra `ASSETS_SHA256.json`; con `-Full`, los 193 hashes.
