"""Primitivas de dibujo para el video (pintura digital estilizada, 720x1280)."""
import math
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageFont

W, H = 720, 1280
FONT_BLACK = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
FONT_BOLD = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
FONT_MED = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
FONT_MONO = "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Bold.ttf"

# Paleta
NIGHT = (10, 18, 30)
ICE = (150, 190, 215)
DIRTY = (200, 202, 194)
SNOW = (215, 225, 232)
TEAL = (28, 66, 72)
MUSTARD = (226, 160, 52)
MUSTARD_HOOD = (214, 138, 40)
CRIMSON = (140, 18, 34)
RED = (220, 40, 40)
BLUE = (50, 90, 235)
SKIN = (196, 150, 120)
SKIN2 = (170, 120, 95)
HAIR = (26, 20, 18)
JACKET = (52, 68, 80)  # chaqueta de trabajo del repartidor
BEANIE = (120, 36, 36)


@lru_cache(maxsize=64)
def font(path, size):
    return ImageFont.truetype(path, size)


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def smooth(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def ramp(t, a, b):
    """0 antes de a, 1 despues de b, suave entre medio."""
    if b <= a:
        return 1.0 if t >= a else 0.0
    return smooth((t - a) / (b - a))


def lerp(a, b, k):
    return a + (b - a) * k


def lerpc(c1, c2, k):
    return tuple(int(lerp(a, b, k)) for a, b in zip(c1, c2))


def vgrad(w, h, stops):
    """stops: lista de (pos 0..1, (r,g,b))."""
    y = np.linspace(0, 1, h)
    out = np.zeros((h, 3), np.float32)
    ps = [s[0] for s in stops]
    for c in range(3):
        out[:, c] = np.interp(y, ps, [s[1][c] for s in stops])
    arr = np.repeat(out[:, None, :], w, axis=1)
    return Image.fromarray(arr.astype(np.uint8), "RGB")


@lru_cache(maxsize=256)
def glow_sprite(r, color, power=2.0, strength=1.0, sx=1.0, sy=1.0):
    rw, rh = max(2, int(r * sx)), max(2, int(r * sy))
    yy, xx = np.mgrid[-rh:rh, -rw:rw].astype(np.float32)
    d = np.sqrt((xx / rw) ** 2 + (yy / rh) ** 2)
    f = np.clip(1 - d, 0, 1) ** power * strength
    arr = np.stack([f * c for c in color], -1)
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")


def add_glow(img, cx, cy, r, color, strength=1.0, power=2.0, sx=1.0, sy=1.0):
    """Luz aditiva sobre img (RGB)."""
    if r < 2 or strength <= 0:
        return
    q = round(strength, 2)
    spr = glow_sprite(int(r), tuple(int(c) for c in color), power, q, sx, sy)
    x0, y0 = int(cx - spr.width / 2), int(cy - spr.height / 2)
    bx0, by0 = max(x0, 0), max(y0, 0)
    bx1, by1 = min(x0 + spr.width, img.width), min(y0 + spr.height, img.height)
    if bx1 <= bx0 or by1 <= by0:
        return
    region = img.crop((bx0, by0, bx1, by1))
    s = spr.crop((bx0 - x0, by0 - y0, bx1 - x0, by1 - y0))
    if img.mode == "RGBA":
        s = s.convert("RGBA"); s.putalpha(s.convert("L"))
    img.paste(ImageChops.add(region, s), (bx0, by0))


def add_poly_light(img, pts, color, alpha=0.35, blur=18):
    """Haz de luz aditivo con forma de poligono."""
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    pad = blur * 3
    x0, y0 = int(max(min(xs) - pad, 0)), int(max(min(ys) - pad, 0))
    x1, y1 = int(min(max(xs) + pad, img.width)), int(min(max(ys) + pad, img.height))
    if x1 <= x0 or y1 <= y0:
        return
    m = Image.new("L", (x1 - x0, y1 - y0), 0)
    ImageDraw.Draw(m).polygon([(x - x0, y - y0) for x, y in pts], fill=int(255 * alpha))
    if blur:
        m = m.filter(ImageFilter.GaussianBlur(blur))
    col = Image.new("RGB", m.size, color)
    lit = Image.composite(col, Image.new("RGB", m.size, 0), m)
    region = img.crop((x0, y0, x1, y1))
    if img.mode == "RGBA":
        lit = lit.convert("RGBA"); lit.putalpha(lit.convert("L"))
    img.paste(ImageChops.add(region, lit), (x0, y0))


def ell(cx, cy, rx, ry, n=20, a0=0, a1=2 * math.pi):
    return [(cx + rx * math.cos(a0 + (a1 - a0) * i / n), cy + ry * math.sin(a0 + (a1 - a0) * i / n))
            for i in range(n + (0 if a1 - a0 >= 2 * math.pi - 1e-6 else 1))]


def rrect(d, box, r, fill):
    d.rounded_rectangle(box, r, fill=fill)


def cam(img, z=1.0, fx=W / 2, fy=H / 2, rot=0.0, shake=(0, 0)):
    """Camara: zoom z centrado en (fx, fy)."""
    w, h = img.size
    cw, ch = w / z, h / z
    x0 = clamp(fx - cw / 2 + shake[0], 0, w - cw)
    y0 = clamp(fy - ch / 2 + shake[1], 0, h - ch)
    if z == 1.0 and not rot and shake == (0, 0):
        return img
    out = img.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))
    if rot:
        out = out.rotate(rot, Image.BILINEAR, expand=False, fillcolor=(0, 0, 0))
    return out


