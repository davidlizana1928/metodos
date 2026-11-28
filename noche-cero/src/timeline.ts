// words.json (lo genera voice.py): [{ word, start, end, bold, seg }]
export type Palabra = { word: string; start: number; end: number; bold: boolean; seg: number };

export type Demo =
  | { tipo: "imagen"; src: string; expandir?: boolean } // imagen en public/ (la tarjeta puede crecer a pantalla completa)
  | { tipo: "texto"; texto: string } // frase clave grande dentro de la tarjeta
  | { tipo: "contador"; desde: number; hasta: number; prefijo?: string; sufijo?: string; etiqueta?: string }
  | { tipo: "ondas"; etiqueta?: string };

export type Guion = {
  titulo: string; // título en Chile
  subtitulo: string; // título original y año, o solo el año
  hook: { segmentos: number[]; frase: string; demo: Demo };
  bloques: { segmentos: number[]; prompt: string; keyword?: string; demo: Demo }[]; // 5 bloques
  cta: { segmentos: number[]; prompt: string; keyword?: string };
};

export type Tramo = { from: number; dur: number; palabras: Palabra[] };

// Todos los tiempos de entrada salen de words.json:
// cada escena empieza en la primera palabra de su primer segmento.
export const calcularTimeline = (palabras: Palabra[], guion: Guion, fps: number) => {
  const escenas = [guion.hook.segmentos, ...guion.bloques.map((b) => b.segmentos), guion.cta.segmentos];
  const inicios = escenas.map((segs, i) => {
    if (i === 0) return 0;
    const w = palabras.find((p) => segs.includes(p.seg));
    if (!w) throw new Error(`No hay palabras para los segmentos ${segs.join(",")}`);
    return Math.round(w.start * fps);
  });
  const fin = Math.round((palabras[palabras.length - 1].end + 1.0) * fps); // voz + 1 s
  const tramos: Tramo[] = escenas.map((segs, i) => ({
    from: inicios[i],
    dur: (i + 1 < inicios.length ? inicios[i + 1] : fin) - inicios[i],
    palabras: palabras.filter((p) => segs.includes(p.seg)),
  }));
  return { hook: tramos[0], bloques: tramos.slice(1, -1), cta: tramos[tramos.length - 1], total: fin };
};

// Fotograma (relativo al tramo) de la primera palabra clave; si no hay, un valor por defecto
export const momentoClave = (tramo: Tramo, fps: number, porDefecto: number, minimo = 0) => {
  const w = tramo.palabras.find((p) => p.bold);
  const f = w ? Math.round(w.start * fps) - tramo.from : porDefecto;
  return Math.min(Math.max(f, minimo), tramo.dur - 10);
};
