import { spring, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../theme";
import type { Palabra } from "../timeline";

// Agrupa de 1 a 3 palabras; corta en puntuación o pausas
const agrupar = (ws: Palabra[]) => {
  const grupos: Palabra[][] = [];
  let g: Palabra[] = [];
  ws.forEach((w, i) => {
    g.push(w);
    const sig = ws[i + 1];
    const corte =
      g.length === 3 || /[.,;:!?…]$/.test(w.word) || !sig || sig.start - w.end > 0.25 || sig.seg !== w.seg;
    if (corte) {
      grupos.push(g);
      g = [];
    }
  });
  return grupos;
};

// Subtítulos al 72 % de altura: palabra activa blanca, siguientes en gris 35 %
export const Subtitles: React.FC<{ palabras: Palabra[] }> = ({ palabras }) => {
  const frame = useCurrentFrame();
  const { fps, height } = useVideoConfig();
  const t = frame / fps;
  const grupos = agrupar(palabras);
  const idx = grupos.findIndex((g, i) => {
    const fin = grupos[i + 1] ? grupos[i + 1][0].start : g[g.length - 1].end + 0.6;
    return t >= g[0].start - 0.05 && t < fin;
  });
  if (idx < 0) return null;
  const g = grupos[idx];
  const pop = spring({ frame: frame - Math.round(g[0].start * fps), fps, config: { damping: 200 }, durationInFrames: 8 });
  return (
    <div
      style={{
        position: "absolute",
        left: 60,
        right: 60,
        top: height * 0.72,
        translate: "0 -50%",
        display: "flex",
        justifyContent: "center",
        flexWrap: "wrap",
        gap: "0 22px",
        fontFamily: theme.fonts.ui,
        fontWeight: 800,
        fontSize: 76,
        lineHeight: 1.15,
        textAlign: "center",
        scale: 0.94 + 0.06 * pop,
        textShadow: "0 6px 30px rgba(0,0,0,0.85)",
      }}
    >
      {g.map((w, i) => {
        const dicha = t >= w.start - 0.03;
        return (
          <span
            key={i}
            style={{
              color: w.bold ? theme.accent : theme.text,
              opacity: dicha ? 1 : 0.35,
              textShadow: w.bold && dicha ? `${theme.accentGlow}, 0 6px 30px rgba(0,0,0,0.85)` : undefined,
            }}
          >
            {w.word}
          </span>
        );
      })}
    </div>
  );
};
