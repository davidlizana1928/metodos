import { spring, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "../theme";

// Píldora de vidrio: el texto se escribe con cursor; la keyword va en acento; botón ↑ circular.
export const PromptBar: React.FC<{
  texto: string;
  keyword?: string;
  inicio?: number; // fotograma (relativo) en que empieza a escribir
  letrasPorSegundo?: number;
  ancho?: number;
}> = ({ texto, keyword, inicio = 0, letrasPorSegundo = 22, ancho = 920 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const escritas = Math.max(0, Math.min(texto.length, Math.floor(((frame - inicio) / fps) * letrasPorSegundo)));
  const listo = escritas >= texto.length;
  const finEscritura = inicio + Math.ceil((texto.length / letrasPorSegundo) * fps);

  const k = keyword ? texto.indexOf(keyword) : -1;
  const partes =
    k >= 0
      ? [
          { t: texto.slice(0, k), kw: false },
          { t: keyword!, kw: true },
          { t: texto.slice(k + keyword!.length), kw: false },
        ]
      : [{ t: texto, kw: false }];
  let resto = escritas;

  const pulso = spring({ frame: frame - finEscritura, fps, config: { damping: 12, stiffness: 180 } });

  return (
    <div
      style={{
        width: ancho,
        display: "flex",
        alignItems: "center",
        gap: 24,
        padding: "22px 22px 22px 44px",
        borderRadius: 999,
        background: theme.card.bg,
        border: theme.card.border,
        boxShadow: theme.card.shadow,
        backdropFilter: "blur(18px)",
        boxSizing: "border-box",
      }}
    >
      <div style={{ flex: 1, fontFamily: theme.fonts.ui, fontWeight: 500, fontSize: 42, lineHeight: 1.25, color: theme.text }}>
        {partes.map((p, i) => {
          const visible = p.t.slice(0, Math.max(0, resto));
          resto -= p.t.length;
          return (
            <span
              key={i}
              style={p.kw ? { color: theme.accent, textShadow: theme.accentGlow, fontWeight: 700 } : undefined}
            >
              {visible}
            </span>
          );
        })}
        <span style={{ color: theme.accent, opacity: !listo || Math.floor(frame / 15) % 2 === 0 ? 1 : 0 }}>▍</span>
      </div>
      <div
        style={{
          width: 88,
          height: 88,
          flexShrink: 0,
          borderRadius: "50%",
          background: theme.accent,
          boxShadow: theme.accentGlow,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontFamily: theme.fonts.ui,
          fontWeight: 800,
          fontSize: 46,
          color: "#16120a",
          scale: listo ? 1 + 0.12 * Math.sin(Math.PI * Math.min(1, pulso)) : 1,
        }}
      >
        ↑
      </div>
    </div>
  );
};
