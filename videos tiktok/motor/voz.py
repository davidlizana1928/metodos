#!/usr/bin/env python3
"""Genera la voz del canal (Kokoro em_alex) frase por frase y entrega los tiempos exactos.

Uso:
  python3 -I "videos tiktok/motor/voz.py" guion.txt carpeta_salida [--velocidad 1.1]

Entrada: guion de voz en texto plano. Cada oración (termina en . ? ! o …) es una frase.
Los «…» agregan 0,35 s de pausa después de la frase. Entre frases normales: 0,12 s.

Salida en carpeta_salida:
  voz.wav       la narración completa, 48 kHz mono
  tiempos.json  [{"n", "texto", "inicio", "fin"}] en segundos, para sincronizar las escenas
"""
import json
import pathlib
import re
import subprocess
import sys

MOTOR = pathlib.Path(__file__).resolve().parent
VOZ = "em_alex"
PAUSA_FRASE = 0.12
PAUSA_SUSPENSIVOS = 0.35


def duracion(wav):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(wav)],
        capture_output=True, text=True, check=True,
    )
    return float(out.stdout.strip())


def frases(texto):
    texto = re.sub(r"\s+", " ", texto.replace("...", "…")).strip()
    partes = re.findall(r"[^.?!…]+(?:…|[.?!]+)?", texto)
    return [p.strip() for p in partes if p.strip(" .")]


def main():
    args = sys.argv[1:]
    if len(args) < 2:
        sys.exit(__doc__)
    guion, salida = pathlib.Path(args[0]), pathlib.Path(args[1])
    velocidad = args[args.index("--velocidad") + 1] if "--velocidad" in args else "1.1"
    salida.mkdir(parents=True, exist_ok=True)
    tmp = salida / "_frases"
    tmp.mkdir(exist_ok=True)

    lista, tiempos, t = [], [], 0.0
    silencios = {}
    for i, f in enumerate(frases(guion.read_text(encoding="utf-8")), 1):
        wav = tmp / f"{i:03d}.wav"
        subprocess.run(
            ["npx", "--prefix", str(MOTOR), "hyperframes", "tts", f.rstrip("…").strip() + ("." if f.endswith("…") else ""),
             "--voice", VOZ, "--lang", "es", "--speed", velocidad, "-o", str(wav)],
            check=True, capture_output=True,
        )
        # Normaliza a 48 kHz mono para concatenar sin saltos
        norm = tmp / f"{i:03d}n.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(wav), "-ar", "48000", "-ac", "1", str(norm)], check=True)
        d = duracion(norm)
        tiempos.append({"n": i, "texto": f, "inicio": round(t, 3), "fin": round(t + d, 3)})
        lista.append(norm)
        pausa = PAUSA_SUSPENSIVOS if f.endswith("…") else PAUSA_FRASE
        if pausa not in silencios:
            s = tmp / f"sil_{int(pausa * 1000)}.wav"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono",
                            "-t", str(pausa), str(s)], check=True)
            silencios[pausa] = s
        lista.append(silencios[pausa])
        t += d + pausa
        print(f"{i:02d} {tiempos[-1]['inicio']:6.2f}-{tiempos[-1]['fin']:6.2f}  {f}")

    concat = tmp / "lista.txt"
    concat.write_text("".join(f"file '{p.resolve()}'\n" for p in lista))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(concat),
                    "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", "48000", str(salida / "voz.wav")], check=True)
    (salida / "tiempos.json").write_text(json.dumps(tiempos, ensure_ascii=False, indent=2), encoding="utf-8")
    palabras = sum(len(x["texto"].split()) for x in tiempos)
    total = duracion(salida / "voz.wav")
    print(f"\nTotal: {total:.1f} s · {palabras} palabras · {palabras / total:.2f} palabras/s")
    if total < 61:
        print("AVISO: la voz dura menos de 61 s. Alargar el guion (objetivo 70-90 s).")


if __name__ == "__main__":
    main()
