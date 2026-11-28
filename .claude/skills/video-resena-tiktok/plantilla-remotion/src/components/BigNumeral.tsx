import { spring, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../theme";

// Numeral grande en Playfair Display Italic
export const BigNumeral: React.FC<{ n: number; size?: number }> = ({ n, size = 300 }) => (
  <div
    style={{
      fontFamily: theme.fonts.numeral,
      fontStyle: "italic",
      fontWeight: 400,
      fontSize: size,
      lineHeight: 1,
      color: theme.text,
      textShadow: "0 10px 60px rgba(240,176,64,0.18)",
    }}
  >
    {String(n).padStart(2, "0")}
  </div>
);

// 5 pasos; el activo es un trazo alargado en acento
export const ProgressDots: React.FC<{ activo: number; total?: number }> = ({ activo, total = 5 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({ frame, fps, config: { damping: 200 } });
  return (
    <div style={{ display: "flex", gap: 14, alignItems: "center" }}>
      {Array.from({ length: total }).map((_, i) => {
        const esActivo = i + 1 === activo;
        return (
          <div
            key={i}
            style={{
              height: 14,
              width: esActivo ? 14 + 50 * s : 14,
              borderRadius: 7,
              background: esActivo ? theme.accent : i + 1 < activo ? "rgba(240,176,64,0.45)" : "rgba(255,255,255,0.22)",
              boxShadow: esActivo ? theme.accentGlow : undefined,
            }}
          />
        );
      })}
    </div>
  );
};
