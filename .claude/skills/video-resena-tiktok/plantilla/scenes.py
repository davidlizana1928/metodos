"""Resident Evil: Noche Cero - 14 escenas procedurales (1080x1920)."""
import math, random, json
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from lib import *

_seg = json.load(open("segments.json"))
PS = [s["start"] for s in _seg]
END = round(_seg[-1]["end"] + 1.0, 3)
# escenas 1..13 = frases 1..13 ; escena 14 = frases 14 (título) + 15 (pregunta)
B = PS[:14] + [END]
TITLE_T = PS[13]
X2 = (B[4] + 0.55 * (B[5] - B[4]), B[5] - 0.05)  # sello x2 dentro de la escena 5 (b)

NAVY = (30, 42, 74)
STRIPE = (176, 180, 186)
BEANIE = (118, 120, 124)
BROWN = (92, 62, 42)
WINE = (72, 30, 44)
BLOND = (196, 170, 110)
CARGRAY = (118, 122, 128)
POLICE = (24, 32, 54)
HAZ = (196, 200, 198)
SNOW = (196, 210, 226)
NIGHT = (14, 20, 36)
GREENV = (110, 210, 120)

_cache = {}


def snap(t, g=0.3):
    return round(t / g) * g


def camera(world, cx, cy, z, shake=0.0, lt=0.0):
    z = max(z, 1.0)
    if shake:
        cx += shake * math.sin(lt * 53)
        cy += shake * math.cos(lt * 47)
    hw, hh = W / (2 * z), H / (2 * z)
    cx = clamp(cx, hw, world.size[0] - hw)
    cy = clamp(cy, hh, world.size[1] - hh)
    a = 1 / z
    return world.transform((W, H), Image.AFFINE, (a, 0, cx - hw, 0, a, cy - hh), Image.BICUBIC)


def cam_path(lt, keys):
    if lt <= keys[0][0]:
        return keys[0][1:]
    for (t0, *a), (t1, *b) in zip(keys, keys[1:]):
        if lt <= t1:
            u = sstep(t0, t1, lt)
            return tuple(lerp(p, q, u) for p, q in zip(a, b))
    return keys[-1][1:]


def blend(a, b, u):
    if u <= 0:
        return a
    if u >= 1:
        return b
    return Image.blend(a, b, u)


def subshots(lt, dur, shots, xf=0.3):
    """shots: list of functions f(t); split dur equally with crossfades on the 0.3 s grid."""
    n = len(shots)
    cuts = [snap(dur * k / n) for k in range(1, n)]
    for k, c in enumerate(cuts):
        if lt < c - xf / 2:
            return shots[k](lt)
        if lt < c + xf / 2:
            return blend(shots[k](lt), shots[k + 1](lt), sstep(c - xf / 2, c + xf / 2, lt))
    return shots[-1](lt)


def cuts_of(dur, n):
    return [0.0] + [snap(dur * k / n) for k in range(1, n)] + [dur]


# ------------------------------------------------------------------ atmosphere

def snowfall(img, lt, n=260, wind=0.25, speed=160, seed=1, col=SNOW, big=12, box=None):
    d = ImageDraw.Draw(img)
    w, h = img.size
    rng = random.Random(seed)
    for i in range(n):
        x0, y0 = rng.uniform(0, w), rng.uniform(0, h)
        sp = rng.uniform(0.6, 1.4)
        s = rng.uniform(1.2, 3.2)
        y = (y0 + speed * sp * lt) % h
        x = (x0 + wind * speed * sp * lt + 12 * math.sin(lt * 1.3 + i)) % w
        if wind > 0.8:
            d.line((x, y, x - wind * 9 * s, y - 9 * s), fill=col, width=max(1, int(s)))
        else:
            d.ellipse((x - s, y - s, x + s, y + s), fill=col)
    for i in range(big):
        x0, y0 = rng.uniform(0, w), rng.uniform(0, h)
        y = (y0 + speed * 2.2 * lt) % h
        x = (x0 + wind * speed * 2.2 * lt) % w
        s = rng.uniform(7, 12)
        ell_a(img, (x - s, y - s, x + s, y + s), col, 0.55, blur=3)


def mountains(d, base, col, seed, amp=300, step=90):
    rng = random.Random(seed)
    pts = [(-50, H)]
    x = -50
    while x < W + 100:
        pts.append((x, base - rng.uniform(0.3, 1.0) * amp))
        x += rng.uniform(step * 0.6, step * 1.4)
    pts.append((W + 100, H))
    d.polygon(pts, fill=col)
    # snow caps
    for (x0, y0), (x1, y1) in zip(pts[1:-2], pts[2:-1]):
        if y1 < y0:
            d.polygon([(x0, y0 + 30), (x1, y1), (x1 + 25, y1 + 40)], fill=shade(col, 1.6))


def town(im, x0, y0, w, lt, k=1.0, seed=3, smoke=True):
    """small mountain city with flickering windows and smoke columns."""
    d = ImageDraw.Draw(im)
    rng = random.Random(seed)
    x = x0
    while x < x0 + w:
        bw = rng.randint(int(18 * k), int(46 * k))
        bh = rng.randint(int(40 * k), int(170 * k))
        d.rectangle((x, y0 - bh, x + bw, y0), fill=(22, 26, 40))
        dark = rng.random() < 0.35  # barrios con luz cortada
        for wy in range(int(y0 - bh + 6 * k), int(y0 - 4), max(3, int(12 * k))):
            for wx in range(int(x + 4 * k), int(x + bw - 4 * k), max(3, int(10 * k))):
                r = rng.random()
                if dark or r < 0.5:
                    continue
                fl = 1.0 if r > 0.1 else (0.3 + 0.7 * (math.sin(lt * 23 + wx) > 0))
                d.rectangle((wx, wy, wx + max(1, int(4 * k)), wy + max(1, int(5 * k))),
                            fill=lerpc((40, 36, 30), (230, 190, 110), fl))
        x += bw + rng.randint(1, int(8 * k) + 1)
    glow(im, x0 + w / 2, y0 - 30 * k, int(w * 0.6), (120, 90, 60), 0.35)
    if smoke:
        for j in range(3):
            sx = x0 + w * (0.2 + 0.3 * j)
            for q in range(6):
                yy = y0 - 60 * k - q * 55 * k - (lt * 20) % (55 * k)
                rr = (18 + q * 10) * k
                ell_a(im, (sx - rr + q * 9 * k, yy - rr, sx + rr + q * 9 * k, yy + rr), (60, 62, 70), 0.35, blur=8 * k)


def creature(d, x, yf, h, seed=0, lt=0.0, col=(14, 18, 16)):
    rng = random.Random(seed)
    sway = math.sin(lt * 2 + seed) * h * 0.03
    hip = (x, yf - h * 0.48)
    sh = (x + h * 0.12 + sway, yf - h * 0.78)
    d.line((hip[0] - h * 0.05, hip[1], hip[0] - h * 0.1, yf), fill=col, width=int(h * 0.07))
    d.line((hip[0] + h * 0.05, hip[1], hip[0] + h * 0.12, yf), fill=col, width=int(h * 0.07))
    d.polygon([(hip[0] - h * 0.09, hip[1]), (hip[0] + h * 0.09, hip[1]), (sh[0] + h * 0.1, sh[1]), (sh[0] - h * 0.12, sh[1] - h * 0.02)], fill=col)
    d.ellipse((sh[0] + h * 0.05, sh[1] - h * 0.02, sh[0] + h * 0.2, sh[1] + h * 0.12), fill=col)  # head, low & forward
    d.line((sh[0] - h * 0.08, sh[1], sh[0] - h * 0.1, yf - h * 0.32), fill=col, width=int(h * 0.05))
    d.line((sh[0] + h * 0.08, sh[1] + h * 0.02, sh[0] + h * 0.18, yf - h * 0.28), fill=col, width=int(h * 0.05))
    for k in range(5):  # irregular growths
        gx = sh[0] + rng.uniform(-0.15, 0.1) * h
        gy = sh[1] + rng.uniform(-0.08, 0.15) * h
        gr = rng.uniform(0.03, 0.07) * h
        d.ellipse((gx - gr, gy - gr, gx + gr, gy + gr * 0.8), fill=shade(col, 1.3))


def dog_creature(d, x, yf, h, lt, f=1, col=(14, 16, 16)):
    L = h * 1.6
    run = math.sin(lt * 14)
    by = yf - h * 0.55
    d.ellipse((x - L / 2, by - h * 0.25, x + L / 2, by + h * 0.22), fill=col)
    for k, (lx, ph) in enumerate([(-0.35, 0), (-0.2, 3), (0.25, 1.5), (0.38, 4.5)]):
        a = math.sin(lt * 14 + ph) * 0.5
        px = x + lx * L
        d.line((px, by, px + math.sin(a) * h * 0.4 * f, yf), fill=col, width=int(h * 0.09))
    hx = x + f * L * 0.55
    hy = by - h * 0.2 + run * h * 0.03
    d.ellipse((hx - h * 0.2, hy - h * 0.18, hx + h * 0.2, hy + h * 0.16), fill=col)
    # jaw opened unnaturally wide
    d.polygon([(hx + f * h * 0.1, hy - h * 0.05), (hx + f * h * 0.55, hy - h * 0.35), (hx + f * h * 0.5, hy - h * 0.2)], fill=col)
    d.polygon([(hx + f * h * 0.1, hy + h * 0.05), (hx + f * h * 0.55, hy + h * 0.4), (hx + f * h * 0.45, hy + h * 0.25)], fill=col)
    for k in range(4):  # dark tentacles from the mouth
        pts = []
        for i in range(12):
            u = i / 11
            pts.append((hx + f * (h * 0.2 + u * h * 0.6), hy + math.sin(u * 5 + lt * 6 + k * 1.7) * h * 0.12 * u + (k - 1.5) * h * 0.06 * u))
        d.line(pts, fill=(30, 40, 34), width=max(2, int(h * 0.04 * (1.2 - 0.3 * k / 3))))
    d.line((x - f * L / 2, by - h * 0.05, x - f * L * 0.7, by - h * 0.25), fill=col, width=int(h * 0.05))


