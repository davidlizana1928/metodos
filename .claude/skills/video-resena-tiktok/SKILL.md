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
4. La primera vez que se genera voz, Kokoro descarga su modelo (≈340 MB) en `~/.cache/hyperframes/tts`; tarda unos segundos más.

## 2. Herramienta por tarea

- **HyperFrames** (por defecto): composición, textos animados, transiciones, subtítulos, mezcla de audio, `check`, `snapshot`, `render`. Antes de escribir composiciones, cargar la skill `hyperframes` y `references/types/vertical.md`. Antes de crear un efecto con nombre, buscar en `hyperframes-registry`.
- **Remotion**: piezas reutilizables en React (plantillas de tarjetas, contadores, gráficos) o cuando el usuario lo pida.
- **ffmpeg**: medir voz y silencios, recortar, normalizar, unir.
- **media-use**: música, efectos, tratamientos de color sobre imágenes.
- **Voz (Alex)**: `python3 -I "videos tiktok/motor/voz.py" guion.txt <carpeta>` genera `voz.wav` con Kokoro `em_alex` y `tiempos.json` con el inicio y fin exactos de cada frase. Es la voz por defecto del canal; la voz del usuario solo si él la entrega.
- **Validador**: `python3 -I "videos tiktok/motor/validar.py" <video.mp4 | carpeta_png>` mide look, quietud y duración contra `ESTILO.md`.
- **Transcripción** (solo para voces que no generamos): `npx hyperframes transcribe voz.mp3 --model small --language es`. En este entorno la descarga del modelo whisper está bloqueada por la red; con la voz Alex no hace falta porque `tiempos.json` ya trae los tiempos.
- **stop-slop**: todo texto que escribas (pantalla, subtítulos, descripción, comentario fijado, diálogos) pasa por sus reglas antes de mostrarse.

## 3. Lenguaje visual: 2D, 3D y 2.5D

Elegir el modo por escena, según lo que la escena necesita explicar. `ESTILO.md` §7 dice cuál prefiere el usuario.

### 3.1 Modos

- **2D vectorial:** ilustración plana o semiplana en SVG, animada con GSAP. Sirve para personajes, iconos, diagramas, mapas simples, textos cinéticos y transiciones con formas. Es el modo más rápido y el más fácil de corregir.
- **3D:** escenas en Three.js (bajo poligonaje o estilizado), dibujadas desde el tiempo de la línea de tiempo en el evento `hf-seek`. Sirve para escenarios, objetos protagonistas y movimientos de cámara (entrar por una pantalla, una puerta, una ventana). Leer `hyperframes/references/types/3d.md` y `runtimes.md`.
- **2.5D:** imágenes planas separadas en capas (fondo, medio, frente) con parallax y movimiento de cámara. Sirve cuando el usuario trae imágenes generadas con IA o ilustraciones propias.

**Acabado elegido** (ver `ESTILO.md` §7): **híbrido**. Personajes y sala en 2D con volumen; lo que muestra la pantalla (la historia) en pintura digital con colores muy vivos. Base de código: `motor/propuesta-acabado/index.html` (filtro `pintura`, rig del Espectador, butacas con oclusión).

- El código (SVG con degradados, luz de borde, sombras, polvo y grano) llega con calidad a **2D con volumen**.
- La **pintura digital realista** con pincelada verdadera no se logra solo con filtros: el filtro de pintura en SVG da un borde temblado, no pinceladas. Para ese acabado, las escenas se pintan como imágenes (generadas con IA por el usuario o con `media-use` de HeyGen si inicia sesión) y se animan en 2.5D, con luz, partículas y textos en código encima.
- Las piezas de la marca (el Espectador, la sala, los textos) se mantienen en código para que sean idénticas en cada video.
- **Personajes animados:** rig en SVG o Lottie, con estados de ánimo por tiempo. Leer `hyperframes/references/types/character.md`.

### 3.2 Reglas técnicas

- Three.js va como archivo local en `lib/` del proyecto (copiar `three.module.js` y `three.core.js` desde `motor/node_modules/three/build/`), nunca desde internet al renderizar.
- Todo lo visible depende solo del tiempo: sin `Math.random()` sin semilla, sin relojes, sin `requestAnimationFrame`.
- Una escena pesada en 3D se perfila una vez con `snapshot` antes del render completo.
- La paleta y las tipografías se leen de `ESTILO.md`; las luces 3D usan esos mismos colores (clave cálida mostaza, contorno frío verde azulado).

