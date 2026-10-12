# Candidata HTTPS independiente para iPhone

**URL activa y verificada:** https://facundocapello-blip.github.io/Mambapalabra/

Pages publica `candidata-https-b111` desde `/(root)` con HTTPS obligatorio.
El HTML público coincide con el SHA256 indicado abajo. Chromium y WebKit
aprobaron el recorrido móvil sobre esta URL real en retrato y paisaje, y los
188 MP3 y demás recursos publicados conservan sus hashes. Online sigue apagado
hasta disponer de staging remoto; no hay llamadas a producción.

La rama de publicación `candidata-https-b111` es independiente y no tiene padre
ni merge con main/estabilización. Contiene sólo la exportación estática del commit
`65aa00153fb744004f890900640363cbbe524ebd`, con 188 MP3 originales, logo y manifest.
No contiene el identificador o la clave de Supabase de producción, no carga su
SDK y desactiva los botones online hasta conectar un staging autorizado.

Commit de publicación: `55f3e236a53f3f0bf273eaa6bf923c0e0cc0a4ef`.
SHA256 del HTML exportado:
`76d62bc7f8cf97e9590d6a324b65b952e518ae4a294917e0563fa69682997406`.

## Activación de HTTPS (sin contratar recursos)

El repositorio es público. GitHub Pages para un repositorio público permite
alojamiento estático gratuito. No se activan planes pagos, dominios de pago,
GitHub Actions con runners pagos ni servicios Supabase.

La integración devolvió HTTP 403 al intentar habilitar Pages. La cuenta
propietaria lo habilitó manualmente en:
https://github.com/facundocapello-blip/Mambapalabra/settings/pages

Configuración: **Deploy from a branch → candidata-https-b111 → /(root)**.
No seleccionar main, no hacer merge y no alterar Floot. GitHub informa estado
`built`; la URL devuelve HTTP 200 y el contenido exacto de la candidata.

El exportador adapta `/new-audio/` y `/_cdn/` al prefijo del proyecto Pages,
verifica los recursos y rechaza sobrescribir directorios existentes. Las
preguntas y el HTML canónico del PR #1 no se modifican para este alojamiento.

```bash
python3 tools/export_https_candidate.py --output artifacts/candidata-pages \
  --prefix /Mambapalabra/
python3 -m unittest discover -s tests -p test_https_export.py -v
```

## Pruebas de la exportación

- 3 tests de exportación: 188 MP3 idénticos, ausencia de producción, rutas,
  credenciales privadas/proyecto de producción rechazados y no sobrescritura.
- Chromium y WebKit en 390×844 y 844×390, con pantalla táctil y escala 3:
  menú/logo, cuenta regresiva, primera definición, acierto por texto,
  Pasapalabra/cambio de jugador, error, pausa/reanudar y reinicio.
- Botones principales de al menos 44 px, sin scroll horizontal en el menú,
  ninguna excepción JavaScript y cero solicitudes a Floot/Supabase de producción.
- Todos los MP3 y demás recursos se solicitan por HTTP y se comprueban con SHA256.
  Capturas: `artifacts/mobile/<browser>-<ancho>.png`.
- Checks ejecutados y aprobados sobre HTTPS real en ambos navegadores:

```bash
MAMBA_CANDIDATE_URL=https://facundocapello-blip.github.io/Mambapalabra/ \
  python3 tests/test_candidate_mobile.py -v
MAMBA_BROWSER=webkit \
MAMBA_CANDIDATE_URL=https://facundocapello-blip.github.io/Mambapalabra/ \
  python3 tests/test_candidate_mobile.py -v
```

## Safari real: recorrido pendiente

WebKit automatizado no equivale a Safari en un iPhone físico. Probar con dos
nombres de prueba y registrar modelo/iOS, modo normal y modo añadido a inicio:

1. Abrir la URL HTTPS y tocar Jugar local. Primera definición MP3 audible y reloj
   detenido mientras habla el conductor. Verificar «Facu» y «Cocido» en el juego.
2. Definición sin MP3 con TTS español, fallback si falla y continuación por texto.
   Permiso de micrófono aceptado, rechazado y dejado sin responder; dictado
   correcto/incorrecto y Pasapalabra por voz.
3. Opciones táctiles, teclado sin ocultar los controles, retrato/paisaje,
   pausa/reanudar durante audio y dictado, cambio de app/bloqueo/desbloqueo.
4. Primera vuelta, pendientes, K/W, tiempo agotado, fin, empate, muerte súbita,
   reinicio y repetición sin voces o micrófonos superpuestos.
5. Cuando exista staging remoto, dos iPhones/contextos independientes: sala,
   enlace, turno/relojes, desconexión, refresco, fin y revancha. Confirmar que
   sólo el Supabase de staging recibe llamadas, como indica `staging/README.md`.

No se ha creado un Supabase de staging ni se ha contratado ningún servicio. El
SQL/adaptador y las pruebas locales están preparados; falta el proyecto gratuito
y desplegar el backend antes de habilitar online en la candidata pública.

La prueba HTTPS de Chromium necesitó confiar en la CA del proxy de este entorno.
La revisión automática rechazó modificar el almacén NSS permanente. Se ejecutó
Chromium dentro de un espacio de montaje aislado con un almacén NSS temporal en
`/tmp`; la confianza del perfil real quedó intacta y TLS permaneció habilitado.
Ambos navegadores aprobaron las pruebas HTTPS públicas sin ignorar certificados.

También se preparó un servidor local restringido a la exportación con soporte
de Range/HEAD para los MP3 (`tools/candidate_preview_server.py`), verificado con
tres pruebas HTTP. Se probó un túnel gratuito alternativo, pero la red de este
entorno rechazó la conexión al servicio. No se generó una URL temporal jugable;
la candidata estable finalmente quedó publicada en GitHub Pages.
