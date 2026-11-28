import { Audio } from "@remotion/media";
import { AbsoluteFill, Series, staticFile, useVideoConfig } from "remotion";
import { Bloque, CTA, Hook } from "./components/Escenas";
import { Fondo } from "./components/Fondo";
import { Subtitles } from "./components/Subtitles";
import { GUION } from "./guion";
import { calcularTimeline, type Palabra } from "./timeline";

export type VideoProps = { palabras: Palabra[]; hayMusica: boolean };

// Timeline: Hook → 5 bloques → CTA, con duraciones exactas sacadas de words.json
export const Video: React.FC<VideoProps> = ({ palabras, hayMusica }) => {
  const { fps } = useVideoConfig();
  const t = calcularTimeline(palabras, GUION, fps);
  return (
    <AbsoluteFill>
      <Fondo />
      <Series>
        <Series.Sequence durationInFrames={t.hook.dur} name="Hook">
          <Hook tramo={t.hook} frase={GUION.hook.frase} demo={GUION.hook.demo} />
        </Series.Sequence>
        {t.bloques.map((tramo, i) => (
          <Series.Sequence key={i} durationInFrames={tramo.dur} name={`Bloque ${i + 1}`}>
            <Bloque n={i + 1} tramo={tramo} {...GUION.bloques[i]} />
          </Series.Sequence>
        ))}
        <Series.Sequence durationInFrames={t.cta.dur} name="CTA">
          <CTA tramo={t.cta} titulo={GUION.titulo} subtitulo={GUION.subtitulo} prompt={GUION.cta.prompt} keyword={GUION.cta.keyword} />
        </Series.Sequence>
      </Series>
      <Subtitles palabras={palabras} />
      <Audio src={staticFile("voz.mp3")} name="Voz (Alex)" />
      {hayMusica && <Audio src={staticFile("music.wav")} name="Música" volume={0.18} />}
    </AbsoluteFill>
  );
};