def text_center(d, xy, s, f, fill, stroke=0, stroke_fill=(0, 0, 0), anchor="mm"):
    d.text(xy, s, font=f, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=stroke_fill)


# ------------------------------------------------------------------ figuras
def _tf(pts, x, y, h, lean=0.0, flip=1, rot=None):
    out = []
    for u, v in pts:
        if rot:
            cx, cy, a = rot
            du, dv = u - cx, v - cy
            u, v = cx + du * math.cos(a) - dv * math.sin(a), cy + du * math.sin(a) + dv * math.cos(a)
        out.append((x + h * (flip * u + lean * v), y - h * v))
    return out


def person(d, x, y, h, jacket=JACKET, pants=(32, 32, 40), skin=SKIN, hair=HAIR, hat=None,
           walk=0.0, crook=0.0, lean=0.0, sil=None, vest=False, hip=0.49, arm=(0, 0, 0, 0),
           boots=(22, 20, 22), hood=None, flip=1, front=False):
    """Persona adulta vista de espaldas (o de frente sin rasgos), pies en (x, y), altura h.
    walk: -1..1 balanceo de piernas; crook: torcido (criaturas)."""
    c = (lambda col: sil if sil is not None else col)
    off = hip - 0.49
    wl = walk * 0.06
    # piernas
    for s in (-1, 1):
        k = wl * s
        leg = [(s * 0.005, hip), (s * 0.115, hip), (s * 0.10 + k, 0.03), (s * 0.03 + k, 0.03)]
        d.polygon(_tf(leg, x, y, h, lean, flip), fill=c(pants))
        bt = [(s * 0.025 + k, 0.05), (s * 0.105 + k, 0.05), (s * 0.11 + k, 0.0), (s * 0.02 + k, 0.0)]
        d.polygon(_tf(bt, x, y, h, lean, flip), fill=c(boots))
    # brazos (detras del torso para que el torso los tape un poco)
    al, ar = arm[0:2], arm[2:4]
    for s, (ax, ay) in ((-1, al), (1, ar)):
        dy = crook * (0.06 if s > 0 else -0.02)
        a = [(s * 0.13, 0.80 + off - dy), (s * 0.20, 0.77 + off - dy), (s * (0.19 + ax), 0.47 + off + ay - dy),
             (s * (0.135 + ax), 0.47 + off + ay - dy), (s * 0.12, 0.72 + off)]
        d.polygon(_tf(a, x, y, h, lean, flip), fill=c(lerpc(jacket, (0, 0, 0), 0.18)))
        hand = ell(s * (0.162 + ax), 0.455 + off + ay - dy, 0.03, 0.035, 10)
        d.polygon(_tf(hand, x, y, h, lean, flip), fill=c(skin))
    # torso
    tor = [(-0.15, 0.80 + off - crook * 0.02), (0.15, 0.80 + off - crook * 0.06), (0.135, hip - 0.02),
           (-0.135, hip - 0.02)]
    d.polygon(_tf(tor, x, y, h, lean, flip), fill=c(jacket))
    d.polygon(_tf(ell(0, 0.795 + off - crook * 0.04, 0.152, 0.045, 18), x, y, h, lean, flip), fill=c(jacket))
    if vest and sil is None:
        vv = [(-0.12, 0.76 + off), (0.12, 0.76 + off), (0.115, hip + 0.02), (-0.115, hip + 0.02)]
        d.polygon(_tf(vv, x, y, h, lean, flip), fill=(178, 196, 60))
        for yy in (0.66, 0.56):
            band = [(-0.12, yy + off), (0.12, yy + off), (0.12, yy - 0.022 + off), (-0.12, yy - 0.022 + off)]
            d.polygon(_tf(band, x, y, h, lean, flip), fill=(225, 228, 220))
    # cuello y cabeza
    hr = (0, 0.84 + off, crook * 0.5)
    neck = [(-0.03, 0.80 + off), (0.03, 0.80 + off), (0.03, 0.86 + off), (-0.03, 0.86 + off)]
    d.polygon(_tf(neck, x, y, h, lean, flip, hr), fill=c(skin))
    hx = crook * 0.04
    if hood is not None:
        d.polygon(_tf(ell(hx, 0.83 + off, 0.09, 0.05, 16), x, y, h, lean, flip, hr), fill=c(hood))
    d.polygon(_tf(ell(hx, 0.905 + off, 0.062, 0.075, 20), x, y, h, lean, flip, hr), fill=c(skin if front else hair))
    if front and sil is None:
        d.polygon(_tf(ell(hx, 0.95 + off, 0.064, 0.04, 16, 0, math.pi), x, y, h, lean, flip, hr),
                  fill=c(hair))
    if not front:
        for s in (-1, 1):
            d.polygon(_tf(ell(hx + s * 0.062, 0.9 + off, 0.012, 0.02, 8), x, y, h, lean, flip, hr), fill=c(skin))
    if hat is not None:
        d.polygon(_tf(ell(hx, 0.925 + off, 0.067, 0.06, 18, 0, math.pi), x, y, h, lean, flip, hr),
                  fill=c(hat))
        band = [(hx - 0.068, 0.93 + off), (hx + 0.068, 0.93 + off), (hx + 0.068, 0.905 + off),
                (hx - 0.068, 0.905 + off)]
        d.polygon(_tf(band, x, y, h, lean, flip, hr), fill=c(lerpc(hat, (0, 0, 0), 0.25)))


