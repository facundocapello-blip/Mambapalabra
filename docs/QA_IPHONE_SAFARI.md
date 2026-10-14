# QA Gate — Mambapalabra

Una versión candidata NO se entrega para prueba física hasta cumplir este gate.

## Flujo obligatorio

1. Código versionado en GitHub con identificador de versión/candidata.
2. Pruebas automáticas aplicables ejecutadas y resultado registrado.
3. Candidata desplegada en STAGING web.
4. URL HTTPS de STAGING confirmada y accesible desde Safari en iPhone.
5. Smoke test web sobre la misma build desplegada.
6. Recién entonces se entrega a Facu la URL para prueba física en iPhone.
7. La prueba física cubre especialmente audio, micrófono, permisos, gestos/touch, fullscreen, cambio de turno y multiplayer.
8. Si falla un punto, la candidata vuelve a desarrollo/QA y NO se promueve a producción.

## Evidencia mínima de entrega

- Versión:
- Commit SHA:
- Rama:
- URL STAGING:
- Pruebas automáticas:
- Smoke test Safari/iPhone-compatible:
- Pendientes conocidos:
- Estado: LISTA PARA PRUEBA IPHONE / BLOQUEADA

## Regla de producción

STAGING -> validación -> producción. Nunca desarrollo o QA directo a producción.

La prueba física del usuario no reemplaza el QA previo: cuando recibe una candidata, ya debe existir una URL funcional y probada para Safari/iPhone.
