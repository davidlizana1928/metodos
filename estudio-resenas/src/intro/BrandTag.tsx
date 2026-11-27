import { loadFont } from "@remotion/google-fonts/Montserrat";
import { Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";

const { fontFamily } = loadFont("normal", { weights: ["800", "900"], subsets: ["latin"] });

// Cinta negra con bordes cian/rojo, igual que las miniaturas del canal
export const BrandTag: React.FC<{ title: string; handle: string }> = ({ title, handle }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const pop = {
    extrapolateLeft: "clamp" as const,
    extrapolateRight: "clamp" as const,
    easing: Easing.spring({ damping: 12, stiffness: 140 }),
  };

  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        right: 0,
        top: 1240,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: 46,
      }}
    >
      <div
        style={{
          position: "relative",
          rotate: "-6deg",
          scale: interpolate(frame, [0, 0.7 * fps], [2.4, 1], { ...pop, output: "perceptual-scale" }),
          opacity: interpolate(frame, [0, 0.15 * fps], [0, 1], { extrapolateRight: "clamp" }),
        }}
      >
        <div style={{ position: "absolute", inset: 0, background: "#25d6e6", translate: interpolate(frame, [0, 0.6 * fps], ["0px 0px", "-16px -14px"], pop) }} />
        <div style={{ position: "absolute", inset: 0, background: "#ff2d55", translate: interpolate(frame, [0, 0.6 * fps], ["0px 0px", "16px 14px"], pop) }} />
        <div
          style={{
            position: "relative",
            background: "#0a0a0f",
            color: "white",
            fontFamily,
            fontWeight: 900,
            fontSize: 92,
            letterSpacing: 1,
            padding: "26px 54px",
            whiteSpace: "nowrap",
          }}
        >
          {title}
        </div>
      </div>
      <div
        style={{
          fontFamily,
          fontWeight: 800,
          fontSize: 52,
          color: "white",
          textShadow: "0 4px 18px rgba(0,0,0,0.9)",
          opacity: interpolate(frame, [0.5 * fps, 1 * fps], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
          translate: interpolate(frame, [0.5 * fps, 1.1 * fps], ["0px 40px", "0px 0px"], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.bezier(0.16, 1, 0.3, 1),
          }),
        }}
      >
        {handle}
      </div>
    </div>
  );
};

