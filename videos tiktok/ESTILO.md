# Estilo de la casa · versión 0.4

Archivo vivo. Cada referencia nueva y cada corrección aprobada lo actualiza. Manda sobre cualquier valor por defecto de HyperFrames o Remotion.

## 1. Firma (aprobada · no cambia sin tu aprobación)

- **Apertura:** «Imagina que…» desde el segundo 0, texto en pantalla ya visible en el primer fotograma.
- **Cierre:** «Se trata de [Título en Chile]…» + tarjeta del título + pregunta espejo «Si fueras tú, ¿…?».
- **Personaje:** el Espectador (hombre adulto, chaqueta mostaza con capucha, siempre de espaldas o de perfil).
- **Escenario ancla:** sala de cine vacía, butacas carmesí, proyector arriba a la izquierda.

## 1.1 Duración

- **Mínimo absoluto: 61 s.** Objetivo: **70 a 90 s**.
- Con la voz Alex (≈3,1 palabras por segundo, pausas incluidas): guion de **215 a 280 palabras**.

## 2. Paleta

- Bruma: `#1d3b3f` → `#0b1a1c` (fondo)
- Mostaza: `#e0a526` (acento, palabra clave del gancho, filete de la tarjeta)
- Carmesí: `#7a1020` (banner de palabra clave)
- Crema: `#f4ead2` (texto principal)

## 3. Tipografía

- Titulares y banners: **Archivo Black**
- Subtítulos, títulos originales y año: **Oswald**, mayúsculas, tracking 0,08 em
- Ningún texto legible bajo 28 px. Máximo 5 palabras por línea en textos de apoyo.

## 4. Textos en pantalla

- **Gancho:** crema, 96 px, palabra clave en mostaza, sombra suave.
- **Banner de palabra clave:** fondo carmesí, texto crema, entrada y salida de 0,15 s.
- **Tarjeta del título:** banda oscura al 72 %, filete mostaza arriba, zona superior. Entra con fundido de 0,4 s en «Se trata de».
- **Zona segura TikTok:** texto entre 288 y 1248 px de alto, y entre 120 y 888 px de ancho.

## 5. Ritmo y movimiento

- Cambio visual cada 2 a 3 s, en el tiempo fuerte de la música.
- Fondo con avance lento continuo (zoom 1,00 → 1,06 por escena).
- Acentos en contratiempos: micro-zoom de 2 a 3 % o sacudida leve.
- **Nada queda quieto más de 3 s**, tampoco el cierre: la sala final sigue con un avance lento, polvo en el haz del proyector o luz de la pantalla que cambia.
- **Dinamismo obligatorio:** el video nunca se siente detenido. En cada escena se mueven al menos 2 cosas a la vez (cámara y algo del lugar).
- Entre lugares se prefiere el **movimiento de cámara continuo** (paneo, entrada por una ventana o pantalla) al corte duro. Referencia: ref01 tuvo 8 cortes duros en 74 s.

## 6. Narración, voz y personalidad del texto

- **Estructura aprobada (ref01):** «Imagina que…» → mundo normal → detonante → escaladas → corte en suspenso → «Se trata de…» → pregunta espejo.
- **Tono explicativo y narrativo:** la voz cuenta la historia como si el espectador la viviera, y explica las reglas del mundo antes de usarlas.
- **Sin nombres hasta el final:** ni personajes, ni actores, ni el título. El primer nombre que aparece en voz o pantalla es el título, en «Se trata de…».
- Segunda persona, presente, frases cortas. Español latinoamericano neutro.
- **Voz: Alex (aprobada)** (Kokoro `em_alex`, español), generada por Claude con `motor/voz.py`, velocidad 1,1. Solo voz generada; la voz del usuario entra únicamente si él lo indica.
- Todo texto pasa por **stop-slop**: sin muletillas, sin «no es X, es Y», sin rayas, sin frases de póster.

## 7. Lenguaje visual

- **Tipo de video:** ilustrativo. Diseño gráfico 2D o 3D animado en código, no grabación.
- **Modos disponibles:** 2D vectorial (SVG), 3D (Three.js), 2.5D (capas con parallax), personajes con rig.
- **Acabado híbrido (elegido por el usuario):**
  - **Personajes y sala en 2D con volumen** (el Espectador tal como en la propuesta v1).
  - **Lo que muestra la pantalla, en pintura digital** con colores muy vivos (pincelada suave + saturación ×1,3).
  - Propuesta v2 en `motor/propuesta-acabado/propuesta-acabado-v2-hibrido.jpg`.