def car_side(img, x, yg, L, f=1, col=CARGRAY, head=True, brake=0.0, light=None):
    d = ImageDraw.Draw(img)
    h = L * 0.36
    d.rounded_rectangle((x - L / 2, yg - h * 0.85, x + L / 2, yg - h * 0.18), radius=int(h * 0.2), fill=col)
    c0 = x - f * L * 0.25
    d.polygon([(c0 - L * 0.08, yg - h * 0.8), (x + f * L * 0.18, yg - h * 0.8), (x + f * L * 0.05, yg - h * 1.35), (c0 + f * L * 0.02, yg - h * 1.35)][::1], fill=col)
    d.polygon([(c0 - L * 0.02 * f + f * 6, yg - h * 0.86), (x + f * L * 0.14, yg - h * 0.86), (x + f * L * 0.04, yg - h * 1.27), (c0 + f * L * 0.05, yg - h * 1.27)],
              fill=(26, 34, 50))
    for wx in (x - L * 0.32, x + L * 0.32):
        d.ellipse((wx - h * 0.3, yg - h * 0.5, wx + h * 0.3, yg + h * 0.1), fill=(14, 14, 16))
        d.ellipse((wx - h * 0.13, yg - h * 0.33, wx + h * 0.13, yg - h * 0.07), fill=(70, 72, 76))
    fx, bx = x + f * L / 2, x - f * L / 2
    if head:
        d.ellipse((fx - h * 0.08, yg - h * 0.68, fx + h * 0.08, yg - h * 0.52), fill=(255, 250, 220))
        glow(img, fx, yg - h * 0.6, int(h * 1.2), (255, 240, 200), 0.8)
        poly_a(img, [(fx, yg - h * 0.66), (fx + f * L * 2.2, yg - h * 1.0), (fx + f * L * 2.2, yg + h * 0.5), (fx, yg - h * 0.5)], (255, 245, 210), 0.18, blur=12)
    d.rectangle((bx - h * 0.04, yg - h * 0.68, bx + h * 0.04, yg - h * 0.5), fill=(170, 20, 20))
    if brake > 0:
        glow(img, bx, yg - h * 0.6, int(h * 2.5), (255, 30, 20), brake)
    if light is not None:  # police bar: light = phase 0..1
        lx = x
        d.rectangle((lx - h * 0.3, yg - h * 1.45, lx + h * 0.3, yg - h * 1.35), fill=(30, 30, 34))
        red = light % 1 < 0.5
        glow(img, lx - h * 0.2, yg - h * 1.42, int(h * (2.2 if red else 0.8)), (255, 30, 40), 1.0 if red else 0.3)
        glow(img, lx + h * 0.2, yg - h * 1.42, int(h * (0.8 if red else 2.2)), (40, 90, 255), 0.3 if red else 1.0)


def courier_side(d, x, yf, h, f=1, arms="down", step=0.0, lean=0.0, pack=True, smile=0.0):
    if pack:
        bx = x - f * h * 0.12
        d.rounded_rectangle((bx - h * 0.07, yf - h * 0.8, bx + h * 0.07, yf - h * 0.52), radius=int(h * 0.02), fill=(236, 238, 240))
        d.rectangle((bx - h * 0.03, yf - h * 0.82, bx + h * 0.03, yf - h * 0.8), fill=(15, 15, 15))
    hx, hy, r = person_side(d, x, yf, h, f, NAVY, BROWN, coatlen=0.34, arms=arms, step=step, lean=lean,
                            beard=(140, 104, 84), smile=smile, pants=(40, 44, 56))
    d.chord((hx - r * 1.08, hy - r * 1.25, hx + r * 1.08, hy - r * 0.05), 180, 360, fill=BEANIE)
    d.rectangle((hx - r * 1.08, hy - r * 0.62, hx + r * 1.08, hy - r * 0.45), fill=shade(BEANIE, 0.85))
    d.line((hx - f * r * 1.0, hy + r * 0.2, hx - f * r * 1.3, hy + r * 0.45), fill=BROWN, width=max(2, int(r * 0.2)))
    d.line((x - h * 0.06, yf - h * 0.66, x + h * 0.06, yf - h * 0.66), fill=STRIPE, width=max(2, int(h * 0.012)))
    return hx, hy, r


def courier_back(d, x, yf, h, step=0.0, pack=True):
    person_back(d, x, yf, h, NAVY, BEANIE, pants=(40, 44, 56), coatlen=0.34, step=step)
    top = yf - h
    for s in (-1, 1):
        d.line((x + s * h * 0.17, top + h * 0.33, x + s * h * 0.17, top + h * 0.36), fill=STRIPE, width=max(2, int(h * 0.04)))
    if pack:
        d.rounded_rectangle((x - h * 0.1, top + h * 0.2, x + h * 0.1, top + h * 0.47), radius=int(h * 0.02), fill=(236, 238, 240))
        d.rectangle((x - h * 0.04, top + h * 0.18, x + h * 0.04, top + h * 0.2), fill=(15, 15, 15))


def metal_box(d, x, y, s):
    d.rectangle((x - s, y - s * 0.6, x + s, y + s * 0.6), fill=(150, 156, 162))
    d.rectangle((x - s, y - s * 0.6, x + s, y - s * 0.35), fill=(186, 192, 198))
    d.line((x - s, y - s * 0.35, x + s, y - s * 0.35), fill=(90, 96, 100), width=max(2, int(s * 0.05)))
    d.rectangle((x - s * 0.12, y - s * 0.42, x + s * 0.12, y - s * 0.28), fill=(60, 64, 68))


# ================================================================ cinema (1 & 14)
SCR = (30, 600, 1050, 1180)
PROJ = (60, 250)


def cinema_bg():
    if "cin" in _cache:
        return _cache["cin"]
    im = vgrad(W, H, [(0, (14, 12, 16)), (0.5, (20, 16, 20)), (1, (8, 6, 8))])
    d = ImageDraw.Draw(im)
    for i in range(40):
        x = i * 27
        d.rectangle((x, 0, x + 27, 560), fill=CRIMSON_D if i % 2 else shade(CRIMSON, 0.55))
    d.rectangle((0, 540, W, 575), fill=(40, 12, 18))
    x0, y0, x1, y1 = SCR
    d.rectangle((x0 - 18, y0 - 18, x1 + 18, y1 + 18), fill=(5, 5, 5))
    d.rectangle((0, 190, 110, 310), fill=(10, 10, 12))
    d.rectangle((35, 220, 95, 280), fill=(30, 30, 34))
    for (y, w, n) in [(1250, 110, 9), (1330, 140, 7)]:
        span = n * w * 1.1
        for i in range(n):
            seat_back(d, W / 2 - span / 2 + (i + 0.5) * span / n, y, w, shade(CRIMSON, 0.55))
    _cache["cin"] = im
    return im


def cinema_world(lt, content, beam=1.0, dim=1.0):
    im = cinema_bg().copy()
    x0, y0, x1, y1 = SCR
    im.paste(content.resize((x1 - x0, y1 - y0)), (x0, y0))
    d = ImageDraw.Draw(im)
    if beam > 0:
        poly_a(im, [(PROJ[0] + 30, PROJ[1] - 8), (x1, y0), (x1, y1), (PROJ[0] + 30, PROJ[1] + 8)], (220, 230, 240), 0.1 * beam, blur=14)
        glow(im, PROJ[0] + 35, PROJ[1], 90, (230, 240, 255), beam)
        rng = random.Random(2)
        for i in range(170):
            t = rng.random()
            yy = lerp(PROJ[1], lerp(y0, y1, rng.random()), t)
            xx = lerp(PROJ[0] + 30, x1, t) + 20 * math.sin(lt * 0.6 + i)
            yy += 14 * math.cos(lt * 0.5 + i * 2)
            s = rng.uniform(1, 2.6)
            c = int(150 + 90 * (0.5 + 0.5 * math.sin(lt * 3 + i))) * beam
            d.ellipse((xx - s, yy - s, xx + s, yy + s), fill=(int(c), int(c), int(c * 0.95)))
    # second row: spectator (shoulders = 0.8 seat width)
    rim = (150, 170, 190)
    for i in range(5):
        x = 108 + i * 216
        if i == 2:
            bust_back(d, x, 1500, 173, (36, 34, 34), DARKHAIR, hood=MUSTARD, hairshape="fade", rim=rim)
            seat_back(d, x - 120, 1540, 60, shade(CRIMSON, 0.7))
        else:
            seat_back(d, x, 1470, 196, shade(CRIMSON, 0.75))
    for i in range(5):  # first row (foreground)
        seat_back(d, 108 + i * 216 + 10, 1700, 206, shade(CRIMSON, 0.95))
    if dim < 1:
        im = Image.eval(im, lambda v: int(v * dim))
    return im


