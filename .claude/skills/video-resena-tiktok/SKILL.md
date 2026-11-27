---
name: video-resena-tiktok
description: Produce el VIDEO terminado de una reseña de cine para TikTok (mp4 vertical 1080x1920) con la voz de Alex en español latino, música y animación 3D hecha con Remotion. Parte de un guion visual (.txt) y un paquete de reseña (.md) creados con la skill resenas-cine-tiktok. Usar cuando el usuario adjunte esos archivos o pida «crea el video», «haz el video», «video de la reseña» o similar.
---

# Video de reseña TikTok (voz de Alex + música + 3D con Remotion)

Convierte un **guion visual** y un **paquete de reseña** en un `.mp4` listo para subir.
Une dos mundos:

- **Audio** (igual que la versión anterior): voz Kokoro **Alex** (`em_alex`, `es-419`) y música sintetizada, mezcladas con ffmpeg a −14 LUFS.
- **Imagen** (nuevo): **Remotion + Three.js**. Sala de cine en 3D real, cámara que vuela hacia la pantalla y entra en la historia, escenas 3D animadas por fotograma y textos animados.

Trabaja de forma directa: no preguntes opciones que ya están definidas aquí. Avanza paso a paso y verifica.
Explica al usuario, en simple, cada paso que haces.

## Entradas

- Guion visual `.txt`: escenas, tiempos estimados, sub-momentos a/b/c, transiciones, escalas, textos en pantalla.
- Paquete `.md`: guion de voz, título en Chile y original, textos de apoyo, música (estilo, tempo, tramos).
- Si faltan, ofrecer crearlos con la skill `resenas-cine-tiktok` (investigación y guiones).

## Salida

- `<repo>/estudio-resenas/out/<slug>-tiktok.mp4` (H.264 CRF 21, máx. 9 Mb/s, AAC 192k, −14 LUFS)
- `<repo>/estudio-resenas/public/<slug>/voz-<slug>.mp3`
- El código de la reseña en `estudio-resenas/src/resenas/<slug>/`

## Archivos de esta skill

- `plantilla-remotion/`: proyecto Remotion base, con estos archivos:
  - `src/resena/Resena.tsx`: estructura fija del canal. Lee `segments.json`, entra a la pantalla, muestra la historia, sale a la sala, pone la tarjeta del título y el audio.
  - `src/resena/Sala3D.tsx`: la sala 3D en dos capas. **Fondo**: paredes, telones y pantalla. **Frente**: butacas carmesí, el **Espectador** de espaldas con capucha mostaza y el haz del proyector arriba a la izquierda. La historia se dibuja entre ambas capas.
  - `src/resena/camara.ts`: recorrido de la cámara y cálculo de dónde cae la pantalla en el video. En `p = 1` la pantalla llena el alto exacto del cuadro, así que el paso sala → historia no tiene salto.
  - `src/resena/TarjetaTitulo.tsx`: tarjeta del título (regla 7.8).
  - `src/resena/TextosApoyo.tsx`: `Banner`, `Sello` y `Numero` (formatos 7.8).
  - `src/resenas/ejemplo-noche-cero/`: ejemplo completo de escena de historia 3D (ciudad nocturna, nieve y camioneta, con cámara por keyframes).
- `plantilla-audio/`:
  - `voice.py`: voz de Alex. Genera `voice.wav` y `segments.json`.
  - `music.py`: synth oscuro por tramos.
  - `music_ambiental.py`: pads suaves.
  - `voice_ejemplo_demo.py`: versión corta de ejemplo.

## Preparar el entorno (una vez por sesión)

