import math, random, json
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
from lib import *

_seg = json.load(open("segments.json"))
PS = [s["start"] for s in _seg]
END = round(_seg[-1]["end"] + 1.0, 3)


def snap(t, g=0.3):
    return round(t / g) * g


# scene boundaries (absolute seconds): voice rules, image waits
B = [0.0, snap(PS[0] + 0.58 * (PS[1] - PS[0])), PS[1], PS[2], PS[3], PS[4], PS[5], PS[6], PS[7], PS[8], PS[9],
     PS[10], PS[11], PS[12], PS[13], PS[14], PS[15], END]
TITLE_T = PS[15]


def camera(world, cx, cy, z, rot=0.0):
    z = max(z, 1.0)
    hw, hh = W / (2 * z), H / (2 * z)
    cx = clamp(cx, hw, world.size[0] - hw)
    cy = clamp(cy, hh, world.size[1] - hh)
    a = 1 / z
    return world.transform((W, H), Image.AFFINE, (a, 0, cx - hw, 0, a, cy - hh), Image.BICUBIC)


def cam_path(lt, keys):
    """keys: list of (t, cx, cy, z) ; smooth interpolation"""
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


def drift(lt, amp=6, sp=0.5, seed=0):
    return amp * math.sin(lt * sp + seed), amp * math.cos(lt * sp * 0.8 + seed * 2)


class Particles:
    def __init__(self, n, box, seed, size=(1, 3), speed=(5, 20), col=(255, 240, 210)):
        rng = random.Random(seed)
        self.p = [(rng.uniform(box[0], box[2]), rng.uniform(box[1], box[3]), rng.uniform(*size), rng.uniform(*speed),
                   rng.uniform(0, 6.28), rng.uniform(0.3, 1)) for _ in range(n)]
        self.box = box
        self.col = col

    def draw(self, img, lt, mask_fn=None, k=1.0):
        d = ImageDraw.Draw(img)
        x0, y0, x1, y1 = self.box
        for (x, y, s, sp, ph, a) in self.p:
            xx = x0 + (x - x0 + math.sin(lt * 0.7 + ph) * 15 + lt * sp * 0.6) % (x1 - x0)
            yy = y0 + (y - y0 + math.cos(lt * 0.5 + ph) * 10 - lt * sp * 0.3) % (y1 - y0)
            if mask_fn and not mask_fn(xx, yy):
                continue
            tw = (0.6 + 0.4 * math.sin(lt * 3 + ph)) * a * k
            c = tuple(int(v * tw) for v in self.col)
            d.ellipse((xx - s, yy - s, xx + s, yy + s), fill=lerpc(img.getpixel((int(clamp(xx, 0, img.size[0] - 1)), int(clamp(yy, 0, img.size[1] - 1)))), c, 0.8))


# ================================================================ SCENE 2 studio world (also used inside cinema screen)
_cache = {}


def studio_bg():
    if "studio" in _cache:
        return _cache["studio"]
    im = vgrad(W, H, [(0, (14, 18, 26)), (0.55, (26, 32, 42)), (0.62, (34, 38, 46)), (1, (18, 20, 26))])
    d = ImageDraw.Draw(im)
    # back wall panels
    for i in range(7):
        x = 40 + i * 150
        d.rectangle((x, 300, x + 130, 1120), fill=(24, 30, 40))
    # light rig
    d.rectangle((0, 120, W, 140), fill=(10, 12, 16))
    for i, x in enumerate([150, 420, 680, 940]):
        d.polygon([(x - 30, 140), (x + 30, 140), (x + 45, 200), (x - 45, 200)], fill=(40, 42, 48))
        glow(im, x, 205, 160, (255, 220, 160), 0.9)
    for i, x in enumerate([150, 420, 680, 940]):
        poly_a(im, [(x - 40, 205), (x + 40, 205), (x + 260 * (0.5 - i / 3) + 180, 1350), (x + 260 * (0.5 - i / 3) - 180, 1350)],
               (255, 225, 180), 0.06, blur=20)
    # monitor
    mx0, my0, mx1, my1 = 290, 520, 790, 830
    d.rectangle((mx0 - 14, my0 - 14, mx1 + 14, my1 + 14), fill=(12, 12, 14))
    d.rectangle((mx0, my0, mx1, my1), fill=(18, 40, 62))
    glow(im, (mx0 + mx1) / 2, (my0 + my1) / 2, 330, (60, 120, 170), 0.5)
    # brain outline
    bx, by = 430, 650
    d.ellipse((bx - 95, by - 70, bx + 95, by + 70), outline=(170, 215, 235), width=4)
    for k in range(5):
        d.arc((bx - 80 + k * 30, by - 55, bx - 30 + k * 30, by + 5), 180, 360, fill=(140, 195, 220), width=3)
        d.arc((bx - 80 + k * 30, by - 5, bx - 30 + k * 30, by + 55), 0, 180, fill=(140, 195, 220), width=3)
    # pulse line -> flat -> continues glowing beyond
    pts = []
    for i in range(0, 120):
        x = 540 + i * 2
        y = 650
        if i < 30:
            y = 650 - (40 if i % 15 == 7 else (-25 if i % 15 == 9 else 0))
        pts.append((x, y))
    d.line(pts, fill=(120, 230, 170), width=4)
    for i in range(6):
        x = 780 - 10 + i * 0  # beyond: dotted rising line
    for i in range(8):
        x = 600 + i * 22
        y = 650 - i * 9
        d.ellipse((x - 4 + 170, y - 4 - 60, x + 4 + 170, y + 4 - 60), fill=(240, 240, 200))
    # floor
    d.polygon([(0, 1180), (W, 1180), (W, H), (0, H)], fill=(20, 22, 28))
    d.ellipse((150, 1150, 930, 1420), fill=(30, 34, 42))
    # side TV camera (foreground right)
    d.rectangle((850, 1100, 1080, 1260), fill=(14, 14, 16))
    d.rectangle((800, 1140, 860, 1220), fill=(10, 10, 12))
    d.line((960, 1260, 900, 1700), fill=(12, 12, 14), width=16)
    d.line((960, 1260, 1040, 1700), fill=(12, 12, 14), width=16)
    _cache["studio"] = im
    return im


def studio_world(lt, red=True):
    im = studio_bg().copy()
    d = ImageDraw.Draw(im)
    # you in the shadow at back left, arms crossed
    person_side(d, 120, 1200, 560, 1, (26, 28, 34), DARKHAIR, skin=(110, 90, 80), arms="crossed", coatlen=0.62)
    # father seated (left, facing right), interviewer (right, facing left)
    seated_side(d, 380, 1190, 620, 1, SWEATER, WHITEHAIR, pants=(60, 60, 66), smile=0.6)
    seated_side(d, 720, 1190, 620, -1, (34, 36, 44), (40, 32, 28), pants=(30, 30, 36))
    d.ellipse((500, 1120, 600, 1135), fill=(14, 14, 16))
    d.rectangle((540, 1128, 560, 1250), fill=(14, 14, 16))
    if red:
        on = 0.85 + 0.15 * math.sin(lt * 6)
        d.ellipse((870, 1110, 896, 1136), fill=(230, 30, 30))
        glow(im, 883, 1123, 60, (255, 40, 30), on)
    return im


# ================================================================ SCENE 1 / 17 cinema
SCR = (300, 560, 1020, 980)  # screen box in cinema world
PROJ = (70, 210)


def cinema_bg():
    if "cinema" in _cache:
        return _cache["cinema"]
    im = vgrad(W, H, [(0, (16, 14, 18)), (0.5, (22, 18, 22)), (1, (8, 6, 8))])
    d = ImageDraw.Draw(im)
    # curtains
    for side in (0, 1):
        for i in range(10):
            x = (i * 26) if side == 0 else (W - 260 + i * 26)
            c = CRIMSON_D if i % 2 else shade(CRIMSON, 0.6)
            d.rectangle((x, 0, x + 26, 1300), fill=c)
    d.rectangle((260, 470, W, 500), fill=(40, 12, 18))
    # screen frame
    x0, y0, x1, y1 = SCR
    d.rectangle((x0 - 20, y0 - 20, x1 + 20, y1 + 20), fill=(6, 6, 6))
    # projector booth
    d.rectangle((0, 150, 120, 270), fill=(10, 10, 12))
    d.rectangle((40, 180, 100, 240), fill=(30, 30, 34))
    # seats: rows in perspective
    rows = [(1180, 60, 13), (1260, 72, 11), (1360, 90, 9), (1490, 112, 8), (1660, 140, 6), (1870, 180, 5)]
    for (y, w, n) in rows:
        span = n * w * 1.25
        for i in range(n):
            x = W / 2 - span / 2 + (i + 0.5) * span / n
            seat_back(d, x, y, w, shade(CRIMSON, 0.55 + 0.45 * (y - 1180) / 700))
    _cache["cinema"] = im
    return im


