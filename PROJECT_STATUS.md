# Estado de Mambapalabra

Actualizado: 2026-10-20 (RC5 aprobada por el usuario como candidata STAGING; historial preservado).

## Fish398 RC5 — candidata STAGING aprobada (20/10/2026)

- **Aprobación explícita del usuario:** «Sí aprobada», tras solicitar publicación y revisar el estado de pruebas de RC5. Aprobada como **candidata de STAGING**, no equivale a autorización de despliegue en producción.
- **Versión publicada:** `B1.13.1-UX1-FISH398-VOZ-UNICA-RC5-STAGING` — https://facundocapello-blip.github.io/mambapalabra-staging/
- **Único ajuste:** velocidad de definiciones Fish +12% frente a RC3 (multiplicador `1.12`, frente a `1.08` en RC4), sin alterar el resto de locuciones, ni regenerar MP3.
- **QA automatizado:** [workflow 39438581046](https://github.com/facundocapello-blip/mambapalabra-staging/actions/runs/39438581046), SUCCESS: regresión de velocidad, flujo completo y muerte súbita en navegadores de CI.
- **Deploy y QA HTTPS:** [workflow 39523263220](https://github.com/facundocapello-blip/mambapalabra-staging/actions/runs/39523263220), SUCCESS: Pages, manifiesto RC5, Chromium/WebKit y dos sesiones online reales en STAGING.
- **Pendiente no declarado como probado:** pruebas directas del micrófono y experiencia acústica en Safari físico. La aprobación del usuario es de la candidata, sin atribuir un ensayo instrumental no realizado.
- **Producción intacta:** https://facundocapello-blip.github.io/Mambapalabra/ . Mantener RC4 y RC3 disponibles para rollback en STAGING. No promover sin pedido explícito.

## Fish398 RC4 — definiciones +8% (20/10/2026)

- **Versión STAGING publicada:** `B1.13.1-UX1-FISH398-VOZ-UNICA-RC4-STAGING` en https://facundocapello-blip.github.io/mambapalabra-staging/ . Reemplaza a RC3 únicamente en STAGING; producción permanece intacta.
- **Pedido y cambio acotado:** locución de definiciones **8% más rápida** que RC3, tanto en local como online y muerte súbita. Multiplicador `1.08` aplicado únicamente a `fish-bank/qNNNN.mp3`; tasa local pasa de `0.92` a `0.9936`, online de `1.0` a `1.08`. `preservesPitch` mantiene el tono. Saludos, frases de correcto/incorrecto, presentación y demás clips conservan la velocidad anterior.
- **Sin regeneración:** los 819 MP3 Fish y 188 MP3 históricos mantienen **exactamente los mismos bytes**. Se cambió solo `index.html`, metadatos de versión y se añadió `FISH_SPEED_RELEASE.json`.
- **Fuente del cambio:** `tools/package_fish_definition_speed_rc4.py` y `tools/qa_fish_definition_speed_rc4.py` en rama `qa/fish-voice-free-api-test`. El paquete RC4 se construyó desde el artefacto RC3 verificado, sin invocar Fish API.
- **QA antes de publicar:** [workflow 39412672267](https://github.com/facundocapello-blip/mambapalabra-staging/actions/runs/39412672267), SUCCESS: sintaxis JS, 1007 MP3 intactos, velocidad selectiva, tono, intro, respuesta incorrecta, repetición, reloj, partida local, muerte súbita y reinicio en Chromium/WebKit (audio acelerado por mock para QA).
- **Publicación y QA HTTPS:** [workflow 39413082764](https://github.com/facundocapello-blip/mambapalabra-staging/actions/runs/39413082764), deploy GitHub Pages SUCCESS y pruebas en Chromium/WebKit de carga, audio Fish, MP3, dos sesiones online reales y sincronización de turnos. El manifiesto publicado registra `definition_speed_multiplier:1.08`.
- **Rollback:** [workflow RC3](https://github.com/facundocapello-blip/mambapalabra-staging/actions/workflows/deploy-fish-rc3-pages.yml) sigue disponible para restaurar la versión anterior de STAGING.
- **Pendiente:** confirmar escucha subjetiva y micrófono en Safari iPhone físico; la automatización usa simulación de reproducción para pruebas de flujo.

## Fish398 RC3 — STAGING Pages (20/10/2026)

- **Versión candidata aislada:** `B1.13.1-UX1-FISH398-VOZ-UNICA-RC3-STAGING`. URL: https://facundocapello-blip.github.io/mambapalabra-staging/ . Este es el STAGING más reciente verificado; el Floot UX1 anterior permanece como referencia histórica, **no** como el último STAGING.
- **Fuente del generador:** rama `qa/fish-voice-free-api-test` del repositorio `facundocapello-blip/mambapalabra-staging`; script `tools/generate_fish_bank.py`, motor `s2.1-pro-free` de Fish Audio. El workflow no debe volver a ejecutarse para regenerar material ya completado.
- **Banco generado:** 398 definiciones del manifiesto `piper-audio/manifest.json` (no confundir con las 194 APROBADAS de la planilla maestra), 796 audios pregunta/error + 15 frases fijas = **811 MP3 Fish**. Se incorporaron **8 MP3 Fish adicionales** de introducciones y muerte súbita. Los **188 MP3 históricos** se conservaron como recursos; la reproducción RC3 utiliza exclusivamente los clips Fish configurados, sin fallback TTS del dispositivo.
- **Evidencia de generación:** [workflow completo 39200425081](https://github.com/facundocapello-blip/mambapalabra-staging/actions/runs/39200425081), resultado SUCCESS; 811/811 MP3 decodificados con FFmpeg y texto/frase/hash validados. Artefacto conservado en GitHub Actions: `Mambapalabra-Fish-Bank-811-Partial-Or-Complete` (ID 12164722798).
- **Evidencia de empaquetado RC3:** [workflow 39361651619](https://github.com/facundocapello-blip/mambapalabra-staging/actions/runs/39361651619), SUCCESS; 811 + 8 MP3 Fish, sin Piper ni TTS de dispositivo, regresiones Chromium y WebKit aprobadas. Artefacto `MAMBAPALABRA_FISH398_VOZ_UNICA_RC3_STAGING_QA` (ID 12237667442).
- **Despliegue:** [workflow 39362004479](https://github.com/facundocapello-blip/mambapalabra-staging/actions/runs/39362004479), SUCCESS. [Smoke real HTTPS 39362154834](https://github.com/facundocapello-blip/mambapalabra-staging/actions/runs/39362154834), SUCCESS: manifiesto de versión, carga de intro/definición, MP3 descargable y turno habilitado en Chromium/WebKit.
- **Online STAGING real:** [workflow 39362429990](https://github.com/facundocapello-blip/mambapalabra-staging/actions/runs/39362429990), SUCCESS en Chromium y WebKit con dos sesiones independientes y backend Supabase STAGING real: crear/unirse, puntaje sincronizado, error y cambio de turno, Pasapalabra del invitado y retorno. La duración del audio se simuló/aceleró para automatizar el recorrido.
- **Partida completa:** [workflow 39362806027](https://github.com/facundocapello-blip/mambapalabra-staging/actions/runs/39362806027), SUCCESS en Chromium y WebKit: 54 respuestas incorrectas, empate, muerte súbita, ganador y reinicio local. Audio acelerado/simulado, no escucha acústica.
- **Pendiente:** prueba de escucha y naturalidad de la locución Fish (especialmente pronunciación de nombres y letras) y micrófono real en Safari iPhone físico; la automatización no prueba el sonido real de parlantes ni reconocimiento de voz. Revancha online completa y desconexión/reconexión no están demostradas por estos workflows.
- **Protección:** producción https://facundocapello-blip.github.io/Mambapalabra/ no se actualizó por este flujo. Mantener RC3 en STAGING hasta la aceptación de voz y QA físico; no volver a generar 811 audios ni mezclar la rama del generador con `main`.

## Versión vigente: B1.13.1 (confirmación del usuario)

- El usuario confirmó el 2026-10-15 que **B1.13.1** es la versión aprobada y que **todas las pruebas y validaciones realizadas dieron OK**.
- El usuario también había informado que la última versión está publicada. Conservar esa confirmación: no reabrir validaciones ya aprobadas sin un fallo nuevo o un cambio que las afecte.
- La evidencia de ejecución de esas pruebas no está registrada en este repositorio; su resultado aquí es **informado por el usuario**, no una nueva ejecución independiente.
- Floot informó `published=true` para https://mambapalabra-b1-candidata.floot.app el 2026-10-15; el proyecto Floot se denomina «Mambapalabra B1.11», pero **ese nombre no prueba la versión del contenido servido**.
- La inspección independiente del identificador de build servido continúa sin documentarse. No contradecir por ese motivo la confirmación del usuario sobre la versión aprobada.

## Fuentes y versiones históricas

- Repositorio de continuidad: https://github.com/facundocapello-blip/Mambapalabra (rama main).
- `README.md` documenta la reconstrucción histórica de B1.11 desde un ZIP B1.10 más cinco reemplazos en ejecución; **B1.11 no debe tratarse como la última versión aprobada**.
- Repositorio de staging: https://github.com/facundocapello-blip/mambapalabra-staging. Su documentación histórica no certifica por sí sola el contenido de la publicación actual.
- La candidata B1.13.1 incluía 188 audios; preservar los audios, el banco, la voz del conductor y Supabase.

## Regla de continuidad

- Considerar **B1.13.1 la última versión aprobada según el usuario**.
- Antes de cualquier modificación, identificar el artefacto fuente exacto para no reconstruir desde B1.11 ni un ZIP viejo.
- Evitar reauditar pruebas ya aprobadas sin cambios; hacer diagnóstico y regresión acotados ante fallos nuevos.
- Conservar la publicación existente, un mecanismo de rollback y la separación entre staging y producción.
- Para cambios interactivos, entregar URL HTTPS publicada y distinguir validación automatizada de prueba en Safari físico.

## Iteración UX1 (2026-10-15) — NO publicada
- Base exacta localizada en Biblioteca: `Mambapalabra-B1.13.1-RC1.zip` (194 entradas/188 MP3; SHA256 ZIP `89fa0a512c42d66f58aa29e82e99ce40d62e315fbf314838fd54446e7ba70fcf`).
- Se creó la candidata `B1.13.1-RC1-UX1-STAGING`, con transiciones de voz más naturales e iPhone horizontal más legible. Se conservaron MP3, banco, reglas, configuración de Supabase y versión aprobada.
- Paquete completo guardado en Biblioteca `/Pasapalabra/Mambapalabra-B1.13.1-UX1-STAGING.zip`; parche y QA en PR borrador de staging https://github.com/facundocapello-blip/mambapalabra-staging/pull/1.
- Chromium automatizado (DOM inyectado): geometría de rosco y controles en 932×430, 667×375 y 430×932; correcta, incorrecta y Pasapalabra; tiempos de locución simulada 192 ms/130 ms con reloj detenido en READING: OK. MP3 reales, dos sesiones online y Safari físico UX1 no se revalidaron.
- **No se publicó UX1.** Floot gratuito no permite crear otro proyecto (límite 5). La rama de staging es borrador, sin merge ni despliegue. La URL de producción conserva su estado anterior.

## UX1 — STAGING publicado (2026-10-15)
- URL **separada y accesible por HTTPS**: https://mambapalabra-b1131-ux1-staging.floot.app
- Proyecto Floot aislado: `16cdf892-1fc3-479e-b954-ab1de1cba72d`. No se modificó el proyecto Floot B1.11 ni la versión estable.
- **Versión estable real** según el release oficial `b1.13.1`: https://facundocapello-blip.github.io/Mambapalabra/ (release https://github.com/facundocapello-blip/Mambapalabra/releases/tag/b1.13.1). Evitar identificar la URL Floot B1.11 histórica como producción actual.
- Staging carga el ZIP original exacto https://raw.githubusercontent.com/facundocapello-blip/Mambapalabra/8648098/Mambapalabra-B1.13.1-RC1.zip y el parche `qa/B1.13.1-RC1-UX1.patch` de https://github.com/facundocapello-blip/mambapalabra-staging/tree/ux/b1131-presenter-iphone . Antes de iniciar verifica SHA256 ZIP `89fa0a512c42d66f58aa29e82e99ce40d62e315fbf314838fd54446e7ba70fcf`, HTML original `465e091e3ae8d55416565fe8c7b81b30f9f937d00338d527b98fd991abf741c8` y HTML UX1 `39a5641ac0fc161ab5eb69ddfcfef462897a7898ab33b7667330627c662e58dd`.
- Dependencias `jszip` y `diff` instaladas. Paquete 188 MP3 original idéntico por hash; sin duplicar almacenamiento Floot. Configuración Supabase staging sin alteraciones.
- **Comprobado:** typecheck Floot limpio; despliegue Floot exitoso, HTTP 200 sobre URL de staging; en VM remoto applyPatch genera HTML con SHA esperado. Chromium local ejecutó lobby → partida y geometría del rosco (27 letras) en 932×430, 667×375 y 430×932; ancho sin desborde, controles 46px horizontal/50px vertical y cero errores de JavaScript tras adaptar el UUID al entorno local inseguro.
- **Pendiente exclusivo de UX1:** reproducción real desde web publicada en Safari físico, micrófono por voz, secuencia online con dos sesiones, fin de tiempo y muerte súbita; no afirmar que estas se reejecutaron. Navegador de preview Floot no disponible porque el usuario no tenía la pestaña abierta; se ensayó Chromium local.
- Floot rechazó duplicar el ZIP por cuota de almacenamiento de la cuenta: solución sin gastos usa descarga pública inmutable verificada por hash. Fuente aprobada y 188 audios sin cambios.

## Banco maestro en UX1 STAGING (2026-10-15)
- Comparado el archivo de Proyecto `MAMBAPALABRA - Banco de Definiciones`, pestaña `Banco`: 223 registros, **194 APROBADA**, 29 DESCARTADA. Las 194 aprobadas ya estaban en `QUESTION_POOL` con texto y reglas idénticas, pero 101 quedaban deshabilitadas por no tener dos MP3 grabados.
- Cambio mínimo: `ACTIVE_QUESTION_POOL=QUESTION_POOL.slice()`; quedan **305 definiciones disponibles** (194 aprobadas + 111 YouTube existentes), sin duplicados ni descartadas. Los 188 MP3 se conservan; 101 definiciones sin audio usan el mecanismo TTS local ya existente.
- Parche separado: https://github.com/facundocapello-blip/mambapalabra-staging/blob/ux/b1131-presenter-iphone/qa/B1.13.1-UX1-BANCO194.patch
- Pruebas: igualdad 194/194 contra Excel, cero duplicados, JavaScript compilado en VM, hash SHA256 HTML `e9f03e8c0fb62d4cec6867efc2c4e4e03d8b8f1edf8cb7d5027794d1044d6546`, typecheck limpio. Navegador Playwright localhost bloqueado por el entorno; Safari iPhone/voz de esta actualización pendiente de comprobación directa.
- Publicación confirmada por Floot (URL HTTPS y HTTP 200): https://mambapalabra-b1131-ux1-staging.floot.app/ . Checkpoint anterior UX1 `2370d6a8-17b0-4935-ad5f-b8f53e671631`; checkpoint nueva versión `6accf0c4-531f-4d40-a1f7-59454a90036f`.
- **No se modificó producción:** https://facundocapello-blip.github.io/Mambapalabra/
