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