def city_panorama(w, h, lt, creatures=False):
    im = vgrad(w, h, [(0, (10, 14, 28)), (0.6, (24, 30, 50)), (1, (40, 46, 62))])
    d = ImageDraw.Draw(im)
    rng = random.Random(4)
    pts = [(0, h)] + [(x, h * 0.45 - rng.uniform(0, h * 0.3)) for x in range(0, w + 80, 80)] + [(w, h)]
    d.polygon(pts, fill=(34, 40, 58))
    for (a, b) in zip(pts[1:-2], pts[2:-1]):
        if b[1] < a[1]:
            d.polygon([(a[0], a[1] + 20), b, (b[0] + 20, b[1] + 30)], fill=(150, 160, 180))
    town(im, int(w * 0.08), int(h * 0.86), int(w * 0.84), lt, k=w / 1020, seed=5)
    if creatures:
        for k in range(5):
            x = (w * 0.15 + k * w * 0.17 + lt * (18 if k % 2 else -14)) % w
            creature(d, x, h * 0.95, h * 0.12, seed=k, lt=lt, col=(8, 10, 10))
    snowfall(im, lt, n=120, wind=0.15, speed=60, seed=9, big=0)
    return im


def scene1(lt, dur):
    e = snap(dur * 0.5)
    content = city_panorama(1020, 580, lt, creatures=lt > e - 0.3)
    im = cinema_world(lt, content)
    cx, cy, z = cam_path(lt, [(0, 540, 1000, 1.0), (e, 540, 960, 1.08), (dur - 0.2, 540, 900, 1.5), (dur + 0.4, 540, 890, 3.2)])
    return camera(im, cx, cy, z)


# ================================================================ 2 car to the mountains
def road_world(lt, carx_u, storm=0.0, spect=False, sign=False, curve=0):
    key = f"road{curve}"
    if key not in _cache:
        im = vgrad(W, H, [(0, (8, 12, 26)), (0.45, (22, 30, 52)), (1, (30, 38, 56))])
        d = ImageDraw.Draw(im)
        mountains(d, 820, (30, 38, 58), 11 + curve, amp=380)
        town(im, 140, 900, 420, 0, k=0.5, seed=8)
        mountains(d, 1120, (40, 48, 66), 21 + curve, amp=200, step=140)
        d.polygon([(0, 1250), (W, 1180), (W, H), (0, H)], fill=(150, 162, 182))
        # road (snowy grey) rising left->right
        d.polygon([(0, 1500), (W, 1300), (W, 1420), (0, 1640)], fill=(64, 70, 82))
        for x in range(0, W, 120):  # guardrail
            y = 1640 - (1640 - 1420) * x / W
            d.rectangle((x, y - 6, x + 8, y + 40), fill=(150, 154, 160))
        d.line((0, 1622, W, 1402), fill=(170, 174, 180), width=8)
        rng = random.Random(5 + curve)
        for i in range(14):  # snowy pines
            x = rng.uniform(0, W)
            y = rng.uniform(1660, 1900)
            s = rng.uniform(60, 120)
            d.polygon([(x, y - s * 2), (x - s * 0.6, y), (x + s * 0.6, y)], fill=(20, 34, 36))
            d.polygon([(x, y - s * 2), (x - s * 0.3, y - s), (x + s * 0.3, y - s)], fill=(190, 200, 214))
        _cache[key] = im
    im = _cache[key].copy()
    x = lerp(-150, W + 150, carx_u)
    yg = 1600 - (1600 - 1380) * clamp(x, 0, W) / W
    if sign:
        d = ImageDraw.Draw(im)
        sx = 860
        sy = 1440 - 160 * sx / W
        d.rectangle((sx - 4, sy - 170, sx + 4, sy), fill=(60, 64, 70))
        d.polygon([(sx - 70, sy - 230), (sx + 60, sy - 230), (sx + 95, sy - 190), (sx + 60, sy - 150), (sx - 70, sy - 150)], fill=(40, 90, 60))
        d.polygon([(sx - 70, sy - 230), (sx + 60, sy - 230), (sx + 75, sy - 212), (sx - 70, sy - 200)], fill=(214, 222, 232))
    if spect:
        d = ImageDraw.Draw(im)
        person_back(d, 300, 1600, 200, (40, 38, 36), DARKHAIR, hood=MUSTARD, hairshape="fade", coatlen=0.4)
        d.line((200, 1560, 420, 1540), fill=(170, 174, 180), width=8)  # rail at knee height
    car_side(im, x, yg, 280, 1, head=True)
    return im


def cab(lt, outside_speed=1.0, phone=None, console=False, thumb=0.0, dashlight=(70, 110, 150), storm=0.3):
    im = Image.new("RGB", (W, H), (10, 12, 20))
    d = ImageDraw.Draw(im)
    # side window with the night outside
    wx0, wy0, wx1, wy1 = 60, 380, 1020, 1100
    out = vgrad(wx1 - wx0, wy1 - wy0, [(0, (10, 16, 32)), (1, (40, 50, 70))])
    od = ImageDraw.Draw(out)
    for k in range(9):
        x = (k * 160 - lt * 600 * outside_speed) % 1300 - 150
        od.polygon([(x, 650), (x - 60, 760), (x + 60, 760)], fill=(16, 26, 30))
    snowfall(out, lt, n=90, wind=1.2 * outside_speed, speed=200, seed=3, big=0)
    im.paste(out, (wx0, wy0))
    d.rounded_rectangle((wx0 - 30, wy0 - 30, wx1 + 30, wy1 + 30), radius=60, outline=(20, 22, 28), width=60)
    # dashboard + wheel
    d.polygon([(0, 1150), (W, 1100), (W, H), (0, H)], fill=(18, 20, 26))
    glow(im, 860, 1180, 260, dashlight, 0.6)
    # passenger seat with strapped medical bag (beyond the driver)
    d.rounded_rectangle((760, 760, 1000, 1150), radius=40, fill=(30, 30, 36))
    d.rounded_rectangle((790, 860, 960, 1080), radius=16, fill=(236, 238, 240))
    d.rectangle((845, 840, 905, 860), fill=(15, 15, 15))
    d.line((770, 820, 990, 1120), fill=(50, 50, 56), width=22)  # seatbelt on the bag
    # driver in profile
    h = 1500
    x = 380
    r = h * 0.068
    hy = 600
    d.rounded_rectangle((x - 150, 760, x + 120, 1500), radius=80, fill=NAVY)
    d.line((x - 120, 900, x + 120, 900), fill=STRIPE, width=14)
    d.rectangle((x - r * 0.4, hy + r * 0.5, x + r * 0.4, 780), fill=SKIN_D)
    head_profile(d, x, hy, r, 1, BROWN, beard=(140, 104, 84))
    d.chord((x - r * 1.08, hy - r * 1.25, x + r * 1.08, hy - r * 0.05), 180, 360, fill=BEANIE)
    d.rectangle((x - r * 1.08, hy - r * 0.62, x + r * 1.08, hy - r * 0.45), fill=shade(BEANIE, 0.85))
    d.ellipse((600, 900, 760, 1260), outline=(12, 12, 14), width=26)
    d.line((x + 60, 960, 640, 1000), fill=shade(NAVY, 0.8), width=70)
    d.ellipse((610, 960, 690, 1040), fill=SKIN)
    if console:
        d.rounded_rectangle((760, 1250, 1000, 1360), radius=30, fill=(30, 30, 36))
        d.rectangle((830, 1270, 930, 1340), fill=(80, 140, 190) if console == "on" else (10, 12, 14))
        d.ellipse((780, 1290, 810, 1320), fill=(60, 60, 66))
        d.ellipse((950, 1290, 980, 1320), fill=(150, 40, 50))
        if console == "on":
            glow(im, 880, 1305, 120, (60, 120, 170), 0.6)
    if phone is not None:
        px, py = 520, 1120
        d.rounded_rectangle((px - 60, py - 105, px + 60, py + 105), radius=14, fill=(12, 12, 14))
        if phone == "call":
            scr = Image.new("RGB", (104, 190), (200, 140, 80))
            im.paste(scr, (px - 52, py - 95))
            glow(im, px, py, 120, (200, 140, 80), 0.4)
        elif phone == "icon":
            glow(im, px, py, 60, (120, 170, 220), 0.7)
            d.rectangle((px - 16, py - 12, px + 16, py + 14), outline=(200, 220, 240), width=4)
        if thumb > 0:
            d.ellipse((px + 70 - 60 * thumb, py - 10, px + 120 - 60 * thumb, py + 40), fill=SKIN)
    return im


def scene2(lt, dur):
    c = cuts_of(dur, 2)
    def a(t):
        im = road_world(t, sstep(-0.5, c[1] + 0.6, t) * 0.75 + 0.1)
        snowfall(im, t, n=150, wind=0.3, speed=90, seed=2, big=4)
        return camera(im, 600, 1350, cam_path(t, [(0, 0, 0, 1.4), (c[1], 0, 0, 1.7)])[2])
    def b(t):
        im = cab(t)
        cx, cy, z = cam_path(t, [(c[1] - 0.3, 560, 900, 1.25), (dur - 0.3, 520, 860, 1.15), (dur + 0.3, 1000, 600, 2.0)])
        return camera(im, cx, cy, z)
    return subshots(lt, dur, [a, b])


