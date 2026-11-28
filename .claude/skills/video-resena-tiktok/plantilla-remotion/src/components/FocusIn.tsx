import { Easing, interpolate, useCurrentFrame } from "remotion";

// Entrada con foco: blur 20px → 0, scale 0.92 → 1, opacity 0 → 1
export const FocusIn: React.FC<{
  delay?: number; // en fotogramas, relativo a la secuencia
  duracion?: number;
  style?: React.CSSProperties;
  children: React.ReactNode;
}> = ({ delay = 0, duracion = 18, style, children }) => {
  const frame = useCurrentFrame();
  const opts = {
    extrapolateLeft: "clamp" as const,
    extrapolateRight: "clamp" as const,
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  };
  const r = [delay, delay + duracion];
  return (
    <div
      style={{
        ...style,
        filter: `blur(${interpolate(frame, r, [20, 0], opts)}px)`,
        scale: interpolate(frame, r, [0.92, 1], opts),
        opacity: interpolate(frame, r, [0, 1], opts),
      }}
    >
      {children}
    </div>
  );
};
