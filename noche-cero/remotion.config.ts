import { Config } from "@remotion/cli/config";
import fs from "node:fs";

Config.setRspack(true);
Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);
Config.setDefaultPremountInSeconds(2);
Config.setChromiumOpenGlRenderer("angle"); // necesario para el 3D sin tarjeta gráfica

// En la nube de Claude Code no se puede descargar Chrome: usar el Chromium preinstalado.
const CHROMIUM = "/opt/pw-browsers/chromium";
if (fs.existsSync(CHROMIUM)) {
  Config.setBrowserExecutable(CHROMIUM);
}

// Una sola pestaña: con varias a la vez, el navegador de la nube corrompe
// fotogramas (mosaicos, tarjetas vacías). Es igual de rápido.
Config.setConcurrency(1);
