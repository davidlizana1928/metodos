---
name: video-resena-tiktok
description: Edita y exporta videos de reseñas para TikTok (9:16) con HyperFrames y Remotion, a partir del guion y el material en «videos tiktok/instrucciones». Muestra fotogramas para aprobar antes del render final, aprende gustos de los videos en «referencias» y mantiene actualizado el estilo de la casa (ESTILO.md). Usar al pedir «edita el video», «arma el video de [título]», «analiza esta referencia» o «actualiza el estilo».
---

# Video reseña TikTok

Convierte el material en bruto en un video listo para publicar, con la firma del canal. Trabaja en tres pasos con aprobación del usuario entre ellos: **fotogramas → correcciones → exportable**.

El contenido (ficha, guion de voz, guion visual) lo produce la skill `resenas-cine-tiktok`. Esta skill edita, anima y exporta. Si el usuario no trae guion, se genera primero con esa skill.

## 0. Rutas

- Raíz: `videos tiktok/`
- Material en bruto: `instrucciones/<AAAA-MM-DD-titulo>/` (guion, voz, imágenes, música, notas). Cuando el usuario dice «brutos», se refiere a esta carpeta.
- Referencias: `referencias/` + `referencias/GUSTOS.md`
- Resultado: `exportables/<AAAA-MM-DD-titulo>.mp4` + `.txt` con descripción y hashtags
- Estilo vivo: `ESTILO.md` (fuente única de paleta, tipografía, tamaños y ritmo)
- Motor: `motor/` (proyecto HyperFrames por video en `motor/proyectos/<slug>/`; Remotion en `motor/remotion/`)

## 1. Preparar el entorno

El contenedor es efímero. Al empezar:

1. Si falta `videos tiktok/motor/node_modules`, ejecutar `bash "videos tiktok/motor/instalar.sh"`.
2. Comandos: `npx hyperframes …` desde la carpeta del proyecto. Para Remotion: `npx remotion render <entrada> <id> <salida> --browser-executable=/opt/pw-browsers/chromium`.
3. No enviar telemetría ni notas de uso a HeyGen (`hyperframes telemetry disable`). Funciones de pago de HeyGen (avatar, voz, `--engine heygen`) solo si el usuario lo pide y entrega su clave.

## 2. Herramienta por tarea

- **HyperFrames** (por defecto): composición, textos animados, transiciones, subtítulos, mezcla de audio, `check`, `snapshot`, `render`. Antes de escribir composiciones, cargar la skill `hyperframes` y `references/types/vertical.md`. Antes de crear un efecto con nombre, buscar en `hyperframes-registry`.
- **Remotion**: piezas reutilizables en React (plantillas de tarjetas, contadores, gráficos) o cuando el usuario lo pida.
- **ffmpeg**: medir voz y silencios, recortar, normalizar, unir.
- **media-use**: música, efectos, tratamientos de color sobre imágenes.
- **Transcripción**: `npx hyperframes transcribe voz.mp3 --model small --language es` para tiempos por palabra.
- **stop-slop**: todo texto que escribas (pantalla, subtítulos, descripción, comentario fijado, diálogos) pasa por sus reglas antes de mostrarse.

## 3. Flujo por video

### 3.1 Leer el material

1. Leer `ESTILO.md` completo. Sus valores mandan.
2. Revisar `instrucciones/<video>/`: guion, voz, imágenes, música, notas del usuario.
3. Si hay voz, medir con ffmpeg duración, silencios (`silencedetect=-35dB:d=0.35`) y transcribir. La imagen se ajusta a la voz, nunca al revés.
4. Si falta algo indispensable, pedirlo en una lista corta. No inventar material.

### 3.2 Construir

1. `npx hyperframes init "videos tiktok/motor/proyectos/<slug>" --non-interactive --skip-skills --resolution portrait`
2. Una escena por subcomposición; paleta y tipografías como variables CSS tomadas de `ESTILO.md`.
3. Respetar la firma de `ESTILO.md` §1 y la zona segura de TikTok.
4. `npx hyperframes check --json` sin errores.

### 3.3 Fotogramas para aprobar (obligatorio antes del render final)

1. `npx hyperframes snapshot --at <segundos clave>`: gancho (0,5 s), cada texto de apoyo, un cambio de escena, «Se trata de» y el último fotograma.
2. Mirar la hoja de contacto antes de enviarla. Corregir lo obvio sin preguntar.
3. Copiar la hoja a `instrucciones/<video>/revision-vN.jpg` y enviarla al usuario.
4. Preguntar solo por: **texto, color, estructura, ritmo, tipografía**. Una lista numerada, una línea por punto.
5. Repetir hasta que el usuario apruebe. Cada corrección que sea un gusto general (no exclusivo de este video) se lleva a `ESTILO.md`.

### 3.4 Exportar

1. Render: `npx hyperframes render -o "videos tiktok/exportables/<AAAA-MM-DD-titulo>.mp4"` (1080×1920, 30 fps).
2. Verificar con ffprobe: resolución, duración (61 s o más si es reseña monetizable), audio presente.
3. Escribir al lado `<AAAA-MM-DD-titulo>.txt` con descripción, hashtags y comentario fijado (formato de `resenas-cine-tiktok` §9).
4. Commit y push de `exportables/`, `ESTILO.md` y el proyecto.

## 4. Analizar una referencia

Cuando el usuario sube un video a `referencias/` y dice qué le gusta:

1. Medir solo ese factor: `npx hyperframes measure <video>` (cortes, movimiento, cajas de texto, look), ffprobe, y fotogramas con `snapshot` o `ffmpeg -vf fps=1/2,tile`.
2. Si el usuario no dijo qué le gusta, preguntarlo antes de analizar. No copiar todo el video.
3. Convertir el gusto en una regla medible (cifra, color hex, px, segundos). Nada de adjetivos sueltos.
4. Anotar en `referencias/GUSTOS.md` y llevar la regla a `ESTILO.md` subiendo la versión y registrando el cambio en su historial.
5. Nunca reproducir logos, personajes, música ni material protegido de la referencia; se toma la técnica, no el contenido.

## 5. Mantener el estilo

- `ESTILO.md` es la memoria de la marca: paleta, tipografía, textos, ritmo, voz, gustos y firma.
- Cambios a la firma (§1) solo con aprobación explícita.
- Si dos gustos chocan, preguntar cuál manda y anotar la decisión.
- Personalidad, frases propias, etiquetas y muletillas de marca que el usuario cree: se guardan en `ESTILO.md` §6 con un ejemplo de uso.

## 6. Respuestas al usuario

- Primera línea: el resultado o lo que falta.
- Micro-párrafos, viñetas, negritas, emojis como anclas. Sin tablas ni muros de texto.
- Al mostrar fotogramas: qué se ve, qué se decidió y qué falta aprobar.
