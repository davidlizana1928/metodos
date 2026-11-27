import { ResenaBase, ResenaProps } from "../../resena/Resena";
import { HistoriaNocheCero } from "./Historia";

export const DemoNocheCero: React.FC<ResenaProps> = (props) => (
  <ResenaBase {...props} historia={<HistoriaNocheCero />} />
);
