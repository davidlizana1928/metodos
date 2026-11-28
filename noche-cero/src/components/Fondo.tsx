import { AbsoluteFill, useCurrentFrame } from "remotion";
import { theme } from "../theme";

// Fondo: degradado #040404 → #0A090E, halo radial superior y grano sutil
export const Fondo: React.FC = () => {
  const frame = useCurrentFrame();
  const seed = frame % 6; // el grano cambia cada fotograma, de forma determinista
  return (
    <AbsoluteFill style={{ background: `linear-gradient(180deg, ${theme.bg.from} 0%, ${theme.bg.to} 100%)` }}>
      <AbsoluteFill
        style={{ background: `radial-gradient(ellipse 85% 42% at 50% 0%, ${theme.halo} 0%, rgba(42,32,19,0) 100%)` }}
      />
      <AbsoluteFill style={{ opacity: theme.grano, mixBlendMode: "overlay" }}>
        <svg width="100%" height="100%">
          <filter id={`grano${seed}`}>
            <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed={seed} stitchTiles="stitch" />
            <feColorMatrix type="saturate" values="0" />
          </filter>
          <rect width="100%" height="100%" filter={`url(#grano${seed})`} />
        </svg>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
