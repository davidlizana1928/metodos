"""Genera la voz del video con Kokoro (gratis, funciona sin internet una vez descargado).

Uso (desde la carpeta amanecer-cosecha):
  pip install kokoro-onnx soundfile
  # Descarga una vez kokoro-v1.0.onnx y voices-v1.0.bin desde
  # https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0
  # y ponlos en voz-generador/
  python voz-generador/generar_voz.py em_alex 1.0

Voces en español: em_alex (hombre), em_santa (hombre), ef_dora (mujer).
El segundo número es la velocidad (1.0 normal, 1.1 más rápido).
Las frases están en voz-generador/frases.json: [segundo de inicio, texto].
"""
import json
import os
import sys

import soundfile as sf
from kokoro_onnx import Kokoro

here = os.path.dirname(os.path.abspath(__file__))
voice = sys.argv[1] if len(sys.argv) > 1 else "em_alex"
speed = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0

k = Kokoro(os.path.join(here, "kokoro-v1.0.onnx"), os.path.join(here, "voices-v1.0.bin"))
lines = json.load(open(os.path.join(here, "frases.json"), encoding="utf-8"))
out = os.path.join(here, "..", "public", "voz")
os.makedirs(out, exist_ok=True)

for i, (start, text) in enumerate(lines):
    samples, sr = k.create(text, voice=voice, speed=speed, lang="es")
    sf.write(os.path.join(out, f"voz-{i:02d}.wav"), samples, sr)
    print(f"voz-{i:02d}.wav  empieza en {start}s  dura {len(samples) / sr:.2f}s")
