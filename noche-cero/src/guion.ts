import type { Guion } from "./timeline";

// ÚNICO archivo que cambia por reseña (junto con public/).
// "segmentos" = números de frase de voice.py (1, 2, 3…). Los tiempos salen de words.json.
// Textos en pantalla: solo los del paquete de reseña; nunca nombres de personas reales ni de personajes.
export const GUION: Guion = {
  titulo: "Resident Evil: Noche Cero",
  subtitulo: "Resident Evil, 2026",
  hook: { segmentos: [1, 2], frase: "Imagina que…", demo: { tipo: "imagen", src: "escenas/ciudad.jpg" } },
  bloques: [
    {
      segmentos: [3, 4],
      prompt: "Tu trabajo: repartidor entre hospitales",
      keyword: "repartidor",
      demo: { tipo: "texto", texto: "Sin armas. Sin entrenamiento." },
    },
    {
      segmentos: [5, 6],
      prompt: "Un último encargo que paga el doble",
      keyword: "el doble",
      demo: { tipo: "contador", desde: 1, hasta: 2, prefijo: "x", etiqueta: "PAGO" },
    },
    {
      segmentos: [7, 8],
      prompt: "Carretera helada, en plena tormenta",
      keyword: "tormenta",
      demo: { tipo: "imagen", src: "escenas/carretera.jpg", expandir: true },
    },
    {
      segmentos: [9, 10],
      prompt: "Un virus escapa del laboratorio",
      keyword: "virus",
      demo: { tipo: "ondas", etiqueta: "ALERTA" },
    },
    {
      segmentos: [11, 12, 13],
      prompt: "Llegaste a entregar… ahora solo sobrevives",
      keyword: "sobrevives",
      demo: { tipo: "texto", texto: "Algo te muerde el brazo." },
    },
  ],
  cta: { segmentos: [14, 15], prompt: "¿Seguirías adelante… o volverías?", keyword: "Seguirías" },
};