1. **Proyecto**: si no existe `<repo>/estudio-resenas`, copiar `plantilla-remotion/` ahí y correr `npm i`.
2. **Voz**: deben existir `~/kokoro/kokoro-q8.onnx` y `~/kokoro/voices_es.npz`. Si faltan:
   ```
   pip install kokoro-onnx soundfile
   mkdir -p ~/kokoro && cd ~/kokoro
   B=https://huggingface.co/onnx-community/Kokoro-82M-v1.0-ONNX/resolve/main
   curl -sSfL -o kokoro-q8.onnx $B/onnx/model_quantized.onnx
   curl -sSfL -o em_alex.bin $B/voices/em_alex.bin
   python3 -c "import numpy as np; np.savez('voices_es.npz', em_alex=np.fromfile('em_alex.bin','float32').reshape(-1,1,256))"
   ```
   Si la red bloquea Hugging Face, pedir acceso a la red. **No** cambiar de voz.
3. **Navegador**: `remotion.config.ts` usa `/opt/pw-browsers/chromium` si existe, porque la nube no puede descargar Chrome. No correr `playwright install`.
4. Requisitos: Node 20+ y ffmpeg. Python con `numpy`, `soundfile` y `kokoro-onnx`.
5. Para el 3D, seguir las skills de Remotion del repo (`remotion-best-practices`, `remotion-markup` y su `3d.md`). Las animaciones solo se mueven con `useCurrentFrame()`. Prohibido `useFrame()`.

## Flujo (en este orden)

1. **Carpeta**: `mkdir -p public/<slug> src/resenas/<slug>`. Copiar `plantilla-audio/{voice.py,music.py o music_ambiental.py}` a una carpeta de trabajo, como `estudio-resenas/audio/<slug>/`.
2. **Voz primero** (`voice.py`):
   - Lista `P`: una frase por cada línea `VOZ:` del guion visual. La frase final se separa en dos: «Se trata de …» y «Si fueras tú…».
   - Ajustar `TITLE_IDX` (o el índice de la pausa corta) para la frase «Se trata de».
   - `FIX`: títulos en inglés como los diría un hablante latino. Por ejemplo, «The Discovery» se escribe «De Discóveri».
   - Velocidad 1.05, pausas de 0,18 s, ningún silencio mayor a 0,4 s. Falla si aparece «θ».
   - Mover `voice.wav` y `segments.json` a `public/<slug>/`. **La imagen se ajusta a estos tiempos, nunca al revés.**
3. **Música**: adaptar `music.py` o `music_ambiental.py` (100 BPM, tramos ligados a los `start` del paquete). Mover `music.wav` a `public/<slug>/`.
4. **Escenas** en `src/resenas/<slug>/`:
   - `Historia.tsx`: toda la historia como **escenas 3D** (`<ThreeCanvas>` envuelto en `<AbsoluteFill>`). El tiempo es el segundo absoluto del video (`frame / fps`).
     - Leer los inicios de frase desde `segmentos` (props) o copiarlos de `segments.json`.
     - Cada escena empieza con su frase.
     - Sub-momentos a/b/c = movimientos de cámara, elementos nuevos o avance de la acción, cada 2 a 3 s, con keyframes de `interpolate`.
     - Escenas distintas: `<Sequence from={...} layout="none">`, o cambiar el contenido según `t`.
     - Transiciones: la cámara empuja hacia el objeto que conecta las escenas (puerta, ventana, vehículo).
     - El Espectador aparece de espaldas en 2 o 3 escenas intermedias. Reutilizar la geometría de `Sala3D.tsx` o la sala completa.
   - `Video.tsx`: `<ResenaBase {...props} historia={<Historia />} />`.
     - La escena 1 (entrar a la pantalla entre 0,3 y 3,7 s) y la última (salir a la sala en «Se trata de» y mostrar la tarjeta) ya las hace `ResenaBase`.
     - Mientras la cámara está en la sala, la historia se ve dentro de la pantalla.
   - Textos de apoyo: **solo** los del paquete, con `Banner`, `Sello` o `Numero` dentro de `<Sequence>`. Nunca en el 20 % inferior ni sobre los botones de la derecha.
   - Registrar la `<Composition>` en `src/Root.tsx`, copiando el bloque de ejemplo: `calculateMetadata={calcularResena}`, `carpeta`, `tituloChile` y `subtitulo` (título original y año, o solo el año).