### 3.3 Componentes del registro para el estilo

Antes de dibujar estos efectos a mano, instalarlos con `npx hyperframes add <nombre>` en el proyecto y adaptarlos a la paleta de `ESTILO.md`:

- `whip-pan-cut`: barrido con desenfoque de movimiento entre lugares.
- `number-wheel` o `count-up`: contador que avanza (se monta sobre un objeto del mundo: cartel, reloj, calendario).
- `caption-pill-karaoke`: base para los subtítulos palabra a palabra (solo si el usuario los aprueba; `ESTILO.md` §4).
- `headline-slam`: entrada con impacto para el banner de palabra clave.
- `soft-blur-in` / `focus-blur-resolve`: profundidad de campo y cambios de foco.
- Para mapas y vistas desde arriba: dibujarlos en SVG con el acabado del estilo (los mapas del registro son de datos reales, no de ficción).

### 3.4 Biblioteca de la marca

Los elementos que se repiten viven en `videos tiktok/motor/biblioteca/` y se reutilizan en vez de redibujarse:

- `personajes/`: el Espectador en 2D (SVG) y en 3D, con sus poses aprobadas.
- `escenarios/`: la sala de cine y otros fondos aprobados.
- `componentes/`: gancho, banner de palabra clave, tarjeta del título, sellos, números, transiciones.

Cada pieza nueva que el usuario aprueba y que sirva para otros videos se guarda aquí y se anota en `ESTILO.md`.

## 4. Flujo por video

### 4.1 Leer el material

1. Leer `ESTILO.md` completo. Sus valores mandan.
2. Revisar `instrucciones/<video>/`: guion, voz, imágenes, música, notas del usuario.
3. **Ajustar el guion a `ESTILO.md` §6.1 (cómo explicar)** sin tocar la estructura: gancho con la paradoja o el resultado dentro de «Imagina que…», un hecho por frase (12 palabras o menos), causa → consecuencia, giros con «pero», números con fuente. Mostrar al usuario los cambios marcados y esperar su visto bueno antes de generar la voz. Aplicar stop-slop.
4. Generar la voz Alex con `voz.py` desde el guion. Debe durar **61 s o más, objetivo 70 a 90 s** (215 a 280 palabras). Si queda corta, alargar el guion con información de la historia, nunca con silencio.
5. Si el usuario entrega su propia voz: medir con ffmpeg duración y silencios (`silencedetect=-35dB:d=0.35`) y transcribir.
6. La imagen se ajusta a la voz, nunca al revés: cada escena dura lo que su frase en `tiempos.json`.
7. Si falta algo indispensable, pedirlo en una lista corta. No inventar material.

### 4.2 Construir

1. `npx hyperframes init "videos tiktok/motor/proyectos/<slug>" --non-interactive --skip-skills --resolution portrait`
2. Escribir la **lista de escenas**, una línea por frase de la voz, y mostrarla al usuario si el video es nuevo:
   ```
   [n] m:ss-m:ss | «frase exacta»
       IMAGEN LITERAL: lo que la frase nombra, visible en ese momento
       ESCALA: personaje / mapa desde arriba / plano general / detalle
       ANIMACIÓN: movimiento de cámara + algo del lugar (2 cosas como mínimo); cambio cada 1,5-2,5 s
       TEXTO: banner, contador o sello (si aporta)
       TRANSICIÓN: continua / barrido con desenfoque / a través de un objeto
   ```
   Una frase sin imagen literal se reescribe (avisando) o se resuelve con un cambio de escala.
3. Una escena por subcomposición; paleta y tipografías como variables CSS tomadas de `ESTILO.md`. Reutilizar la biblioteca antes de dibujar algo nuevo.
4. Respetar la firma de `ESTILO.md` §1 y la zona segura de TikTok.
5. Dinamismo: en cada escena se mueven al menos 2 cosas a la vez (cámara y algo del lugar); nada queda quieto más de 3 s.
6. `npx hyperframes check --json` sin errores.

### 4.3 Fotogramas para aprobar (obligatorio antes del render final)

