import { loadFont as loadJakarta } from "@remotion/google-fonts/PlusJakartaSans";
import { loadFont as loadPlayfair } from "@remotion/google-fonts/PlayfairDisplay";

const jakarta = loadJakarta("normal", { weights: ["400", "500", "700", "800"], subsets: ["latin"] });
const playfair = loadPlayfair("italic", { weights: ["400", "700"], subsets: ["latin"] });

// Tokens del estilo "UI premium oscuro". Cambiar aquí cambia todo el video.
export const theme = {
  width: 1080,
  height: 1920,
  fps: 30,
  bg: { from: "#040404", to: "#0A090E" },
  halo: "#2A2013",
  grano: 0.06, // opacidad del grano
  accent: "#F0B040",
  accentGlow: "0 0 24px rgba(240,176,64,0.4)",
  card: {
    bg: "rgba(37,32,29,0.7)",
    border: "1px solid rgba(255,255,255,0.1)",
    radius: 28,
    shadow: "0 30px 80px #000",
  },
  text: "#F5F2EC",
  textDim: "rgba(245,242,236,0.35)",
  fonts: {
    ui: jakarta.fontFamily, // Plus Jakarta Sans
    numeral: playfair.fontFamily, // Playfair Display Italic
  },
} as const;
