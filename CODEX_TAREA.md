# Codex — primera tarea B1.11

**Única fuente de verdad:** ZIP B1.10 publicado por Floot en la URL indicada en README, más cinco adaptaciones B1.11 del wrapper `pages/_index.tsx`. La rama no es producción. No reconstruir, ni cambiar reglas, ni publicar.

## Fase cero (obligatoria)
- Descargar el ZIP original público de Floot y validar 188 MP3, index.html y rutas. Consolidar B1.11 en `game/index.html` mediante las cinco modificaciones idénticas a Floot: insertar `deviceSpeak` antes de `hostSpeak`; usar TTS cuando no haya `paths`; usar TTS si falla un MP3; preparar SpeechSynthesis en `primeAV`; cambiar etiqueta B1.10 por B1.11. Verificar que cada ancla de reemplazo aparece una sola vez antes de tocar archivo.
- Conservar `new-audio/` y todos los demás recursos originales. No inventar audios ni modificar pronunciaciones aprobadas de «Facu» y «Cocido».
- Reportar hashes SHA256 y obtener captura de menú y primera partida de la candidata (Chromium). Usar servidor HTTP local: el código utiliza `/new-audio/`.

## Después
- Crear una batería de tests Playwright con Chromium y WebKit: inicio, primera definición, letra correcta, incorrecta y cambio, Pasapalabra botón/voz, reloj sólo en ANSWERING, pausa, fin, muerte súbita, reset, y online en 2 contextos aislados.
- Diagnóstico raíz y arreglo mínimo: cobertura K/W (el banco activo tiene 204 preguntas pero sólo 25 letras); fallback de voz que puede bloquear en READING si falla TTS/MP3; lifecycle de micrófono y temporizadores; invitaciones `?sala` cuando ya no existe wrapper; Supabase online.
- Backend Supabase relacionado: `mcrnstwmubtiiacyiaeu` estaba INACTIVE en octubre 2026. **No reactivarlo ni alterar producción**. Preparar pruebas de backend en staging.
- Toda corrección requiere reproducir bug, probar fix, flujo completo y regresión. Separar funcional de visual.

**Entrega:** código completo en PR a esta rama o desde rama hija, pruebas reales con comandos y resultados, pendientes de iPhone Safari. Prohibido publicar.
