# ESTADO — Mambapalabra

Actualizado: 2026-11-04

## Publicado
- `https://facundocapello-blip.github.io/Mambapalabra/` — rama `production`, 200 y consola sin errores (verificado 02/11).
- Versión visible en el lobby: **B1.13.1-UX1 · RC6** (leída del HTML publicado, no de este archivo).
- Publicado: `948596e` (= `origin/production`, upstream configurado el 04/11). Encima de `064fad4` van solo docs y `qa/smoke.ps1`, sin cambios de producto.

## Abierto
- Probar en iPhone real: checklist en `~/work/mambapalabra-prueba-iphone.md`.
- Letras flojas: K tiene 6 palabras y W 7 (las demás, 10–20). No es un bug; si se emparejan, las nuevas salen sin voz.

## Trampas
- GitHub Pages cachea 10 minutos: usar `?v=2` antes de decir que algo no se publicó.
- No renombrar ni mover nada de `fish-bank/`, `fish-audio/`, `new-audio/`: el mapa está hardcodeado en `index.html`.
- El modo Online está deshabilitado a propósito (el Supabase al que apuntaba no existe).
- `main` no tiene el juego. Publicar desde `main` deja el sitio roto.

## Verificar
- `powershell -NoProfile -File qa/smoke.ps1` — HTTP, build B1.13 y 10 assets al azar contra `ASSETS_SHA256.json`; con `-Full`, los 193 hashes.
