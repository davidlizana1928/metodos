import { Composition, Folder } from "remotion";
import { calcularResena } from "./resena/Resena";
import { DemoNocheCero } from "./resenas/ejemplo-noche-cero/Video";

// Una <Composition> por reseña. Copiar el bloque y cambiar id, componente, carpeta y títulos.
export const RemotionRoot: React.FC = () => {
  return (
    <Folder name="Resenas">
      <Composition
        id="EjemploNocheCero"
        component={DemoNocheCero}
        durationInFrames={500}
        fps={30}
        width={1080}
        height={1920}
        calculateMetadata={calcularResena}
        defaultProps={{
          carpeta: "ejemplo-noche-cero",
          tituloChile: "Resident Evil: Noche Cero",
          subtitulo: "Resident Evil, 2026",
          segmentos: [],
        }}
      />
    </Folder>
  );
};
