import { theme } from "../theme";

// Tarjeta de vidrio con perspectiva 3D (rotateX / rotateY en grados)
export const GlassCard: React.FC<{
  rotateX?: number;
  rotateY?: number;
  width: number | string;
  height: number | string;
  radius?: number;
  padding?: number;
  style?: React.CSSProperties;
  children?: React.ReactNode;
}> = ({ rotateX = 0, rotateY = 0, width, height, radius = theme.card.radius, padding = 0, style, children }) => (
  <div style={{ perspective: 1600, ...style }}>
    <div
      style={{
        width,
        height,
        padding,
        boxSizing: "border-box",
        background: theme.card.bg,
        border: theme.card.border,
        borderRadius: radius,
        boxShadow: theme.card.shadow,
        backdropFilter: "blur(18px)",
        overflow: "hidden",
        transform: `rotateX(${rotateX}deg) rotateY(${rotateY}deg)`,
        transformStyle: "preserve-3d",
        position: "relative",
      }}
    >
      {children}
    </div>
  </div>
);
