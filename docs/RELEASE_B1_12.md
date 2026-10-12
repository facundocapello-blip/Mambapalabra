# MAMBAPALABRA B1.12 — Candidata STAGING

Base exacta: `candidata-https-b111` con cambios de PR #1–#4 ya fusionados al 12/10/2026.

## Qué contiene B1.12
- Dos círculos debajo del rosco: segundos **fijos** de jugador 1 (izquierda) y jugador 2 (derecha). Nombre del jugador debajo de su círculo. Aciertos siguen en el marcador superior.
- Temporizadores del motor independientes; corren únicamente en ANSWERING.
- Micrófono activable únicamente con RESPONDER (sin permiso automático al inicio).
- 188 audios originales conservados sin modificar.
- Online conectado al proyecto **MAMBAPALABRA-STAGING** gratuito, sin tráfico al Supabase original.
- El número de versión se actualizó de B1.11 a B1.12 **sin cambiar la lógica de juego de la candidata ya revisada**.
- Manifiesto actualizado: `online=staging` y SHA256 del HTML publicado. El manifiesto anterior decía incorrectamente `disabled`.

## Validación
- Tests móviles ya existentes: `tests/test_ui_relojes_mic.py` (Chromium y WebKit), y prueba real de dos contextos `tests/test_staging_live_ui.py`.
- `tools/package_release_b112.py`: verifica el SHA256 del HTML, presencia de botones online, ausencia de claves privadas y 188 MP3 byte a byte; genera ZIP autónomo de artefactos estáticos.
- Las pruebas exactas de esta rama deberán pasar por CI antes de fusionar a la rama de GitHub Pages. WebKit automatizado **no** equivale a Safari real.

## Pendientes
- Dos iPhones reales: cambio de turno, relojes, permiso micrófono, reconexión.
- Partida completa online: tiempo agotado, empate/muerte súbita, resultado, revancha.
- No modificar Floot ni el Supabase original.
