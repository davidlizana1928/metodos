import { loadFont } from "@remotion/google-fonts/PlayfairDisplay";
import { Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { projectScreen, screenPower } from "./camera";

const { fontFamily } = loadFont("italic", { weights: ["700"], subsets: ["latin"] });

// "Imagina que..." escrito letra por letra, pegado a la pantalla del cine
export const ScreenText: React.FC<{ text: string; startFrame: number }> = ({
  text,
  startFrame,
}) => {
  const frame = useCurrentFrame();
  const { width, height, fps } = useVideoConfig();
  const rect = projectScreen(frame, width, height);
  const power = screenPower(frame);

  const charsPerSecond = 13;
  const typed = Math.floor(
    interpolate(frame, [startFrame, startFrame + (text.length / charsPerSecond) * fps], [0, text.length], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    }),
  );
  const cursorOn = Math.floor(frame / 8) % 2 === 0;
  const done = typed >= text.length;

  return (
    <div
      style={{
        position: "absolute",
        left: rect.left,
        top: rect.top,
        width: rect.width,
        height: rect.height,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        opacity: power,
      }}
    >
      <div
        style={{
          fontFamily,
          fontStyle: "italic",
          fontWeight: 700,
          fontSize: Math.min(rect.width, width * 0.92) * 0.13,
          color: "#14121c",
          whiteSpace: "pre",
          textShadow: `${-rect.width * 0.004}px 0 #25d6e6, ${rect.width * 0.004}px 0 #ff2d55`,
          scale: interpolate(frame, [startFrame, startFrame + 3 * fps], [0.96, 1.02], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.bezier(0.16, 1, 0.3, 1),
          }),
        }}
      >
        {text.slice(0, typed)}
        <span style={{ opacity: !done || cursorOn ? 1 : 0, color: "#ff2d55" }}>|</span>
      </div>
    </div>
  );
};
