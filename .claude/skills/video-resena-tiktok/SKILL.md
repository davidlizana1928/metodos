---
name: video-resena-tiktok
description: Produce el VIDEO terminado de una reseña de cine para TikTok (mp4 vertical 1080x1920, 30 fps) en estilo "UI premium oscuro" con Remotion, con la voz de Alex en español latino, subtítulos palabra por palabra y música. Parte de un guion visual (.txt) y un paquete de reseña (.md) creados con la skill resenas-cine-tiktok. Usar cuando el usuario adjunte esos archivos o pida «crea el video», «haz el video», «video de la reseña» o similar.
---

# Video de reseña TikTok — Remotion, estilo «UI premium oscuro»

Convierte un **guion visual** y un **paquete de reseña** en un `.mp4` listo para subir.
El motor es **Remotion (TypeScript)**: ya no se usan `lib.py`, `render.py` ni `scenes.py`.

Trabaja de forma directa: no preguntes opciones que ya están definidas aquí. Avanza paso a paso y verifica.
Explica al usuario, en simple, cada paso que haces.

## Entradas

- Guion visual `.txt` y paquete `.md` de `resenas-cine-tiktok`, con el guion de voz, los títulos, los textos de apoyo y la música.
- Si faltan, ofrecer crearlos con la skill `resenas-cine-tiktok`.

## Salida (en `<repo>/<slug>/`)

- `out/<slug>-tiktok.mp4` (H.264 CRF 18, audio normalizado a −14 LUFS)
- `public/voz.mp3` y `public/words.json`
- El proyecto Remotion completo de la reseña, para poder editarlo después

## Archivos de esta skill

- `plantilla-remotion/`: base del proyecto, que se copia entera a `<slug>/`.
  - `package.json`, `tsconfig.json` y `remotion.config.ts` (usa el Chromium preinstalado de la nube si existe).
  - `src/theme.ts`: **tokens del estilo**.
  - `src/components/`:
    - `Fondo`: degradado, halo superior y grano.
    - `GlassCard`: tarjeta de vidrio con rotación 3D.
    - `PromptBar`: texto que se escribe solo.
    - `BigNumeral` y `ProgressDots`: número grande y puntos de avance.
    - `Subtitles`: subtítulos palabra por palabra.
    - `FocusIn`: entrada con desenfoque.
    - `Waveform` y `Counter`: forma de onda y contador.
    - `Camera`: movimiento de cámara sobre toda la escena.
    - `Demo`: el contenido dentro de la tarjeta.
    - `Escenas`: las escenas `Hook`, `Bloque` y `CTA`.
  - `src/timeline.ts`: tipos y cálculo de los fotogramas a partir de `words.json`.
  - `src/guion.ts`: **el único archivo de código que cambia por reseña**. Trae como ejemplo *Resident Evil: Noche Cero*.
  - `src/Video.tsx`: el `<Series>` con Hook → 5 bloques → CTA, más subtítulos y audio.
  - `src/Root.tsx`: lee `words.json`, detecta si existe `music.wav` y calcula la duración.
- `plantilla-audio/`:
  - `voice.py`: voz de Alex. Genera `public/voz.mp3`, `public/words.json` y `public/segments.json`.
  - `music.py` y `music_ambiental.py`: música sintetizada, que se guarda en `public/music.wav`.

## Tokens del estilo (`src/theme.ts`)

- **Fondo**: degradado `#040404` → `#0A090E`, halo radial superior `#2A2013` → transparente y grano sutil.
- **Acento**: `#F0B040`, con glow `0 0 24px` al 40 %.
- **Tarjetas**: fondo `rgba(37,32,29,0.7)`, borde 1px `rgba(255,255,255,0.1)`, radio 28px y sombra `0 30px 80px #000`.
- **Fuentes** con `@remotion/google-fonts`: Plus Jakarta Sans para la interfaz y Playfair Display Italic para numerales y frases.

## Componentes

- **GlassCard**: perspectiva 3D, con `rotateX` y `rotateY` por props.
- **PromptBar**: píldora de vidrio con texto que se escribe solo y cursor. La keyword va en el color de acento y a la derecha hay un botón circular de acento con flecha ↑, que pulsa al terminar.
- **BigNumeral** («01» a «05») y **ProgressDots**: 5 pasos; el activo es un trazo alargado de acento.
- **Subtitles**: lee `words.json` y muestra de 1 a 3 palabras al 72 % de la altura.
  - Las palabras ya dichas van en blanco y las siguientes en gris al 35 %.
  - Las palabras clave (`bold`) van en acento con glow.
