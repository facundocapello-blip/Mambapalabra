# ESTADO — Mambapalabra

Actualizado: 2026-11-15

## Publicado
- 16/11: pausa entre la letra y la definición acortada a ~0,25 s en 472 clips `qNNNN` (antes mediana 0,53 s, máx. 1 s). Corte por frames MP3 sin recomprimir; mismos nombres de archivo, hashes actualizados. Globo de la letra dentro del círculo, con colita hacia el mini yo.
- 15/11: mini yo de Facu como conductor en el centro del rosco (sprite de Black Mamba, `static/faca-sprite.png`, sin halo blanco): saluda en la intro, gesticula al leer, piensa al esperar, salta si acierta, se agarra la cabeza si erra o se acaba el tiempo, mira a los costados en pasapalabra. Letra en globo (dice "CONTIENE" cuando corresponde), ficha del aro en contorno, aro de tiempo desde arriba, RESPONDER deshabilitado legible. La definición ya no se ve antes de que el conductor la lea.
- 15/11: Justicia (J, #144) con definición nueva sin la respuesta ("Poder del Estado encargado de aplicar las leyes y resolver los conflictos."); `q0144.mp3` regenerado con la misma voz Fish.
- 15/11: precarga de la segunda intro (`04_intro_solo`) mientras suena la primera y de las preguntas de muerte súbita (la primera mientras suena "Empate…", las siguientes mientras suena el resultado). Limpieza: sin `announcePlayer` ni `PHRASES.switchTo`.
- 15/11: conductor sin anuncio de nombres (el turno se anuncia por `aria-live` en `#activeName`); aviso "Vamos con las pendientes" al empezar la segunda vuelta; cues cortos (correcto, tiempo, pendientes) a 1,12×; precarga de los próximos audios mientras el jugador responde (bache cue→definición de 113–473 ms a 6–20 ms en prueba local). Auditoría en `reviews/audit-plan-full.md` (sin commitear).
- 15/11: +124 preguntas de YouTube (Pasapalabra programas 213, 214 y 215) con voz Fish. Banco del juego 398 → 522; Sheet Banco A-0429…T-0552.
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
