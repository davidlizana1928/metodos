"""Genera la voz guia con Kokoro (voz em_alex, masculina) frase por frase y guarda los tiempos reales.
Uso: python3 voz.py [velocidad]
Requiere los archivos de hexgrad/Kokoro-82M (kokoro-v1_0.pth, config.json, voices/em_alex.pt) en /tmp/kokoro."""
import json, sys, wave, pathlib
import numpy as np
from kokoro import KModel, KPipeline

HERE = pathlib.Path(__file__).parent
OUT = HERE / "build"; OUT.mkdir(exist_ok=True)
MODEL_DIR = pathlib.Path("/tmp/kokoro")
VOICE = str(MODEL_DIR / "voices" / "em_alex.pt")
SPEED = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0
SR = 24000
GAP, ELLIPSIS = 0.16, 0.18  # pausas controladas por nosotros (maximo 0,4 s en todo el video)
THR = 0.01

FRASES = [
 "Imagina que tu trabajo es llevar paquetes médicos urgentes… y esta noche te toca el peor viaje de tu vida.",
 "No eres héroe, no sabes pelear y nunca has disparado un arma.",
 "Tu turno ya terminó, pero te piden una última entrega: un paquete que puede salvar vidas, directo al hospital de una ciudad en las montañas.",
 "Antes de salir, tu novia te contó que está embarazada… y no sabes si estás listo para volver a casa.",
 "Pero esta noche, en una carretera cubierta de hielo, una mujer aparece de la nada frente a tu auto. La atropellas. Sigue viva, pero algo en ella no está bien.",
 "Y lo peor es que ella no es la única. En toda la ciudad, la gente se está contagiando con un virus que la convierte en criaturas violentas que atacan a cualquiera.",
 "Una casa aislada parece un refugio, hasta que escuchas a un perro que ya no es un perro.",
 "Lo que no sabes es que ese paquete importa mucho más de lo que crees… y que detrás del virus está la empresa más poderosa de la ciudad, con hombres armados en las calles.",
 "Tú, que solo querías terminar tu turno, ahora cuentas tus balas una por una y aprendes a disparar para seguir vivo.",
 "Y justo cuando el hospital por fin aparece a lo lejos…",
 "Se trata de Resident Evil: Noche cero. Si fueras tú, ¿terminarías la entrega o darías la vuelta para volver con ella?",
]

model = KModel(config=str(MODEL_DIR / "config.json"), model=str(MODEL_DIR / "kokoro-v1_0.pth")).eval()
pipe = KPipeline(lang_code="e", model=model)


def tts(text):
    """Sintetiza un fragmento y recorta sus silencios de borde (la pausa la ponemos nosotros)."""
    chunks = [a for _, _, a in pipe(text, voice=VOICE, speed=SPEED)]
    a = np.concatenate(chunks).astype(np.float32)
    idx = np.where(np.abs(a) > THR)[0]
    a = a[max(idx[0] - 120, 0): idx[-1] + 240]
    # pausas internas de Kokoro: si pasan de 0,3 s, se acortan a 0,3 s (maximo 0,4 s en todo el video)
    loud = np.abs(a) > THR
    out, run, i = [], 0, 0
    while i < len(a):
        j = i
        while j < len(a) and loud[j] == loud[i]:
            j += 1
        seg = a[i:j]
        if not loud[i] and (j - i) > 0.3 * SR:
            seg = a[i:i + int(0.3 * SR)]
        out.append(seg)
        i = j
    return np.concatenate(out)


audio, tiempos, t = [], [], 0.0
for i, f in enumerate(FRASES):
    partes = [s.strip() for s in f.split("…") if s.strip()]
    ini = t
    for j, parte in enumerate(partes):
        seg = tts(parte if j == len(partes) - 1 or parte.endswith(("?", ".")) else parte + ",")
        audio.append(seg); t += len(seg) / SR
        if j < len(partes) - 1:
            audio.append(np.zeros(int(ELLIPSIS * SR), np.float32)); t += ELLIPSIS
    tiempos.append([round(ini, 3), round(t, 3)])
    if i < len(FRASES) - 1:
        audio.append(np.zeros(int(GAP * SR), np.float32)); t += GAP

a = np.concatenate(audio)
a = a / np.abs(a).max() * 0.9
with wave.open(str(OUT / "voz.wav"), "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((a * 32767).astype(np.int16).tobytes())
json.dump(tiempos, open(OUT / "tiempos_voz.json", "w"), indent=1)
print("total", round(t, 2))
for i, x in enumerate(tiempos):
    print(i + 1, x)
