import { AbsoluteFill, Interactive, interpolate, Sequence, useCurrentFrame, useVideoConfig } from "remotion";
import { BrandTag } from "./BrandTag";
import { CinemaScene } from "./CinemaScene";
import { ScreenText } from "./ScreenText";

export type IntroProps = {
  readonly phrase: string;
  readonly title: string;
  readonly handle: string;
};

// Fundido desde negro al inicio y viñeta oscura en los bordes
const Vignette: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <AbsoluteFill
      style={{
        background:
          "radial-gradient(ellipse at 50% 40%, rgba(0,0,0,0) 45%, rgba(0,0,0,0.75) 100%)",
      }}
    >
      <AbsoluteFill
        style={{
          backgroundColor: "black",
          opacity: interpolate(frame, [0, 0.8 * fps], [1, 0], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
        }}
      />
    </AbsoluteFill>
  );
};

export const IntroImagina: React.FC<IntroProps> = ({ phrase, title, handle }) => {
  const { fps } = useVideoConfig();
  return (
    <AbsoluteFill style={{ backgroundColor: "black" }}>
      <CinemaScene />
      <ScreenText text={phrase} startFrame={Math.round(2.3 * fps)} />
      <Vignette />
      <Sequence from={Math.round(4.9 * fps)} name="Marca del canal" layout="none">
        <Interactive.Div name="Cinta de marca" style={{ position: "absolute", inset: 0 }}>
          <BrandTag title={title} handle={handle} />
        </Interactive.Div>
      </Sequence>
    </AbsoluteFill>
  );
};