# ================================================================ 3 his usual job
def scene3(lt, dur):
    def a(t):
        im = vgrad(W, H, [(0, (196, 206, 212)), (0.6, (176, 188, 194)), (1, (120, 130, 136))])
        d = ImageDraw.Draw(im)
        d.polygon([(0, 1300), (W, 1300), (W, H), (0, H)], fill=(150, 160, 164))
        for x in (120, 420, 700):
            d.rectangle((x, 420, x + 170, 520), fill=(90, 150, 170))  # blank signs
        for gx in (820, 960):  # stretchers in the back
            d.rectangle((gx - 60, 1060, gx + 60, 1080), fill=(220, 224, 226))
            d.line((gx - 50, 1080, gx - 50, 1180), fill=(120, 124, 128), width=6)
            d.line((gx + 50, 1080, gx + 50, 1180), fill=(120, 124, 128), width=6)
        for x in (180, 600, 900):
            d.rectangle((x - 90, 140, x + 90, 160), fill=(250, 252, 255))
        # nurse behind counter
        hx, hy, r = person_side(d, 300, 1700, 900, 1, (70, 140, 140), (60, 40, 30), coatlen=0.5, arms="forward")
        d.ellipse((hx - r * 1.4, hy - r * 0.8, hx - r * 0.7, hy - r * 0.1), fill=(60, 40, 30))
        d.rectangle((0, 1240, 560, 1300), fill=(220, 224, 226))
        d.rectangle((0, 1300, 540, 1800), fill=(130, 150, 160))  # counter at waist height
        courier_side(d, 760, 1800, 930, -1, arms="forward", pack=False)
        cooler_y = 1180 - 40 * sstep(0.3, 1.2, t)
        d.rounded_rectangle((420, cooler_y - 70, 600, cooler_y + 70), radius=12, fill=(244, 246, 248))
        d.rectangle((470, cooler_y - 85, 550, cooler_y - 70), fill=(20, 20, 20))
        return camera(im, 540, 1150, 1.25 + 0.04 * t)
    def b(t):
        im = vgrad(W, H, [(0, (10, 14, 26)), (1, (28, 32, 44))])
        d = ImageDraw.Draw(im)
        d.rectangle((0, 300, W, 1300), fill=(58, 62, 70))
        d.rectangle((300, 680, 640, 1300), fill=(220, 230, 236))  # ER door, light
        glow(im, 470, 1000, 500, (200, 220, 230), 0.5)
        d.rectangle((300, 620, 640, 660), fill=(160, 30, 40))
        d.polygon([(0, 1300), (W, 1300), (W, H), (0, H)], fill=(36, 40, 50))
        for x in range(60, W, 260):
            d.line((x, 1500, x + 120, H), fill=(200, 200, 160), width=6)
        # bored guard sitting by the door
        seated_side(d, 760, 1240, 560, -1, (40, 44, 52), (40, 32, 28))
        u = sstep(0, 2.0, t)
        courier_back(d, lerp(470, 560, u), lerp(1320, 1700, u), lerp(620, 900, u) * 1.0, step=math.sin(t * 7) * 0.6)
        return camera(im, 540, 1150, 1.12)
    def c(t):
        console = "on" if t < dur - 0.4 else "off"
        im = cab(t, outside_speed=0.0, console=console, dashlight=(160, 120, 70))
        return camera(im, 820, 1180, 1.9 + 0.1 * (t / dur))
    return subshots(lt, dur, [a, b, c])


# ================================================================ 4 the call
def girlfriend_screen(w, h, lt):
    im = vgrad(w, h, [(0, (230, 170, 100)), (1, (170, 110, 60))])
    d = ImageDraw.Draw(im)
    d.rectangle((0, h * 0.55, w, h), fill=(150, 96, 54))  # counter
    d.rectangle((w * 0.62, h * 0.12, w * 0.95, h * 0.4), fill=(250, 214, 150))  # warm window
    cx = w * 0.5
    r = w * 0.13
    hy = h * 0.3
    d.ellipse((cx - r * 1.4, hy - r * 1.2, cx + r * 1.4, hy + r * 3.4), fill=(20, 16, 18))  # long black hair
    d.ellipse((cx - r, hy - r, cx + r, hy + r * 1.1), fill=(214, 176, 146))
    d.ellipse((cx - r * 0.45, hy - r * 0.1, cx - r * 0.25, hy + r * 0.1), fill=(40, 30, 26))
    d.ellipse((cx + r * 0.25, hy - r * 0.1, cx + r * 0.45, hy + r * 0.1), fill=(40, 30, 26))
    d.arc((cx - r * 0.35, hy + r * 0.3, cx + r * 0.35, hy + r * 0.7), 20, 160, fill=(150, 90, 80), width=3)
    d.rounded_rectangle((cx - r * 2.2, hy + r * 1.5, cx + r * 2.2, h * 1.05), radius=int(r), fill=(236, 226, 204))  # cream sweater
    d.ellipse((cx - r * 1.6, h * 0.66, cx + r * 1.4, h * 0.9), fill=(228, 218, 196))  # early belly
    d.ellipse((cx - r * 0.6, h * 0.72, cx + r * 0.6, h * 0.8), fill=(214, 176, 146))  # hand on belly
    return im


def scene4(lt, dur):
    e = snap(dur * 0.5)
    def a(t):
        im = Image.new("RGB", (W, H), (10, 12, 20))
        d = ImageDraw.Draw(im)
        d.polygon([(0, 1250), (W, 1180), (W, H), (0, H)], fill=(18, 20, 26))
        out = vgrad(W, 900, [(0, (8, 12, 26)), (1, (30, 36, 52))])
        snowfall(out, t, n=120, wind=0.8, speed=220, seed=4, big=3)
        im.paste(out, (0, 200))
        d.rectangle((0, 160, W, 220), fill=(10, 12, 16))
        d.rectangle((0, 1080, W, 1250), fill=(14, 16, 20))
        # phone on dash mount, palm-sized, big in frame
        px0, py0, px1, py1 = 300, 520, 780, 1360
        d.rectangle((500, 1360, 580, 1500), fill=(20, 20, 22))
        d.rounded_rectangle((px0, py0, px1, py1), radius=50, fill=(8, 8, 10))
        im.paste(girlfriend_screen(px1 - px0 - 40, py1 - py0 - 60, t), (px0 + 20, py0 + 30))
        glow(im, 540, 940, 520, (200, 140, 80), 0.35)
        return camera(im, 540, 960, 1.05 + 0.04 * t)
    def b(t):
        th = sstep(e + 0.6, e + 1.2, t)
        mode = "call" if th < 0.9 else "black"
        if t > dur - 0.5:
            mode = "icon"
        im = cab(t, phone=mode, thumb=th * (1 - sstep(e + 1.4, e + 1.8, t)), dashlight=(70, 100, 140))
        cx, cy, z = cam_path(t, [(e - 0.3, 470, 860, 1.3), (dur - 0.5, 480, 960, 1.35), (dur + 0.3, 520, 1120, 2.6)])
        return camera(im, cx, cy, z)
    return subshots(lt, dur, [a, b])


# ================================================================ 5 the last job
def scene5(lt, dur):
    e = snap(dur * 0.45)
    if "lot" not in _cache:
        im = vgrad(W, H, [(0, (8, 12, 24)), (0.55, (24, 30, 46)), (1, (30, 34, 44))])
        d = ImageDraw.Draw(im)
        d.rectangle((0, 520, W, 1260), fill=(70, 74, 82))
        d.rectangle((0, 500, W, 540), fill=(50, 54, 60))
        d.rectangle((640, 640, 900, 880), fill=(220, 210, 170))  # window with wall clock
        d.ellipse((720, 680, 820, 780), fill=(240, 240, 236), outline=(40, 40, 40), width=5)
        d.line((770, 730, 770, 690), fill=(20, 20, 20), width=6)  # late: hands near 11:50
        d.line((770, 730, 745, 705), fill=(20, 20, 20), width=8)
        d.rectangle((160, 860, 360, 1260), fill=(36, 34, 32))  # side door 2 m
        d.polygon([(0, 1260), (W, 1260), (W, H), (0, H)], fill=(44, 48, 58))
        for x in range(0, W, 240):
            d.line((x, 1300, x - 60, H), fill=(190, 190, 150), width=6)
        glow(im, 540, 300, 300, (230, 200, 140), 0.5)
        d.rectangle((530, 300, 550, 1260), fill=(30, 30, 34))
        _cache["lot"] = im
    im = _cache["lot"].copy()
    d = ImageDraw.Draw(im)
    car_side(im, 760, 1520, 520, -1, head=False)
    opened = sstep(e - 0.3, e, lt)
    if opened > 0:
        d.rectangle((160, 860, 360, 1260), fill=lerpc((36, 34, 32), (230, 220, 190), opened))
    courier_side(d, 470, 1560, 700, -1, arms="forward" if lt > e else "down", pack=True)
    d.ellipse((330, 1210, 360, 1230), fill=(200, 190, 120))  # keys
    if lt > e - 0.2:
        w = sstep(e - 0.2, e + 0.8, lt)
        person_side(d, lerp(200, 280, w), 1560, 680, 1, (40, 40, 44), (50, 40, 30), coatlen=0.4, arms="forward")
        d.polygon([(lerp(200, 280, w) - 50, 1560 - 680 + 130), (lerp(200, 280, w) + 50, 1560 - 680 + 130),
                   (lerp(200, 280, w) + 55, 1560 - 680 + 330), (lerp(200, 280, w) - 55, 1560 - 680 + 330)], fill=(230, 110, 30))
        metal_box(d, 375, 1080 - 10 * w, 60)
    cx, cy, z = cam_path(lt, [(0, 540, 1250, 1.1), (e, 420, 1150, 1.4), (dur - 0.3, 380, 1090, 2.0), (dur + 0.3, 375, 1060, 3.4)])
    return camera(im, cx, cy, z)