- **FocusIn**: el desenfoque baja de 20px a 0, la escala sube de 0,92 a 1 y la opacidad de 0 a 1.
- **Waveform** con cabezal y **Counter** con separador de miles (por ejemplo, 1 → 1.000).
- **Camera**: aplica translate y scale a toda la escena con `spring({ damping: 200 })`, sin cortes duros.

## Timeline (`<Series>` en `src/Video.tsx`)

- **Hook**: «Imagina que…» en Playfair, más una tarjeta con la primera imagen o demo. Abarca las frases del gancho.
- **5 bloques**. Cada uno sigue este orden:
  1. el numeral y los puntos de avance
  2. la PromptBar escribe una frase corta del paquete, con su keyword
  3. la demo en GlassCard **entra cuando la voz dice la primera palabra clave del bloque**, tomada de `words.json`
- **Salida de cada bloque**: blur-out con zoom de cámara.
- **Revelar una imagen**: una tarjeta `imagen` con `expandir: true` crece a pantalla completa.
- **CTA**: tarjeta «SE TRATA DE / Título / título original y año». Cuando empieza «Si fueras tú…», la PromptBar escribe la pregunta espejo.
- **Duraciones**:
  - Cada escena empieza en la primera palabra de su primer segmento de voz (datos de `words.json`, a 30 fps).
  - El video termina 1 s después de la última palabra.
  - Las cifras de referencia (Hook de 0 a 5 s, bloques de unos 9 s, CTA de 50 a 56 s) son aproximadas: **manda la voz**.
  - El canal exige **61 s o más**, y un guion de 220 a 250 palabras da entre 65 y 78 s.
- **Reparto del guion del canal en las escenas** (`segmentos` en `guion.ts`):
  - Hook = gancho (frases 1 y 2).
  - Bloques 1 a 5 = mundo normal, detonante, escalada, segunda escalada, y transformación más corte en suspenso.
  - CTA = «Se trata de…» más la pregunta espejo.
- **Reglas del canal en el CTA**: nunca pedir likes, seguidores ni comentarios a cambio de algo (regla 8). El CTA es el título más la pregunta espejo.

## Preparar el entorno (una vez por sesión)

1. Requisitos: Node 20 o más, ffmpeg, y Python con `numpy`, `soundfile` y `kokoro-onnx` (`pip install kokoro-onnx soundfile`).
2. **Voz**: deben existir `~/kokoro/kokoro-q8.onnx` y `~/kokoro/voices_es.npz`. Si faltan:
   ```
   mkdir -p ~/kokoro && cd ~/kokoro
   B=https://huggingface.co/onnx-community/Kokoro-82M-v1.0-ONNX/resolve/main
   curl -sSfL -o kokoro-q8.onnx $B/onnx/model_quantized.onnx
   curl -sSfL -o em_alex.bin $B/voices/em_alex.bin
   python3 -c "import numpy as np; np.savez('voices_es.npz', em_alex=np.fromfile('em_alex.bin','float32').reshape(-1,1,256))"
   ```
   Si la red bloquea Hugging Face, pedir acceso a la red. **No** cambiar de voz.
3. **Navegador**: en la nube no se puede descargar Chrome. `remotion.config.ts` ya apunta a `/opt/pw-browsers/chromium`. No correr `playwright install`.
4. Seguir las skills de Remotion del repo (`remotion-best-practices` y `remotion-markup`). Todo se anima con `useCurrentFrame()`, sin animaciones CSS.

## Flujo (en este orden)

1. **Proyecto**:
   - `cp -r <skill>/plantilla-remotion/. <repo>/<slug>/` y `cp <skill>/plantilla-audio/{voice.py,music.py} <repo>/<slug>/`.
   - `cd <slug> && npm i`.
   - Borrar las imágenes del ejemplo en `public/escenas/` si las hubiera.
2. **Voz primero** (`python3 voice.py`, desde `<slug>/`):
   - `P`: una frase por cada línea `VOZ:` del guion visual. La frase final se separa en «Se trata de …» y «Si fueras tú…».
   - Marcar con `*asteriscos*` las **palabras clave**: 1 o 2 por bloque, las mismas keywords de la PromptBar. Quedan con `bold: true` en `words.json`, se ven en acento en los subtítulos y **marcan cuándo entra la demo de cada bloque**.
   - `FIX`: títulos en inglés como los diría un hablante latino.
   - Voz Alex (`em_alex`, `es-419`), velocidad 1.05, pausas de 0,18 s y ninguna mayor a 0,4 s.
   - Resultado: `public/voz.mp3`, `public/words.json` con `[{word, start, end, bold, seg}]` y `public/segments.json`.
   - Los tiempos de cada palabra se reparten **en proporción a sus letras** dentro de cada segmento de Kokoro.
