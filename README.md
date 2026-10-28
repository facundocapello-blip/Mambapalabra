# Mambapalabra

Juego del rosco para dos jugadores, en un solo dispositivo. 398 definiciones con voz
generada (Fish Audio). Sin backend: todo corre en el navegador.

**En vivo:** https://facundocapello-blip.github.io/Mambapalabra/

## Cómo se publica

GitHub Pages sirve la rama **`production`**. No hay build: se publica lo que está en la rama.

```powershell
git checkout production
git add -A
git commit -m "Produccion: ..."
git push origin production
```

El deploy tarda entre 30 y 60 segundos. Verificar siempre en vivo:

```powershell
(Invoke-WebRequest "https://facundocapello-blip.github.io/Mambapalabra/?v=2" -UseBasicParsing).StatusCode
```

## Estructura

| Archivo | Qué es |
|---|---|
| `index.html` | El juego entero: HTML, CSS y JS en un solo archivo (~380 KB). |
| `fish-bank/` | 398 clips de pregunta (`q0001.mp3`…) y 398 de respuesta (`w0001.mp3`…). |
| `fish-audio/` | Clips fijos: intros, correcto, incorrecto, muerte súbita. |
| `new-audio/` | Voz anterior y clips de desbloqueo de audio. |
| `_cdn/static/` | Logo. |
| `icon-192.png`, `icon-512.png`, `apple-touch-icon.png` | Íconos de app. |
| `manifest.webmanifest` | Manifest PWA. |
| `*_RELEASE.json` | Metadata de cada banco de audio (versión y alcance). |
| `ASSETS_SHA256.json` | Hashes de los assets. |

## Lo que no hay que romper

- Las carpetas de audio **no se renombran ni se mueven**: el mapa de clips está escrito
  adentro de `index.html`.
- `main` **no tiene el juego**. La copia archivada del build RC6 vive en el repo
  `mambapalabra-staging`, rama `release/rc6-build`, tag `rc6-2026-10-21`.
- El modo Online está deshabilitado: apuntaba a un proyecto Supabase que ya no existe.

## Cómo se verifica

1. El lobby carga y el subtítulo dice la versión (`B1.13.1-UX1 · RC6`).
2. "Jugar local" arranca la partida y suena la voz.
3. Consola sin errores.
4. Los assets clave responden 200.
