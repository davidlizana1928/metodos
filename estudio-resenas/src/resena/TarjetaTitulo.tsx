import { loadFont } from "@remotion/google-fonts/Montserrat";
import { Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";

const { fontFamily } = loadFont("normal", { weights: ["500", "800"], subsets: ["latin"] });

// Tarjeta del título (regla 7.8): banda oscura semitransparente en la zona superior,
// bajo la barra de TikTok y lejos de los botones de la derecha. Entra con «Se trata de».
export const TarjetaTitulo: React.FC<{ titulo: string; subtitulo: string }> = ({ titulo, subtitulo }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <div
      style={{
        position: "absolute",
        top: 250,
        left: 90,
        right: 150,
        padding: "34px 40px 38px",
        borderRadius: 28,
        background: "rgba(6,8,10,0.66)",
        textAlign: "center",
        fontFamily,
        opacity: interpolate(frame, [0, 0.4 * fps], [0, 1], { extrapolateRight: "clamp" }),
        translate: interpolate(frame, [0, 0.6 * fps], ["0px 24px", "0px 0px"], {
          extrapolateRight: "clamp",
          easing: Easing.bezier(0.16, 1, 0.3, 1),
        }),
      }}
    >
      <div style={{ fontWeight: 800, fontSize: 74, lineHeight: 1.08, color: "#f2ede2" }}>{titulo}</div>
      <div style={{ width: 200, height: 5, background: "#c8243a", margin: "22px auto 18px" }} />
      <div style={{ fontWeight: 500, fontSize: 40, color: "#d9d4c8" }}>{subtitulo}</div>
    </div>
  );
};
