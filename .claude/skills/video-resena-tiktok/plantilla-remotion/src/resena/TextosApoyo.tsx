import { loadFont } from "@remotion/google-fonts/Montserrat";
import { Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";

const { fontFamily } = loadFont("normal", { weights: ["900"], subsets: ["latin"] });

// Formatos de textos de apoyo del canal (regla 7.8). Se usan solo si el paquete los pide.
// Envolver cada uno en <Sequence from=... durationInFrames=...>.

const entradaSalida = (frame: number, dur: number, fps: number) =>
  interpolate(frame, [0, 0.15 * fps, dur - 0.15 * fps, dur], [0, 1, 1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

// Banner de palabra clave: fondo rojo oscuro, tercio inferior (sobre el 20 % inferior)
export const Banner: React.FC<{ texto: string; duracion: number }> = ({ texto, duracion }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <div style={{ position: "absolute", left: 0, right: 0, top: 1260, display: "flex", justifyContent: "center" }}>
      <div
        style={{
          background: "#7a1020",
          color: "#f6efdf",
          fontFamily,
          fontWeight: 900,
          fontSize: 78,
          padding: "14px 40px",
          opacity: entradaSalida(frame, duracion * fps, fps),
        }}
      >
        {texto}
      </div>
    </div>
  );
};

// Sello sobre un objeto: recuadro rotado -8° con un leve zoom que se apaga
export const Sello: React.FC<{ texto: string; x: number; y: number; duracion: number }> = ({ texto, x, y, duracion }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <div
      style={{
        position: "absolute",
        left: x,
        top: y,
        rotate: "-8deg",
        border: "8px solid #e8e1d0",
        color: "#e8e1d0",
        fontFamily,
        fontWeight: 900,
        fontSize: 84,
        padding: "4px 26px",
        opacity: entradaSalida(frame, duracion * fps, fps),
        scale: interpolate(frame, [0, 0.5 * fps], [1.25, 1], {
          extrapolateRight: "clamp",
          easing: Easing.bezier(0.16, 1, 0.3, 1),
        }),
      }}
    >
      {texto}
    </div>
  );
};

// Número junto a un objeto: amarillo con contorno oscuro
export const Numero: React.FC<{ texto: string; x: number; y: number; duracion: number }> = ({ texto, x, y, duracion }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <div
      style={{
        position: "absolute",
        left: x,
        top: y,
        color: "#ffd23a",
        fontFamily,
        fontWeight: 900,
        fontSize: 120,
        WebkitTextStroke: "6px #111",
        paintOrder: "stroke fill",
        opacity: entradaSalida(frame, duracion * fps, fps),
      }}
    >
      {texto}
    </div>
  );
};