- **Dirección:** mucho más realista que ref01 y con **colores vívidos**.
- **Luz en 3D:** clave cálida mostaza, contorno frío verde azulado, ambiente oscuro.

### 7.1 Nivel de diseño mínimo (ref01: «muy básico»)

Toda escena cumple estos puntos. Lo que no los cumple se rehace antes de mostrarlo.

1. **Personas con forma humana:** cabeza, cuello, hombros, brazos con codo y manos; ropa con pliegues o costuras. Nunca figuras de rectángulos. Rostro estilizado permitido (sin parecido con actores), visto de perfil, tres cuartos o espalda.
2. **Volumen:** al menos 3 tonos por objeto (luz, base, sombra) y sombra de contacto en el suelo.
3. **Luz con dirección:** una fuente visible o motivada (ventana, lámpara, pantalla) y su reflejo en las caras y objetos cercanos.
4. **Profundidad:** mínimo 3 planos (frente, medio, fondo) que se mueven a distinta velocidad.
5. **Atmósfera:** bruma, polvo en el aire o partículas, y grano o textura suave encima de todo.
6. **Detalles que informan:** cada lugar tiene 2 o más objetos que cuentan dónde estamos (cuadros, carteles sin texto, plantas, cables, ropa tendida).
7. **Vida en la escena:** algo se mueve siempre, aunque sea poco (humo, cortina, luz que parpadea, respiración del personaje).
8. **Look vívido:** saturación 0,40 a 0,75; contraste 40 o más; luminosidad 45 a 170 (ref01: saturación 0,20 a 0,28, se veía apagado). Lo mide `motor/validar.py`.
9. **Escala real:** el Espectador sentado tiene hombros de 0,8 veces el ancho de su butaca; el respaldo tapa su espalda.
10. **De espaldas se ve pelo, no cara:** una nuca sin pelo se lee como un rostro vacío (error corregido en la propuesta v1).
11. **El texto no tapa a ningún sujeto** (personas, el objeto protagonista, la acción).
12. **Sentado dentro, no encima:** una persona sentada queda detrás del respaldo de su butaca; solo se ven cabeza y hombros sobre él. Nunca se dibuja el cuerpo por delante de su propio asiento.
13. **La luz sigue su fuente:** el haz del proyector va del proyector a la pantalla y la ilumina entera; no deja bordes ni líneas marcadas sobre la imagen proyectada.
14. **Nada ajeno al video dentro del fotograma:** ni etiquetas de prueba, ni rótulos de comparación, ni marcas de agua. Las comparaciones se rotulan fuera de la imagen, en el mensaje.

### 7.2 Validación por fotograma

Ningún fotograma llega al usuario sin pasar dos filtros:

1. **Medición** con `motor/validar.py`: look de cada segundo, tramos quietos de más de 3 s y duración.
2. **Registro de errores** (no se repiten): cada error que el usuario marca o que Claude encuentra se agrega a §7.1 como regla. Errores ya corregidos: texto sobre el Espectador; Espectador más grande que su butaca; nuca sin pelo que parecía una cara; Espectador encima de la butaca; etiqueta de prueba dentro del fotograma; haz del proyector con borde sobre la pantalla.
3. **Revisión visual** de Claude: hoja de contacto completa + acercamiento a cada sujeto, punto por punto de §7.1. Lo que falla se rehace antes de mostrarlo.

## 8. Gustos extraídos de referencias

- **ref01:** estructura «Imagina que…» / «Se trata de…» y narración sin nombres hasta el final. Diseño rechazado por básico (ver §7.1). Detalle en `referencias/GUSTOS.md`.

## 9. Historial de cambios

- v0 (28-11-2026): estilo base tomado de la skill «resenas-cine-tiktok». Plantilla de prueba en `motor/plantilla/`.
- v0.1 (28-11-2026): **aprobados** texto, color, tipografía y posición de la plantilla v0. Se agrega el lenguaje visual ilustrativo 2D/3D (§7).
- v0.2 (28-11-2026): ref01. Estructura narrativa aprobada (§6), nivel de diseño mínimo (§7.1), nada quieto más de 3 s y transiciones con movimiento de cámara (§5).
- v0.3 (28-11-2026): duración 61 s mínimo y objetivo 70-90 s; voz Alex; dinamismo obligatorio; acabado preferido pintura digital o 2D con volumen; look vívido con rangos medibles; validación por fotograma (§7.2).
- v0.4 (28-11-2026): acabado híbrido (2D con volumen + pantalla en pintura digital vívida); voz Alex aprobada; reglas 12-14 y registro de errores corregidos.
