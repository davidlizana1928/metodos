import { interpolate, random, useCurrentFrame } from "remotion";
import { theme } from "../theme";

// Forma de onda con cabezal que avanza (barras ya recorridas en acento)
export const Waveform: React.FC<{ duracion: number; ancho?: number; alto?: number; barras?: number }> = ({
  duracion,
  ancho = 820,
  alto = 220,
  barras = 56,
}) => {
  const frame = useCurrentFrame();
  const avance = interpolate(frame, [0, duracion], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const paso = ancho / barras;
  return (
    <div style={{ position: "relative", width: ancho, height: alto }}>
      {Array.from({ length: barras }).map((_, i) => {
        const base = 0.25 + 0.75 * random(`onda${i}`);
        const vivo = 0.75 + 0.25 * Math.sin(frame / 4 + i * 0.7);
        const h = alto * base * vivo;
        const pasada = i / barras < avance;
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: i * paso + paso * 0.2,
              top: (alto - h) / 2,
              width: paso * 0.6,
              height: h,
              borderRadius: paso,
              background: pasada ? theme.accent : "rgba(255,255,255,0.2)",
              boxShadow: pasada ? theme.accentGlow : undefined,
            }}
          />
        );
      })}
      <div
        style={{
          position: "absolute",
          left: avance * ancho - 2,
          top: -16,
          width: 4,
          height: alto + 32,
          borderRadius: 2,
          background: theme.text,
          boxShadow: "0 0 18px rgba(255,255,255,0.6)",
        }}
      />
    </div>
  );
};

// Contador con separador de miles (1 → 1.000)
const miles = (n: number) => String(n).replace(/\B(?=(\d{3})+(?!\d))/g, ".");

export const Counter: React.FC<{
  desde?: number;
  hasta?: number;
  duracion: number;
  prefijo?: string;
  sufijo?: string;
  size?: number;
}> = ({ desde = 1, hasta = 1000, duracion, prefijo = "", sufijo = "", size = 200 }) => {
  const frame = useCurrentFrame();
  const v = Math.round(
    interpolate(frame, [0, duracion], [desde, hasta], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: (t) => 1 - Math.pow(1 - t, 3),
    }),
  );
  return (
    <div
      style={{
        fontFamily: theme.fonts.ui,
        fontWeight: 800,
        fontSize: size,
        color: theme.accent,
        textShadow: theme.accentGlow,
        fontVariantNumeric: "tabular-nums",
      }}
    >
      {prefijo}
      {miles(v)}
      {sufijo}
    </div>
  );
};
