# MAMBAPALABRA — Codex / estabilización B1.11

**Versión publicada:** B1.11 · https://mambapalabra-b1-candidata.floot.app/

**No modificar producción.** Este repositorio fue preparado para trabajar en una rama de estabilización, manteniendo intacto el juego publicado.

## Base exacta

El juego publicado carga un ZIP histórico B1.10 y le aplica **cinco reemplazos en tiempo de ejecución** desde `pages/_index.tsx` de Floot. Por lo tanto, **el ZIP B1.10 sin compilar NO es B1.11**.

**ZIP de origen (188 audios MP3 incluidos):**
https://mambapalabra-b1-candidata.floot.app/_cdn/static/b280c36c-b922-47d1-9a6d-ef7327c9b517-mambapalabra-b1-10-visual.zip

El archivo `tools/build_b111.py` de la rama de estabilización reproduce esos cambios y genera un HTML B1.11 editable y un ZIP autocontenido. No usar otras versiones como fuente.

## Trabajo inicial para Codex

1. Descargar el ZIP exacto y consolidar B1.11, verificando sus anclas y 188 MP3.
2. Verificar inicio local, lectura de definición, respuesta correcta, incorrecta, Pasapalabra y relojes ANSWERING.
3. Identificar y corregir el problema de **K y W deshabilitadas**, sin cambiar preguntas aprobadas sin autorización.
4. Impedir que un fallo de MP3/TTS bloquee indefinidamente el turno.
5. Comprobar muerte súbita, fin y reinicio.
6. Preparar pruebas online con dos sesiones aisladas. El proyecto Supabase asociado figuró **INACTIVE** el 12/10/2026; no modificar producción sin plan.
7. Automatizar pruebas de regresión con Playwright Chromium y WebKit. Safari físico requiere validación diferenciada.

**Entrega:** PR con causa, corrección mínima, pruebas ejecutadas y resultados. Sin despliegue.

**Importante:** Este repositorio es público. No añadir credenciales privadas ni service_role keys.