5. **Verificar antes de renderizar todo**:
   - Renderizar 2 o 3 fotogramas por escena: `npx remotion still <Id> hoja/fNN.png --frame=NN --scale=0.4`.
   - Unirlos con `ffmpeg ... -filter_complex hstack=N` y mirar la hoja.
   - Corregir caras tapadas, objetos fuera de cuadro, escala, textos ilegibles y reglas de imagen.
6. **Render completo**: es lento por el 3D (unos 15 a 25 min por minuto de video en la nube). Correrlo **en segundo plano** y siempre con `--concurrency=1`: con varias pestañas a la vez el 3D sale corrupto, repetido en mosaico.
   ```
   npx remotion render <Id> out/<slug>-video.mp4 --muted --concurrency=1
   cd public/<slug>
   ffmpeg -i ../../out/<slug>-video.mp4 -i voice.wav -i music.wav -filter_complex "[1:a]aresample=44100,aformat=channel_layouts=stereo,apad=pad_dur=2,asplit=2[vo][sc];[2:a]aformat=channel_layouts=stereo,volume=0.22[m];[m][sc]sidechaincompress=threshold=0.05:ratio=4:attack=20:release=300[md];[vo][md]amix=inputs=2:duration=longest:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]" -map 0:v -map "[a]" -c:v libx264 -preset medium -crf 21 -maxrate 9M -bufsize 18M -pix_fmt yuv420p -c:a aac -b:a 192k -ar 44100 -shortest -movflags +faststart ../../out/<slug>-tiktok.mp4
   ```
   Después, exportar la voz a mp3 (`voz-<slug>.mp3`) y borrar `out/<slug>-video.mp4`.
7. **Control final**:
   - Duración de 61 s o más (salvo demos).
   - Sonoridad cercana a −14 LUFS (`ffmpeg -af ebur128`).
   - Revisar 4 fotogramas del mp4 final.
8. **Entregar**:
   - Enviar el mp4 y el mp3 al usuario.
   - Hacer commit y push a la rama de trabajo, sin `node_modules` ni `out`.
   - Resumen breve: duración, voz, música, qué se cumplió del guion y qué falta hacer en la app (etiqueta IA, plataforma, etc.).

## Identidad visual (ya implementada en la plantilla)

- **Sala**:
  - butacas de terciopelo carmesí, pocas y grandes en primer plano
  - bruma verde azulada con acentos mostaza y carmesí
  - telones rojos
  - proyector arriba a la izquierda, con haz y polvo
  - pantalla grande al frente
- **El Espectador**:
  - hombre adulto, pelo oscuro corto con costados rebajados, capucha mostaza
  - siempre de espaldas
  - hombros de unas 0,8 veces el ancho de su butaca
- **Tarjeta del título**:
  - banda oscura semitransparente arriba, en Montserrat
  - título en Chile en grande; título original y año en pequeño
  - entra con «Se trata de» y se mantiene hasta el final

## Reglas de imagen (siempre)

- Solo adultos con proporciones adultas. Sin caras reales ni parecidos con actores. Sin logos ni símbolos de sagas. Sin texto legible dentro de la imagen 3D: todo texto va como capa de Remotion.
- Ningún arma apuntando a personas: al suelo, a la pared o fuera de cuadro.
- Muertes, violencia y criaturas: con siluetas, a media distancia, sin sangre ni cuerpos expuestos. Nada del desenlace.
- Escala coherente con la sección 7.7 de `resenas-cine-tiktok`. Por ejemplo, un auto mide unas 0,83 veces la altura de una persona.

## Qué NO hacer

- No cambiar la voz (Alex, `es-419`) sin que el usuario lo pida.
- No inventar textos en pantalla extra.
- No alargar con silencios para llegar a la duración.
- No usar animaciones CSS ni `useFrame()`: todo se mueve con `useCurrentFrame()`.
- No usar material de la película: ni escenas, ni pósters, ni música.
