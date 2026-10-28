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
- Hay **398 definiciones**, ~15 por letra. Las flojas son K (6) y W (7): se repiten cada
  pocas partidas y no es un bug.
- La rotación por letra se guarda en `localStorage` (`mamba:questionRotation:v2`). Si el
  estado no coincide con el pool, se resetea solo.

## Lo que no se toca
- `main` y la rama `qa/b112-guest-voice-handoff` (la usa el workflow de staging).
- La copia archivada del RC6 (`mambapalabra-staging`, tag `rc6-2026-10-21`).
- El modo Online: está deshabilitado a propósito.

## Verificación mínima antes de dar algo por cerrado
1. HTTP 200 en la URL con `?v=2`.
2. Lobby con la versión visible.
3. "Jugar local" arranca y suena.
4. Consola sin errores.