def creature(d, x, y, h, t, seed=0, color=(14, 18, 24)):
    """Silueta adulta caminando torcida (sin detalles, sin sangre)."""
    ph = t * 2.2 + seed * 1.7
    person(d, x, y, h, sil=color, walk=math.sin(ph) * 0.7, crook=0.35 + 0.15 * math.sin(ph * 0.5 + seed),
           lean=0.08 * math.sin(ph * 0.5 + seed), arm=(0.02, -0.04 + 0.03 * math.sin(ph), 0.05, 0.05))


def spectator_seated(d, img, x, y, s, turn=0.0):
    """El Espectador sentado: capucha mostaza, pelo oscuro corto, costados rebajados.
    (x, y) = base de los hombros, s = escala (ancho de cabeza ~ s)."""
    hood = MUSTARD_HOOD
    sh = [(x - 1.55 * s, y + 0.9 * s), (x - 1.35 * s, y - 0.25 * s), (x - 0.6 * s, y - 0.55 * s),
          (x + 0.6 * s, y - 0.55 * s), (x + 1.35 * s, y - 0.25 * s), (x + 1.55 * s, y + 0.9 * s)]
    d.polygon(sh, fill=hood)
    # sombra lateral de la chaqueta
    d.polygon([(x + 0.7 * s, y - 0.5 * s), (x + 1.35 * s, y - 0.25 * s), (x + 1.55 * s, y + 0.9 * s),
               (x + 0.9 * s, y + 0.9 * s)], fill=lerpc(hood, (40, 20, 10), 0.35))
    # capucha caida
    d.polygon(ell(x, y - 0.5 * s, 0.75 * s, 0.32 * s, 22), fill=lerpc(hood, (60, 30, 5), 0.25))
    d.polygon(ell(x, y - 0.56 * s, 0.5 * s, 0.18 * s, 18), fill=lerpc(hood, (30, 15, 0), 0.45))
    # cuello
    d.rectangle([x - 0.22 * s, y - 0.9 * s, x + 0.22 * s, y - 0.5 * s], fill=SKIN2)
    hx = x + turn * 0.05 * s
    hy = y - 1.25 * s
    # cabeza: piel en los costados (rebajados), pelo arriba
    d.polygon(ell(hx, hy, 0.5 * s, 0.6 * s, 26), fill=lerpc(SKIN2, HAIR, 0.55))
    d.polygon(ell(hx, hy - 0.22 * s, 0.5 * s, 0.4 * s, 22, math.pi, 2 * math.pi), fill=HAIR)
    d.polygon(ell(hx - turn * 0.1 * s, hy - 0.05 * s, 0.38 * s, 0.5 * s, 22), fill=HAIR)
    if turn <= 0.05:
        for sd in (-1, 1):
            d.polygon(ell(hx + sd * 0.5 * s, hy + 0.05 * s, 0.08 * s, 0.14 * s, 10), fill=SKIN2)
    else:
        # perfil hacia la derecha: oreja, mejilla, nariz y barba ligera
        k = turn
        d.polygon(ell(hx + 0.28 * s * k, hy + 0.08 * s, 0.32 * s * k + 0.02 * s, 0.42 * s, 18), fill=SKIN2)
        d.polygon(ell(hx + 0.1 * s, hy + 0.05 * s, 0.08 * s, 0.14 * s, 10), fill=lerpc(SKIN2, (0, 0, 0), 0.2))
        nose = [(hx + 0.5 * s * k + 0.05 * s, hy - 0.02 * s), (hx + 0.66 * s * k + 0.05 * s, hy + 0.18 * s),
                (hx + 0.5 * s * k + 0.05 * s, hy + 0.22 * s)]
        d.polygon(nose, fill=SKIN2)
        d.polygon(ell(hx + 0.36 * s * k, hy + 0.38 * s, 0.24 * s * k + 0.02 * s, 0.16 * s, 14),
                  fill=lerpc(SKIN2, HAIR, 0.6))
        d.polygon(ell(hx - 0.05 * s, hy - 0.08 * s, 0.4 * s, 0.42 * s, 22, math.pi * 0.95, math.pi * 1.95),
                  fill=HAIR)