def x2_stamp(img, t):
    """sello «x2» rotado -8° sobre la caja metálica (escena 5)."""
    a = sstep(X2[0], X2[0] + 0.15, t)
    if a <= 0 or t > X2[1] + 0.2:
        return
    a *= 1 - sstep(X2[1], X2[1] + 0.2, t)
    s = 1 + 0.25 * (1 - sstep(X2[0], X2[0] + 0.2, t))
    f = font(FONT_N, int(150 * s))
    lay = Image.new("L", (520, 340), 0)
    ld = ImageDraw.Draw(lay)
    tw = ld.textlength("x2", font=f)
    ld.rounded_rectangle((260 - tw / 2 - 40, 50, 260 + tw / 2 + 40, 300), radius=30, outline=255, width=14)
    ld.text((260 - tw / 2, 60), "x2", font=f, fill=255)
    lay = lay.rotate(8, resample=Image.BICUBIC, expand=False)  # PIL: positive = counter-clockwise -> -8° clockwise visual
    m = lay.point(lambda v: int(v * a * 0.92))
    img.paste((200, 30, 40), (520 - 260, 860 - 170), m)


# ================================================================ 6 the storm
def scene6(lt, dur):
    def a(t):
        im = road_world(t, sstep(-0.3, dur * 0.6, t) * 0.6, curve=1)
        snowfall(im, t, n=420, wind=1.6, speed=320, seed=6, big=10)
        return camera(im, 520, 1400, 1.5, shake=3, lt=t)
    def b(t):
        im = road_world(t, 0.25 + sstep(dur * 0.5, dur, t) * 0.7, sign=True, spect=True, curve=2)
        snowfall(im, t, n=420, wind=1.6, speed=320, seed=7, big=10)
        out = camera(im, 560, 1420, 1.55, shake=3, lt=t)
        k = sstep(dur - 0.35, dur, t)
        if k > 0:
            out = blend(out, Image.new("RGB", (W, H), (226, 234, 242)), k)
        return out
    return subshots(lt, dur, [a, b])


# ================================================================ 7 the accident
def woman_front(d, x, yf, h):
    r = h * 0.07
    top = yf - h
    d.rectangle((x - h * 0.06, top + h * 0.6, x - h * 0.02, yf), fill=(30, 26, 26))
    d.rectangle((x + h * 0.02, top + h * 0.6, x + h * 0.06, yf), fill=(30, 26, 26))
    d.polygon([(x - h * 0.12, top + h * 0.18), (x + h * 0.12, top + h * 0.18), (x + h * 0.16, top + h * 0.8), (x - h * 0.16, top + h * 0.8)], fill=WINE)
    d.ellipse((x - r * 1.3, top - r * 0.2, x + r * 1.3, top + r * 2.6), fill=BLOND)  # matted hair covering
    d.ellipse((x - r * 0.8, top + r * 0.5, x + r * 0.8, top + r * 2.2), fill=(220, 214, 206))
    d.ellipse((x - r * 1.3, top - r * 0.2, x + r * 1.3, top + r * 1.0), fill=BLOND)


def scene7(lt, dur):
    def a(t):
        im = vgrad(W, H, [(0, (6, 8, 16)), (0.5, (14, 18, 30)), (1, (40, 44, 56))])
        d = ImageDraw.Draw(im)
        d.polygon([(0, 1500), (W, 1500), (700, 1000), (380, 1000)], fill=(60, 64, 74))
        poly_a(im, [(200, 1900), (880, 1900), (700, 950), (380, 950)], (255, 245, 210), 0.3, blur=30)
        k = sstep(0, dur / 3, t)
        woman_front(d, 540, lerp(1150, 1350, k), lerp(280, 520, k))
        snowfall(im, t, n=260, wind=0.2, speed=420, seed=8, big=14)
        d.rounded_rectangle((-40, 300, W + 40, 1500), radius=80, outline=(8, 8, 10), width=120)
        d.polygon([(0, 1500), (W, 1500), (W, H), (0, H)], fill=(14, 16, 20))
        return camera(im, 540, 1100, 1.1 + 0.15 * k, shake=2 + 6 * k, lt=t)
    def b(t):
        im = vgrad(W, H, [(0, (6, 10, 22)), (0.5, (20, 26, 44)), (1, (170, 182, 200))])
        d = ImageDraw.Draw(im)
        d.polygon([(0, 1300), (W, 1250), (W, 1600), (0, 1650)], fill=(120, 130, 146))
        for k in range(3):  # curved tire marks
            d.arc((100 + k * 40, 1200, 1100 + k * 40, 1800), 200, 260, fill=(70, 76, 86), width=10)
        u = sstep(dur / 3, 2 * dur / 3, t)
        car = Image.new("RGBA", (700, 400), (0, 0, 0, 0))
        tmp = Image.new("RGB", (700, 400), (0, 0, 0))
        car_side(tmp, 350, 330, 520, 1, head=True, brake=1.0)
        mask = tmp.convert("L").point(lambda v: 255 if v > 6 else 0)
        rot = tmp.rotate(-12 * u, resample=Image.BICUBIC)
        mrot = mask.rotate(-12 * u, resample=Image.BICUBIC)
        im.paste(rot, (int(lerp(100, 300, u)), 1100), mrot)
        glow(im, lerp(250, 450, u), 1420, 380, (255, 30, 20), 0.6)
        snowfall(im, t, n=260, wind=0.4, speed=260, seed=9, big=8)
        return camera(im, 540, 1350, 1.3, shake=6, lt=t)
    def c(t):
        im = vgrad(W, H, [(0, (6, 10, 22)), (0.5, (20, 26, 44)), (1, (170, 182, 200))])
        d = ImageDraw.Draw(im)
        d.polygon([(0, 1250), (W, 1200), (W, H), (0, H)], fill=(150, 160, 176))
        for k in range(3):
            d.arc((-100 + k * 40, 1250, 900 + k * 40, 1900), 200, 290, fill=(90, 96, 106), width=10)
        tmp = Image.new("RGB", (760, 420), (0, 0, 0))
        car_side(tmp, 380, 340, 560, 1, head=True, brake=0.6)
        mask = tmp.convert("L").point(lambda v: 255 if v > 6 else 0)
        im.paste(tmp.rotate(-16, resample=Image.BICUBIC), (120, 1000), mask.rotate(-16, resample=Image.BICUBIC))
        # woman lying on the snow, back to camera, a few meters away (no injury shown)
        lx, ly = 760, 1560
        d.ellipse((lx - 170, ly - 45, lx + 120, ly + 45), fill=WINE)
        d.ellipse((lx + 100, ly - 50, lx + 190, ly + 30), fill=BLOND)
        d.line((lx - 160, ly + 10, lx - 290, ly + 30), fill=(30, 26, 26), width=26)
        u = sstep(2 * dur / 3, dur, t)
        courier_side(d, lerp(420, 560, u), 1640, 760, 1, arms="forward", step=math.sin(t * 9))
        snowfall(im, t, n=200, wind=0.2, speed=140, seed=10, big=6)
        if t > dur - 0.6:
            ph = (t * 4) % 1
            glow(im, 540, 600, 900, (255, 40, 50) if ph < 0.5 else (50, 90, 255), 0.5 * sstep(dur - 0.6, dur, t))
        return camera(im, 540, 1300, 1.2)
    return subshots(lt, dur, [a, b, c])


# ================================================================ 8 the patrol car
def policeman(d, x, yf, h, f=1):
    hx, hy, r = person_side(d, x, yf, h, f, POLICE, (120, 120, 116), coatlen=0.45, arms="forward", pants=(24, 30, 48))
    d.ellipse((hx - r * 1.2, hy - r * 1.5, hx + r * 1.2, hy - r * 0.1), fill=(70, 52, 40))  # fur hat
    d.rectangle((hx - r * 1.2, hy - r * 0.6, hx + r * 1.2, hy - r * 0.15), fill=(90, 70, 52))
    d.line((hx + f * r * 0.55, hy + r * 0.45, hx + f * r * 1.05, hy + r * 0.45), fill=(150, 150, 146), width=max(3, int(r * 0.2)))  # grey moustache
    return hx, hy, r


