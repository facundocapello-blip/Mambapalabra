# Mambapalabra — reglas para trabajar acá

Leer `README.md` primero. Reglas específicas de este repo:

## Publicación
- La rama publicada es **`production`**. `main` no tiene el juego: no publicar desde ahí.
- Un cambio chico por commit, mensaje `Produccion: ...`.
- Después de pushear: esperar el deploy y verificar en vivo. "Pusheado" no es "publicado".
- Si el cambio se ve en pantalla, comprobar que el lobby muestre la versión correcta.

## Audio y assets
- No renombrar, mover ni recomprimir nada dentro de `fish-bank/`, `fish-audio/` o
  `new-audio/`: el mapa de archivos está hardcodeado en `index.html` y se rompe en silencio.
- Si se cambia un asset, actualizar su hash en `ASSETS_SHA256.json`.
- El audio de iOS se desbloquea con el primer toque ("Jugar local"). Si algo toca esa cadena,
  probarlo en un iPhone real, no solo en el navegador de escritorio.

## Datos del juego
- Hay **522 definiciones**, ~15 por letra. El rosco tiene **25 letras: K y W están fuera**
  (decisión de Facu, 16/11/2026). Sus definiciones siguen en el banco pero no se sortean.
  Para volver a incluirlas, restaurar "K" y "W" en `LETTERS` de `index.html`.
- La rotación por letra se guarda en `localStorage` (`mamba:questionRotation:v2`). Si el
  estado no coincide con el pool, se resetea solo.

## Lo que no se toca
- `main` y la rama `qa/b112-guest-voice-handoff` (la usa el workflow de staging).
- La copia archivada del RC6 (`mambapalabra-staging`, tag `rc6-2026-10-21`).
- El modo Online: activo (nov 2026) contra el Supabase MAMBAPALABRA-STAGING (ref qbzrqinnhrgeqvgtifrt, función multiplayer-room). Si responde 503/521, el proyecto está pausado: restaurarlo en Supabase.

## Verificación mínima antes de dar algo por cerrado
1. HTTP 200 en la URL con `?v=2`.
2. Lobby con la versión visible.
3. "Jugar local" arranca y suena.
4. Consola sin errores.

---

## Skills y plugins recomendados en DeepSeek Harness

Mapa curado para este proyecto. Las skills se cargan con la herramienta `skill`;
los plugins ya están instalados en el perfil de DSH.

**Skills**

- `impeccable` — Cualquier cambio de UI: rosco, fichas, contraste, foco.
- `office` — Documentar en ESTADO.md o generar material de presentación.

**Plugins**

- **plugin-dock (Hub)** — Escribís el pedido en el composer y el Hub propone con qué IA.
- **subagent-claude-code** — Delegar refactors o auditorías pesadas a Claude Code.
- **better-sidebar** — Archivos, Git y terminal junto al chat.

**Comandos**

`/arrancar` · `/estado` · `/revisar` · `/cerrar`
