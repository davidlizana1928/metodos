"""Musica sintetica a 100 BPM + efectos, mezclada por debajo de la voz (ducking)."""
import json, wave, pathlib
import numpy as np

HERE = pathlib.Path(__file__).parent
BUILD = HERE / "build"
SR = 44100
lt = json.load(open(BUILD / "linea_tiempo.json"))
FIN = lt["fin"]
N = int(FIN * SR)
t = np.arange(N) / SR
BEAT = 0.6  # 100 BPM


def read_wav(p):
    with wave.open(str(p)) as w:
        sr = w.getframerate()
        a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    x = np.interp(np.arange(int(len(a) * SR / sr)) / SR, np.arange(len(a)) / sr, a)
    return x


def lowpass(x, fc):
    a = np.exp(-2 * np.pi * fc / SR)
    from scipy.signal import lfilter
    return lfilter([1 - a], [1, -a], x)


def env_at(times, length, attack=0.002, decay=0.2):
    e = np.zeros(N, np.float32)
    n = int(length * SR)
    k = np.arange(n) / SR
    shape = np.minimum(k / attack, 1) * np.exp(-k / decay)
    for tm in times:
        i = int(tm * SR)
        if i >= N:
            continue
        m = min(n, N - i)
        e[i:i + m] += shape[:m]
    return e


rng = np.random.default_rng(1)
m = np.zeros(N, np.float32)

# --- pad oscuro: progresion menor que cambia cada 2 compases (4,8 s)
chords = [[38, 45, 53], [34, 41, 50], [31, 38, 46], [33, 40, 49]]  # Dm, Bb, Gm, A (MIDI)
bar = BEAT * 4
pad = np.zeros(N, np.float32)
for c in range(int(FIN / (bar * 2)) + 1):
    t0, t1 = c * bar * 2, (c + 1) * bar * 2
    i0, i1 = int(t0 * SR), min(int(t1 * SR) + int(0.3 * SR), N)
    if i0 >= N:
        break
    tt = np.arange(i1 - i0) / SR
    seg = np.zeros(i1 - i0, np.float32)
    for note in chords[c % 4]:
        f = 440 * 2 ** ((note - 69) / 12)
        for det in (-0.12, 0.0, 0.11):
            ph = 2 * np.pi * f * (1 + det / 100) * tt
            seg += (2 * ((f * (1 + det / 100) * tt) % 1) - 1) * 0.05 + np.sin(ph) * 0.05
    fade = np.minimum(1, tt / 0.4) * np.minimum(1, (tt[-1] - tt) / 0.3)
    pad[i0:i1] += seg * fade
pad = lowpass(lowpass(pad, 700), 900)
pad *= 0.8 + 0.2 * np.sin(2 * np.pi * t / (bar * 2))
m += pad * 0.9

# --- sub grave en los tiempos fuertes (cada compas) y bombo suave en cada tiempo
beats = np.arange(0, FIN, BEAT)
kick_t = np.arange(int(0.35 * SR)) / SR
kick = np.sin(2 * np.pi * (50 * kick_t + 60 * (1 - np.exp(-kick_t * 30)) / 30)) * np.exp(-kick_t * 9)
for b in beats:
    i = int(b * SR)
    accent = 1.0 if (round(b / BEAT) % 4 == 0) else 0.45
    seg = kick[:max(0, min(len(kick), N - i))]
    m[i:i + len(seg)] += seg * 0.55 * accent

# --- tic de reloj en el medio tiempo (0,3 s): tension
noise = rng.normal(0, 1, N).astype(np.float32)
hp = noise - lowpass(noise, 5000)
ticks = np.arange(BEAT / 2, FIN, BEAT / 2)
m += hp * env_at(ticks, 0.05, 0.001, 0.012) * 0.10

# --- latido grave desde el atropello hasta el final
heart = [b for b in beats if lt["escenas"][7][0] <= b < FIN - 1.5 and round(b / BEAT) % 2 == 0]
hb = np.zeros(N, np.float32)
for b in heart:
    for off, g in ((0, 1.0), (0.18, 0.7)):
        i = int((b + off) * SR)
        seg = kick[:max(0, min(len(kick), N - i))]
        hb[i:i + len(seg)] += seg * g
m += lowpass(hb, 120) * 0.5

