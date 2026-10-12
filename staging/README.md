# Staging online B1.11: separado de producción

La candidata HTTPS publicada inicialmente es sólo local: no carga el SDK ni
contiene la URL o la clave del Supabase de producción. Los botones online están
desactivados hasta que exista un proyecto de staging autorizado.

No se ha creado ni contratado un proyecto Supabase. El backend preparado es una
implementación nueva del contrato del cliente, no una copia certificada de las
Edge Functions/RPC de producción. No se extraen datos ni claves de producción.

## Validación local sin contratar servicios

El esquema está en `supabase/migrations/202610120001_rooms.sql` y el adaptador en
`supabase/functions/multiplayer-room/index.ts`. PostgreSQL mantiene transacciones
de ingreso y sincronización, tokens privados con hash, versiones, idempotencia,
titular del turno y expiración de 2 horas. Hay un máximo de 100 salas de prueba.
Anon puede leer estado público para Realtime, pero no escribir ni leer tokens.

Crear exclusivamente este contenedor de pruebas, sin puertos publicados:

```bash
docker run --rm -d --name mamba-b111-staging-pg \
  -e POSTGRES_HOST_AUTH_METHOD=trust \
  postgres@sha256:2d2b8998d31037bf721cfdf764d76ba74171b4fab3431b7f72c27c56ddbdf9e3
```

Esperar `docker exec mamba-b111-staging-pg pg_isready -U postgres`. En este
PostgreSQL vacío, crear roles de fixture `anon`, `authenticated`, `service_role`
y aplicar el SQL. Estos roles ya existen en un Supabase de staging real.

```bash
docker exec mamba-b111-staging-pg psql -U postgres -c \
  'CREATE ROLE anon; CREATE ROLE authenticated; CREATE ROLE service_role;'
docker exec -i mamba-b111-staging-pg psql -U postgres -v ON_ERROR_STOP=1 \
  < staging/supabase/migrations/202610120001_rooms.sql
python3 tests/test_staging_pg.py -v
npx deno test --allow-env staging/supabase/functions/multiplayer-room/index_test.ts
docker stop mamba-b111-staging-pg
```

El test de dos contextos de navegador ejecuta el protocolo contra PostgreSQL
real mediante un adaptador HTTP local. Los tests Edge validan CORS, métodos,
tamaño, envelope RPC y sanitización de errores. No llaman a Supabase real.
Esto no certifica todavía la plataforma desplegada, Realtime o Safari físico.

## Activación futura de staging

1. Usar un proyecto Supabase nuevo o existente separado, sólo tras confirmar su
   plan gratuito, cuotas disponibles y ausencia de cargos automáticos. No crear
   infraestructura ni usar un plan pago desde estos scripts.
2. Verificar el identificador del proyecto: **prohibido**
   `mcrnstwmubtiiacyiaeu`. Aplicar el SQL sólo en el staging vacío; no en producción.
3. Desplegar la función `multiplayer-room` de esta carpeta, con el `config.toml`
   de staging. `SUPABASE_URL` y `SUPABASE_SERVICE_ROLE_KEY` deben ser los secretos
   server-side del staging; no incluirlos en HTML, repositorios o chat.
   Configurar `MAMBA_CANDIDATE_ORIGIN=https://facundocapello-blip.github.io`.
4. Usar exclusivamente una clave pública `sb_publishable_...` de staging para
   exportar la web con `tools/export_https_candidate.py --staging-url ...
   --staging-key-file ...`. El exportador rechaza el identificador de producción
   y las claves privadas. No modifica el código ni las preguntas originales.
5. Publicar esa exportación sólo en `candidata-https-b111`, sin merge, y verificar
   por red que todas las llamadas van al proyecto de staging autorizado.

## Dos jugadores por HTTPS

- Dos navegadores/contextos con almacenamiento aislado y nombres de prueba:
  anfitrión crea sala, invitado entra por enlace/código; un tercer ingreso recibe
  `room_full` y no desplaza al invitado.
- Inicio y preguntas sincronizadas; sólo el titular puede responder/pasar.
  Reloj detenido en READING/VALIDATING y corriendo sólo en ANSWERING del titular.
- Respuesta correcta/incorrecta, Pasapalabra, handoff y pendientes; no duplicar
  puntaje en retries de una operación ni aceptar versiones obsoletas.
- Cortar conexión y refrescar ambos clientes; probar recuperación explícita,
  token inválido, expiración y reconexión con la última versión confirmada.
- Fin, empate, muerte súbita y revancha. Revisar logs sin volcar tokens.
- Confirmar en el inspector que no hay solicitudes a Supabase/Floot de producción.

Pendiente para ejecutar este recorrido real: proyecto de staging gratuito,
despliegue de función/SQL y clave pública de ese proyecto. No se han contratado
recursos ni se han modificado servicios de producción.