def scene8(lt, dur):
    ph = (lt * 2.2) % 1
    tint = (255, 40, 50) if ph < 0.5 else (50, 90, 255)
    def a(t):
        im = vgrad(W, H, [(0, (6, 10, 22)), (0.55, (24, 30, 46)), (1, (160, 172, 190))])
        d = ImageDraw.Draw(im)
        d.polygon([(0, 1300), (W, 1260), (W, H), (0, H)], fill=(140, 150, 166))
        car_side(im, 280, 1500, 600, 1, col=POLICE, head=True, light=t * 2.2)
        policeman(d, 700, 1640, 820, -1)
        glow(im, 610, 1180, 70, (255, 250, 220), 1.0)  # flashlight
        poly_a(im, [(600, 1180), (300, 1500), (420, 1560)], (255, 250, 220), 0.2, blur=10)
        # woman wrapped in a blanket, head down
        x = 860
        d.rounded_rectangle((x - 90, 1060, x + 90, 1640), radius=50, fill=(108, 96, 80))
        d.ellipse((x - 50, 990, x + 50, 1090), fill=BLOND)
        d.line((x - 30, 1080, x - 10, 1110), fill=(80, 160, 100), width=4)  # faint green veins
        snowfall(im, t, n=200, wind=0.3, speed=150, seed=11, big=6)
        return camera(im, 600, 1300, 1.2)
    def b(t):
        im = vgrad(W, H, [(0, (6, 10, 22)), (0.55, (24, 30, 46)), (1, (160, 172, 190))])
        d = ImageDraw.Draw(im)
        d.polygon([(0, 1300), (W, 1260), (W, H), (0, H)], fill=(140, 150, 166))
        u = sstep(dur / 3 + 0.8, 2 * dur / 3 + 0.3, t)
        x = lerp(520, 1400, u ** 1.5)
        car_side(im, x, 1520, 700, 1, col=POLICE, head=True, light=t * 2.2)
        d = ImageDraw.Draw(im)
        hy = 1520 - 700 * 0.36 * 1.2
        d.ellipse((x + 20, hy - 50, x + 90, hy + 20), fill=BEANIE)  # courier in front seat
        d.ellipse((x - 140, hy - 40, x - 80, hy + 20), fill=BLOND)  # woman in back
        snowfall(im, t, n=220, wind=0.3, speed=150, seed=12, big=6)
        return camera(im, 600, 1350, 1.25)
    def c(t):
        im = vgrad(W, H, [(0, (4, 8, 18)), (1, (24, 30, 44))])
        d = ImageDraw.Draw(im)
        mountains(d, 900, (20, 26, 40), 40, amp=300)
        d.polygon([(0, 1250), (W, 1150), (W, H), (0, H)], fill=(120, 130, 146))
        d.line((0, 1500, W, 1250), fill=(70, 76, 86), width=40)
        u = sstep(2 * dur / 3, dur - 0.3, t)
        lx = lerp(150, 780, u)
        ly = lerp(1460, 1300, u) + (math.sin(t * 40) * 20 if u > 0.75 else 0)
        vis = 1 - sstep(0.85, 1.0, u)
        glow(im, lx, ly, 90, (255, 30, 40) if (t * 4.4) % 1 < 0.5 else (50, 90, 255), vis)
        rng = random.Random(3)
        for i in range(30):
            x = rng.uniform(0, W)
            y = rng.uniform(1150, 1400)
            s = rng.uniform(60, 140)
            d.polygon([(x, y - s * 2), (x - s * 0.6, y), (x + s * 0.6, y)], fill=(10, 20, 22))
        snowfall(im, t, n=180, wind=0.3, speed=120, seed=13, big=4)
        return camera(im, 540, 1250, 1.2)
    out = subshots(lt, dur, [a, b, c])
    return out


# ================================================================ 9 the outbreak
def scene9(lt, dur):
    def a(t):
        im = vgrad(W, H, [(0, (6, 10, 20)), (0.7, (20, 26, 38)), (1, (110, 120, 136))])
        d = ImageDraw.Draw(im)
        mountains(d, 700, (20, 26, 40), 50, amp=260)
        d.rectangle((280, 300, 800, 1500), fill=(40, 46, 56))
        for f in range(10):
            y = 340 + f * 112
            for c in range(5):
                x = 310 + c * 98
                broken = f == 2 and c in (1, 2, 3)
                col = (20, 26, 30) if broken else ((150, 170, 170) if (f + c) % 3 else (60, 70, 76))
                d.rectangle((x, y, x + 80, y + 80), fill=col)
                if broken:
                    d.polygon([(x, y), (x + 40, y + 30), (x + 80, y)], fill=(90, 110, 110))
        for (ax, ay) in [(290, 300), (790, 300), (540, 1480)]:
            on = (math.sin(t * 6 + ax) > 0)
            glow(im, ax, ay, 160, (255, 170, 40), 1.0 if on else 0.25)
        d.polygon([(0, 1500), (W, 1500), (W, H), (0, H)], fill=(120, 130, 146))
        return camera(im, 540, 1000, 1.1 + 0.05 * t)
    def b(t):
        im = vgrad(W, H, [(0, (6, 10, 20)), (1, (26, 32, 46))])
        d = ImageDraw.Draw(im)
        d.rectangle((0, 200, 420, 1000), fill=(40, 46, 56))
        d.rectangle((300, 400, 400, 480), fill=(20, 26, 30))
        mountains(d, 1300, (24, 30, 44), 51, amp=200)
        rng = random.Random(4)
        for i in range(16):  # valley houses
            x = 380 + i * 45 + rng.randint(-10, 10)
            y = 1480 + rng.randint(-20, 60)
            d.rectangle((x, y - 40, x + 36, y), fill=(30, 30, 36))
            d.polygon([(x - 4, y - 40), (x + 18, y - 62), (x + 40, y - 40)], fill=(170, 180, 196))
            d.rectangle((x + 12, y - 28, x + 22, y - 16), fill=(220, 180, 110))
        u = sstep(dur / 3 - 0.3, 2 * dur / 3 + 0.3, t)
        for k in range(12):
            q = k / 11
            px = lerp(360, 380 + 700 * u, q)
            py = lerp(440, 440 + 1050 * u, q ** 1.3)
            rr = 50 + 120 * q
            ell_a(im, (px - rr, py - rr * 0.6, px + rr, py + rr * 0.6), GREENV, 0.25 * (1 - q * 0.4), blur=26)
        return camera(im, 600, 1050, 1.15)
    def c(t):
        im = vgrad(W, H, [(0, (6, 10, 18)), (1, (34, 40, 52))])
        d = ImageDraw.Draw(im)
        d.rectangle((0, 600, 300, 1400), fill=(30, 32, 40))
        d.rectangle((780, 560, W, 1400), fill=(28, 30, 38))
        d.polygon([(0, 1400), (W, 1400), (W, H), (0, H)], fill=(130, 140, 156))
        # abandoned car, doors open; overturned truck
        car_side(im, 250, 1560, 400, 1, head=False)
        d.polygon([(330, 1460), (420, 1380), (430, 1470)], fill=CARGRAY)
        d.rounded_rectangle((680, 1380, 1060, 1560), radius=30, fill=(150, 140, 110))
        for wx in (740, 1000):
            d.ellipse((wx - 40, 1330, wx + 40, 1410), fill=(16, 16, 18))
        for lx in (420, 860):  # flickering street lamps, twice a person's height
            on = 0.35 + 0.65 * (math.sin(t * 17 + lx) > -0.3)
            d.rectangle((lx - 6, 1000, lx + 6, 1450), fill=(30, 30, 34))
            glow(im, lx, 1000, 260, (230, 200, 130), on * 0.8)
        for k in range(4):
            creature(d, 360 + k * 120 + 12 * math.sin(t + k), 1450, 220, seed=k + 3, lt=t)
        ell_a(im, (0, 1100, W, 1500), GREENV, 0.08, blur=40)
        out = camera(im, 540, 1250, 1.15)
        k2 = sstep(dur - 0.4, dur + 0.2, t)
        if k2 > 0:
            out = blend(out, Image.new("RGB", (W, H), (60, 120, 80)), 0.7 * k2)
        return out
    return subshots(lt, dur, [a, b, c])


# ================================================================ 10 the farm
def farm_bg():
    if "farm" in _cache:
        return _cache["farm"]
    im = vgrad(W, H, [(0, (6, 10, 22)), (0.5, (20, 26, 42)), (0.55, (170, 182, 200)), (1, (130, 140, 158))])
    d = ImageDraw.Draw(im)
    d.polygon([(560, 1000), (700, 860), (1060, 860), (1080, 1000), (1080, 1200), (560, 1200)], fill=(130, 30, 30))  # red barn
    d.polygon([(540, 1010), (700, 850), (1060, 850), (1080, 1010)], fill=(180, 190, 204))
    d.rectangle((60, 860, 500, 1200), fill=(78, 64, 50))  # farmhouse
    d.polygon([(40, 870), (280, 700), (520, 870)], fill=(180, 190, 204))
    d.rectangle((220, 980, 330, 1200), fill=(30, 24, 20))
    for x in (100, 400):
        d.rectangle((x, 940, x + 60, 1010), fill=(230, 190, 100))
        glow(im, x + 30, 975, 90, (230, 170, 80), 0.5)
    for x in range(0, W, 70):  # fence
        d.rectangle((x, 1300, x + 10, 1400), fill=(60, 50, 40))
    d.line((0, 1330, W, 1330), fill=(60, 50, 40), width=8)
    d.line((0, 1370, W, 1370), fill=(60, 50, 40), width=8)
    _cache["farm"] = im
    return im


