---
name: video-resena-tiktok
description: Crea videos ilustrativos para TikTok (9:16) con diseño gráfico 2D, 3D o 2.5D, animados en código con HyperFrames y Remotion, a partir del guion y el material en «videos tiktok/instrucciones». Muestra fotogramas para aprobar antes del render final, aprende gustos de los videos en «referencias» y mantiene actualizado el estilo de la casa (ESTILO.md). Usar al pedir «haz el video de [tema]», «edita el video», «analiza esta referencia» o «actualiza el estilo».
---

# Video reseña TikTok

Convierte un guion en un video ilustrativo listo para publicar, con la firma del canal. Las ilustraciones y la animación se construyen en código (SVG, CSS, Three.js), no se graban: cada pieza es diseño gráfico 2D o 3D. Trabaja en tres pasos con aprobación del usuario entre ellos: **fotogramas → correcciones → exportable**.

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

## 3. Lenguaje visual: 2D, 3D y 2.5D

Elegir el modo por escena, según lo que la escena necesita explicar. `ESTILO.md` §7 dice cuál prefiere el usuario.

### 3.1 Modos

- **2D vectorial:** ilustración plana o semiplana en SVG, animada con GSAP. Sirve para personajes, iconos, diagramas, mapas simples, textos cinéticos y transiciones con formas. Es el modo más rápido y el más fácil de corregir.
- **3D:** escenas en Three.js (bajo poligonaje o estilizado), dibujadas desde el tiempo de la línea de tiempo en el evento `hf-seek`. Sirve para escenarios, objetos protagonistas y movimientos de cámara (entrar por una pantalla, una puerta, una ventana). Leer `hyperframes/references/types/3d.md` y `runtimes.md`.
- **2.5D:** imágenes planas separadas en capas (fondo, medio, frente) con parallax y movimiento de cámara. Sirve cuando el usuario trae imágenes generadas con IA o ilustraciones propias.
- **Personajes animados:** rig en SVG o Lottie, con estados de ánimo por tiempo. Leer `hyperframes/references/types/character.md`.

### 3.2 Reglas técnicas

- Three.js va como archivo local en `lib/` del proyecto (copiar `three.module.js` y `three.core.js` desde `motor/node_modules/three/build/`), nunca desde internet al renderizar.
- Todo lo visible depende solo del tiempo: sin `Math.random()` sin semilla, sin relojes, sin `requestAnimationFrame`.
- Una escena pesada en 3D se perfila una vez con `snapshot` antes del render completo.
- La paleta y las tipografías se leen de `ESTILO.md`; las luces 3D usan esos mismos colores (clave cálida mostaza, contorno frío verde azulado).

### 3.3 Biblioteca de la marca

Los elementos que se repiten viven en `videos tiktok/motor/biblioteca/` y se reutilizan en vez de redibujarse:

- `personajes/`: el Espectador en 2D (SVG) y en 3D, con sus poses aprobadas.
- `escenarios/`: la sala de cine y otros fondos aprobados.
- `componentes/`: gancho, banner de palabra clave, tarjeta del título, sellos, números, transiciones.

Cada pieza nueva que el usuario aprueba y que sirva para otros videos se guarda aquí y se anota en `ESTILO.md`.

## 4. Flujo por video

### 4.1 Leer el material

1. Leer `ESTILO.md` completo. Sus valores mandan.
2. Revisar `instrucciones/<video>/`: guion, voz, imágenes, música, notas del usuario.
3. Si hay voz, medir con ffmpeg duración, silencios (`silencedetect=-35dB:d=0.35`) y transcribir. La imagen se ajusta a la voz, nunca al revés.
4. Si falta algo indispensable, pedirlo en una lista corta. No inventar material.

### 4.2 Construir

1. `npx hyperframes init "videos tiktok/motor/proyectos/<slug>" --non-interactive --skip-skills --resolution portrait`
2. Escribir una lista de escenas: frase de la voz, modo (2D, 3D o 2.5D), qué se ve y qué explica. Mostrarla al usuario si el video es nuevo.
3. Una escena por subcomposición; paleta y tipografías como variables CSS tomadas de `ESTILO.md`. Reutilizar la biblioteca antes de dibujar algo nuevo.
4. Respetar la firma de `ESTILO.md` §1 y la zona segura de TikTok.
5. `npx hyperframes check --json` sin errores.

### 4.3 Fotogramas para aprobar (obligatorio antes del render final)

1. `npx hyperframes snapshot --at <segundos clave>`: gancho (0,5 s), cada texto de apoyo, un cambio de escena, «Se trata de» y el último fotograma.
2. Mirar la hoja de contacto antes de enviarla. Corregir lo obvio sin preguntar.
3. Copiar la hoja a `instrucciones/<video>/revision-vN.jpg` y enviarla al usuario.
4. Preguntar solo por: **texto, color, estructura, ritmo, tipografía**. Una lista numerada, una línea por punto.
5. Repetir hasta que el usuario apruebe. Cada corrección que sea un gusto general (no exclusivo de este video) se lleva a `ESTILO.md`.

### 4.4 Exportar

1. Render: `npx hyperframes render -o "videos tiktok/exportables/<AAAA-MM-DD-titulo>.mp4"` (1080×1920, 30 fps).
2. Verificar con ffprobe: resolución, duración (61 s o más si es reseña monetizable), audio presente.
3. Escribir al lado `<AAAA-MM-DD-titulo>.txt` con descripción, hashtags y comentario fijado (formato de `resenas-cine-tiktok` §9).
4. Commit y push de `exportables/`, `ESTILO.md` y el proyecto.

## 5. Analizar una referencia

Cuando el usuario sube un video a `referencias/` y dice qué le gusta:

0. Si el video llega por el chat, copiarlo a `referencias/` con un nombre corto y la fecha. Si el usuario no lo adjuntó, avisarle en la primera línea.
1. Medir solo ese factor: `npx hyperframes measure <video>` (cortes, movimiento, cajas de texto, look), ffprobe, y fotogramas con `snapshot` o `ffmpeg -vf fps=1/2,tile`.
2. Si el usuario no dijo qué le gusta, preguntarlo antes de analizar. No copiar todo el video.
3. Clasificar el gusto: 2D, 3D, 2.5D, tipografía, color, ritmo, transición, sonido o narración.
4. Convertir el gusto en una regla medible (cifra, color hex, px, segundos). Nada de adjetivos sueltos.
5. Anotar en `referencias/GUSTOS.md` y llevar la regla a `ESTILO.md` subiendo la versión y registrando el cambio en su historial.
6. Nunca reproducir logos, personajes, música ni material protegido de la referencia; se toma la técnica, no el contenido.

## 6. Mantener el estilo

- `ESTILO.md` es la memoria de la marca: paleta, tipografía, textos, ritmo, voz, gustos y firma.
- Cambios a la firma (§1) solo con aprobación explícita.
- Si dos gustos chocan, preguntar cuál manda y anotar la decisión.
- Personalidad, frases propias, etiquetas y muletillas de marca que el usuario cree: se guardan en `ESTILO.md` §6 con un ejemplo de uso.

## 7. Respuestas al usuario

- Primera línea: el resultado o lo que falta.
- Micro-párrafos, viñetas, negritas, emojis como anclas. Sin tablas ni muros de texto.
- Al mostrar fotogramas: qué se ve, qué se decidió y qué falta aprobar.