3. **Música (opcional)**:
   - Adaptar `music.py` o `music_ambiental.py`: los tramos se ligan a los `start` de `public/segments.json` que indique el paquete.
   - Se guarda en `public/music.wav`, y `Root.tsx` la detecta sola. Volumen 0,18 por debajo de la voz.
4. **Guion de escenas** (`src/guion.ts`):
   - Datos generales: `titulo` (título en Chile) y `subtitulo` (título original y año, o solo el año).
   - `hook`: `segmentos`, `frase` («Imagina que…») y `demo`.
   - `bloques` (5): `segmentos`, `prompt` (frase corta, de 45 caracteres como máximo), `keyword` (debe aparecer tal cual dentro de `prompt`) y `demo`.
   - `cta`: `segmentos`, `prompt` (versión corta de la pregunta espejo) y `keyword`.
   - Tipos de `demo`:
     - `imagen`: archivo en `public/`, con opción `expandir: true`.
     - `texto`: una frase clave en Playfair.
     - `contador`: valores `desde` y `hasta`, con `prefijo`, `sufijo` y `etiqueta` opcionales.
     - `ondas`: forma de onda, con `etiqueta` opcional.
   - Reglas de los textos: solo datos verificados del paquete. Cifras solo si están en 2 fuentes. Nunca nombres de personas reales ni de personajes.
   - **Imágenes**: las genera el usuario según el guion visual, o se crean con Remotion (por ejemplo, un `still` de una escena 3D). Van en `public/escenas/` y deben cumplir las reglas de imagen.
5. **Previsualizar**:
   - **En local**: `npm run dev` (Remotion Studio) y revisar el video completo.
   - **En la nube** no hay pantalla: renderizar fotogramas sueltos con `npx remotion still Video hoja/fNN.png --frame=NN --scale=0.4`, unos 2 por escena. Unirlos con `ffmpeg -filter_complex hstack=N` y revisar la hoja.
   - Qué revisar:
     - que las tarjetas no tapen la PromptBar ni los subtítulos (al 72 %)
     - que no haya textos cortados
     - que la keyword aparezca en acento
     - que la demo entre a tiempo
     - que la tarjeta de imagen crezca bien
6. **Render** (en segundo plano; tarda unos minutos):
   ```
   npx remotion render Video out/video.mp4 --codec h264 --crf 18
   ffmpeg -i out/video.mp4 -af loudnorm=I=-14:TP=-1.5:LRA=11 -c:v copy -c:a aac -b:a 192k -ar 44100 -movflags +faststart out/<slug>-tiktok.mp4
   ```
   La segunda línea (normalizar a −14 LUFS) es obligatoria si hay música. Si solo hay voz, igual se recomienda.
   `remotion.config.ts` fija una sola pestaña (`Config.setConcurrency(1)`). **No subirlo**: con varias pestañas, el navegador de la nube corrompe fotogramas (mosaicos repetidos, tarjetas vacías). Tampoco usar `backdrop-filter` ni `transform-style: preserve-3d`, que dejan fantasmas en el render.
7. **Control final**:
   - Duración de 61 s o más.
   - Sonoridad cercana a −14 LUFS (`ffmpeg -af ebur128`).
   - Revisar 4 fotogramas del mp4 final.
   - Borrar `out/video.mp4`.
8. **Entregar**:
   - Enviar el mp4 y `voz.mp3` al usuario.
   - Hacer commit y push a la rama de trabajo, sin `node_modules` ni `out`.
   - Resumen breve: duración, voz, música, escenas y lo que falta hacer en la app (etiqueta IA, plataforma, etc.).

## Reglas de imagen y texto (siempre)

- Solo adultos con proporciones adultas. Sin caras reales ni parecidos con actores. Sin logos, pósters ni material de la película.
- Ningún arma apuntando a personas. Muertes, violencia y criaturas: en silueta, sin sangre, y nada del desenlace.
- Sin texto legible dentro de las imágenes: todo texto es una capa de Remotion.
- Los textos de apoyo y las PromptBar nunca tapan el 20 % inferior ni los botones de la derecha.

## Qué NO hacer

- No cambiar la voz (Alex, `es-419`) sin que el usuario lo pida.
- No inventar cifras ni textos que no estén en el paquete.
- No alargar con silencios para llegar a la duración.
- No usar animaciones CSS ni Tailwind animate: todo se mueve con `useCurrentFrame()`, `interpolate` y `spring`.
- No poner tiempos fijos a mano: las entradas de las escenas y de las demos salen de `words.json`.