def pine(d, x, y, h, col=(12, 26, 30), snow=(190, 205, 212), snowk=0.5):
    """Pino estilizado con nieve. (x, y) base."""
    d.rectangle([x - h * 0.03, y - h * 0.12, x + h * 0.03, y], fill=lerpc(col, (0, 0, 0), 0.4))
    tiers = 4
    for i in range(tiers):
        b = y - h * (0.1 + i * 0.2)
        wdt = h * (0.32 - i * 0.065)
        top = b - h * 0.34
        d.polygon([(x - wdt, b), (x + wdt, b), (x, top)], fill=col)
        if snowk > 0:
            d.polygon([(x - wdt * 0.8, b - h * 0.02), (x - wdt * 0.1, b - h * 0.05), (x - wdt * 0.15, top + h * 0.12)],
                      fill=lerpc(col, snow, snowk))


def snow_layer(img, t, n=220, seed=1, speed=140, size=(1.0, 3.2), alpha=200, wind=-30, region=None, streak=0):
    """Nieve cayendo sobre img (RGB). Deterministica en t."""
    rng = np.random.default_rng(seed)
    x0 = rng.uniform(0, img.width, n); y0 = rng.uniform(0, img.height, n)
    sz = rng.uniform(size[0], size[1], n); sp = rng.uniform(0.6, 1.3, n) * speed
    ph = rng.uniform(0, 6.28, n)
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for i in range(n):
        y = (y0[i] + sp[i] * t * (sz[i] / size[1] + 0.4)) % img.height
        x = (x0[i] + wind * t * (sz[i] / size[1]) + 12 * math.sin(t * 1.3 + ph[i])) % img.width
        r = sz[i]
        a = int(alpha * (0.45 + 0.55 * sz[i] / size[1]))
        if streak:
            d.line([(x, y), (x - wind * 0.02 * streak, y - streak * r)], fill=(235, 240, 245, a), width=max(1, int(r)))
        else:
            d.ellipse([x - r, y - r, x + r, y + r], fill=(235, 240, 245, a))
    if region is not None:
        m = Image.new("L", img.size, 0); ImageDraw.Draw(m).polygon(region, fill=255)
        ov.putalpha(ImageChops.multiply(ov.getchannel("A"), m))
    img.paste(ov, (0, 0), ov)


