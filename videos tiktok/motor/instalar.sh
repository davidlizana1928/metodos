#!/usr/bin/env bash
# Reinstala el motor de video en un contenedor nuevo. Uso: bash "videos tiktok/motor/instalar.sh"
set -e
cd "$(dirname "$0")"
npm install
npx hyperframes telemetry disable >/dev/null 2>&1 || true
pip install -q yt-dlp || true
# Fondos en pintura digital (SD-Turbo) y recortador de fondos (rembg), en un entorno aparte
if [ ! -x /root/sd/bin/python ]; then
  python3 -m venv /root/sd
  /root/sd/bin/pip install -q torch diffusers transformers accelerate safetensors "rembg[cpu]"
fi
# Blender (3D), instalado para más adelante
command -v blender >/dev/null || apt-get install -y -qq blender || true
# Skills de HyperFrames: el repo ya las trae en .claude/skills. Para refrescarlas:
#   npx hyperframes skills update
echo "Motor listo: HyperFrames, Remotion, ffmpeg, yt-dlp, SD-Turbo + rembg (/root/sd), Blender"
