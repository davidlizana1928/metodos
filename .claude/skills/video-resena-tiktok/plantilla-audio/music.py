"""Synth de terror ochentero, 100 BPM, 4 tramos ligados a las frases de la voz."""
import numpy as np, soundfile as sf, json

SR = 44100
seg = json.load(open("segments.json"))
D = seg[-1]["end"] + 1.0
T2, T3, T4 = seg[4]["start"], seg[8]["start"], seg[13]["start"]  # encargo, brote, título
n = int(D * SR)
t = np.arange(n) / SR
beat = 0.6
rng = np.random.default_rng(7)


def hz(m):
    return 440 * 2 ** ((m - 69) / 12)


def env_sec(a, b, fade=1.0):
    return np.clip((t - a) / fade, 0, 1) * np.clip((b - t) / fade, 0, 1)


def saw(f, tt):
    return 2 * ((f * tt) % 1) - 1


def lowpass(x, a):
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc += a * (x[i] - acc)
        y[i] = acc
    return y


# --- cold pad (whole piece): Am - F - Dm - E (minor, tense)
chords = [[57, 60, 64], [53, 57, 60], [50, 53, 57], [52, 56, 59]]
pad = np.zeros(n)
cl = 4 * 2.4
for ci in range(int(D / cl) + 1):
    s = int(ci * cl * SR)
    e = min(n, int(((ci + 1) * cl + 0.8) * SR))
    if s >= n:
        break
    tt = np.arange(e - s) / SR
    ev = np.minimum(1, tt / 1.5) * np.minimum(1, ((e - s) / SR - tt) / 0.8)
    for m in chords[ci % 4]:
        for det in (-0.15, 0.15):
            pad[s:e] += ev * np.sin(2 * np.pi * hz(m) * (1 + det / 100) * tt + rng.uniform(0, 6)) * 0.04
dens = 1 + 0.6 * env_sec(T3, T4, 2.0)
pad *= dens

# --- pulse (soft from start, stronger later): low A eighths
pulse = np.zeros(n)
pl = int(0.25 * SR)
ptt = np.arange(pl) / SR
for b in np.arange(0, D, beat / 2):
    i = int(b * SR)
    ci = int(b / cl) % 4
    f = hz(chords[ci][0] - 24)
    note = saw(f, ptt) * np.exp(-ptt * 9)
    lvl = 0.12 if b < T2 else (0.22 if b < T4 else 0.05)
    pulse[i:i + pl] += note[: n - i] * lvl
pulse = lowpass(pulse.astype(np.float32), 0.08)

# --- light percussion from T2 to T4
perc = np.zeros(n)
kl = int(0.3 * SR)
ktt = np.arange(kl) / SR
kick = np.sin(2 * np.pi * (45 + 60 * np.exp(-ktt * 30)) * ktt) * np.exp(-ktt * 10)
hl = int(0.04 * SR)
hat = rng.standard_normal(hl) * np.exp(-np.arange(hl) / SR * 120)
hat = np.diff(np.concatenate([[0], hat]))
for k, b in enumerate(np.arange(0, D, beat)):
    if not (T2 - 0.01 <= b < T4):
        continue
    i = int(b * SR)
    if k % 2 == 0:
        perc[i:i + kl] += kick[: n - i] * 0.35
    j = int((b + beat / 2) * SR)
    if j < n:
        perc[j:j + hl] += hat[: n - j] * 0.05

# --- dissonant layer (brote -> título): minor second drone + tremolo
dis = np.zeros(n)
m = env_sec(T3, T4, 3.0)
dis += m * (np.sin(2 * np.pi * hz(69) * t) + np.sin(2 * np.pi * hz(70) * t)) * 0.025
dis *= 0.6 + 0.4 * np.sin(2 * np.pi * 5 * t)

y = pad + pulse + perc + dis
y *= np.minimum(1, t / 0.5) * np.minimum(1, (D - t) / 2.0)
y = y / np.abs(y).max() * 0.9
sf.write("music.wav", y.astype(np.float32), SR)
print(round(D, 3), T2, T3, T4)
