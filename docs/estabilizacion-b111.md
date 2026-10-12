# Estabilización de Mambapalabra B1.11

La candidata está en `game/index.html`. La fuente original y B1.11 consolidada
permanecen intactas para comparar y reproducir el origen. No se modifica Floot,
el wrapper publicado, las funciones de Supabase ni la base de producción.

## Fuente y recursos conservados

El adjunto `MAMBAPALABRA_PARA_CODEX_B111.zip` contiene ambos HTML con los mismos
hashes que el repositorio, pero no incluye audios. Se recuperó el ZIP exacto del
README y se verificaron estos hashes:

| Archivo | SHA256 |
| --- | --- |
| ZIP histórico B1.10 | `7d3e4675e39bd296ac9da6ab9d2720badae27453742f0dd68b7d94148ed6a14d` |
| HTML original B1.10 | `1ce6484c1e50355e4f33e4eba28eabff305ce31831272f3e13135ecb4943e6ba` |
| B1.11 consolidada exacta | `736a580452da46313d09aae29e5394b7632ccdba4e17e462ad97f59a89b9b1c4` |

Los 188 MP3, el logo y el manifest están en `game/`, con hashes por archivo en
`game/ASSETS_SHA256.json`. Se conservan también `v33_name_facu.mp3`,
`v33w_072.mp3` (Cocido) y `unlock.mp3`. El empaquetador verifica todos los bytes
antes de producir el ZIP autocontenido. No se generan ni se sustituyen audios.

## Causas y correcciones

| Problema | Causa | Comportamiento de la candidata |
| --- | --- | --- |
| Turno congelado si falla la voz | `readingCanFinish` trataba un fallo como lectura sin terminar; dejaba `READING` y todos los controles bloqueados. También impedía consolidar el puntaje de muerte súbita cuando fallaba la locución del resultado. | Una reproducción fallida permite continuar con la definición visible, responder y conservar el puntaje. La cancelación sigue invalidando la operación anterior. Reintentar audio continúa disponible. |
| TTS sin inicio o durante pausa | El timeout único no distinguía arranque de lectura, no pausaba SpeechSynthesis y seguía consumiendo el plazo durante pausa. Errores síncronos de construcción/enumeración de voces podían rechazar la operación. | Plazo de inicio de 10 s; plazo de lectura de al menos 30 s proporcional al texto. Pausa/reanuda la voz y el plazo restante; limpieza y cancelación por secuencia; captura fallos síncronos. |
| Inicio bloqueado por permisos/audio | `audio.play()` y `getUserMedia()` podían quedar pendientes indefinidamente. | Desbloqueo de audio limitado a 10 s; espera de permiso de micrófono limitada a 5 s y cierre de streams que llegan tarde. El modo texto sigue disponible. Reinicios concurrentes respetan la última solicitud. |
| K/W deshabilitadas | El filtro exigía dos MP3 nuevos por pregunta; K/W tienen definiciones históricas, pero no esas grabaciones. | Mantiene las 204 preguntas activas y añade las cuatro filas originales Koala, Karate, Wifi y Waterpolo. Total: 208. No cambia texto, respuesta ni aliases; no inventa preguntas. Dos alternativas por letra permiten preguntas distintas para ambos jugadores y rotación entre partidas. |
| Tiempo inconsistente o respuesta fuera de plazo | El reloj local usaba `Date.now()`; el vencimiento se comprobaba sólo cada 200 ms. Una validación con tiempo cero podía reanudar sin intervalo ni timeout. | Mide duración con `performance.now()`, verifica plazo antes de respuesta/Pasapalabra y ejecuta timeout al intentar arrancar con tiempo agotado. Los timestamps online conservan `Date.now()` para el protocolo existente. Los callbacks capturan la instancia de partida. |
| Dictado deja `VALIDATING` congelado | Se esperaba `onresult`/`onend` sin límite después de `onspeechend`. | Espera final limitada a 1,5 s, aborta el contexto tardío y permite texto; no declara cerrado un motor que no confirmó `onend`. No admite resultados de sesiones abandonadas. |
| Doble respuesta en muerte súbita al reanudar | Reanudar convertía cualquier `VALIDATING` en `ANSWERING`, incluso cuando ya se procesaba una respuesta aceptada. | Sólo abandona dictados incompletos; la validación aceptada mantiene los controles cerrados hasta terminar. |
| Invitación de candidata dirige a producción | La URL estaba fijada al dominio de Floot. | Usa el origen y la ruta actuales con `?sala`, sin cambiar la producción existente. |

## Regresiones y aislamiento

Las cinco pruebas existentes se ejecutaron y pasaron antes de cambiar el código.
Trece regresiones nuevas fallan al ejecutarlas contra B1.11 original y pasan
contra la candidata. Reproducen el bloqueo por fallo de
voz, la falta de K/W, el reloj dependiente de la hora del sistema, respuestas
fuera de plazo, dictado sin cierre, TTS sin arranque y pausa de TTS, además del
desbloqueo de audio y el retorno incorrecto desde validación con tiempo cero.

Las pruebas de navegador sirven el HTML completo con un acceso de inspección
inyectado exclusivamente por el servidor de tests. Ese acceso no está en
`game/index.html` ni en el ZIP entregable. Cada caso usa almacenamiento aislado;
las solicitudes externas están bloqueadas. Los fallos de voz/micrófono se
inyectan en el navegador; una prueba adicional usa `HTMLMediaElement` real,
decodifica y reproduce un MP3 original y comprueba que el reloj no avance en
READING. Capturas de menú y primera partida en `artifacts/<browser>/`.

El test online abre dos contextos aislados contra un servidor local que simula
el contrato de salas, versiones y tokens. Comprueba creación, ingreso, traspaso,
controles por titular, estado de pendiente, acierto sincronizado y reloj del
rival detenido. Esto **no certifica el backend real ni sus RPC/Edge Functions**.

## Validación y límites

- Constructor histórico: 5 pruebas, sin omisiones.
- Conservación y empaquetado: 3 pruebas; 188 MP3 verificados byte por byte.
- Chromium y WebKit: 29 pruebas por navegador; regresiones del motor, partida completa de 54 respuestas,
  muerte súbita, pausa, reinicio, 30 reinicios locales, audio real y dos sesiones
  online simuladas. Comandos reproducibles en README y CI para ambas plataformas.
- JavaScript inline: verificar con `node --check` además de la ejecución real.
- El ZIP candidato se genera con `python3 tools/package_candidate.py`, sin red
  ni publicación. Debe servirse por HTTP con su carpeta como raíz.
- Pendiente: Safari/iPhone físico, voces y dictado de dispositivos reales,
  backend de staging autorizado y multijugador real (reconexión, concurrencia,
  resultados y revancha). El README informa Supabase de producción INACTIVE;
  no se reactiva, se despliega ni se modifica ese proyecto.

El entorno cloud ejecutó WebKit con bibliotecas oficiales de Debian verificadas
por APT, extraídas en una caché local por falta de permisos de instalación global.
Se usa `/tmp` como temporal y una caché escribible. El detector de bibliotecas
globales de Playwright no ve esa instalación local; se comprobó la carga real
de las bibliotecas y del navegador. La CI usa `playwright install --with-deps`
en Ubuntu y no necesita ese ajuste local.
