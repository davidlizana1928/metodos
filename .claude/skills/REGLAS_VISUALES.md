# Reglas visuales del video (reseñas de cine)

Estas reglas salen de la revisión de `resena-resident-evil-noche-cero`. Todo código nuevo de escenas debe cumplirlas.

## 1. Escala y proporciones (obligatorio)

Todo objeto se dibuja con medidas reales en metros, usando `escala.py`. Nunca se elige un tamaño en píxeles a ojo.

Medidas de referencia:

| Objeto | Medida real |
|---|---|
| Persona adulta | 1,75 m de alto, hombros de 0,45 m |
| Auto de reparto | 1,75 m de ancho, 1,45 m de alto |
| Patrulla | 1,80 m de ancho, 1,50 m de alto |
| Camioneta negra | 1,95 m de ancho, 1,90 m de alto |
| Butaca de cine | 0,55 m de ancho, respaldo de 0,95 m |
| Pantalla de cine | 12 m de ancho |
| Caja térmica | 0,50 x 0,30 m |
| Mostrador | 1,00 m de alto |
| Buzón | 1,10 m de alto |
| Mujer adulta | 1,65 m de alto |

Reglas concretas:
- **Un solo plano de profundidad**: un objeto apoyado en el suelo se mide con `ppm(y)`, donde `y` es la línea de sus pies. Dos objetos del mismo plano comparten `ppm`.
- **Auto y persona en el mismo plano**: el auto mide alrededor de 0,83 veces la persona. Si el auto se ve más alto que la persona, o es menos de la mitad, está mal.
- **Hombros vs butaca**: los hombros de quien está sentado son ~0,8 veces una butaca de la misma fila.
- **Pantalla vs butaca**: la pantalla se ve unas 4 a 5 butacas de ancho desde la fila del espectador. Con 12 m de pantalla, eso implica que está a unas 5 veces la distancia de la fila. No llenar la sala con butacas: en primer plano caben 4 a 5 por fila, y al fondo se dibujan más pequeñas.
- **Mostrador**: el borde superior está a 1,00 m del suelo. Quien está detrás mide su altura real a esa profundidad; el mostrador tapa lo que queda debajo.
- **Objetos cercanos**: un personaje en primer plano puede llenar el cuadro, pero debe medir 1,75 m a esa profundidad.

Verificación: `python3 escala.py` imprime OK o MAL para las proporciones clave. Correrlo antes de cada render.

## 2. Texto en pantalla (buenas prácticas que funcionaron)

Los textos le dan dinamismo y enganche. Se mantienen estas reglas:
- Máximo 3 textos extra por video, y solo números o palabras clave («ÚLTIMA ENTREGA», «URGENTE», «4»). Nunca nombres.
- **Banner de palabra clave**: fondo rojo oscuro con texto blanco o crema en fuente Inter Display Black, centrado en la zona baja, con entrada y salida suaves de 0,15 s.
- **Sello sobre un objeto**: «URGENTE» va rotado -8°, dentro de un recuadro blanco, sobre la etiqueta de la caja, con un leve zoom que se apaga en 0,15 s.
- **Número junto a un objeto**: el «4» amarillo con contorno oscuro va al lado de las balas, para que se lea como cantidad.
- **Tarjeta del título**: banda oscura semitransparente en la zona superior, bajo la barra de TikTok. El título va en rojo y crema en dos líneas y el año en pequeño. Entra con fundido de 0,35 s y se mantiene hasta el final.
- Duración de cada texto: 1 a 1,5 s. Ningún texto tapa la cara de quien mira ni los botones de la derecha.

## 3. Ritmo y voz

- Voz guía: `voz.py` con Kokoro, voz `em_alex` (masculina) como regla general del proyecto. Velocidad 1,0.
- Pausas: entre frases 0,16 s, en «…» 0,18 s. Ningún silencio dentro de la voz pasa de 0,3 s, y el video cierra con 1 s.
- Los cortes de imagen caen en los tiempos fuertes del compás de 100 BPM (cada 0,6 s).
