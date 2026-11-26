import { Composition } from "remotion";
import { IntroImagina } from "./intro/IntroImagina";

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
    </>
  );
};
