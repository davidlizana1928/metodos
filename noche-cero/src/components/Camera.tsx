import { AbsoluteFill, spring, useCurrentFrame, useVideoConfig } from "remotion";

export type CamKey = { at: number; scale?: number; x?: number; y?: number };

// Contenedor de cámara: aplica translate/scale a toda la escena.
// Entre cada keyframe se mueve con spring({ damping: 200 }), sin cortes duros.
export const Camera: React.FC<{ keyframes: CamKey[]; children: React.ReactNode }> = ({ keyframes, children }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  let scale = keyframes[0]?.scale ?? 1;
  let x = keyframes[0]?.x ?? 0;
  let y = keyframes[0]?.y ?? 0;
  for (const k of keyframes.slice(1)) {
    const p = spring({ frame: frame - k.at, fps, config: { damping: 200 } });
    scale += ((k.scale ?? scale) - scale) * p;
    x += ((k.x ?? x) - x) * p;
    y += ((k.y ?? y) - y) * p;
  }
  return (
    <AbsoluteFill style={{ scale, translate: `${x}px ${y}px`, transformOrigin: "50% 50%" }}>{children}</AbsoluteFill>
  );
};
