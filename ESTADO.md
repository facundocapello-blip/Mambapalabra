# ESTADO — Mambapalabra

Actualizado: 2026-10-28

## Publicado
- `https://facundocapello-blip.github.io/Mambapalabra/` — rama `production`.
- Versión visible en el lobby: **B1.13.1-UX1 · RC6**. HTTP 200 verificado.
- Último commit: `1a36902` (README + AGENTS.md).

## Abierto
- Probar en iPhone real: checklist en `~/work/mambapalabra-prueba-iphone.md`.
- Letras flojas: K tiene 6 palabras y W 7 (las demás, 10–20). Se repiten cada ~3 partidas.
  No es un bug. Si se emparejan, las nuevas salen sin voz.

## Trampas
- GitHub Pages cachea 10 minutos: usar `?v=2` antes de decir que algo no se publicó.
- No renombrar ni mover nada de `fish-bank/`, `fish-audio/`, `new-audio/`: el mapa está
  hardcodeado en `index.html`.
- El modo Online está deshabilitado a propósito (el Supabase al que apuntaba no existe).
- `main` no tiene el juego. Publicar desde `main` deja el sitio roto.
