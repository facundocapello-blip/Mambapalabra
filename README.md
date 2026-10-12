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

## Candidata de estabilización (sin despliegue)

`game/index.html` contiene el juego completo con correcciones de audio, cobertura
K/W y temporizadores. `game/B1_11_CONSOLIDADA.html` sigue siendo la referencia
B1.11 exacta; el constructor histórico no sobrescribe la candidata.
Los 188 MP3, el logo y el manifest del ZIP original se conservan sin cambios.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m playwright install --with-deps chromium webkit
python3 -m http.server 8000 --bind 127.0.0.1 --directory game
```

Servir siempre `game/` como raíz HTTP para conservar `/new-audio/` y `/_cdn/`.
El juego local no requiere claves ni Supabase; online conserva la integración
existente, pero requiere validar un backend de staging autorizado.

```bash
python3 -m unittest discover -s tests -p 'test_build_b111.py' -v
python3 -m unittest discover -s tests -p 'test_candidate_assets.py' -v
MAMBA_BROWSER=chromium MAMBA_CHROMIUM='' .venv/bin/python tests/test_game_browser.py -v
MAMBA_BROWSER=webkit .venv/bin/python tests/test_game_browser.py -v
python3 tools/package_candidate.py
```

La CI ejecuta ambos navegadores y conserva capturas y el ZIP candidato como
artefactos. No publica ni invoca servicios de producción.
Ver [diagnóstico, alcance y resultados](docs/estabilizacion-b111.md).