# --- riser cuando aparece el hospital y corte cuando se apagan las luces
esc = lt["escenas"]
h0 = esc[16][0]; off = h0 + esc[16][2][0]
riser = np.zeros(N, np.float32)
i0, i1 = int(h0 * SR), int(off * SR)
k = np.linspace(0, 1, i1 - i0)
riser[i0:i1] = (lowpass(noise[i0:i1], 2500) * 0.25 + np.sin(2 * np.pi * (200 + 500 * k ** 2) * k * (i1 - i0) / SR) * 0.08) * k ** 2
m += riser
duck_drop = np.ones(N, np.float32)
j0, j1 = int(off * SR), int((off + 0.15) * SR)
duck_drop[j0:] = 0.35
duck_drop[j0:j1] = np.linspace(1, 0.35, j1 - j0)

# --- efectos
sfx = np.zeros(N, np.float32)
def hit(tm, dur, f0, f1, gain, noise_amt=0.6, lp=3000):
    i = int(tm * SR); n = int(dur * SR)
    if i >= N: return
    n = min(n, N - i)
    tt = np.arange(n) / SR
    tone = np.sin(2 * np.pi * (f0 * tt + (f1 - f0) * tt ** 2 / (2 * dur)))
    s = (tone * (1 - noise_amt) + lowpass(rng.normal(0, 1, n), lp) * noise_amt) * np.exp(-tt / (dur / 4))
    sfx[i:i + n] += s * gain
e0 = esc[0]
hit(e0[2][0], 0.25, 900, 300, 0.25, 0.8, 6000)                 # click del proyector
for i, d in ((0, 0.25), (4, 0.3), (5, 0.35), (10, 0.3), (13, 0.3)):  # whoosh en transiciones
    tm = esc[i][1] - d
    n = int(0.6 * SR); a = int(tm * SR)
    if a + n < N:
        w = lowpass(rng.normal(0, 1, n), 1500) * np.sin(np.linspace(0, np.pi, n)) ** 2
        sfx[a:a + n] += w * 0.35
hit(esc[1][0] + esc[1][2][0], 0.5, 300, 200, 0.12, 0.9, 1500)    # limpiaparabrisas
hit(esc[8][0], 0.7, 90, 40, 0.9, 0.5, 900)                       # golpe en el parabrisas (sin mostrar impacto)
hit(esc[8][0] + 0.02, 0.4, 3000, 2000, 0.25, 0.9, 8000)          # cristal que se agrieta
hit(esc[15][0] + esc[15][2][1] + 0.22, 0.45, 150, 60, 0.9, 0.8, 4000)  # disparo a la lata
hit(off, 0.6, 80, 40, 0.7, 0.4, 600)                             # apagon del hospital
ring = esc[6][0]
for k2 in range(3):                                              # celular vibrando
    tm = ring + 0.2 + k2 * 0.5
    if tm < ring + esc[6][2][0]:
        i = int(tm * SR); n = int(0.3 * SR)
        tt = np.arange(n) / SR
        sfx[i:i + n] += np.sign(np.sin(2 * np.pi * 150 * tt)) * 0.05 * (np.sin(2 * np.pi * 25 * tt) > 0)

# --- mezcla: voz arriba, musica por debajo con ducking
voz = read_wav(BUILD / "voz.wav")
v = np.zeros(N, np.float32); v[:min(len(voz), N)] = voz[:N]
env = np.abs(v)
env = lowpass(lowpass(env, 6), 6)
env = env / (env.max() + 1e-9)
duck = 1 - 0.55 * np.clip(env * 4, 0, 1)
music = m * duck * duck_drop
music = music / (np.abs(music).max() + 1e-9) * 0.30
fade_in = np.minimum(1, t / 0.3); fade_out = np.minimum(1, (FIN - t) / 0.8)
music *= fade_in * fade_out
sfx_m = sfx / (np.abs(sfx).max() + 1e-9) * 0.35
mix_full = v * 0.92 + music + sfx_m
mix_novoz = music / 0.30 * 0.6 + sfx_m

def write(p, x):
    x = x / max(1.0, np.abs(x).max() / 0.98)
    with wave.open(str(p), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())
write(BUILD / "mezcla.wav", mix_full)
write(BUILD / "musica_y_efectos.wav", mix_novoz)
print("ok", FIN)
