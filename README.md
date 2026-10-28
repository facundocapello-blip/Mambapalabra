# MAMBAPALABRA

## Producción (vigente desde 2026-10-28)

El juego publicado vive en la branch **`production`** de este repositorio, no en `main`.
GitHub Pages sirve esa branch desde la raíz:

- URL: https://facundocapello-blip.github.io/Mambapalabra/
- Versión: **B1.13.1-UX1-FISH398-VOZ-UNICA-RC6** (398 definiciones + 398 respuestas con voz Fish)
- Tag: `production-rc6`
- Branch espejo con el build archivado: `mambapalabra-staging`, branch `release/rc6-build`

`main` queda solo con documentación. Para cambiar el juego hay que trabajar sobre
`production`. El modo **Online está fuera de servicio**: el proyecto Supabase
`qbzrqinnhrgeqvgtifrt` ya no existe y la sección quedó oculta.

---

# Documentación histórica de estabilización B1.11

> **Estado vigente:** el usuario confirmó B1.13.1 como versión aprobada, con pruebas y validaciones OK (15/10/2026). Este README describe solamente la base histórica B1.11; ver [PROJECT_STATUS.md](PROJECT_STATUS.md). No usar B1.11 como fuente para cambios nuevos.

**Referencia de publicación:** https://mambapalabra-b1-candidata.floot.app/

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
