---
name: video-resena-tiktok
description: Produce el VIDEO terminado (mp4 vertical 1080x1920 con voz de Alex en español latino, música y animación) de una reseña de cine para TikTok a partir de un guion visual (.txt) y un paquete de reseña (.md). Usar cuando el usuario adjunte esos archivos y pida «crea el video», «haz el video» o similar.
---

# Video de reseña TikTok (voz + música + animación)

Convierte un **guion visual** y un **paquete de reseña** en un `.mp4` listo para subir.
Trabaja de forma directa: no preguntes opciones que ya están definidas aquí; avanza paso a paso y verifica.

## Entradas
- Guion visual `.txt`: escenas, tiempos estimados, sub-momentos a/b/c, transiciones, escalas, reglas de imagen, textos en pantalla.
- Paquete `.md`: guion de voz completo, texto en pantalla (título, textos de apoyo), música (estilo, BPM, tramos).

## Salida (en `<repo>/<slug-pelicula>/`)
- `<slug>-tiktok.mp4` (H.264 CRF 21, máx. 9 Mb/s, AAC 192k, −14 LUFS)
- `voz-<slug>.mp3`
- `src/` con los scripts usados (copias adaptadas de `plantilla/`)

## Requisitos del entorno
- Voz: `~/kokoro/kokoro-q8.onnx` y `~/kokoro/voices_es.npz` (los instala el script de preparación del entorno).
  Si faltan: `pip install kokoro-onnx soundfile` y descargar de
  `https://huggingface.co/onnx-community/Kokoro-82M-v1.0-ONNX/resolve/main/` → `onnx/model_quantized.onnx` (guardar como `kokoro-q8.onnx`) y `voices/em_alex.bin`;
  convertir: `np.savez('voices_es.npz', em_alex=np.fromfile('em_alex.bin','float32').reshape(-1,1,256))`.
  Si la red bloquea Hugging Face, pedir acceso a la red; **no** cambiar de voz.
- `ffmpeg`, Python con `numpy`, `Pillow`.

## Flujo (en este orden)

1. **Preparar carpeta**: `mkdir -p <slug>/src` y copiar `plantilla/{lib.py,render.py,voice.py,music.py}`.
2. **Voz primero** (`voice.py`):
   - Reemplazar la lista `P` con el guion de voz dividido en frases: **una frase por cada línea `VOZ:` del guion visual**;
     separar la frase final en dos: «Se trata de …» (marca la tarjeta del título) y la pregunta «Si fueras tú…».
   - Ajustar `FIX` para que los títulos en inglés suenen como los diría un hablante latino (ej.: «The Discovery» → «De Discóveri», «Resident Evil» → «Résident Ívil»).
   - Voz **Alex** (`em_alex`), fonemas `es-419`, velocidad 1.05 (la plantilla ya lo hace y falla si aparece «θ»).
   - Pausas: 0,18 s entre frases, 0,15 s antes de «Se trata de»; ningún silencio > 0,4 s (comprobarlo).
   - Genera `voice.wav` y `segments.json` (tiempos reales). **La imagen se ajusta a estos tiempos, nunca al revés.**
3. **Música** (`music.py`): sintetizada, 100 BPM (pulso 0,6 s; medio tiempo 0,3 s), tramos ligados a los `start` de las frases que indique el paquete. Usar `music.py` (synth oscuro por tramos) o `music_ambiental.py` (pads suaves) como base y adaptar acordes/capas al estilo pedido.
4. **Escenas** (`scenes.py`): escribir una función por escena del guion visual, partiendo de `plantilla/scenes.py` (motor: `camera`, `cam_path`, `subshots`, `snowfall`, `town`, `car_side`, `creature`, `cinema_world`, `title_card`, `overlays`…) y de `scenes_ejemplo_the_discovery.py` como segundo ejemplo.
   - `B` = inicios de frase (escena i empieza con su frase); la última escena dura hasta `voz + 1,0 s`.
   - Sub-momentos a/b/c con `subshots` (cortes en la rejilla de 0,3 s, fundidos de 0,3 s).
   - Respetar escalas, detalles que informan y transiciones del guion (empujes de cámara hacia el punto de salida).
   - Sala de cine con el **Espectador** (capucha mostaza, siempre de espaldas) al inicio, al final y donde el guion lo pida.
   - Textos en pantalla **solo** los del paquete: tarjeta del título (entra con «Se trata de», arriba, con banda oscura detrás, fuera de los botones de TikTok) y textos de apoyo vía `overlays()` (fuera del 20 % inferior).
   - `FOG` por escena (tinte, intensidad) para la atmósfera.
5. **Verificar antes de renderizar todo**: `python3 render.py stills t1,t2,... hoja.png` con 2-3 instantes por escena; mirar la hoja y corregir (caras tapadas, objetos fuera de cuadro, textos ilegibles, reglas de imagen).
6. **Render completo**: `python3 render.py full` (4 procesos, ~5 min) → `chunks.txt`, luego:
   ```
   ffmpeg -f concat -safe 0 -i chunks.txt -c copy video_only.mp4
   ffmpeg -i video_only.mp4 -i voice.wav -i music.wav -filter_complex "[1:a]aresample=44100,aformat=channel_layouts=stereo,apad=pad_dur=2,asplit=2[vo][sc];[2:a]aformat=channel_layouts=stereo,volume=0.22[m];[m][sc]sidechaincompress=threshold=0.05:ratio=4:attack=20:release=300[md];[vo][md]amix=inputs=2:duration=longest:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]" -map 0:v -map "[a]" -c:v libx264 -preset medium -crf 21 -maxrate 9M -bufsize 18M -pix_fmt yuv420p -c:a aac -b:a 192k -ar 44100 -shortest -movflags +faststart ../<slug>-tiktok.mp4
   ```
   Exportar la voz a mp3, borrar `chunk_*.mp4`, `video_only.mp4`, `__pycache__`.
7. **Control final**: duración ≥ 61 s, sonoridad ≈ −14 LUFS, 4 fotogramas extraídos del mp4 revisados.
8. **Entregar**: enviar el mp4 y el mp3 al usuario; commit + push a la rama de trabajo.
   Resumen breve: duración, voz, música, qué se cumplió del guion, y lo pendiente para la app (etiqueta IA, plataforma, etc.).

## Reglas de imagen (siempre)
- Solo adultos con proporciones adultas; sin caras reales ni parecidos con actores; sin logos ni símbolos de sagas; sin texto legible dentro de la imagen.
- Ningún arma apuntando a personas (al suelo, a la pared o fuera de cuadro).
- Muertes, violencia y criaturas: con siluetas, a media distancia, sin sangre ni cuerpos expuestos; nada del desenlace.

## Qué NO hacer
- No cambiar la voz (Alex, `es-419`) sin que el usuario lo pida; nunca voces inglesas con fonemas españoles ni pronunciación de España.
- No inventar textos en pantalla extra.
- No alargar con silencios para llegar a la duración.
