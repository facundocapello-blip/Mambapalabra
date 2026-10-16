# Estado de Mambapalabra

Actualizado: 2026-10-15.

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