1. `npx hyperframes snapshot --at <segundos clave>`: gancho (0,5 s), cada texto de apoyo, un cambio de escena, «Se trata de» y el último fotograma.
2. **Validación por fotograma** (`ESTILO.md` §7.2), en este orden:
   - `validar.py` sobre la carpeta de PNG: look de cada fotograma dentro de rango.
   - Mirar la hoja completa y hacer un acercamiento (`ffmpeg -vf crop=…`) a cada persona y objeto protagonista. Revisar los puntos de §7.1 uno por uno: forma humana, escala, de espaldas se ve pelo, el texto no tapa sujetos, luz con dirección, 3 planos, atmósfera.
   - Lo que falla se rehace y se vuelve a validar. Al usuario solo llegan fotogramas que pasaron.
   - Revisar también el **registro de errores** de `ESTILO.md` §7.2: ninguno de esos errores puede reaparecer.
   - Cuando el usuario marca un error nuevo (por ejemplo, con una captura anotada), corregirlo en todos los fotogramas donde aparezca, agregarlo a §7.1 como regla y al registro de §7.2.
3. Copiar la hoja a `instrucciones/<video>/revision-vN.jpg` y enviarla al usuario.
4. Preguntar solo por: **texto, color, estructura, ritmo, tipografía**. Una lista numerada, una línea por punto.
5. Repetir hasta que el usuario apruebe. Cada corrección que sea un gusto general (no exclusivo de este video) se lleva a `ESTILO.md`.

### 4.4 Exportar

1. Render: `npx hyperframes render -o "videos tiktok/exportables/<AAAA-MM-DD-titulo>.mp4"` (1080×1920, 30 fps).
2. `validar.py` sobre el MP4: duración (61 s mínimo, objetivo 70 a 90 s), sin tramos quietos de más de 3 s, look en rango. Con ffprobe: 1080×1920 y audio presente. Si falla, se corrige antes de entregar.
3. Escribir al lado `<AAAA-MM-DD-titulo>.txt` con descripción, hashtags y comentario fijado (formato de `resenas-cine-tiktok` §9).
4. Commit y push de `exportables/`, `ESTILO.md` y el proyecto.

## 5. Analizar una referencia

Cuando el usuario sube un video a `referencias/` y dice qué le gusta:

0. Si el video llega por el chat, copiarlo a `referencias/` con un nombre corto y la fecha. Si el usuario no lo adjuntó, avisarle en la primera línea.
1. Medir con números: `npx hyperframes measure cuts` (cortes duros y planos), `measure look` (luz, contraste, saturación), `silencedetect` de ffmpeg (pausas de la voz) y una hoja de fotogramas (`ffmpeg -vf "fps=1/3,scale=240:-1,tile=5x5"`), más el inicio y los últimos 8 s por separado. Si viene en varias partes, unirlas antes con `concat`.
   - Transcripción de la voz: `npx hyperframes transcribe <video> --model small --language es`. Si falla por red (descarga del modelo bloqueada), seguir sin ella y avisar al usuario.
2. Si el usuario no dijo qué le gusta, preguntarlo antes de analizar. No copiar todo el video.
3. Clasificar el gusto: 2D, 3D, 2.5D, tipografía, color, ritmo, transición, sonido o narración.
4. Convertir el gusto en una regla medible (cifra, color hex, px, segundos). Nada de adjetivos sueltos.
5. Anotar en `referencias/GUSTOS.md` y llevar la regla a `ESTILO.md` subiendo la versión y registrando el cambio en su historial.
6. Registrar también lo que **no** le gusta, como regla de lo que hay que superar (ejemplo: ref01 «diseño muy básico» → `ESTILO.md` §7.1).
7. Nunca reproducir logos, personajes, música ni material protegido de la referencia; se toma la técnica, no el contenido.

## 6. Mantener el estilo

- `ESTILO.md` es la memoria de la marca: paleta, tipografía, textos, ritmo, voz, gustos y firma.
- Cambios a la firma (§1) solo con aprobación explícita.
- Si dos gustos chocan, preguntar cuál manda y anotar la decisión.
- Personalidad, frases propias, etiquetas y muletillas de marca que el usuario cree: se guardan en `ESTILO.md` §6 con un ejemplo de uso.

## 7. Respuestas al usuario

- Primera línea: el resultado o lo que falta.
- Micro-párrafos, viñetas, negritas, emojis como anclas. Sin tablas ni muros de texto.
- Al mostrar fotogramas: qué se ve, qué se decidió y qué falta aprobar.
