"""Voz de Alex (Kokoro em_alex, es-419) → public/voz.mp3 + public/words.json + public/segments.json

Uso (desde la carpeta del proyecto <slug>/):  python3 voice.py [velocidad]
- P: una frase por línea VOZ: del guion visual. Separar «Se trata de…» y «Si fueras tú…».
- Marcar palabras clave con *asteriscos* → bold: true en words.json (se ven en acento).
"""
import os, re, sys, json, subprocess
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro

KDIR = os.path.expanduser("~/kokoro")
VOICE = os.environ.get("VOICE", "em_alex")
LANG = "es-419"
assert VOICE.startswith("em_") or VOICE.startswith("ef_"), "Solo voces de español de Kokoro (em_/ef_)"
k = Kokoro(os.path.join(KDIR, "kokoro-q8.onnx"), os.path.join(KDIR, "voices_es.npz"))
SPEED = float(sys.argv[1]) if len(sys.argv) > 1 else 1.05
SR = 24000
OUT = "public"
# Pronunciación de títulos en inglés como la diría un hablante latino
FIX = {"Resident Evil": "Résident Ívil"}

P = [
    "Imagina que la ciudad a la que viajas se llena de *monstruos* esta noche…",
    "y tú no eres un héroe: eres el *repartidor* que debe cruzarla.",
    # … una frase por línea VOZ: …
    "Se trata de *Resident Evil: Noche Cero*…",
    "Si fueras tú, ¿seguirías adelante para entregar el paquete… o lo dejarías todo para volver con tu novia?",
]


def limpia(t):
    return t.replace("*", "")


def synth(t):
    t = limpia(t)
    for a, r in FIX.items():
        t = t.replace(a, r)
    ph = k.tokenizer.phonemize(t, LANG)
    assert "θ" not in ph, "Pronunciación de España detectada"
    a, _ = k.create(ph, voice=VOICE, speed=SPEED, is_phonemes=True)
    return a


def compress(a, maxs=0.30, th=0.015):
    w = int(SR * 0.02); keep = []; run = []
    for i in range(0, len(a), w):
        c = a[i:i + w]
        if np.abs(c).max() < th:
            run.append(c)
        else:
            keep += run[:int(maxs * SR / w)]; run = []; keep.append(c)
    keep += run[:int(maxs * SR / w)]
    return np.concatenate(keep)


def trim(a, th=0.01):
    idx = np.where(np.abs(a) > th)[0]
    return a[max(idx[0] - int(SR * 0.01), 0):idx[-1] + int(SR * 0.02)]


def palabras(frase, start, end, seg):
    """Reparte la duración del segmento entre sus palabras, en proporción a sus letras.
    La puntuación suma peso (la voz hace una micro pausa ahí)."""
    toks = []
    for m in re.finditer(r"\*([^*]+)\*(\S*)|\S+", frase):
        if m.group(1):  # *palabra clave* (puede tener varias palabras); la puntuación pegada queda con la última
            ws = m.group(1).split()
            ws[-1] += m.group(2)
            toks += [(w, True) for w in ws]
        else:
            toks.append((m.group(0), False))
    # pegar la puntuación suelta (por ejemplo «…») a la palabra anterior
    pesos = [len(re.sub(r"[^\wáéíóúüñÁÉÍÓÚÜÑ]", "", w)) + 1.5 + (2.5 if re.search(r"[.,;:!?…]$", w) else 0) for w, _ in toks]
    total = sum(pesos); t = start; out = []
    for (w, b), p in zip(toks, pesos):
        d = (end - start) * p / total
        out.append({"word": w, "start": round(t, 3), "end": round(t + d * 0.92, 3), "bold": b, "seg": seg})
        t += d
    return out


os.makedirs(OUT, exist_ok=True)
segs = []; words = []; t = 0.0; out = []
GAP = 0.18
for i, p in enumerate(P):
    a = compress(trim(synth(p)))
    if i > 0:
        g = 0.15 if limpia(p).startswith("Se trata de") or i == 1 else GAP
        out.append(np.zeros(int(g * SR), np.float32)); t += g
    s, e = t, t + len(a) / SR
    segs.append({"i": i + 1, "start": round(s, 3), "end": round(e, 3), "text": limpia(p)})
    words += palabras(p, s, e, i + 1)
    out.append(a.astype(np.float32)); t = e
y = np.concatenate(out); y = y / np.abs(y).max() * 0.89
sf.write(f"{OUT}/voz.wav", y, SR)
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", f"{OUT}/voz.wav", "-ar", "44100", "-b:a", "192k", f"{OUT}/voz.mp3"], check=True)
os.remove(f"{OUT}/voz.wav")
json.dump(segs, open(f"{OUT}/segments.json", "w"), ensure_ascii=False, indent=1)
json.dump(words, open(f"{OUT}/words.json", "w"), ensure_ascii=False, indent=1)
for s in segs:
    print(s["i"], s["start"], s["end"], round(s["end"] - s["start"], 2))
print("total", round(t, 2), "s ·", len(words), "palabras ·", sum(w["bold"] for w in words), "clave")
