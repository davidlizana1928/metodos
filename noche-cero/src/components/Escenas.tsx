import { AbsoluteFill, interpolate, Sequence, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../theme";
import { momentoClave, type Demo as DemoT, type Tramo } from "../timeline";
import { BigNumeral, ProgressDots } from "./BigNumeral";
import { Camera } from "./Camera";
import { Demo } from "./Demo";
import { FocusIn } from "./FocusIn";
import { PromptBar } from "./PromptBar";

// Salida de cada escena: blur-out en los últimos 0,4 s (la cámara hace zoom a la vez)
const BlurOut: React.FC<{ dur: number; children: React.ReactNode }> = ({ dur, children }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const r = [dur - 0.4 * fps, dur];
  const o = { extrapolateLeft: "clamp" as const, extrapolateRight: "clamp" as const };
  return (
    <AbsoluteFill style={{ filter: frame >= r[0] ? `blur(${interpolate(frame, r, [0, 20], o)}px)` : undefined, opacity: interpolate(frame, r, [1, 0.2], o) }}>
      {children}
    </AbsoluteFill>
  );
};

const zoomSalida = (dur: number, fps: number) => ({ at: Math.round(dur - 0.45 * fps), scale: 1.14 });

// HOOK: «Imagina que…» en Playfair + tarjeta con la primera imagen
export const Hook: React.FC<{ tramo: Tramo; frase: string; demo: DemoT }> = ({ tramo, frase, demo }) => {
  const { fps } = useVideoConfig();
  return (
    <Camera keyframes={[{ at: 0, scale: 1.06 }, { at: 1, scale: 1 }, zoomSalida(tramo.dur, fps)]}>
      <BlurOut dur={tramo.dur}>
        <FocusIn style={{ position: "absolute", top: 230, left: 0, right: 0, textAlign: "center" }}>
          <div style={{ fontFamily: theme.fonts.numeral, fontStyle: "italic", fontSize: 130, color: theme.text }}>{frase}</div>
        </FocusIn>
        <FocusIn delay={Math.round(0.5 * fps)} duracion={22} style={{ position: "absolute", inset: 0 }}>
          <Demo demo={demo} duracion={tramo.dur} />
        </FocusIn>
      </BlurOut>
    </Camera>
  );
};

// BLOQUE: numeral → PromptBar escribe → demo en GlassCard (entra con la palabra clave de words.json)
export const Bloque: React.FC<{
  n: number;
  tramo: Tramo;
  prompt: string;
  keyword?: string;
  demo: DemoT;
}> = ({ n, tramo, prompt, keyword, demo }) => {
  const { fps } = useVideoConfig();
  const fPrompt = Math.round(0.6 * fps);
  const fDemo = momentoClave(tramo, fps, Math.round(2.4 * fps), Math.round(1.8 * fps));
  const fExpandir = Math.min(fDemo + Math.round(1.6 * fps), tramo.dur - Math.round(1.2 * fps));
  return (
    <Camera
      keyframes={[
        { at: 0, scale: 1.08, y: 60 },
        { at: 1, scale: 1, y: 0 },
        { at: fDemo, scale: 1, y: -20 },
        zoomSalida(tramo.dur, fps),
      ]}
    >
      <BlurOut dur={tramo.dur}>
        <FocusIn style={{ position: "absolute", top: 170, left: 90, display: "flex", alignItems: "flex-end", gap: 36 }}>
          <BigNumeral n={n} size={230} />
          <div style={{ paddingBottom: 46 }}>
            <ProgressDots activo={n} />
          </div>
        </FocusIn>
        <FocusIn delay={fPrompt - 6} style={{ position: "absolute", top: 420, left: 80 }}>
          <PromptBar texto={prompt} keyword={keyword} inicio={fPrompt} />
        </FocusIn>
        {/* la demo aparece cuando la voz dice la palabra clave */}
        <AbsoluteFillDesde desde={fDemo}>
          <FocusIn duracion={20} style={{ position: "absolute", inset: 0 }}>
            <Demo demo={demo} duracion={tramo.dur - fDemo} expandirEn={fExpandir - fDemo} />
          </FocusIn>
        </AbsoluteFillDesde>
      </BlurOut>
    </Camera>
  );
};

// CTA: «Se trata de…» con tarjeta del título + pregunta espejo en la PromptBar
export const CTA: React.FC<{ tramo: Tramo; titulo: string; subtitulo: string; prompt: string; keyword?: string }> = ({
  tramo,
  titulo,
  subtitulo,
  prompt,
  keyword,
}) => {
  const { fps } = useVideoConfig();
  const pregunta = tramo.palabras.find((p) => p.word.startsWith("Si") && p.seg !== tramo.palabras[0].seg);
  const fPregunta = pregunta ? Math.round(pregunta.start * fps) - tramo.from : Math.round(2.2 * fps);
  return (
    <Camera keyframes={[{ at: 0, scale: 1.08 }, { at: 1, scale: 1 }, { at: fPregunta, scale: 1, y: -60 }]}>
      <FocusIn style={{ position: "absolute", top: 330, left: 90, right: 90 }}>
        <div
          style={{
            background: theme.card.bg,
            border: theme.card.border,
            borderRadius: theme.card.radius,
            boxShadow: theme.card.shadow,
            padding: "56px 50px",
            textAlign: "center",
          }}
        >
          <div style={{ fontFamily: theme.fonts.ui, fontWeight: 700, fontSize: 30, letterSpacing: 8, color: theme.textDim }}>
            SE TRATA DE
          </div>
          <div style={{ fontFamily: theme.fonts.ui, fontWeight: 800, fontSize: 86, lineHeight: 1.06, color: theme.text, margin: "22px 0" }}>
            {titulo}
          </div>
          <div style={{ width: 160, height: 4, margin: "0 auto 22px", background: theme.accent, boxShadow: theme.accentGlow }} />
          <div style={{ fontFamily: theme.fonts.numeral, fontStyle: "italic", fontSize: 46, color: theme.textDim }}>{subtitulo}</div>
        </div>
      </FocusIn>
      <AbsoluteFillDesde desde={fPregunta}>
        <FocusIn style={{ position: "absolute", top: 940, left: 80 }}>
          <PromptBar texto={prompt} keyword={keyword} inicio={0} letrasPorSegundo={20} />
        </FocusIn>
      </AbsoluteFillDesde>
    </Camera>
  );
};

// Monta a sus hijos recién desde un fotograma (con el tiempo local reiniciado)
const AbsoluteFillDesde: React.FC<{ desde: number; children: React.ReactNode }> = ({ desde, children }) => (
  <Sequence from={desde} layout="none">
    {children}
  </Sequence>
);
