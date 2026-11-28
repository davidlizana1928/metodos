#!/usr/bin/env bash
# Reinstala el motor de video en un contenedor nuevo. Uso: bash "videos tiktok/motor/instalar.sh"
set -e
cd "$(dirname "$0")"
npm install
npx hyperframes telemetry disable >/dev/null 2>&1 || true
pip install -q yt-dlp || true
# Skills de HyperFrames: el repo ya las trae en .claude/skills. Para refrescarlas:
#   npx hyperframes skills update
echo "Motor listo: HyperFrames $(npx hyperframes --version 2>/dev/null | head -1), Remotion, ffmpeg, yt-dlp"
