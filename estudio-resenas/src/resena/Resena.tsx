import { Audio } from "@remotion/media";
import {
  AbsoluteFill,
  CalculateMetadataFunction,
  Sequence,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { progresoSala, rectPantalla } from "./camara";
import { SalaFondo, SalaFrente } from "./Sala3D";
import { TarjetaTitulo } from "./TarjetaTitulo";

export type Segmento = { i: number; start: number; end: number; text: string };

export type ResenaProps = {
  readonly carpeta: string; // carpeta en public/ con voice.wav, music.wav y segments.json
  readonly tituloChile: string;
  readonly subtitulo: string; // título original y año, o solo el año
  readonly segmentos: Segmento[];
};

// Lee segments.json (tiempos reales de la voz de Alex) y fija la duración: voz + 1 s
export const calcularResena: CalculateMetadataFunction<ResenaProps> = async ({ props }) => {
  const res = await fetch(staticFile(`${props.carpeta}/segments.json`));
  const segmentos: Segmento[] = await res.json();
  const fps = 30;
  return {
    fps,
    durationInFrames: Math.ceil((segmentos[segmentos.length - 1].end + 1) * fps),
    props: { ...props, segmentos },
  };
};

export const inicioTitulo = (segmentos: Segmento[]) =>
  segmentos.find((s) => s.text.startsWith("Se trata de"))?.start ?? 0;

// La historia se ve DENTRO de la pantalla del cine mientras la cámara entra o sale,
// y a pantalla completa en el medio. Butacas y Espectador quedan por delante.
const SalaConHistoria: React.FC<{
  historia: React.ReactNode;
  entrada: [number, number];
  salida: [number, number];
}> = ({ historia, entrada, salida }) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const p = progresoSala(frame / fps, entrada, salida);
  const enHistoria = p >= 0.999;
  const r = rectPantalla(p, width, height);
  // la historia (vertical) se ajusta al alto de la pantalla, centrada
  const escala = r.height / height;

  return (
    <AbsoluteFill style={{ backgroundColor: "black" }}>
      {!enHistoria && <SalaFondo p={p} />}
      <div
        style={{
          position: "absolute",
          left: enHistoria ? 0 : r.left,
          top: enHistoria ? 0 : r.top,
          width: enHistoria ? width : r.width,
          height: enHistoria ? height : r.height,
          overflow: "hidden",
          background: "#04070a",
        }}
      >
        <div
          style={{
            position: "absolute",
            width,
            height,
            left: enHistoria ? 0 : (r.width - width) / 2,
            top: enHistoria ? 0 : (r.height - height) / 2,
            scale: enHistoria ? 1 : escala,
            maskImage: enHistoria
              ? undefined
              : "linear-gradient(90deg, transparent 0%, black 6%, black 94%, transparent 100%)",
          }}
        >
          {historia}
        </div>
      </div>
      {!enHistoria && <SalaFrente p={p} />}
    </AbsoluteFill>
  );
};

// Estructura fija del canal (regla 7.3):
// escena 1 = sala + Espectador, la cámara entra a la pantalla;
// escenas del medio = la historia; última = la cámara vuelve a la sala y entra el título.
export const ResenaBase: React.FC<ResenaProps & { historia: React.ReactNode }> = ({
  carpeta,
  tituloChile,
  subtitulo,
  segmentos,
  historia,
}) => {
  const { fps } = useVideoConfig();
  const tTitulo = inicioTitulo(segmentos);
  return (
    <AbsoluteFill style={{ backgroundColor: "black" }}>
      <SalaConHistoria historia={historia} entrada={[0.3, 3.7]} salida={[tTitulo - 0.1, tTitulo + 1.9]} />
      <AbsoluteFill
        style={{ background: "radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 50%, rgba(0,0,0,0.6) 100%)" }}
      />
      <Sequence from={Math.round(tTitulo * fps)} name="Tarjeta del título" layout="none">
        <TarjetaTitulo titulo={tituloChile} subtitulo={subtitulo} />
      </Sequence>
      <Audio src={staticFile(`${carpeta}/voice.wav`)} name="Voz (Alex)" />
      <Audio src={staticFile(`${carpeta}/music.wav`)} name="Música" volume={0.22} />
    </AbsoluteFill>
  );
};
