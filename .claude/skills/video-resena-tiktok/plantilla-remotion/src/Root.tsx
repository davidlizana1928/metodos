import { CalculateMetadataFunction, Composition, staticFile } from "remotion";
import { GUION } from "./guion";
import { calcularTimeline, type Palabra } from "./timeline";
import { theme } from "./theme";
import { Video, type VideoProps } from "./Video";

// Lee public/words.json, detecta si hay música y fija la duración (voz + 1 s)
const calcular: CalculateMetadataFunction<VideoProps> = async ({ props }) => {
  const palabras: Palabra[] = await (await fetch(staticFile("words.json"))).json();
  const musica = await fetch(staticFile("music.wav"), { method: "HEAD" }).then((r) => r.ok).catch(() => false);
  const { total } = calcularTimeline(palabras, GUION, theme.fps);
  return { durationInFrames: total, props: { ...props, palabras, hayMusica: musica } };
};

export const RemotionRoot: React.FC = () => (
  <Composition
    id="Video"
    component={Video}
    durationInFrames={1800}
    fps={30}
    width={1080}
    height={1920}
    calculateMetadata={calcular}
    defaultProps={{ palabras: [], hayMusica: false }}
  />
);
