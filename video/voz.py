"""Genera la voz guia (TTS Piper) frase por frase y guarda los tiempos reales."""
import json, subprocess, sys, wave, numpy as np, pathlib
HERE = pathlib.Path(__file__).parent
VOICE = sys.argv[1]           # ruta al modelo .onnx
OUT = HERE / "build"; OUT.mkdir(exist_ok=True)
SR = 22050
LS = float(sys.argv[2]) if len(sys.argv) > 2 else 0.85
GAP, ELLIPSIS = 0.22, 0.20

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
 "Se trata de Résident Ívil: Noche cero. Si fueras tú, ¿terminarías la entrega o darías la vuelta para volver con ella?",
]

def tts(text):
    p = OUT / "_seg.wav"
    subprocess.run([sys.executable, "-m", "piper", "-m", VOICE, "-f", str(p),
                    "--length-scale", str(LS), "--sentence-silence", "0.15"],
                   input=text.encode(), check=True, capture_output=True)
    with wave.open(str(p)) as w:
        a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    thr = 0.01
    idx = np.where(np.abs(a) > thr)[0]
    return a[max(idx[0] - 200, 0): idx[-1] + 400]

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
print("total", round(t, 2)); [print(i + 1, x) for i, x in enumerate(tiempos)]