def dust_in_beam(img, t, pts, n=70, seed=3, color=(255, 230, 170)):
    """Polvo flotando dentro de un haz (poligono)."""
    rng = np.random.default_rng(seed)
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    m = Image.new("L", img.size, 0); ImageDraw.Draw(m).polygon(pts, fill=255)
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    for i in range(n):
        x = rng.uniform(min(xs), max(xs)) + 18 * math.sin(t * 0.5 + i)
        y = rng.uniform(min(ys), max(ys)) + 14 * math.cos(t * 0.4 + i * 1.3) - 6 * t
        r = rng.uniform(0.8, 2.2)
        d.ellipse([x - r, y - r, x + r, y + r], fill=color + (int(rng.uniform(80, 200)),))
    ov.putalpha(ImageChops.multiply(ov.getchannel("A"), m))
    img.paste(ov, (0, 0), ov)


def thermal_box(d, x, y, w, h, label=True, top=True):
    """Caja termica blanca con cruz medica y etiqueta roja. (x, y) esquina sup. izq. del frente."""
    if top:
        d.polygon([(x, y), (x + w, y), (x + w * 0.92, y - h * 0.22), (x + w * 0.08, y - h * 0.22)],
                  fill=(232, 236, 236))
    d.rectangle([x, y, x + w, y + h], fill=(214, 220, 222))
    d.rectangle([x, y + h * 0.9, x + w, y + h], fill=(170, 178, 182))
    cx, cy, s = x + w * 0.3, y + h * 0.45, min(w, h) * 0.17
    d.rectangle([cx - s, cy - s * 0.33, cx + s, cy + s * 0.33], fill=(200, 28, 36))
    d.rectangle([cx - s * 0.33, cy - s, cx + s * 0.33, cy + s], fill=(200, 28, 36))
    if label:
        d.rectangle([x + w * 0.55, y + h * 0.25, x + w * 0.92, y + h * 0.62], fill=(205, 30, 38))
        for k in range(3):
            yy = y + h * (0.32 + k * 0.09)
            d.rectangle([x + w * 0.6, yy, x + w * (0.86 - k * 0.08), yy + h * 0.035], fill=(250, 220, 220))


def hexagon(cx, cy, r, rot=0.0):
    return [(cx + r * math.cos(rot + i * math.pi / 3), cy + r * math.sin(rot + i * math.pi / 3)) for i in range(6)]


def hex_logo(d, cx, cy, r, col=(240, 240, 240), bg=None):
    """Logotipo corporativo generico: hexagono doble (sin parecido con logos reales)."""
    if bg:
        d.polygon(hexagon(cx, cy, r * 1.05, math.pi / 6), fill=bg)
    d.polygon(hexagon(cx, cy, r, math.pi / 6), outline=col, width=max(2, int(r * 0.14)))
    d.polygon(hexagon(cx, cy, r * 0.45, math.pi / 6), fill=col)


# --------------------------------------------------------------- posproceso
_rng = np.random.default_rng(7)
GRAIN = [(_rng.normal(0, 4.5, (H, W, 1))).astype(np.float32) for _ in range(6)]
_yy, _xx = np.mgrid[0:H, 0:W].astype(np.float32)
VIGN = (1 - 0.55 * np.clip(np.sqrt(((_xx - W / 2) / (W * 0.62)) ** 2 + ((_yy - H / 2) / (H * 0.62)) ** 2) - 0.35,
                           0, 1) ** 1.4)[..., None].astype(np.float32)
HAZE = np.array([22, 48, 50], np.float32)


def grade(img, fi, haze=0.10, soft=0.7):
    """Bruma verde azulada, negros levantados, vineta y grano."""
    if soft:
        img = img.filter(ImageFilter.GaussianBlur(soft))
    a = np.asarray(img, np.float32)
    a = a * (1 - haze) + HAZE * haze + 6
    a = a * VIGN + GRAIN[fi % len(GRAIN)]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGB")
