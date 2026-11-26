"""Arma la linea de tiempo a partir de la voz real y renderiza el video.
Uso: python3 render.py [preview|video]"""
import json, math, subprocess, sys, pathlib
from multiprocessing import Pool
import numpy as np
from PIL import Image, ImageDraw
from base import *
import escenas

HERE = pathlib.Path(__file__).parent
BUILD = HERE / "build"
FPS = 30

# --- tiempos del guion (segundos originales) ---
FRASES_ORIG = [0.0, 6.2, 9.7, 17.1, 23.2, 32.1, 41.5, 46.8, 57.1, 63.3, 66.8, 74.0]
ESCENAS_ORIG = [  # (inicio, fin, [cambios])
    (0.0, 3.5, [1.5, 2.5]), (3.5, 6.2, [5.0]), (6.2, 9.7, [8.0]), (9.7, 13.4, [11.5]),
    (13.4, 17.1, [14.5, 15.5]), (17.1, 20.3, [18.8]), (20.3, 23.2, [22.0]), (23.2, 28.8, [25.5, 27.5]),
    (28.8, 29.4, []), (29.4, 32.1, [30.8]), (32.1, 35.0, [33.5]), (35.0, 41.5, [37.4, 39.8]),
    (41.5, 46.8, [43.8, 45.5]), (46.8, 51.5, [49.2]), (51.5, 57.1, [53.9, 56.0]), (57.1, 63.3, [59.5, 61.5]),
    (63.3, 66.8, [65.2]), (66.8, 74.0, [69.0, 71.5]),
]
# fundidos (escena i -> i+1), en segundos
FUNDIDOS = {0: 0.25, 4: 0.3, 5: 0.35, 10: 0.3, 13: 0.3}

voz = json.load(open(BUILD / "tiempos_voz.json"))
FIN = voz[-1][1] + 1.0  # 1 s de silencio maximo despues de la pregunta
REAL = [v[0] for v in voz] + [FIN]


def mapa(t):
    """Tiempo del guion -> tiempo real segun la voz grabada."""
    for k in range(len(FRASES_ORIG) - 1):
        a, b = FRASES_ORIG[k], FRASES_ORIG[k + 1]
        if t <= b + 1e-6:
            return REAL[k] + (t - a) / (b - a) * (REAL[k + 1] - REAL[k])
    return FIN


def q(t, grid=0.3):  # detalles al medio tiempo (100 BPM -> 0,3 s)
    return round(t / grid) * grid


ESC = []
for i, (a, b, evs) in enumerate(ESCENAS_ORIG):
    ra, rb = mapa(a), mapa(b)
    ev = [clamp(q(mapa(e)) - ra, 0.1, rb - ra - 0.1) for e in evs]
    ESC.append((ra, rb, ev))

# textos en pantalla (tiempos reales)
T_ULTIMA = ESC[3][0] + ESC[3][2][0] - 0.2
T_URGENTE = ESC[4][0] + ESC[4][2][0]
T_CUATRO = ESC[15][0] + ESC[15][2][0] + 0.9
T_TITULO = ESC[17][0]


def scene_at(t):
    for i, (a, b, ev) in enumerate(ESC):
        if t < b or i == len(ESC) - 1:
            return i
    return len(ESC) - 1


def render_scene(i, t):
    a, b, ev = ESC[i]
    return escenas.SCENES[i](clamp(t - a, 0, b - a), b - a, ev)


