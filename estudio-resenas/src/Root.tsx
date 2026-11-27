import { Composition, Folder } from "remotion";
import { IntroImagina } from "./intro/IntroImagina";
import { calcularResena } from "./resena/Resena";
import { DemoNocheCero } from "./resenas/demo-noche-cero/Video";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="IntroImagina"
        component={IntroImagina}
        durationInFrames={225}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          phrase: "Imagina que...",
          title: "SERIES Y PELÍCULAS",
          handle: "@rec_peliseries",
        }}
      />
      <Folder name="Resenas">
        <Composition
          id="DemoNocheCero"
          component={DemoNocheCero}
          durationInFrames={500}
          fps={30}
          width={1080}
          height={1920}
          calculateMetadata={calcularResena}
          defaultProps={{
            carpeta: "demo-noche-cero",
            tituloChile: "Resident Evil: Noche Cero",
            subtitulo: "Resident Evil, 2026",
            segmentos: [],
          }}
        />
      </Folder>
    </>
  );
};