def cinema_world(lt, screen_mode="studio", beam=1.0, bright=1.0, flicker=1.0):
    im = cinema_bg().copy()
    d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = SCR
    sw, sh = x1 - x0, y1 - y0
    if screen_mode == "studio":
        st = studio_world(0).crop((60, 760, 1020, 1320)).resize((sw, sh), Image.BICUBIC)
        base = Image.new("RGB", (sw, sh), (190, 196, 200))
        im.paste(blend(base, st, sstep(0.1, 0.6, lt) * 0.92 + 0.0), (x0, y0))
    elif screen_mode == "white":
        v = int(255 * bright)
        im.paste((v, v, int(v * 0.98)), (x0, y0, x1, y1))
        glow(im, (x0 + x1) / 2, (y0 + y1) / 2, 700, (200, 205, 210), 0.5 * bright)
    else:
        im.paste((150, 155, 160), (x0, y0, x1, y1))
    # beam
    k = beam * flicker
    if k > 0:
        pts = [(PROJ[0] + 30, PROJ[1]), (x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        poly_a(im, [(PROJ[0] + 30, PROJ[1] - 8), (x1, y0), (x1, y1), (PROJ[0] + 30, PROJ[1] + 8)], (240, 230, 205), 0.13 * k, blur=14)
        glow(im, PROJ[0] + 35, PROJ[1], 90, (255, 240, 200), 1.0 * k)
    # spectator: seated, back view, centre
    sd = ImageDraw.Draw(im)
    bust_back(sd, 540, 1430, 170, (36, 34, 34), DARKHAIR, hood=MUSTARD, hairshape="fade",
              rim=lerpc((60, 50, 40), (230, 225, 210), 0.6 * bright))
    seat_back(sd, 430, 1470, 112, shade(CRIMSON, 0.8))
    seat_back(sd, 650, 1470, 112, shade(CRIMSON, 0.8))
    d.rounded_rectangle((440, 1640, 640, 1800), radius=30, fill=shade(CRIMSON, 0.75))
    return im


_dust_cin = Particles(260, (60, 150, 1040, 1000), 1)


def beam_mask(x, y):
    x0, y0, x1, y1 = SCR
    if x < PROJ[0] + 30 or x > x1:
        return False
    t = (x - PROJ[0] - 30) / (x1 - PROJ[0] - 30)
    return PROJ[1] + (y0 - PROJ[1]) * t - 10 < y < PROJ[1] + (y1 - PROJ[1]) * t + 10


def scene1(lt, dur):
    beam = sstep(0, 0.35, lt)
    im = cinema_world(lt, "studio", beam=beam)
    _dust_cin.draw(im, lt, beam_mask, beam)
    sc = ((SCR[0] + SCR[2]) / 2, (SCR[1] + SCR[3]) / 2)
    e = snap(B[0] + 2.4) if dur > 3 else dur * 0.66
    dx, dy = drift(lt)
    cx, cy, z = cam_path(lt, [(0, 540, 960, 1.0), (e, 540 + dx, 1000, 1.06), (dur, sc[0], sc[1] + 40, 2.2), (dur + 0.4, sc[0], sc[1] + 20, 3.2)])
    return camera(im, cx, cy, z)


def scene2(lt, dur):
    im = studio_world(lt)
    e1 = min(dur * 0.4, 1.2)
    e2 = dur * 0.78
    dx, dy = drift(lt, 5)
    cx, cy, z = cam_path(lt, [(0, 540, 1040, 1.1), (e1, 380 + dx, 1000, 1.45), (e2 - 0.2, 200, 960, 1.6), (e2, 200, 960, 1.6),
                              (dur + 0.3, 540, 675, 3.0)])
    return camera(im, cx, cy, z)


# ================================================================ SCENE 3 city
def city_aerial_bg():
    if "aerial" in _cache:
        return _cache["aerial"]
    im = vgrad(W, H, [(0, (70, 80, 90)), (0.35, (120, 124, 126)), (0.42, (160, 140, 110)), (0.47, (110, 116, 118)), (1, (40, 46, 52))])
    d = ImageDraw.Draw(im)
    rng = random.Random(5)
    for layer, (base, col, wmin) in enumerate([(820, (88, 96, 102), 60), (960, (66, 74, 82), 80), (1150, (46, 52, 60), 110), (1400, (32, 36, 44), 150)]):
        x = -20
        while x < W:
            w = rng.randint(wmin, wmin * 2)
            hgt = rng.randint(150, 520) + layer * 60
            d.rectangle((x, base - hgt, x + w, H), fill=col)
            for wy in range(base - hgt + 20, H, 26 + layer * 6):
                for wx in range(x + 10, x + w - 10, 18 + layer * 6):
                    lit = rng.random() < 0.05
                    c = (190, 160, 100) if lit else shade(col, 0.7)
                    d.rectangle((wx, wy, wx + 6 + layer * 2, wy + 10 + layer * 3), fill=c)
            x += w + rng.randint(4, 20)
    _cache["aerial"] = im
    return im


def storefront(lt):
    if "store" not in _cache:
        im = vgrad(W, H, [(0, (44, 50, 56)), (0.7, (60, 64, 68)), (0.72, (80, 82, 82)), (1, (52, 54, 56))])
        d = ImageDraw.Draw(im)
        d.rectangle((60, 380, 1020, 1300), fill=(18, 22, 26))
        d.rectangle((60, 380, 1020, 400), fill=(30, 30, 32))
        _cache["store"] = im
    im = _cache["store"].copy()
    d = ImageDraw.Draw(im)
    # 3x3 tvs with the same news
    for r in range(3):
        for c in range(3):
            x0 = 110 + c * 300
            y0 = 460 + r * 270
            d.rectangle((x0, y0, x0 + 260, y0 + 200), fill=(10, 10, 12))
            d.rectangle((x0 + 10, y0 + 10, x0 + 250, y0 + 190), fill=(40, 90, 130))
            # tiny anchor: white-haired man silhouette + brain icon
            d.ellipse((x0 + 60, y0 + 60, x0 + 100, y0 + 100), fill=(220, 220, 215))
            d.ellipse((x0 + 66, y0 + 72, x0 + 94, y0 + 104), fill=(196, 160, 130))
            d.rounded_rectangle((x0 + 45, y0 + 105, x0 + 115, y0 + 190), radius=12, fill=(120, 124, 128))
            d.ellipse((x0 + 150, y0 + 60, x0 + 220, y0 + 110), outline=(200, 230, 240), width=3)
            d.rectangle((x0 + 10, y0 + 160, x0 + 250, y0 + 190), fill=(150, 30, 40))
            glow(im, x0 + 130, y0 + 100, 170, (60, 110, 150), 0.35 + 0.05 * math.sin(lt * 9 + r + c))
    # sidewalk flowers + candles near door
    rng = random.Random(9)
    for i in range(14):
        x = 120 + i * 62 + rng.randint(-10, 10)
        y = 1380 + rng.randint(-10, 30)
        d.line((x, y, x + rng.randint(-14, 14), y - 60), fill=(50, 80, 50), width=4)
        for k in range(4):
            fx = x + rng.randint(-18, 18)
            fy = y - 60 + rng.randint(-18, 10)
            d.ellipse((fx - 10, fy - 10, fx + 10, fy + 10), fill=rng.choice([CRIMSON, (230, 225, 220), (200, 140, 60)]))
    for i in range(7):
        x = 160 + i * 120
        y = 1440
        d.rectangle((x - 9, y - 34, x + 9, y), fill=(230, 220, 200))
        fl = 0.8 + 0.2 * math.sin(lt * 11 + i * 1.7)
        glow(im, x, y - 44, 40, (255, 190, 90), fl)
    # lone person watching (back view)
    person_back(d, 720, 1700, 820, (50, 54, 60), DARKHAIR, coatlen=0.6, rim=(110, 150, 180))
    return im


def plaza(lt):
    if "plaza" not in _cache:
        im = vgrad(W, H, [(0, (110, 118, 122)), (0.45, (140, 144, 146)), (0.46, (96, 100, 104)), (1, (60, 64, 68))])
        d = ImageDraw.Draw(im)
        for i in range(20):
            y = 880 + i ** 1.6 * 8
            d.line((0, y, W, y), fill=(86, 90, 94), width=2)
        for i in range(-10, 11):
            d.line((540 + i * 30, 880, 540 + i * 220, H), fill=(86, 90, 94), width=2)
        d.rectangle((0, 600, 300, 880), fill=(78, 84, 90))
        d.rectangle((760, 560, W, 880), fill=(72, 78, 86))
        # row of empty chairs receding
        for i in range(16):
            t = i / 15
            s = lerp(1.0, 0.18, t ** 0.7)
            x = lerp(150, 760, t ** 0.8)
            y = lerp(1700, 930, t ** 0.75)
            cw = 150 * s
            col = (34, 36, 40)
            d.rectangle((x - cw / 2, y - cw * 1.4, x + cw / 2, y - cw * 1.25), fill=col)
            d.rectangle((x + cw * 0.4, y - cw * 1.4, x + cw * 0.5, y - cw * 0.55), fill=col)
            d.polygon([(x - cw / 2, y - cw * 0.6), (x + cw / 2, y - cw * 0.6), (x + cw * 0.6, y - cw * 0.48), (x - cw * 0.4, y - cw * 0.48)], fill=col)
            for lx in (x - cw * 0.4, x + cw * 0.45):
                d.line((lx, y - cw * 0.5, lx, y), fill=col, width=max(2, int(6 * s)))
            # flower on the seat
            d.line((x - cw * 0.2, y - cw * 0.62, x + cw * 0.15, y - cw * 0.66), fill=(50, 90, 50), width=max(2, int(5 * s)))
            d.ellipse((x - cw * 0.3, y - cw * 0.75, x - cw * 0.08, y - cw * 0.55), fill=CRIMSON)
        _cache["plaza"] = im
    im = _cache["plaza"].copy()
    d = ImageDraw.Draw(im)
    for i, (x0, sp, h) in enumerate([(880, -14, 170), (330, 10, 130), (980, -8, 110)]):
        person_back(d, x0 + sp * lt, 900 + h * 0.6, h, (60, 62, 66), DARKHAIR, step=math.sin(lt * 5 + i) * 0.6)
    return im


def scene3(lt, dur):
    e1 = snap(B[2] + dur * 0.34) - B[2]
    e2 = snap(B[2] + dur * 0.69) - B[2]
    xf = 0.35
    def A(t):
        im = city_aerial_bg().copy()
        cx, cy, z = cam_path(t, [(0, 540, 760, 1.0), (e1 + 0.3, 540, 1300, 1.6)])
        return camera(im, cx, cy, z)
    def Bs(t):
        im = storefront(t)
        cx, cy, z = cam_path(t, [(e1 - 0.3, 300, 1000, 1.5), (e2 + 0.3, 760, 1000, 1.35)])
        return camera(im, cx, cy, z)
    def C(t):
        im = plaza(t)
        cx, cy, z = cam_path(t, [(e2 - 0.3, 540, 1200, 1.05), (dur - 0.4, 520, 1100, 1.22), (dur + 0.3, 540, 700, 1.6)])
        return camera(im, cx, cy, z)
    if lt < e1 - xf / 2:
        return A(lt)
    if lt < e1 + xf / 2:
        return blend(A(lt), Bs(lt), sstep(e1 - xf / 2, e1 + xf / 2, lt))
    if lt < e2 - xf / 2:
        return Bs(lt)
    if lt < e2 + xf / 2:
        return blend(Bs(lt), C(lt), sstep(e2 - xf / 2, e2 + xf / 2, lt))
    return C(lt)


# ================================================================ SCENE 4 counter
def scene4(lt, dur):
    if "counter" not in _cache:
        im = vgrad(W, H, [(0, (22, 26, 32)), (0.6, (36, 40, 46)), (1, (20, 22, 26))])
        d = ImageDraw.Draw(im)
        d.rectangle((40, 160, 1040, 1150), fill=(28, 32, 38))
        for y in range(200, 1150, 60):
            d.line((40, y, 1040, y), fill=(34, 38, 44), width=2)
        d.rectangle((80, 360, 1000, 860), fill=(10, 10, 12))
        _cache["counter"] = im
    im = _cache["counter"].copy()
    d = ImageDraw.Draw(im)
    e = snap(B[3] + dur * 0.5) - B[3]
    n = 4183207 + int(lt / 0.3) * 37 + (int(sstep(e - 0.05, e + 0.05, lt) * 214560))
    s = f"{n:,}".replace(",", ".")
    d.rectangle((100, 380, 980, 840), fill=(226, 232, 234))
    glow(im, 540, 610, 900, (200, 210, 220), 0.55)
    f = font(FONT_N, 150)
    tw = d.textlength(s, font=f)
    pulse = sstep(e - 0.05, e + 0.25, lt) * (1 - sstep(e + 0.25, e + 0.6, lt))
    d.text((540 - tw / 2, 520), s, font=f, fill=lerpc((30, 34, 40), (150, 24, 38), pulse))
    # crowd from behind, lit from above
    rng = random.Random(4)
    rim = (235, 240, 240)
    rows = [(1360, 130, 8), (1530, 170, 6), (1750, 230, 5)]
    for ri, (y, s, nn) in enumerate(rows):
        for i in range(nn):
            x = (i + 0.5) * W / nn + rng.randint(-30, 30) + (ri % 2) * 40
            if ri == 2 and i == 2:
                bust_back(d, x, y, s, (40, 38, 36), DARKHAIR, hood=MUSTARD, rim=rim, hairshape="fade")
            else:
                bust_back(d, x, y, s, rng.choice([(50, 54, 60), (60, 58, 56), (40, 44, 50)]),
                          rng.choice([DARKHAIR, (70, 50, 36), (120, 110, 100)]), rim=rim)
    cx, cy, z = cam_path(lt, [(0, 540, 1000, 1.0), (dur, 540, 960, 1.12), (dur + 0.3, 900, 700, 1.4)])
    return camera(im, cx, cy, z)


# ================================================================ SCENE 5 apartment
def scene5(lt, dur):
    e = snap(B[4] + dur * 0.75) - B[4]
    if "apt" not in _cache:
        im = vgrad(W, H, [(0, (14, 18, 28)), (1, (8, 10, 16))])
        d = ImageDraw.Draw(im)
        # window right top with far counter glow
        d.rectangle((640, 240, 1000, 760), fill=(24, 32, 46))
        for x in range(660, 1000, 40):
            h = random.Random(x).randint(80, 260)
            d.rectangle((x, 760 - h, x + 34, 760), fill=(14, 18, 26))
        d.rectangle((640, 240, 1000, 760), outline=(6, 8, 12), width=16)
        d.line((820, 240, 820, 760), fill=(6, 8, 12), width=10)
        glow(im, 900, 520, 70, (230, 235, 240), 0.8)
        d.rectangle((884, 508, 916, 528), fill=(235, 240, 240))
        # tv stand
        d.rectangle((60, 980, 520, 1040), fill=(20, 18, 18))
        d.rectangle((70, 640, 510, 960), fill=(6, 6, 8))
        # table with clippings
        d.polygon([(380, 1380), (1080, 1380), (1080, 1460), (330, 1460)], fill=(36, 28, 24))
        rng = random.Random(2)
        for i in range(7):
            x = 420 + i * 90 + rng.randint(-20, 20)
            y = 1385 + rng.randint(-5, 20)
            a = rng.uniform(-0.3, 0.3)
            pts = [(x, y), (x + 80, y + 10 * a), (x + 76, y + 50), (x - 4, y + 46)]
            d.polygon(pts, fill=(190, 184, 168))
            d.rectangle((x + 6, y + 8, x + 26, y + 30), fill=(120, 120, 120))
            d.ellipse((x + 10, y + 8, x + 22, y + 18), fill=(230, 230, 225))
            for k in range(3):
                d.line((x + 32, y + 12 + k * 9, x + 70, y + 12 + k * 9), fill=(120, 116, 106), width=2)
        _cache["apt"] = im
    im = _cache["apt"].copy()
    d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = 86, 656, 494, 944
    off = sstep(e, e + 0.35, lt)
    if off < 1:
        tv = Image.new("RGB", (x1 - x0, y1 - y0), (40, 80, 120))
        td = ImageDraw.Draw(tv)
        td.ellipse((140, 50, 270, 190), fill=WHITEHAIR)
        td.ellipse((152, 75, 258, 205), fill=SKIN)
        td.arc((180, 140, 230, 175), 20, 160, fill=SKIN_D, width=4)
        td.ellipse((178, 120, 188, 130), fill=(30, 26, 24))
        td.ellipse((222, 120, 232, 130), fill=(30, 26, 24))
        td.rounded_rectangle((110, 200, 300, 300), radius=40, fill=SWEATER)
        sy = 1 - sstep(0, 0.6, off)
        sx = 1 - sstep(0.6, 1.0, off)
        nw, nh = max(2, int(tv.size[0] * max(sx, 0.02))), max(2, int(tv.size[1] * max(sy, 0.015)))
        tv = tv.resize((nw, nh))
        if off > 0:
            tv = Image.blend(tv, Image.new("RGB", tv.size, (240, 245, 250)), off)
        im.paste(tv, ((x0 + x1) // 2 - nw // 2, (y0 + y1) // 2 - nh // 2))
        glow(im, 290, 800, 500, (60, 110, 160), 0.45 * (1 - off))
    dot = sstep(e + 0.2, e + 0.4, lt) * (1 - 0.3 * sstep(e + 0.4, dur, lt))
    if dot > 0:
        glow(im, 290, 800, 30, (230, 240, 250), dot)
    # you, seated from behind, looking at tv, remote in hand
    bust_back(d, 760, 1250, 300, COAT, DARKHAIR, rim=lerpc((30, 40, 60), (80, 130, 180), 1 - off))
    d.line((640, 1320, 600, 1300), fill=(15, 15, 15), width=18)
    cx, cy, z = cam_path(lt, [(0, 600, 1000, 1.08), (dur, 520, 940, 1.2), (dur + 0.3, 290, 800, 1.6)])
    return camera(im, cx, cy, z)


# ================================================================ SCENE 6 decision
def scene6(lt, dur):
    e = snap(B[5] + dur * 0.67) - B[5]
    def bag(t):
        im = vgrad(W, H, [(0, (26, 24, 26)), (1, (14, 12, 14))])
        d = ImageDraw.Draw(im)
        d.rectangle((0, 1050, W, H), fill=(40, 30, 24))
        glow(im, 300, 300, 600, (90, 80, 60), 0.4)
        # bag body
        d.polygon([(200, 1000), (880, 1000), (940, 1500), (140, 1500)], fill=(58, 36, 24))
        c = sstep(0.2, 1.4, t)
        fy = lerp(560, 1060, c)
        if c < 0.55:
            d.polygon([(200, 1000), (880, 1000), (900 - 30 * c, fy), (180 + 30 * c, fy)], fill=(72, 46, 30))
        # papers inside
        for i, (dx, rot) in enumerate([(-120, -4), (0, 3), (120, -2)]):
            x = 540 + dx
            d.polygon([(x - 140, 760 + i * 10), (x + 140, 770 + i * 10), (x + 140, 1080), (x - 140, 1080)], fill=(214, 208, 192))
            if i == 0:
                d.line([(x - 110, 960), (x - 60, 900), (x - 10, 930), (x + 50, 840), (x + 110, 870)], fill=(60, 90, 130), width=5)
            if i == 2:
                for k in range(5):
                    hh = [60, 110, 80, 150, 40][k]
                    d.rectangle((x - 110 + k * 45, 1000 - hh, x - 80 + k * 45, 1000), fill=(80, 100, 120))
            if i == 1:
                d.rectangle((x - 70, 820, x + 70, 990), fill=(130, 130, 130))
                d.ellipse((x - 40, 840, x + 40, 920), fill=WHITEHAIR)
                d.ellipse((x - 32, 856, x + 32, 930), fill=(170, 150, 130))
                d.rounded_rectangle((x - 60, 930, x + 60, 990), radius=20, fill=(100, 102, 106))
                d.line((x - 90, 1000, x + 90, 800), fill=(200, 20, 30), width=12)
        # recorder
        d.rounded_rectangle((720, 900, 820, 1060), radius=12, fill=(20, 20, 22))
        for k in range(4):
            for j in range(3):
                d.ellipse((738 + j * 24, 920 + k * 20, 748 + j * 24, 930 + k * 20), fill=(60, 60, 64))
        d.ellipse((760, 1020, 776, 1036), fill=(200, 30, 30))
        # flap closing
        if c >= 0.55:
            d.polygon([(200, 1000), (880, 1000), (900 - 30 * c, fy), (180 + 30 * c, fy)], fill=(72, 46, 30))
            d.rectangle((520, fy - 40, 560, fy + 20), fill=(150, 120, 70))
        # hands
        for s in (-1, 1):
            hx = 540 + s * lerp(420, 300, c)
            hy = lerp(620, 1080, c)
            d.line((hx + s * 200, hy - 260, hx, hy), fill=COAT, width=110)
            d.ellipse((hx - 70, hy - 40, hx + 70, hy + 60), fill=SKIN)
        return camera(im, 540, 960 + 40 * c, 1.05 + 0.05 * t)
    def door(t):
        im = vgrad(W, H, [(0, (18, 20, 24)), (1, (10, 10, 12))])
        d = ImageDraw.Draw(im)
        o = sstep(e, e + 0.8, t)
        x0, y0, x1, y1 = 330, 480, 760, 1500
        im.paste((215, 225, 228), (x0, y0, x1, y1))
        glow(im, 545, 1000, 650, (180, 200, 205), 0.6 * o)
        dw = (x1 - x0) * (1 - o * 0.85)
        d.polygon([(x0, y0), (x0 + dw, y0 - 30 * o), (x0 + dw, y1 + 30 * o), (x0, y1)], fill=(52, 38, 30))
        d.ellipse((x0 + dw - 40, 1000, x0 + dw - 20, 1020), fill=(180, 160, 90))
        ell_a(im, (x0 - 200 * o, y1 - 300 - 200 * o, x1 + 300 * o, y1 + 250), (200, 210, 212), 0.55 * o, blur=60)
        person_back(d, 560, 1720 - 120 * sstep(e + 0.3, dur, t), 900, COAT, DARKHAIR, coatlen=0.66,
                    step=math.sin(t * 7) * 0.5 * sstep(e + 0.3, e + 0.5, t))
        cx, cy, z = cam_path(t, [(e - 0.3, 540, 1000, 1.05), (dur - 0.3, 545, 1000, 1.25), (dur + 0.3, 545, 1000, 2.4)])
        return camera(im, cx, cy, z)
    if lt < e - 0.15:
        return bag(lt)
    if lt < e + 0.15:
        return blend(bag(lt), door(lt), sstep(e - 0.15, e + 0.15, lt))
    return door(lt)


# ================================================================ SCENE 7/8 ferry
def sea_bg():
    if "sea" in _cache:
        return _cache["sea"]
    im = vgrad(W, H, [(0, (120, 130, 134)), (0.4, (150, 156, 156)), (0.46, (112, 122, 126)), (1, (64, 74, 80))])
    d = ImageDraw.Draw(im)
    # island + mansion
    d.polygon([(560, 880), (640, 760), (720, 720), (820, 700), (900, 730), (990, 800), (1080, 870), (1080, 890), (560, 890)], fill=(78, 86, 90))
    d.rectangle((770, 650, 880, 710), fill=(70, 76, 80))
    d.polygon([(760, 652), (825, 615), (890, 652)], fill=(64, 70, 74))
    for k in range(4):
        d.rectangle((782 + k * 24, 670, 792 + k * 24, 684), fill=(220, 180, 110))
    _cache["sea"] = im
    return im


def waves(d, lt, y0, y1, col):
    for i in range(18):
        y = lerp(y0, y1, (i / 17) ** 1.5)
        amp = lerp(2, 10, i / 17)
        pts = [(x, y + amp * math.sin(x / (40 + i * 8) + lt * (1.2 + i * 0.05) + i)) for x in range(0, W + 20, 20)]
        d.line(pts, fill=col, width=max(1, int(lerp(1, 4, i / 17))))


def ferry_world(lt, woman_x, woman_turn, close=False, wind=0.0, smile=0.0):
    im = sea_bg().copy()
    d = ImageDraw.Draw(im)
    waves(d, lt, 900, 1350, (140, 150, 154))
    # deck
    d.polygon([(0, 1500), (W, 1500), (W, H), (0, H)], fill=(66, 56, 48))
    for i in range(8):
        d.line((0, 1500 + i ** 1.5 * 12, W, 1500 + i ** 1.5 * 12), fill=(52, 44, 38), width=3)
    # far passengers + spectator at other end
    person_back(d, 70, 1520, 230, (40, 40, 40), DARKHAIR, hood=MUSTARD, hairshape="fade")
    person_side(d, 1000, 1510, 200, 1, (60, 64, 70), (90, 80, 70))
    # railing
    d.rectangle((0, 1310, W, 1326), fill=(170, 170, 166))
    d.rectangle((0, 1400, W, 1410), fill=(150, 150, 146))
    for x in range(20, W, 120):
        d.rectangle((x, 1310, x + 12, 1520), fill=(150, 150, 146))
    # lifebuoy hanging on railing between them
    bx = (woman_x + 640) / 2
    d.ellipse((bx - 70, 1340, bx + 70, 1480), fill=(200, 80, 60))
    d.ellipse((bx - 38, 1372, bx + 38, 1448), fill=(100, 110, 116))
    for a in (45, 135, 225, 315):
        d.pieslice((bx - 70, 1340, bx + 70, 1480), a - 12, a + 12, fill=(214, 206, 196))
    d.ellipse((bx - 38, 1372, bx + 38, 1448), fill=(104, 114, 118))
    # you: leaning on railing facing right (towards island)
    person_side(d, 640, 1620, 760, 1, COAT, DARKHAIR, arms="rail", coatlen=0.62, lean=0.4)
    # woman
    walking = woman_x < 400
    f = 1
    hx, hy, r = person_side(d, woman_x, 1620, 720, f, GREEN, BROWNHAIR, style="bob", coatlen=0.6,
                            step=math.sin(lt * 7) * (1 if walking else 0), wind=wind, smile=smile)
    return im


def scene7(lt, dur):
    e1 = snap(B[6] + dur * 0.33) - B[6]
    e2 = snap(B[6] + dur * 0.66) - B[6]
    wx = lerp(-60, 420, sstep(0.2, e2 - 0.3, lt))
    im = ferry_world(lt, wx, 0)
    cx, cy, z = cam_path(lt, [(0, 540, 1100, 1.0), (e1 - 0.2, 540, 1080, 1.05), (e1 + 1.0, 820, 720, 2.0), (e2 - 0.5, 820, 700, 2.1),
                              (e2 + 0.6, 520, 1250, 1.45), (dur, 520, 1240, 1.5), (dur + 0.3, 700, 1150, 1.7)])
    return camera(im, cx, cy, z)


def scene8(lt, dur):
    e = snap(B[7] + dur * 0.55) - B[7]
    wind = sstep(e - 0.2, e + 0.3, lt)
    im = ferry_world(lt, 420, 0, wind=wind, smile=sstep(e, e + 0.5, lt) * 0.8)
    a = lt / dur
    cx, cy, z = cam_path(lt, [(0, 470, 1170, 2.3), (dur, 600, 1150, 2.5)])
    out = camera(im, cx + 30 * math.sin(a * 2), cy, z)
    # foam at end
    k = sstep(dur - 0.45, dur + 0.15, lt)
    if k > 0:
        for i in range(14):
            rr = 200 + i * 90
            ell_a(out, (540 - rr * k * 1.2 + i * 20 - 200, 1900 - rr * k * 1.5, 540 + rr * k * 1.2 + i * 10, 1900 + rr * 0.5),
                  (236, 240, 240), 0.35 + 0.65 * k, blur=30)
    return out


# ================================================================ SCENE 9 beach
def scene9(lt, dur):
    e1 = snap(B[8] + dur * 0.55) - B[8]
    e2 = snap(B[8] + dur * 0.83) - B[8]
    if "beach" not in _cache:
        im = vgrad(W, H, [(0, (96, 104, 110)), (0.36, (150, 140, 120)), (0.4, (196, 150, 80)), (0.42, (120, 126, 128)), (0.55, (84, 94, 100)), (1, (60, 62, 64))])
        d = ImageDraw.Draw(im)
        d.polygon([(0, 1060), (W, 1020), (W, H), (0, H)], fill=(92, 90, 88))
        rng = random.Random(7)
        for i in range(1400):
            y = rng.uniform(1030, H)
            s = lerp(3, 26, (y - 1030) / 890)
            x = rng.uniform(0, W)
            g = rng.randint(70, 130)
            d.ellipse((x - s, y - s * 0.6, x + s, y + s * 0.6), fill=(g, g - 2, g - 6))
        _cache["beach"] = im
    im = _cache["beach"].copy()
    d = ImageDraw.Draw(im)
    for i in range(5):
        y = 1040 + i * 8
        xs = 20 * math.sin(lt * 1.5 + i)
        d.line((0, y + xs * 0.2, W, y - 30 + xs * 0.2), fill=(200, 205, 205), width=3)
    run = sstep(0.0, e1, lt)
    away = sstep(e2, dur + 0.5, lt)
    wx, wy, wh = 560, 1110 + 60 * away, 300 + 40 * away
    yx = lerp(140, 500, run)
    yy = lerp(1850, 1115, run) + 60 * away
    yh = lerp(700, 310, run) + 40 * away
    step = math.sin(lt * 12) * (1 - sstep(e1 - 0.2, e1, lt))
    # woman back view at shoreline
    person_back(d, wx, wy, wh, GREEN, BROWNHAIR, hairshape="bob", coatlen=0.58)
    if lt > e1:
        d.line((wx - wh * 0.15, wy - wh * 0.47, yx + yh * 0.05, yy - yh * 0.47), fill=SKIN, width=8)
    person_back(d, yx, yy, yh, COAT if lt < e2 else (60, 64, 72), DARKHAIR, coatlen=0.55, step=step)
    if lt > e2:
        k = sstep(e2, e2 + 0.4, lt)
        top = wy - wh
        d.rounded_rectangle((wx - wh * 0.16, top + wh * 0.17, wx + wh * 0.16, top + wh * (0.17 + 0.5 * k)), radius=10, fill=COAT)
    cx, cy, z = cam_path(lt, [(0, 540, 1200, 1.05), (dur, 540, 1120, 1.5), (dur + 0.3, 540, 700, 1.7)])
    return camera(im, cx, cy, z)


# ================================================================ SCENE 10 gate
def scene10(lt, dur):
    e = snap(B[9] + dur * 0.7) - B[9]
    if "mansion" not in _cache:
        im = vgrad(W, H, [(0, (44, 52, 58)), (0.5, (70, 76, 80)), (1, (40, 40, 42))])
        d = ImageDraw.Draw(im)
        d.rectangle((80, 260, 1000, 1080), fill=(82, 80, 76))
        d.polygon([(60, 270), (540, 90), (1020, 270)], fill=(56, 56, 58))
        for r in range(4):
            for c in range(6):
                x = 140 + c * 145
                y = 340 + r * 180
                d.rectangle((x, y, x + 70, y + 110), fill=(232, 186, 110))
                glow(im, x + 35, y + 55, 90, (180, 120, 50), 0.35)
                d.line((x + 35, y, x + 35, y + 110), fill=(60, 50, 40), width=4)
        for y in range(280, 1080, 40):
            d.line((80, y, 1000, y), fill=(74, 72, 68), width=2)
        d.rectangle((460, 820, 620, 1080), fill=(40, 30, 24))
        d.polygon([(0, 1080), (W, 1080), (W, H), (0, H)], fill=(52, 52, 50))
        d.polygon([(470, 1080), (610, 1080), (900, H), (180, H)], fill=(78, 76, 72))
        _cache["mansion"] = im
    im = _cache["mansion"].copy()
    d = ImageDraw.Draw(im)
    # followers in a row on both sides, backlit, faceless (in shadow), badge
    for side in (-1, 1):
        for i in range(5):
            x = 540 + side * (140 + i * 22)
            y = 1150 + i * 60
            h = 300 + i * 70
            x = 540 + side * (120 + i * 70)
            top = y - h
            r = h * 0.068
            d.rounded_rectangle((x - h * 0.12, top + h * 0.18, x + h * 0.12, top + h * 0.78), radius=int(h * 0.05), fill=FOLLOW)
            d.rectangle((x - h * 0.08, top + h * 0.78, x + h * 0.08, y), fill=(70, 72, 76))
            d.ellipse((x - r, top, x + r, top + 2 * r), fill=(90, 80, 72))
            d.chord((x - r * 1.02, top - r * 0.04, x + r * 1.02, top + 2 * r), 180, 360, fill=(50, 46, 44))
            d.ellipse((x - h * 0.07 - 7, top + h * 0.28 - 7, x - h * 0.07 + 7, top + h * 0.28 + 7), fill=(220, 210, 180))
    # gate opening
    o = sstep(0, 1.2, lt)
    for side in (-1, 1):
        n = 9
        span = 540 * (1 - 0.85 * o)
        for i in range(n + 1):
            x = 540 + side * (i / n) * span if side > 0 else 540 - (i / n) * span
            xx = (W - (i / n) * span) if side > 0 else (i / n) * span
            d.rectangle((xx - 7, 700, xx + 7, 1800), fill=(20, 20, 22))
            d.polygon([(xx - 12, 700), (xx, 660), (xx + 12, 700)], fill=(20, 20, 22))
        x0 = W - span if side > 0 else 0
        x1 = W if side > 0 else span
        d.rectangle((x0, 760, x1, 776), fill=(20, 20, 22))
        d.rectangle((x0, 1700, x1, 1716), fill=(20, 20, 22))
    walk = sstep(0, dur + 0.4, lt)
    yf = lerp(1960, 1700, walk)
    person_back(d, 430, yf, 760, COAT, DARKHAIR, step=math.sin(lt * 7) * 0.6, coatlen=0.6)
    person_back(d, 650, yf + 10, 720, GREEN, BROWNHAIR, hairshape="bob", step=math.sin(lt * 7 + 3) * 0.6, coatlen=0.58)
    cx, cy, z = cam_path(lt, [(0, 540, 1100, 1.0), (e, 540, 1050, 1.3), (dur + 0.3, 540, 950, 1.9)])
    return camera(im, cx, cy, z)


# ================================================================ SCENE 11 hall
def scene11(lt, dur):
    e1 = snap(B[10] + dur * 0.41) - B[10]
    e2 = snap(B[10] + dur * 0.68) - B[10]
    if "hall" not in _cache:
        im = vgrad(W, H, [(0, (40, 44, 48)), (0.55, (58, 60, 62)), (1, (30, 30, 32))])
        d = ImageDraw.Draw(im)
        for i in range(3):
            x = 90 + i * 330
            d.rectangle((x, 250, x + 240, 820), fill=(140, 150, 154))
            d.rectangle((x, 640, x + 240, 820), fill=(110, 122, 128))
            d.line((x + 120, 250, x + 120, 820), fill=(40, 40, 42), width=8)
            d.line((x, 520, x + 240, 520), fill=(40, 40, 42), width=8)
            glow(im, x + 120, 520, 240, (100, 110, 115), 0.4)
        d.rectangle((0, 900, W, H), fill=(50, 44, 40))
        _cache["hall"] = im
    im = _cache["hall"].copy()
    d = ImageDraw.Draw(im)
    # curtain behind father: opens at the end
    co = sstep(dur - 0.55, dur + 0.2, lt)
    cw = 210 * (1 - co)
    d.rectangle((330, 560, 750, 1000), fill=(10, 14, 22))
    glow(im, 540, 780, 200, (60, 110, 170), 0.6 * co)
    d.rectangle((330, 560, 330 + cw, 1000), fill=shade(CRIMSON, 0.6))
    d.rectangle((750 - cw, 560, 750, 1000), fill=shade(CRIMSON, 0.6))
    # chalkboard with brain waves (right wall)
    d.rectangle((790, 860, 1060, 1040), fill=(28, 40, 36))
    for k in range(3):
        pts = [(800 + x, 900 + k * 45 + 14 * math.sin(x / (8 + k * 5))) for x in range(0, 250, 4)]
        d.line(pts, fill=(220, 222, 214), width=3)
    # father standing at front
    turn = sstep(e2, e2 + 0.35, lt)
    fx = 540 + 40 * co
    person_side(d, fx, 1060, 420, -1 if turn < 0.5 else 1, SWEATER, WHITEHAIR, arms="forward" if (lt % 1.2) < 0.6 else "down",
                pants=(60, 60, 66), coatlen=0.4)
    if turn >= 0.5:
        r = 420 * 0.068
        hy = 1060 - 420 + r
        d.ellipse((fx - r, hy - r, fx + r, hy + r), fill=SKIN)
        d.chord((fx - r * 1.05, hy - r * 1.1, fx + r * 1.05, hy + r * 0.5), 180, 360, fill=WHITEHAIR)
        d.ellipse((fx - r * 0.45, hy - r * 0.05, fx - r * 0.25, hy + r * 0.15), fill=(30, 26, 24))
        d.ellipse((fx + r * 0.25, hy - r * 0.05, fx + r * 0.45, hy + r * 0.15), fill=(30, 26, 24))
    # rows of seated followers, heads nod together
    nod = sstep(e1 - 0.15, e1 + 0.1, lt) * (1 - sstep(e1 + 0.3, e1 + 0.6, lt))
    rng = random.Random(11)
    rows = [(1130, 60, 13), (1210, 74, 11), (1310, 92, 9), (1440, 116, 7), (1600, 146, 6)]
    for ri, (y, s, n) in enumerate(rows):
        for i in range(n):
            x = (i + 0.5) * W / n + (ri % 2) * s * 0.3
            if ri == 4 and i == 1:
                bust_back(d, x, y, s * 1.2, (40, 38, 36), DARKHAIR, hood=MUSTARD, hairshape="fade", nod=nod)
                continue
            if ri == 4 and i >= 4:
                continue
            bust_back(d, x, y, s, FOLLOW, rng.choice([DARKHAIR, (80, 60, 40), (130, 124, 114)]), nod=nod)
    # you + woman standing at the back right
    person_back(d, 830, 2000, 900, COAT, DARKHAIR, coatlen=0.6)
    person_back(d, 1010, 2010, 860, GREEN, BROWNHAIR, hairshape="bob", coatlen=0.58)
    cx, cy, z = cam_path(lt, [(0, 540, 1100, 1.0), (e2 - 0.2, 560, 1000, 1.2), (e2 + 0.4, 560, 880, 1.9), (dur, 560, 860, 2.0),
                              (dur + 0.3, 560, 800, 2.8)])
    return camera(im, cx, cy, z)


# ================================================================ SCENE 12/13/15/16 lab
def lab_bg():
    if "lab" in _cache:
        return _cache["lab"]
    im = vgrad(W, H, [(0, (12, 22, 34)), (0.55, (20, 36, 52)), (0.56, (16, 28, 40)), (1, (8, 14, 22))])
    d = ImageDraw.Draw(im)
    # stairs top-left
    for i in range(10):
        x = 40 + i * 40
        y = 200 + i * 70
        d.rectangle((x, y, x + 200, y + 70), fill=(30, 44, 58))
        d.line((x, y, x + 200, y), fill=(60, 84, 104), width=4)
    d.line((40, 160, 460, 900), fill=(70, 90, 110), width=8)
    # big screen on right wall
    d.rectangle((560, 380, 1040, 840), fill=(6, 8, 10))
    d.rectangle((560, 380, 1040, 840), outline=(50, 64, 76), width=10)
    # side monitors
    for (x, y) in [(470, 900), (960, 900)]:
        d.rectangle((x - 70, y, x + 70, y + 100), fill=(8, 12, 14))
        d.line((x - 60, y + 50, x + 60, y + 50), fill=(90, 220, 140), width=3)
        glow(im, x, y + 50, 70, (40, 120, 70), 0.6)
    # ceiling lights
    for x in (300, 780):
        d.rectangle((x - 80, 90, x + 80, 104), fill=(190, 220, 240))
        glow(im, x, 110, 320, (80, 140, 190), 0.5)
    _cache["lab"] = im
    return im


def gurney(d, x, y, w, covered=False):
    d.rectangle((x - w / 2, y, x + w / 2, y + 26), fill=(150, 160, 166))
    for lx in (x - w * 0.4, x + w * 0.4):
        d.line((lx, y + 26, lx, y + 260), fill=(110, 120, 126), width=10)
        d.ellipse((lx - 16, y + 254, lx + 16, y + 286), fill=(30, 30, 32))
    d.rectangle((x - w / 2 + 10, y - 22, x + w / 2 - 10, y), fill=(196, 206, 210))
    if covered:
        d.chord((x - w / 2 + 10, y - 120, x + w / 2 - 10, y + 40), 180, 360, fill=(232, 236, 238))
        d.rectangle((x - w / 2 + 10, y - 40, x + w / 2 - 10, y + 60), fill=(232, 236, 238))
    # head sensor cap
    d.ellipse((x - w / 2 - 60, y - 70, x - w / 2 + 40, y + 10), outline=(150, 180, 200), width=6)


def lab_world(lt, covered=False, cables=True):
    im = lab_bg().copy()
    d = ImageDraw.Draw(im)
    gx, gy, gw = 520, 1240, 520
    if cables:
        for k in range(6):
            p0 = (gx - gw / 2 - 10, gy - 30 + k * 6)
            p1 = (600 + k * 70, 840)
            pts = []
            for i in range(31):
                t = i / 30
                cx = lerp(p0[0], p1[0], t)
                cy = lerp(p0[1], p1[1], t) + math.sin(t * math.pi) * (260 + k * 30)
                pts.append((cx, cy))
            d.line(pts, fill=[(40, 60, 80), (70, 40, 40), (30, 50, 60)][k % 3], width=7)
    gurney(d, gx, gy, gw, covered)
    return im


def scene12(lt, dur):
    e1 = snap(B[11] + dur * 0.38) - B[11]
    e2 = snap(B[11] + dur * 0.76) - B[11]
    im = lab_world(lt)
    cx, cy, z = cam_path(lt, [(0, 260, 420, 1.9), (e1, 330, 1100, 1.5), (e1 + 0.3, 330, 1150, 1.5), (e2, 800, 700, 1.6), (dur, 800, 610, 2.0),
                              (dur + 0.3, 520, 1200, 2.2)])
    return camera(im, cx, cy, z)


def scene13(lt, dur):
    e = snap(B[12] + dur * 0.57) - B[12]
    if "overhead" not in _cache:
        im = Image.new("RGB", (W, H), (22, 32, 42))
        d = ImageDraw.Draw(im)
        for x in range(0, W, 120):
            d.line((x, 0, x, H), fill=(30, 42, 54), width=3)
        for y in range(0, H, 120):
            d.line((0, y, W, y), fill=(30, 42, 54), width=3)
        # wall strip with clock at top
        d.rectangle((0, 0, W, 260), fill=(16, 22, 30))
        d.ellipse((440, 40, 640, 240), fill=(210, 214, 210))
        d.ellipse((450, 50, 630, 230), outline=(30, 30, 30), width=6)
        for k in range(12):
            a = k / 12 * 2 * math.pi
            d.line((540 + 75 * math.sin(a), 140 - 75 * math.cos(a), 540 + 85 * math.sin(a), 140 - 85 * math.cos(a)), fill=(30, 30, 30), width=5)
        d.line((540, 140, 540, 75), fill=(20, 20, 20), width=10)
        d.line((540, 140, 540, 60), fill=(20, 20, 20), width=5)
        # gurney top-down
        d.rounded_rectangle((330, 460, 750, 1700), radius=30, fill=(150, 160, 166))
        d.rounded_rectangle((350, 480, 730, 1680), radius=24, fill=(200, 208, 212))
        d.rectangle((350, 480, 730, 640), fill=(214, 220, 222))
        for y in (900, 1250, 1500):
            for side in (-1, 1):
                x0 = 330 if side < 0 else 750
                d.rectangle((x0 - side * 0 - (110 if side < 0 else 0), y, x0 + (110 if side > 0 else 0), y + 44), fill=(40, 40, 44))
                bx = x0 - 110 if side < 0 else x0 + 90
                d.rectangle((bx, y + 6, bx + 20, y + 38), outline=(170, 170, 170), width=4)
        # sensors
        for k in range(6):
            a = math.pi + k / 5 * math.pi
            x = 540 + 120 * math.cos(a)
            y = 560 + 70 * math.sin(a)
            d.ellipse((x - 18, y - 18, x + 18, y + 18), fill=(120, 150, 170))
            d.line((x, y, x + (k - 2.5) * 90, 300), fill=(40, 60, 80), width=5)
        glow(im, 540, 1000, 700, (60, 110, 150), 0.45)
        _cache["overhead"] = im
    im = _cache["overhead"].copy()
    fl = 1 - 0.7 * (sstep(e - 0.05, e, lt) * (1 - sstep(e + 0.1, e + 0.2, lt)))
    out = camera(im, 540, 960, 1.05 + 0.03 * lt)
    off = sstep(dur - 0.3, dur, lt)
    fl *= 1 - off
    if fl < 1:
        out = Image.eval(out, lambda v: int(v * fl))
    return out


def scene14(lt, dur):
    e1 = snap(B[13] + dur * 0.31) - B[13]
    e2 = snap(B[13] + dur * 0.62) - B[13]
    def corridor(t, brother_light=0.0):
        if "morgue" not in _cache:
            im = Image.new("RGB", (W, H), (150, 170, 150))
            d = ImageDraw.Draw(im)
            vx, vy = 540, 900
            ix0, iy0, ix1, iy1 = 400, 700, 680, 1080
            d.polygon([(0, 0), (W, 0), (ix1, iy0), (ix0, iy0)], fill=(120, 140, 124))
            d.polygon([(0, H), (W, H), (ix1, iy1), (ix0, iy1)], fill=(96, 110, 100))
            d.polygon([(0, 0), (ix0, iy0), (ix0, iy1), (0, H)], fill=(170, 190, 172))
            d.polygon([(W, 0), (ix1, iy0), (ix1, iy1), (W, H)], fill=(160, 180, 162))
            for k in range(1, 14):
                t2 = k / 14
                xl = lerp(0, ix0, t2 ** 0.6)
                d.line((xl, lerp(0, iy0, t2 ** 0.6), xl, lerp(H, iy1, t2 ** 0.6)), fill=(140, 160, 142), width=2)
                xr = lerp(W, ix1, t2 ** 0.6)
                d.line((xr, lerp(0, iy0, t2 ** 0.6), xr, lerp(H, iy1, t2 ** 0.6)), fill=(132, 152, 134), width=2)
            for yy in range(0, H, 90):
                d.line((0, yy, ix0, lerp(yy, (iy0 + iy1) / 2, 0) * 0 + iy0 + (iy1 - iy0) * yy / H), fill=(150, 170, 152), width=2)
                d.line((W, yy, ix1, iy0 + (iy1 - iy0) * yy / H), fill=(142, 162, 144), width=2)
            d.rectangle((ix0, iy0, ix1, iy1), fill=(36, 44, 40))
            d.rectangle((470, 760, 610, 1080), fill=(24, 30, 28))
            # exit sign (pictogram only)
            d.rectangle((500, 712, 580, 748), fill=(40, 170, 90))
            d.polygon([(520, 730), (550, 718), (550, 742)], fill=(230, 250, 230))
            d.rectangle((548, 725, 568, 735), fill=(230, 250, 230))
            # ceiling lights
            for k in range(4):
                t2 = k / 4
                y = lerp(40, iy0 - 10, t2 ** 0.7)
                w = lerp(260, 60, t2 ** 0.7)
                d.rectangle((540 - w, y, 540 + w, y + lerp(30, 6, t2)), fill=(220, 240, 220))
            # security camera, off
            d.rectangle((820, 120, 900, 160), fill=(40, 44, 42))
            d.polygon([(820, 160), (850, 160), (830, 200)], fill=(40, 44, 42))
            d.ellipse((800, 130, 830, 160), fill=(20, 22, 20))
            _cache["morgue"] = im
        im = _cache["morgue"].copy()
        d = ImageDraw.Draw(im)
        push = sstep(0, e1, t)
        y = lerp(1500, 1700, push)
        gurney(d, 540, y - 250, 560, covered=True)
        person_side(d, 830, y + 50, 760, -1, COAT, DARKHAIR, arms="forward", step=math.sin(t * 6) * 0.4, coatlen=0.62)
        person_side(d, 250, y + 40, 740, 1, GREEN, BROWNHAIR, style="bob", arms="forward", step=math.sin(t * 6 + 2) * 0.4, coatlen=0.6)
        person_back(d, 560, 1080, 360, WORK, DARKHAIR)
        if brother_light > 0:
            poly_a(im, [(600, 760), (1080, 500), (1080, 1100)], (250, 250, 220), 0.25 * brother_light, blur=15)
        return im
    def A(t):
        return camera(corridor(t), 540, 1000, cam_path(t, [(0, 0, 0, 1.0), (e1, 0, 0, 1.15)])[2])
    def Bs(t):
        im = Image.new("RGB", (W, H), (40, 54, 46))
        d = ImageDraw.Draw(im)
        d.rectangle((300, 300, 820, 1500), fill=(16, 18, 20))
        d.rectangle((300, 300, 820, 1500), outline=(90, 110, 96), width=14)
        d.rectangle((520, 220, 640, 270), fill=(40, 170, 90))
        d.polygon([(545, 245), (585, 228), (585, 262)], fill=(230, 250, 230))
        sweep = math.sin((t - e1) * 3) * 0.3
        poly_a(im, [(700, 940), (240 + 300 * sweep, 520), (200 + 300 * sweep, 1100)], (250, 248, 220), 0.35, blur=18)
        person_side(d, 760, 1760, 1100, -1, WORK, DARKHAIR, beard=(40, 30, 24), arms="forward", coatlen=0.45)
        d.rectangle((560, 900, 640, 940), fill=(30, 30, 30))
        glow(im, 560, 920, 50, (255, 250, 220), 0.9)
        return camera(im, 540 + 10 * (t - e1), 1000, 1.05)
    rain = Particles(240, (0, 0, W, H), 3, size=(1, 2), speed=(0, 0))
    def C(t):
        im = vgrad(W, H, [(0, (14, 18, 22)), (1, (24, 28, 32))])
        d = ImageDraw.Draw(im)
        d.rectangle((0, 1400, W, H), fill=(30, 34, 38))
        # van rear, doors open
        d.rectangle((260, 600, 820, 1440), fill=(70, 74, 78))
        d.rectangle((300, 660, 780, 1400), fill=(10, 10, 12))
        d.polygon([(260, 600), (120, 560), (120, 1460), (260, 1440)], fill=(84, 88, 92))
        d.polygon([(820, 600), (960, 560), (960, 1460), (820, 1440)], fill=(84, 88, 92))
        for x in (275, 790):
            d.rectangle((x - 8, 1180, x + 22, 1260), fill=(200, 30, 30))
            glow(im, x + 7, 1220, 80, (255, 40, 30), 0.8)
        load = sstep(e2, dur - 0.3, t)
        d.rectangle((300 + 120 * load, 1250 - 60 * load, 780 - 120 * load, 1290 - 60 * load), fill=(150, 160, 166))
        d.chord((320 + 120 * load, 1150 - 60 * load, 760 - 120 * load, 1270 - 60 * load), 180, 360, fill=(220, 224, 226))
        rng = random.Random(int(t * 30))
        for i in range(260):
            x = rng.uniform(0, W)
            y = rng.uniform(0, H)
            d.line((x, y, x - 8, y + 50), fill=(130, 140, 150), width=2)
        k = sstep(dur - 0.6, dur + 0.3, t)
        return camera(im, 540, 1000 - 200 * k, 1.05 + 0.6 * k)
    xf = 0.3
    if lt < e1 - xf / 2:
        return A(lt)
    if lt < e1 + xf / 2:
        return blend(A(lt), Bs(lt), sstep(e1 - xf / 2, e1 + xf / 2, lt))
    if lt < e2 - xf / 2:
        return Bs(lt)
    if lt < e2 + xf / 2:
        return blend(Bs(lt), C(lt), sstep(e2 - xf / 2, e2 + xf / 2, lt))
    return C(lt)


def scene15(lt, dur):
    e = snap(B[14] + dur * 0.69) - B[14]
    im = lab_world(lt, covered=True, cables=True)
    d = ImageDraw.Draw(im)
    # papers falling under the gurney
    rng = random.Random(15)
    fall = sstep(0.1, e - 0.2, lt)
    for i in range(5):
        x0 = 280 + i * 90 + rng.randint(-20, 20)
        y = lerp(1250, 1600 + rng.randint(-20, 40), fall)
        rot = rng.uniform(-0.5, 0.5) * (1 - fall) + rng.uniform(-0.15, 0.15)
        w, h = 140, 180 * (0.3 + 0.7 * abs(math.cos(rot + fall * 3 * (1 - fall))))
        pts = [(x0, y), (x0 + w, y + w * rot * 0.3), (x0 + w, y + h), (x0, y + h - w * rot * 0.3)]
        if fall > 0.9:
            pts = [(x0, y), (x0 + w, y + 10), (x0 + w + 20, y + 60), (x0 + 20, y + 50)]
        d.polygon(pts, fill=(214, 208, 192))
        if i == 2:
            cx = sum(p[0] for p in pts) / 4
            cy = sum(p[1] for p in pts) / 4
            d.rectangle((cx - 25, cy - 18, cx + 25, cy + 18), fill=(130, 130, 130))
            d.line((cx - 40, cy + 22, cx + 40, cy - 22), fill=(200, 20, 30), width=7)
    if lt < e:
        for s in (-1, 1):
            hx = 400 + s * 60
            d.line((hx + s * 40, 950, hx, 1180), fill=COAT, width=90)
            d.ellipse((hx - 50, 1150, hx + 50, 1230), fill=SKIN)
    # you and father side by side, profile, facing right to the gurney
    person_side(d, 160, 1500, 1000, 1, COAT, DARKHAIR, coatlen=0.62)
    person_side(d, 330, 1500, 960, 1, SWEATER, WHITEHAIR, coatlen=0.45, arms="down", pants=(60, 60, 66))
    d.line((300, 1500 - 960 + 200, 205, 1500 - 1000 + 200), fill=shade(SWEATER, 0.8), width=44)
    d.ellipse((180, 1500 - 1000 + 176, 230, 1500 - 1000 + 224), fill=SKIN)
    cx, cy, z = cam_path(lt, [(0, 420, 1450, 1.8), (e - 0.2, 420, 1420, 1.85), (e + 0.8, 300, 900, 1.6), (dur, 320, 880, 1.6),
                              (dur + 0.3, 700, 700, 1.9)])
    return camera(im, cx, cy, z)


def scene16(lt, dur):
    e = snap(B[15] + dur * 0.52) - B[15]
    im = lab_bg().copy()
    d = ImageDraw.Draw(im)
    s = sstep(e, e + 0.3, lt)
    light = sstep(e + 0.1, dur + 0.25, lt)
    x0, y0, x1, y1 = 560, 380, 1040, 840
    if s > 0:
        rng = np.random.default_rng(int(lt * 30))
        nz = (rng.random(((y1 - y0) // 4, (x1 - x0) // 4)) * 120 * s).astype(np.uint8)
        nim = Image.fromarray(nz).resize((x1 - x0, y1 - y0), Image.NEAREST).convert("RGB")
        im.paste(nim, (x0 + int(rng.integers(-4, 5) * s), y0 + int(rng.integers(-4, 5) * s)))
    if light > 0:
        cx, cy = 800, 610
        rr = lerp(10, 900, light ** 1.4)
        glow(im, cx, cy, rr, (255, 255, 250), 1.6 * min(1, light * 2), power=1.2)
    rim = lerpc((40, 70, 100), (255, 255, 250), light)
    # five figures from behind looking at the screen
    rows = [(330, COAT, DARKHAIR, None, "short"), (500, SWEATER, WHITEHAIR, None, "short"), (680, WORK, DARKHAIR, None, "short"),
            (850, GREEN, BROWNHAIR, None, "bob"), (1010, (40, 38, 36), DARKHAIR, MUSTARD, "fade")]
    for (x, c, hcol, hood, hs) in rows:
        bust_back(d, x, 1350, 220, c, hcol, hood=hood, rim=rim, hairshape=hs)
    cx, cy, z = cam_path(lt, [(0, 680, 1000, 1.05), (dur, 760, 800, 1.35)])
    out = camera(im, cx, cy, z)
    wk = sstep(dur - 0.35, dur + 0.15, lt)
    if wk > 0:
        out = blend(out, Image.new("RGB", (W, H), (250, 250, 246)), wk)
    return out


def title_card(img, a):
    if a <= 0:
        return
    big = font(FONT_B, 86)
    small = font(FONT_R, 44)
    layer = Image.new("L", (W, 420), 0)
    ld = ImageDraw.Draw(layer)
    t1 = "THE DISCOVERY"
    t2 = "The Discovery · 2017"
    w1 = ld.textlength(t1, font=big)
    w2 = ld.textlength(t2, font=small)
    ld.text(((W - w1) / 2, 80), t1, font=big, fill=255)
    ld.text(((W - w2) / 2, 220), t2, font=small, fill=255)
    sh = layer.filter(ImageFilter.GaussianBlur(10))
    y = 170
    band = Image.new("L", (W, 520), 0)
    ImageDraw.Draw(band).rounded_rectangle((60, 120, W - 60, 380), radius=60, fill=200)
    band = band.filter(ImageFilter.GaussianBlur(50))
    img.paste((10, 8, 10), (0, y - 60), band.point(lambda v: int(v * a)))
    img.paste((0, 0, 0), (0, y), sh.point(lambda v: int(v * 0.8 * a)))
    img.paste((246, 240, 226), (0, y), layer.point(lambda v: int(v * a)))
    ld2 = Image.new("L", (W, 420), 0)
    ImageDraw.Draw(ld2).rectangle(((W - 220) / 2, 300, (W + 220) / 2, 304), fill=255)
    img.paste(MUSTARD, (0, y), ld2.point(lambda v: int(v * a)))


def scene17(lt, dur):
    e1 = snap(B[16] + dur * 0.35) - B[16]
    e2 = snap(B[16] + dur * 0.71) - B[16]
    fl = 1.0
    if e1 < lt < e1 + 0.6:
        fl = 0.45 + 0.55 * abs(math.sin((lt - e1) * 18))
    bright = 1 - 0.5 * sstep(e2, dur, lt)
    im = cinema_world(lt, "white", beam=1.0, bright=bright, flicker=fl)
    _dust_cin.draw(im, lt + 20, beam_mask, fl * bright)
    sc = ((SCR[0] + SCR[2]) / 2, (SCR[1] + SCR[3]) / 2)
    cx, cy, z = cam_path(lt, [(0, sc[0], sc[1], 3.4), (1.6, 560, 1000, 1.08), (dur, 540, 960, 1.0)])
    out = camera(im, cx, cy, z)
    if bright < 1:
        out = Image.eval(out, lambda v: int(v * (0.55 + 0.45 * bright)))
    return out


SCENES = [scene1, scene2, scene3, scene4, scene5, scene6, scene7, scene8, scene9, scene10, scene11, scene12, scene13, scene14,
          scene15, scene16, scene17]

FOG = {  # tint, strength, scale
    0: ((70, 60, 60), 0.10), 1: ((60, 80, 100), 0.12), 2: ((150, 160, 160), 0.35), 3: ((120, 130, 140), 0.18),
    4: ((40, 60, 90), 0.10), 5: ((140, 150, 150), 0.15), 6: ((170, 178, 178), 0.42), 7: ((170, 178, 178), 0.25),
    8: ((150, 156, 156), 0.30), 9: ((120, 130, 130), 0.25), 10: ((100, 110, 112), 0.12), 11: ((50, 90, 120), 0.14),
    12: ((50, 90, 120), 0.10), 13: ((120, 160, 130), 0.15), 14: ((50, 90, 120), 0.12), 15: ((50, 90, 120), 0.10),
    16: ((70, 60, 60), 0.10),
}