def scene10(lt, dur):
    def a(t):
        im = vgrad(W, H, [(0, (6, 10, 22)), (0.45, (22, 28, 44)), (0.5, (150, 162, 182)), (1, (120, 130, 150))])
        d = ImageDraw.Draw(im)
        u = t / (dur / 3)
        cx = lerp(380, 640, u)
        for k in range(10):  # footprints
            d.ellipse((cx - 300 + k * 40, 1660 + (k % 2) * 20, cx - 280 + k * 40, 1672 + (k % 2) * 20), fill=(100, 110, 126))
        dog_creature(d, cx - 520 + 40 * math.sin(t * 3), 1560, 300, t)
        courier_side(d, cx, 1700, 780, 1, arms="crossed", step=math.sin(t * 12))
        metal_box(d, cx + 55, 1700 - 780 * 0.62, 45)
        snowfall(im, t, n=200, wind=0.4, speed=170, seed=14, big=8)
        return camera(im, cx - 60, 1350, 1.15, shake=4, lt=t)
    def b(t):
        im = farm_bg().copy()
        d = ImageDraw.Draw(im)
        courier_back(d, 275, 1260, 300)
        person_back(d, 840, 1560, 520, (40, 38, 36), DARKHAIR, hood=MUSTARD, hairshape="fade", coatlen=0.4)
        snowfall(im, t, n=160, wind=0.3, speed=150, seed=15, big=6)
        cx, cy, z = cam_path(t, [(dur / 3 - 0.3, 540, 1150, 1.05), (2 * dur / 3, 360, 1080, 1.5)])
        return camera(im, cx, cy, z)
    def c(t):
        im = Image.new("RGB", (W, H), (20, 18, 16))
        d = ImageDraw.Draw(im)
        d.rectangle((0, 0, W, H), fill=(60, 48, 36))
        x0, y0, x1, y1 = 300, 300, 780, 1600  # 2 m door, farmer almost fills it
        o = sstep(2 * dur / 3 - 0.3, 2 * dur / 3 + 0.4, t)
        d.rectangle((x0, y0, x1, y1), fill=lerpc((30, 22, 18), (240, 200, 120), o))
        glow(im, 540, 900, 600, (230, 170, 80), 0.6 * o)
        if o > 0:
            d.rectangle((x0 + 30, y0 + 200, x0 + 90, y0 + 300), fill=(200, 160, 90))  # wall phone, back of hall
            d.rectangle((x0 + 50, y0 + 220, x0 + 70, y0 + 280), fill=(60, 40, 30))
            # farmer silhouette (backlit): tall, beard, plaid shirt, overalls, deformed arm
            fx, fy, fh = 540, 1600, 1260
            fd = ImageDraw.Draw(im)
            person_back(fd, fx, fy, fh, (56, 22, 22), (120, 118, 112), skin=(70, 66, 60), pants=(14, 14, 16), coatlen=0.45, legs=True)
            fd.rectangle((fx - fh * 0.1, fy - fh * 0.65, fx + fh * 0.1, fy - fh * 0.38), fill=(26, 30, 40))
            for k in range(6):
                gx = fx + fh * 0.17 + (k % 2) * 20
                gy = fy - fh * 0.75 + k * 45
                fd.ellipse((gx - 30, gy - 24, gx + 34, gy + 26), fill=(30, 34, 30))
            fd.ellipse((fx - fh * 0.06, fy - fh * 0.93, fx + fh * 0.06, fy - fh * 0.8), fill=(130, 128, 122))  # white beard hint
        d.rectangle((0, 1600, W, H), fill=(160, 170, 186))
        out = camera(im, 540, 1000, 1.05 + 0.08 * o)
        return Image.eval(out, lambda v: int(v * 0.85))
    return subshots(lt, dur, [a, b, c])


# ================================================================ 11 learning to survive
def shotgun(d, x0, y0, x1, y1, w=16):
    d.line((x0, y0, x1, y1), fill=(30, 30, 32), width=w)
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    d.line((x0, y0, x0 - ux * L * 0.3 + uy * 30, y0 - uy * L * 0.3 - ux * 30), fill=(90, 60, 36), width=int(w * 2.2))


def scene11(lt, dur):
    def barn(t):
        im = vgrad(W, H, [(0, (26, 20, 16)), (1, (14, 10, 8))])
        d = ImageDraw.Draw(im)
        for x in range(0, W, 90):
            d.rectangle((x, 0, x + 84, 1400), fill=(60, 40, 28))
        glow(im, 540, 300, 500, (200, 150, 80), 0.4)
        d.polygon([(0, 1400), (W, 1400), (W, H), (0, H)], fill=(50, 40, 30))
        for k, (tx, ty) in enumerate([(120, 700), (220, 680), (900, 720)]):  # farm tools
            d.line((tx, ty, tx, ty + 360), fill=(80, 60, 40), width=10)
            d.rectangle((tx - 30, ty + 330, tx + 30, ty + 360), fill=(90, 92, 96))
        return im, d
    def a(t):
        im, d = barn(t)
        u = sstep(0.3, dur / 3 - 0.3, t)
        flip = 0.4 < u < 0.75
        if u < 0.2:
            shotgun(d, 380, 760, 780, 760)
            d.line((400, 740, 400, 780), fill=(40, 30, 20), width=6)
            d.line((760, 740, 760, 780), fill=(40, 30, 20), width=6)
        courier_side(d, 540, 1700, 1000, 1 if not flip else -1, arms="forward")
        if u >= 0.2:
            if flip:  # held backwards a moment, aimed at nothing (the wall/floor)
                shotgun(d, 420, 1180, 120, 1240)
            else:
                shotgun(d, 600, 1200, 900, 1380)
        d.ellipse((620, 980, 700, 1020), fill=(200, 205, 210)) if (t % 1.4) < 0.5 else None  # breath
        return camera(im, 540, 1150, 1.2)
    def b(t):
        im, d = barn(t)
        d.rectangle((150, 1250, 950, 1290), fill=(80, 56, 36))  # workbench, hip height
        d.rectangle((180, 1290, 210, 1700), fill=(60, 42, 28))
        d.rectangle((890, 1290, 920, 1700), fill=(60, 42, 28))
        d.rectangle((430, 1160, 640, 1250), fill=(60, 70, 50))  # ammo box
        for k in range(5):
            d.rounded_rectangle((450 + k * 36, 1130, 474 + k * 36, 1200), radius=8, fill=(170, 40, 30))
            d.rectangle((450 + k * 36, 1180, 474 + k * 36, 1200), fill=(200, 170, 80))
        hx = 560 + 120 * math.sin(t * 2)
        d.line((hx + 300, 900, hx + 20, 1160), fill=NAVY, width=80)
        d.ellipse((hx - 30, 1130, hx + 50, 1190), fill=SKIN)
        return camera(im, 560, 1200, 1.6)
    def c(t):
        im = vgrad(W, H, [(0, (14, 16, 18)), (1, (26, 28, 30))])
        d = ImageDraw.Draw(im)
        d.polygon([(0, 0), (W, 0), (700, 900), (380, 900)], fill=(50, 52, 54))
        d.polygon([(0, H), (W, H), (700, 1150), (380, 1150)], fill=(40, 42, 44))
        d.polygon([(0, 0), (380, 900), (380, 1150), (0, H)], fill=(64, 66, 68))
        d.polygon([(W, 0), (700, 900), (700, 1150), (W, H)], fill=(58, 60, 62))
        d.rectangle((380, 900, 700, 1150), fill=(4, 4, 6))
        poly_a(im, [(560, 1000), (300, 860), (780, 860)], (250, 245, 220), 0.0)
        u = sstep(2 * dur / 3, dur, t)
        poly_a(im, [(460, 1260), (360, 960), (720, 960)], (250, 245, 220), 0.3, blur=20)
        courier_back(d, 540, 1900 - 80 * u, 1100, step=math.sin(t * 4) * 0.4)
        shotgun(d, 640, 1350, 760, 1700, w=14)  # pointed at the floor
        glow(im, 460, 1280, 60, (255, 250, 220), 1.0)
        if t > dur - 0.5:  # something moves at the end of the tunnel + flash
            creature(d, 560, 1120, 170, seed=2, lt=t, col=(30, 30, 28))
            glow(im, 540, 1030, 900, (255, 255, 245), sstep(dur - 0.25, dur + 0.05, t) * 2.0)
        return camera(im, 540, 1150, 1.1 + 0.05 * u)
    return subshots(lt, dur, [a, b, c])


