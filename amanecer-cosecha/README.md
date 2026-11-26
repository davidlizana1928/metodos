# Amanecer en la cosecha — motion graphics con Remotion

Video vertical (1080×1920, 30 cuadros por segundo, 1:25) hecho solo con código,
según el guion visual de "Los Juegos del Hambre: Amanecer en la cosecha".

## Cómo usarlo

```bash
npm install          # instala las dependencias (solo la primera vez)
npm run dev          # abre Remotion Studio para ver y ajustar el video
npx remotion render AmanecerCosecha out/amanecer-cosecha.mp4   # exporta el MP4
```

## Dónde está cada cosa

| Archivo | Qué tiene |
| --- | --- |
| `src/Root.tsx` | Tamaño, duración y velocidad del video. |
| `src/Video.tsx` | **El montaje.** Cada toma es un `<Sequence>` con su segundo de inicio (`from`) y su duración. Las frases de la voz están como comentarios. |
| `src/scenes/Intro.tsx` | Cine, perfil con el ojo, vela, humo que dibuja la urna y la plaza EN VIVO. |
| `src/scenes/World.tsx` | Mapa con pulsos y filas, arena, pueblo minero, pradera, visión dorada, fuegos artificiales y los íconos x2. |
| `src/scenes/Capital.tsx` | Sorteo, guardias, foco, tren, estadio, lentes rojos, colgante, cúpula, ventana, valle con escotillas y lente gigante. |
| `src/scenes/Overlays.tsx` | Textos en pantalla, destellos, golpe negro, pulso de cada medio tiempo, grano y viñeta. |
| `src/lib/base.tsx` | Paleta de colores, cámara, polvo, chispas, siluetas, el Espectador y la urna. |
| `src/lib/map.tsx` | El mapa pintado del país. |

## Ajustar a tu voz grabada

1. Copia tu audio a `public/voz.mp3` (todavía no está conectado al video:
   hay que agregar un `<Audio>` en `src/Video.tsx`).
2. En `src/Video.tsx` cambia los `from` y `durationInFrames` de cada toma
   (por ejemplo `from={9 * fps}` = empieza en el segundo 9).
3. El pulso de la música está en `BeatPulse` (`halfBeat` = 0,3 s para 100 BPM).