def overlay_text(img, t):
    d = ImageDraw.Draw(img, "RGBA")
    def banner(txt, y, size, alpha, col=(245, 240, 230), box=(150, 16, 30)):
        f = font(FONT_BLACK, size)
        bb = d.textbbox((W / 2, y), txt, font=f, anchor="mm")
        pad = 18
        d.rectangle([bb[0] - pad, bb[1] - pad * 0.6, bb[2] + pad, bb[3] + pad * 0.6], fill=box + (int(220 * alpha),))
        d.text((W / 2, y), txt, font=f, fill=col + (int(255 * alpha),), anchor="mm")
    # ULTIMA ENTREGA: parte baja (sobre la zona de la descripcion de TikTok), 1,5 s
    if T_ULTIMA <= t < T_ULTIMA + 1.5:
        a = min(1, (t - T_ULTIMA) / 0.15, (T_ULTIMA + 1.5 - t) / 0.15)
        banner("ÚLTIMA ENTREGA", 880, 54, a)
    # URGENTE sobre la etiqueta de la caja, 1 s
    if T_URGENTE <= t < T_URGENTE + 1.0:
        a = min(1, (t - T_URGENTE) / 0.1, (T_URGENTE + 1.0 - t) / 0.1)
        k = 1 + 0.15 * max(0, 1 - (t - T_URGENTE) / 0.15)
        f = font(FONT_BLACK, int(92 * k))
        cx, cy = 520, 640
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        od = ImageDraw.Draw(ov)
        bb = od.textbbox((cx, cy), "URGENTE", font=f, anchor="mm")
        od.rectangle([bb[0] - 16, bb[1] - 12, bb[2] + 16, bb[3] + 12], outline=(255, 255, 255, int(255 * a)), width=8)
        od.text((cx, cy), "URGENTE", font=f, fill=(255, 255, 255, int(255 * a)), anchor="mm")
        ov = ov.rotate(-8, Image.BILINEAR, center=(cx, cy))
        img.paste(ov, (0, 0), ov)
    # "4" junto a las balas alineadas, 1 s
    if T_CUATRO <= t < T_CUATRO + 1.0:
        a = min(1, (t - T_CUATRO) / 0.1, (T_CUATRO + 1.0 - t) / 0.1)
        d.text((600, 690), "4", font=font(FONT_BLACK, 190), fill=(255, 214, 90, int(255 * a)), anchor="mm",
               stroke_width=6, stroke_fill=(30, 20, 10, int(200 * a)))
    # tarjeta del titulo: zona superior, bajo la barra de TikTok, lejos de los botones
    if t >= T_TITULO:
        a = min(1, (t - T_TITULO) / 0.35)
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        od = ImageDraw.Draw(ov)
        od.rectangle([0, 150, W, 380], fill=(0, 0, 0, int(110 * a)))
        f1 = font(FONT_BLACK, 66); f2 = font(FONT_BLACK, 82); f3 = font(FONT_MED, 28)
        y0 = 210 - 12 * (1 - a)
        od.text((W / 2 - 20, y0), "RESIDENT EVIL:", font=f1, fill=(235, 40, 50, int(255 * a)), anchor="mm",
                stroke_width=3, stroke_fill=(20, 0, 0, int(255 * a)))
        od.text((W / 2 - 20, y0 + 78), "NOCHE CERO", font=f2, fill=(245, 240, 232, int(255 * a)), anchor="mm",
                stroke_width=3, stroke_fill=(20, 0, 0, int(255 * a)))
        od.text((W / 2 - 20, y0 + 145), "Resident Evil · 2026", font=f3, fill=(230, 210, 170, int(235 * a)),
                anchor="mm")
        img.paste(ov, (0, 0), ov)
    return img


HAZE_BY_SCENE = {0: 0.06, 3: 0.08, 5: 0.04, 15: 0.08, 17: 0.06}


def frame(fi):
    t = fi / FPS
    i = scene_at(t)
    img = render_scene(i, t)
    a, b, _ = ESC[i]
    fd = FUNDIDOS.get(i)
    if fd and i + 1 < len(ESC) and t > b - fd:
        nxt = render_scene(i + 1, b)
        img = Image.blend(img, nxt, smooth((t - (b - fd)) / fd))
    img = grade(img, fi, haze=HAZE_BY_SCENE.get(i, 0.11))
    img = overlay_text(img, t)
    return img


def frame_bytes(fi):
    return frame(fi).resize((1080, 1920), Image.LANCZOS).tobytes()


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "video"
    if mode == "preview":
        ts = [float(x) for x in sys.argv[2:]] or [0.3 + (a + b) / 2 * 0 + a + 0.6 * (b - a) for a, b, _ in ESC]
        thumbs = [frame(int(t * FPS)).resize((240, 427)) for t in ts]
        cols = 6
        rows = math.ceil(len(thumbs) / cols)
        sheet = Image.new("RGB", (cols * 240, rows * 427), 0)
        for k, th in enumerate(thumbs):
            ImageDraw.Draw(th).text((6, 6), f"{ts[k]:.1f}", fill=(255, 255, 0))
            sheet.paste(th, ((k % cols) * 240, (k // cols) * 427))
        sheet.save(BUILD / "preview.png")
        print("ok", BUILD / "preview.png")
        sys.exit()
    n = int(FIN * FPS)
    out = BUILD / "imagen.mp4"
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", "1080x1920", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow",
                           "-crf", "24", "-pix_fmt", "yuv420p", str(out)], stdin=subprocess.PIPE)
    with Pool(4) as p:
        for k, buf in enumerate(p.imap(frame_bytes, range(n), chunksize=4)):
            ff.stdin.write(buf)
            if k % 150 == 0:
                print(f"{k}/{n}", flush=True)
    ff.stdin.close(); ff.wait()
    json.dump({"escenas": ESC, "fin": FIN, "ultima": T_ULTIMA, "urgente": T_URGENTE, "cuatro": T_CUATRO,
               "titulo": T_TITULO}, open(BUILD / "linea_tiempo.json", "w"), indent=1)
    print("listo", out)
