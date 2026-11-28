import { Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../theme";
import type { Demo as DemoT } from "../timeline";
import { GlassCard } from "./GlassCard";
import { Counter, Waveform } from "./Waveform";

const W = 880;
const H = 640;

// Contenido de demostración dentro de una GlassCard con leve rotación 3D.
// Con imagen + expandir, la tarjeta crece a pantalla completa en "expandirEn".
export const Demo: React.FC<{ demo: DemoT; duracion: number; expandirEn?: number }> = ({ demo, duracion, expandirEn }) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const giroY = interpolate(frame, [0, duracion], [-10, 6]);
  const giroX = interpolate(frame, [0, duracion], [8, 2]);
  const e =
    demo.tipo === "imagen" && demo.expandir && expandirEn !== undefined
      ? spring({ frame: frame - expandirEn, fps, config: { damping: 200 } })
      : 0;

  const etiqueta = (txt?: string) =>
    txt ? (
      <div
        style={{
          fontFamily: theme.fonts.ui,
          fontWeight: 700,
          fontSize: 30,
          letterSpacing: 6,
          color: theme.textDim,
          marginBottom: 20,
        }}
      >
        {txt}
      </div>
    ) : null;

  let contenido: React.ReactNode;
  if (demo.tipo === "imagen") {
    contenido = (
      <Img
        src={staticFile(demo.src)}
        style={{ width: "100%", height: "100%", objectFit: "cover", scale: interpolate(frame, [0, duracion], [1.08, 1]) }}
      />
    );
  } else if (demo.tipo === "texto") {
    contenido = (
      <div
        style={{
          height: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          padding: 70,
          textAlign: "center",
          fontFamily: theme.fonts.numeral,
          fontStyle: "italic",
          fontSize: 92,
          lineHeight: 1.12,
          color: theme.text,
        }}
      >
        {demo.texto}
      </div>
    );
  } else if (demo.tipo === "contador") {
    contenido = (
      <div style={{ height: "100%", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
        {etiqueta(demo.etiqueta)}
        <Counter desde={demo.desde} hasta={demo.hasta} prefijo={demo.prefijo} sufijo={demo.sufijo} duracion={Math.min(45, duracion)} size={240} />
      </div>
    );
  } else {
    contenido = (
      <div style={{ height: "100%", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
        {etiqueta(demo.etiqueta)}
        <Waveform duracion={duracion} ancho={740} />
      </div>
    );
  }

  return (
    <div
      style={{
        position: "absolute",
        left: interpolate(e, [0, 1], [(width - W) / 2, 0]),
        top: interpolate(e, [0, 1], [height * 0.335, 0]),
        zIndex: e > 0 ? 5 : undefined,
      }}
    >
      <GlassCard
        width={interpolate(e, [0, 1], [W, width])}
        height={interpolate(e, [0, 1], [H, height])}
        radius={interpolate(e, [0, 1], [theme.card.radius, 0])}
        rotateX={giroX * (1 - e)}
        rotateY={giroY * (1 - e)}
      >
        {contenido}
      </GlassCard>
    </div>
  );
};