# ================================================================ 12 the bite
def scene12(lt, dur):
    def a(t):
        im = vgrad(W, H, [(0, (6, 10, 22)), (1, (30, 36, 50))])
        d = ImageDraw.Draw(im)
        town(im, 560, 900, 500, t, k=0.7, seed=12)
        for y in range(500, 1700, 40):  # brick wall taller than him
            for x in range(0 if (y // 40) % 2 else 40, 520, 80):
                d.rectangle((x, y, x + 76, y + 36), fill=(90, 46, 36))
        d.polygon([(0, 1700), (W, 1600), (W, H), (0, H)], fill=(150, 160, 176))
        courier_side(d, 600, 1760, 1000, 1, arms="down", lean=-0.3)
        if (t % 1.2) < 0.6:
            ell_a(im, (700, 900, 800, 960), (210, 216, 222), 0.5, blur=8)
        snowfall(im, t, n=120, wind=0.1, speed=60, seed=16, big=4)
        return camera(im, 560, 1250, 1.15)
    def b(t):
        im = vgrad(W, H, [(0, (16, 18, 26)), (1, (30, 32, 40))])
        d = ImageDraw.Draw(im)
        d.rectangle((0, 300, W, 1600), fill=(60, 36, 30))
        # forearm close-up, sleeve rolled
        d.polygon([(100, 1300), (980, 1000), (1020, 1160), (140, 1460)], fill=SKIN)
        d.polygon([(40, 1200), (300, 1110), (380, 1360), (100, 1470)], fill=NAVY)
        d.line((210, 1160, 300, 1400), fill=STRIPE, width=18)
        bx, by = 620, 1170
        for k in range(8):  # bite marks (small dark dots, no blood)
            a = k / 8 * 2 * math.pi
            d.ellipse((bx + 50 * math.cos(a) - 7, by + 26 * math.sin(a) - 7, bx + 50 * math.cos(a) + 7, by + 26 * math.sin(a) + 7), fill=(110, 60, 60))
        g = sstep(dur / 3, 2 * dur / 3, t)
        rng = random.Random(5)
        for k in range(9):
            ang = rng.uniform(0, 2 * math.pi)
            pts = [(bx, by)]
            x, y = bx, by
            for s in range(int(12 * g) + 1):
                ang += rng.uniform(-0.4, 0.4)
                x += math.cos(ang) * 22
                y += math.sin(ang) * 10
                pts.append((x, y))
            if len(pts) > 1:
                d.line(pts, fill=(60, 150, 80), width=5)
        glow(im, bx, by, int(80 + 200 * g), (60, 160, 80), 0.25 * g)
        return camera(im, 580, 1200, 1.3)
    def c(t):
        im = vgrad(W, H, [(0, (6, 10, 22)), (1, (30, 36, 50))])
        d = ImageDraw.Draw(im)
        town(im, 520, 820, 540, t, k=0.8, seed=12)
        d.polygon([(0, 1500), (W, 1450), (W, H), (0, H)], fill=(150, 160, 176))
        d.rectangle((60, 1600, 300, 1700), fill=(236, 238, 240))  # open first aid kit
        d.rectangle((150, 1610, 210, 1640), fill=(170, 30, 40))
        metal_box(d, 380, 1660, 60)
        hx, hy, r = courier_side(d, 260, 1560, 760, 1, arms="forward")
        u = sstep(2 * dur / 3, dur, t)
        d.rectangle((370, 1560 - 760 + 300, 380 + 70 * u, 1560 - 760 + 340), fill=(240, 240, 236))  # bandage
        snowfall(im, t, n=140, wind=0.1, speed=60, seed=17, big=4)
        out = camera(im, 500, 1250, 1.15)
        k = sstep(dur - 0.4, dur + 0.2, t)
        if k > 0:
            out = blend(out, Image.new("RGB", (W, H), (240, 242, 245)), 0.6 * k)
        return out
    return subshots(lt, dur, [a, b, c])


# ================================================================ 13 the company employees
def employee(d, x, yf, h, f, braid=False, glasses=False):
    hx, hy, r = person_side(d, x, yf, h, f, HAZ, (24, 20, 18) if braid else (60, 50, 40), coatlen=0.72, arms="forward",
                            pants=HAZ, style="short")
    d.rectangle((hx - r * 0.5, hy + r * 1.0, hx + r * 0.7, hy + r * 1.35), fill=(220, 224, 224))  # mask at the neck
    if braid:
        d.line((hx - f * r * 0.9, hy, hx - f * r * 1.1, hy + r * 2.2), fill=(24, 20, 18), width=int(r * 0.4))
    if glasses:
        d.ellipse((hx + f * r * 0.3, hy - r * 0.25, hx + f * r * 0.75, hy + r * 0.12), outline=(30, 30, 30), width=max(2, int(r * 0.1)))
    # long gun pointing at the ground
    shotgun(d, x + f * h * 0.08, yf - h * 0.5, x + f * h * 0.2, yf - h * 0.12, w=max(6, int(h * 0.018)))
    return hx, hy, r


def scene13(lt, dur):
    def street(t):
        im = vgrad(W, H, [(0, (6, 10, 22)), (0.5, (20, 26, 40)), (1, (140, 150, 168))])
        d = ImageDraw.Draw(im)
        d.rectangle((0, 400, 260, 1350), fill=(30, 32, 40))
        d.rectangle((820, 380, W, 1350), fill=(28, 30, 38))
        d.polygon([(0, 1350), (W, 1350), (W, H), (0, H)], fill=(150, 160, 176))
        # white van, no logos, engine on
        d.rounded_rectangle((340, 1000, 760, 1300), radius=30, fill=(214, 218, 220))
        d.rectangle((370, 1030, 520, 1120), fill=(40, 50, 60))
        for wx in (420, 690):
            d.ellipse((wx - 40, 1260, wx + 40, 1340), fill=(16, 16, 18))
        for k in range(4):
            ell_a(im, (300 - k * 40 - 10 * math.sin(t * 3), 1250 - k * 30, 360 - k * 30, 1300 - k * 30), (200, 205, 210), 0.3 - k * 0.06, blur=10)
        return im, d
    def a(t):
        im, d = street(t)
        employee(d, 420, 1420, 420, 1, glasses=True)
        employee(d, 660, 1420, 390, -1, braid=True)
        for (fx, fy) in [(470, 1100), (610, 1110)]:
            glow(im, fx, fy, 60, (255, 250, 230), 1.0)
            poly_a(im, [(fx, fy), (fx - 200, 1900), (fx + 200, 1900)], (255, 250, 230), 0.14, blur=20)
        snowfall(im, t, n=200, wind=0.2, speed=100, seed=18, big=6)
        return camera(im, 540, 1220, 1.35)
    def b(t):
        im, d = street(t)
        employee(d, 420, 1420, 420, 1, glasses=True)
        employee(d, 660, 1420, 390, -1, braid=True)
        courier_back(d, 540, 1640, 520)
        poly_a(im, [(480, 1110), (420, 1600), (640, 1600)], (255, 250, 230), 0.14, blur=20)
        # spectator in the foreground corner, adult proportions, seen from behind
        person_back(d, 180, 2050, 1150, (40, 38, 36), DARKHAIR, hood=MUSTARD, hairshape="fade", coatlen=0.4)
        snowfall(im, t, n=200, wind=0.2, speed=100, seed=19, big=8)
        cx, cy, z = cam_path(t, [(dur / 2 - 0.3, 540, 1200, 1.05), (dur - 0.3, 540, 1150, 1.0)])
        return camera(im, cx, cy, z)
    return subshots(lt, dur, [a, b])


# ================================================================ 14 back to the theatre
def street_small(w, h, lt):
    im = vgrad(w, h, [(0, (8, 12, 26)), (1, (40, 46, 62))])
    town(im, int(w * 0.1), int(h * 0.62), int(w * 0.8), lt, k=w / 1020 * 0.8, seed=5)
    d = ImageDraw.Draw(im)
    d.rectangle((0, int(h * 0.7), w, h), fill=(140, 150, 168))
    courier_back(d, w * 0.5, h * 0.9, h * 0.3)
    snowfall(im, lt, n=90, wind=0.1, speed=40, seed=20, big=0)
    return im


def kitchen_window(w, h):
    im = Image.new("RGB", (w, h), (40, 30, 24))
    d = ImageDraw.Draw(im)
    d.rectangle((w * 0.12, h * 0.12, w * 0.88, h * 0.88), fill=(250, 210, 140))
    d.line((w * 0.5, h * 0.12, w * 0.5, h * 0.88), fill=(60, 44, 30), width=10)
    d.line((w * 0.12, h * 0.5, w * 0.88, h * 0.5), fill=(60, 44, 30), width=10)
    d.ellipse((w * 0.6, h * 0.55, w * 0.8, h * 0.8), fill=(200, 140, 80))  # warm lamp
    return im


def scene14(lt, dur):
    c = cuts_of(dur, 3)
    sw, sh = 1020, 580
    if lt < c[1] + 0.3:
        content = street_small(sw, sh, lt)
        if lt > c[1] - 0.3:
            content = blend(content, split_content(sw, sh, lt), sstep(c[1] - 0.3, c[1] + 0.3, lt))
    else:
        content = split_content(sw, sh, lt)
    dim = 1 - 0.35 * sstep(c[2], dur, lt)
    im = cinema_world(lt, content, beam=1.0, dim=dim)
    cx, cy, z = cam_path(lt, [(0, 540, 890, 3.0), (1.2, 540, 950, 1.15), (c[2], 540, 960, 1.05), (dur, 540, 960, 1.0)])
    return camera(im, cx, cy, z)


def split_content(w, h, lt):
    left = city_panorama(w // 2, h, lt).resize((w // 2, h))
    im = Image.new("RGB", (w, h))
    im.paste(left, (0, 0))
    im.paste(kitchen_window(w - w // 2, h), (w // 2, 0))
    ImageDraw.Draw(im).rectangle((w // 2 - 4, 0, w // 2 + 4, h), fill=(10, 10, 10))
    return im


def title_card(img, a):
    if a <= 0:
        return
    big = font(FONT_B, 66)
    small = font(FONT_R, 40)
    layer = Image.new("L", (W, 420), 0)
    ld = ImageDraw.Draw(layer)
    t1 = "Resident Evil: Noche Cero"
    t2 = "Resident Evil, 2026"
    w1 = ld.textlength(t1, font=big)
    w2 = ld.textlength(t2, font=small)
    ld.text(((W - w1) / 2, 90), t1, font=big, fill=255)
    ld.text(((W - w2) / 2, 200), t2, font=small, fill=255)
    y = 170
    band = Image.new("L", (W, 520), 0)
    ImageDraw.Draw(band).rounded_rectangle((70, 120, W - 70, 360), radius=60, fill=210)
    band = band.filter(ImageFilter.GaussianBlur(45))
    img.paste((8, 6, 8), (0, y - 60), band.point(lambda v: int(v * a)))
    sh = layer.filter(ImageFilter.GaussianBlur(8))
    img.paste((0, 0, 0), (0, y), sh.point(lambda v: int(v * 0.8 * a)))
    img.paste((240, 236, 226), (0, y), layer.point(lambda v: int(v * a)))
    ld2 = Image.new("L", (W, 420), 0)
    ImageDraw.Draw(ld2).rectangle(((W - 220) / 2, 275, (W + 220) / 2, 279), fill=255)
    img.paste(CRIMSON, (0, y), ld2.point(lambda v: int(v * a)))


def overlays(img, t):
    x2_stamp(img, t)


SCENES = [scene1, scene2, scene3, scene4, scene5, scene6, scene7, scene8, scene9, scene10, scene11, scene12, scene13, scene14]

FOG = {
    0: ((60, 60, 70), 0.08), 1: ((120, 140, 170), 0.18), 2: ((150, 170, 180), 0.08), 3: ((60, 70, 90), 0.08),
    4: ((90, 100, 120), 0.14), 5: ((190, 200, 214), 0.35), 6: ((160, 170, 190), 0.22), 7: ((120, 130, 160), 0.22),
    8: ((70, 130, 100), 0.25), 9: ((150, 160, 180), 0.22), 10: ((100, 90, 70), 0.10), 11: ((150, 160, 176), 0.18),
    12: ((150, 160, 180), 0.22), 13: ((60, 60, 70), 0.08),
}
