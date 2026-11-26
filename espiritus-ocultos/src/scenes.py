"""Espíritus ocultos: En compañía del miedo (2003) - 12 escenas procedurales (1080x1920)."""
import math, random, json
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from lib import *

_seg = json.load(open("segments.json"))
PS = [s["start"] for s in _seg]
END = round(_seg[-1]["end"] + 1.0, 3)
# escena i = frase i (12 frases, 12 escenas)
B = PS[:12] + [END]
TITLE_T = PS[10]

# ---------------------------------------------------------------- paleta
TAN = (184, 140, 108)
DKB = (50, 33, 24)          # castaño oscuro (doctora)
COATW = (226, 230, 228)
BLOUSE = (118, 122, 126)
PAT = (166, 170, 172)       # buzo gris claro
GRAYH = (178, 178, 176)
SUIT = (28, 36, 64)
TIE = (112, 26, 40)
PALE = (214, 220, 224)
GOWN = (222, 228, 230)
WETH = (8, 9, 12)
DBLOND = (142, 114, 68)
SHIRT = (150, 186, 214)
OLIVE = (92, 98, 52)
GUARD = (24, 32, 58)
FLUO = (200, 255, 220)
RAINC = (150, 172, 205)
FLAME = (255, 140, 40)
POLICEC = (22, 24, 30)

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


def pick(lt, cuts, shots, xf=0.3):
    """cuts: tiempos de corte internos (en la rejilla de 0,3 s)."""
    for k, c in enumerate(cuts):
        if lt < c - xf / 2:
            return shots[k](lt)
        if lt < c + xf / 2:
            return blend(shots[k](lt), shots[k + 1](lt), sstep(c - xf / 2, c + xf / 2, lt))
    return shots[-1](lt)


def subshots(lt, dur, shots, xf=0.3):
    n = len(shots)
    return pick(lt, [snap(dur * k / n) for k in range(1, n)], shots, xf)


def cuts_of(dur, n):
    return [0.0] + [snap(dur * k / n) for k in range(1, n)] + [dur]


def whip(a, b, u):
    """paneo rápido (giro de cámara) de la imagen a a la b, con desenfoque de movimiento."""
    if u <= 0:
        return a
    if u >= 1:
        return b
    strip = Image.new("RGB", (W * 2, H))
    strip.paste(a, (0, 0))
    strip.paste(b, (W, 0))
    off = int(sstep(0, 1, u) * W)
    im = strip.crop((off, 0, off + W, H))
    k = int(60 * math.sin(math.pi * u)) + 1
    if k > 2:
        im = im.resize((W // k, H), Image.BILINEAR).resize((W, H), Image.BILINEAR)
    return im


def rain(img, lt, n=260, slant=0.18, speed=1400, seed=1, col=RAINC, ln=40, box=None):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box or (0, 0, img.size[0], img.size[1])
    w, h = x1 - x0, y1 - y0
    rng = random.Random(seed)
    for i in range(n):
        sx, sy = rng.uniform(0, w), rng.uniform(0, h)
        sp = rng.uniform(0.7, 1.3)
        y = (sy + speed * sp * lt) % h
        x = (sx + slant * speed * sp * lt) % w
        l = ln * sp
        c = shade(col, rng.uniform(0.6, 1.0))
        d.line((x0 + x, y0 + y, x0 + x - slant * l, y0 + y - l), fill=c, width=2)


# ================================================================ figuras
def bun_side(d, hx, hy, r, f, col=DKB):
    d.ellipse((hx - f * r * 1.0 - r * 0.42, hy + r * 0.05, hx - f * r * 1.0 + r * 0.42, hy + r * 0.8), fill=col)
    d.ellipse((hx - f * r * 1.0 - r * 0.2, hy + r * 0.2, hx - f * r * 1.0 + r * 0.1, hy + r * 0.5), fill=shade(col, 1.4))


def eye_side(d, hx, hy, r, f, open_=1.0, col=(30, 26, 24)):
    ex = hx + f * r * 0.48
    if open_ > 0.5:
        d.ellipse((ex - r * 0.09, hy - r * 0.16, ex + r * 0.09, hy + r * 0.02), fill=col)
    else:
        d.line((ex - r * 0.12, hy - r * 0.05, ex + r * 0.12, hy - r * 0.02), fill=col, width=max(2, int(r * 0.06)))


def face_side(d, x, hy, r, f, hair, skin=TAN, eye=1.0, bun=False, smile=0.0, beard=None):
    head_profile(d, x, hy, r, f, hair, skin, "short", beard, smile, eye=False)
    eye_side(d, x, hy, r, f, eye)
    d.line((x + f * r * 0.3, hy - r * 0.32, x + f * r * 0.65, hy - r * 0.3), fill=shade(hair, 0.8), width=max(2, int(r * 0.07)))
    if bun:
        bun_side(d, x, hy, r, f, hair)


def person_front(d, x, yf, h, top, pants, hair, skin=TAN, coat=None, inner=None, tie=None, glasses=False,
                 hair_style="short", expr="neutral", arms="down", band=False, coatlen=0.36, legs=True,
                 look=0.0, talk=0.0, badge=False, hand_up=0.0):
    r = h * 0.068
    T = yf - h
    hy = T + r
    shy = T + h * 0.185
    hw = h * 0.12
    bot = T + h * (0.18 + coatlen)
    lw = h * 0.058
    if legs:
        for s in (-1, 1):
            lx = x + s * h * 0.045
            d.rectangle((lx - lw / 2, T + h * 0.48, lx + lw / 2, yf - h * 0.02), fill=pants)
            d.ellipse((lx - lw * 0.75, yf - h * 0.035, lx + lw * 0.75, yf + h * 0.005), fill=(20, 20, 22))
    aw = h * 0.052
    acol = shade(coat or top, 0.9)
    for s in (-1, 1):
        ax = x + s * (hw + aw * 0.35)
        if s > 0 and hand_up > 0:   # gesto: mano levantada (saludo)
            ex, ey = ax + aw * 0.4, shy + h * 0.17
            hxp, hyp = lerp(ax, ax + aw * 0.6, hand_up), lerp(T + h * 0.5, shy - h * 0.06, hand_up)
            d.line((ax, shy + h * 0.03, ex, ey), fill=acol, width=int(aw))
            d.line((ex, ey, hxp, hyp + aw * 0.4), fill=acol, width=int(aw))
            d.ellipse((hxp - aw * 0.55, hyp - aw * 0.4, hxp + aw * 0.55, hyp + aw * 0.6), fill=skin)
            continue
        if arms == "table":
            d.rounded_rectangle((ax - aw / 2, shy + h * 0.01, ax + aw / 2, T + h * 0.4), radius=int(aw * 0.4), fill=acol)
            continue
        d.rounded_rectangle((ax - aw / 2, shy + h * 0.01, ax + aw / 2, T + h * 0.51), radius=int(aw * 0.4), fill=acol)
        d.ellipse((ax - aw * 0.55, T + h * 0.49, ax + aw * 0.55, T + h * 0.57), fill=skin)
        if band and s < 0:
            d.rectangle((ax - aw * 0.55, T + h * 0.475, ax + aw * 0.55, T + h * 0.495), fill=(246, 246, 244))
    d.rounded_rectangle((x - hw, shy, x + hw, bot), radius=int(h * 0.04), fill=top)
    if inner:
        d.polygon([(x - hw * 0.35, shy), (x + hw * 0.35, shy), (x, shy + h * 0.2)], fill=inner)
    if tie:
        d.polygon([(x - hw * 0.12, shy + h * 0.01), (x + hw * 0.12, shy + h * 0.01), (x + hw * 0.16, shy + h * 0.2),
                   (x, shy + h * 0.24), (x - hw * 0.16, shy + h * 0.2)], fill=tie)
        d.polygon([(x - hw * 0.35, shy), (x, shy + h * 0.1), (x + hw * 0.35, shy)], fill=(230, 232, 236))
        d.polygon([(x - hw * 0.12, shy + h * 0.005), (x + hw * 0.12, shy + h * 0.005), (x, shy + h * 0.04)], fill=tie)
    if coat:
        cb = T + h * 0.74
        for s in (-1, 1):
            d.polygon([(x + s * hw * 1.06, shy + 2), (x + s * hw * 0.38, shy), (x + s * hw * 0.3, cb), (x + s * hw * 1.18, cb)],
                      fill=coat)
            d.line((x + s * hw * 0.38, shy, x + s * hw * 0.62, shy + h * 0.12), fill=shade(coat, 0.82), width=max(2, int(h * 0.006)))
        if badge:
            d.rectangle((x - hw * 0.85, shy + h * 0.07, x - hw * 0.5, shy + h * 0.115), fill=(240, 244, 248))
            d.rectangle((x - hw * 0.85, shy + h * 0.07, x - hw * 0.5, shy + h * 0.08), fill=(60, 90, 140))
    if arms == "table":
        for s in (-1, 1):
            ax = x + s * (hw + aw * 0.35)
            hxp, hyp = x + s * hw * 0.45, T + h * 0.47
            d.line((ax, T + h * 0.38, hxp, hyp), fill=shade(acol, 0.92), width=int(aw * 1.1))
            d.ellipse((hxp - aw * 0.75, hyp - aw * 0.5, hxp + aw * 0.75, hyp + aw * 0.45), fill=skin)
            if band and s < 0:
                d.rectangle((hxp + aw * 0.45, hyp - aw * 0.5, hxp + aw * 0.9, hyp + aw * 0.45), fill=(246, 246, 244))
    # cabeza
    d.rectangle((x - r * 0.42, hy + r * 0.5, x + r * 0.42, shy + 2), fill=shade(skin, 0.82))
    d.ellipse((x - r * 1.0, hy - r * 0.1, x - r * 0.72, hy + r * 0.35), fill=shade(skin, 0.9))
    d.ellipse((x + r * 0.72, hy - r * 0.1, x + r * 1.0, hy + r * 0.35), fill=shade(skin, 0.9))
    d.ellipse((x - r * 0.84, hy - r, x + r * 0.84, hy + r * 1.05), fill=skin)
    if hair_style == "bun":
        d.chord((x - r * 0.9, hy - r * 1.1, x + r * 0.9, hy + r * 0.5), 180, 360, fill=hair)
        d.polygon([(x - r * 0.9, hy - r * 0.3), (x - r * 0.25, hy - r * 0.85), (x - r * 0.78, hy + r * 0.15)], fill=hair)
        d.polygon([(x + r * 0.9, hy - r * 0.3), (x + r * 0.25, hy - r * 0.85), (x + r * 0.78, hy + r * 0.15)], fill=hair)
        d.ellipse((x + r * 0.62, hy + r * 0.35, x + r * 1.05, hy + r * 0.8), fill=shade(hair, 0.85))
    elif hair_style == "slick":
        d.chord((x - r * 0.9, hy - r * 1.15, x + r * 0.9, hy + r * 0.3), 180, 360, fill=hair)
        d.rectangle((x - r * 0.9, hy - r * 0.45, x - r * 0.76, hy + r * 0.1), fill=hair)
        d.rectangle((x + r * 0.76, hy - r * 0.45, x + r * 0.9, hy + r * 0.1), fill=hair)
        for k in range(3):
            d.line((x - r * 0.4 + k * r * 0.35, hy - r * 0.55, x - r * 0.3 + k * r * 0.35, hy - r * 1.0),
                   fill=shade(hair, 1.25), width=max(1, int(r * 0.05)))
    elif hair_style == "long":
        d.chord((x - r * 0.92, hy - r * 1.1, x + r * 0.92, hy + r * 0.4), 180, 360, fill=hair)
        d.rectangle((x - r * 1.0, hy - r * 0.4, x - r * 0.7, hy + r * 1.9), fill=hair)
        d.rectangle((x + r * 0.7, hy - r * 0.4, x + r * 1.0, hy + r * 1.9), fill=hair)
    elif hair_style == "curly":
        for k in range(9):
            a = math.pi * (1 + k / 8)
            d.ellipse((x + math.cos(a) * r * 0.8 - r * 0.32, hy - r * 0.1 + math.sin(a) * r * 0.9 - r * 0.32,
                       x + math.cos(a) * r * 0.8 + r * 0.32, hy - r * 0.1 + math.sin(a) * r * 0.9 + r * 0.32), fill=hair)
    else:
        d.chord((x - r * 0.9, hy - r * 1.1, x + r * 0.9, hy + r * 0.4), 180, 360, fill=hair)
    # rasgos
    ey = hy + r * 0.08
    ec = (34, 28, 24)
    for s in (-1, 1):
        ex = x + s * r * 0.36
        if expr == "closed":
            d.arc((ex - r * 0.16, ey - r * 0.1, ex + r * 0.16, ey + r * 0.1), 10, 170, fill=ec, width=max(2, int(r * 0.06)))
        else:
            d.ellipse((ex - r * 0.17, ey - r * 0.09, ex + r * 0.17, ey + r * 0.09), fill=(236, 232, 226))
            ix = ex + look * r * 0.08
            d.ellipse((ix - r * 0.075, ey - r * 0.075, ix + r * 0.075, ey + r * 0.075), fill=ec)
        by = hy - r * 0.18
        if expr == "confused":
            inner = by - r * (0.12 if s < 0 else 0.02)
            outer = by + r * 0.02
        elif expr == "determined":
            inner, outer = by + r * 0.06, by - r * 0.04
        elif expr == "warm":
            inner, outer = by - r * 0.02, by + r * 0.02
        else:
            inner, outer = by, by
        d.line((x + s * r * 0.15, inner, x + s * r * 0.55, outer), fill=shade(hair, 0.7), width=max(2, int(r * 0.08)))
    d.line((x, hy + r * 0.12, x - r * 0.08, hy + r * 0.42), fill=shade(skin, 0.75), width=max(1, int(r * 0.05)))
    d.line((x - r * 0.08, hy + r * 0.42, x + r * 0.06, hy + r * 0.44), fill=shade(skin, 0.75), width=max(1, int(r * 0.05)))
    my = hy + r * 0.66
    if expr in ("smile", "warm"):
        d.arc((x - r * 0.3, my - r * 0.18, x + r * 0.3, my + r * 0.12), 20, 160, fill=(120, 60, 54), width=max(2, int(r * 0.07)))
    elif expr == "confused" or talk > 0:
        o = 0.06 + 0.1 * talk
        d.ellipse((x - r * 0.12, my - r * o, x + r * 0.12, my + r * o), fill=(90, 44, 40))
    else:
        d.line((x - r * 0.22, my, x + r * 0.22, my), fill=(120, 64, 58), width=max(2, int(r * 0.06)))
    if glasses:
        for s in (-1, 1):
            ex = x + s * r * 0.36
            d.ellipse((ex - r * 0.25, ey - r * 0.2, ex + r * 0.25, ey + r * 0.2), outline=(40, 40, 44), width=max(2, int(r * 0.05)))
        d.line((x - r * 0.11, ey, x + r * 0.11, ey), fill=(40, 40, 44), width=max(2, int(r * 0.05)))
    return x, hy, r


def doc_front(d, x, yf, h, mode="doc", **k):
    if mode == "doc":
        return person_front(d, x, yf, h, BLOUSE, (50, 52, 58), DKB, TAN, coat=COATW, hair_style="bun", badge=True, **k)
    return person_front(d, x, yf, h, PAT, PAT, DKB, TAN, hair_style="bun", band=True, coatlen=0.34, **k)


def doc_side(d, x, yf, h, f, mode="doc", arms="down", step=0.0, eye=1.0, smile=0.0, file=False):
    if mode == "doc":
        hx, hy, r = person_side(d, x, yf, h, f, COATW, DKB, TAN, coatlen=0.5, arms=arms, step=step,
                                pants=(50, 52, 58), smile=smile)
        top = yf - h
        d.rectangle((x + f * h * 0.02, top + h * 0.25, x + f * h * 0.05, top + h * 0.29), fill=(60, 90, 140))
    else:
        hx, hy, r = person_side(d, x, yf, h, f, PAT, DKB, TAN, coatlen=0.34, arms=arms, step=step,
                                pants=PAT, smile=smile)
    face_side(d, hx, hy, r, f, DKB, TAN, eye=eye, bun=True, smile=smile)
    top = yf - h
    if mode != "doc":  # pulsera
        if arms == "down":
            px, py = x + f * h * 0.02, top + h * 0.48
        elif arms == "forward":
            px, py = x + f * h * 0.15, top + h * 0.41
        else:
            px, py = None, None
        if px is not None:
            d.rectangle((px - h * 0.025, py - h * 0.012, px + h * 0.025, py + h * 0.012), fill=(248, 248, 246))
    if file and arms == "forward":
        fx, fy = x + f * h * 0.17, top + h * 0.42
        d.polygon([(fx - h * 0.07, fy - h * 0.06), (fx + h * 0.07, fy - h * 0.1), (fx + h * 0.08, fy - h * 0.01), (fx - h * 0.06, fy + h * 0.03)],
                  fill=(214, 190, 130))
    return hx, hy, r


def doc_back(d, x, yf, h, mode="doc", step=0.0):
    if mode == "doc":
        hd = person_back(d, x, yf, h, COATW, DKB, TAN, coatlen=0.5, step=step, pants=(50, 52, 58))
    else:
        hd = person_back(d, x, yf, h, PAT, DKB, TAN, coatlen=0.34, step=step, pants=PAT)
    hx, hy, r = hd
    d.ellipse((hx - r * 0.45, hy + r * 0.35, hx + r * 0.45, hy + r * 1.05), fill=shade(DKB, 0.85))
    return hd


def spect_back(d, x, yf, h):
    return person_back(d, x, yf, h, (40, 38, 36), DARKHAIR, hood=MUSTARD, hairshape="fade", coatlen=0.4)


def guard_side(d, x, yf, h, f, arms="down", step=0.0, female=False, hair=DARKHAIR):
    hx, hy, r = person_side(d, x, yf, h, f, GUARD, hair, SKIN, coatlen=0.34, arms=arms, step=step, pants=shade(GUARD, 0.8))
    if female:
        bun_side(d, hx, hy, r, f, hair)
    top = yf - h
    d.line((x - h * 0.07, top + h * 0.5, x + h * 0.07, top + h * 0.5), fill=(14, 16, 20), width=max(2, int(h * 0.02)))
    return hx, hy, r


def husband_front(d, x, yf, h, **k):
    return person_front(d, x, yf, h, SUIT, SUIT, GRAYH, SKIN, tie=TIE, glasses=True, coatlen=0.4, **k)


def colleague_front(d, x, yf, h, **k):
    return person_front(d, x, yf, h, OLIVE, (46, 48, 56), DBLOND, SKIN, coat=COATW, inner=SHIRT, hair_style="slick", **k)


def colleague_side(d, x, yf, h, f, arms="down", step=0.0):
    hx, hy, r = person_side(d, x, yf, h, f, COATW, DBLOND, SKIN, coatlen=0.5, arms=arms, step=step, pants=(46, 48, 56))
    top = yf - h
    d.polygon([(x + f * h * 0.04, top + h * 0.19), (x + f * h * 0.075, top + h * 0.2), (x + f * h * 0.08, top + h * 0.45),
               (x + f * h * 0.05, top + h * 0.45)], fill=OLIVE)
    return hx, hy, r


def girl_sprite(h, view="front", hand=0.0):
    """joven de la carretera: RGBA, pies en el borde inferior, centro horizontal."""
    key = ("girl", int(h), view, round(hand, 2))
    if key in _cache:
        return _cache[key]
    w = int(h * 0.62)
    im = Image.new("RGBA", (w, int(h) + 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x = w / 2
    yf = h
    r = h * 0.066
    T = yf - h
    hy = T + r
    shy = T + h * 0.185
    hw = h * 0.105
    gb = yf - h * 0.07
    # pelo largo por detrás
    d.polygon([(x - r * 1.0, hy - r * 0.2), (x + r * 1.0, hy - r * 0.2), (x + r * 1.3, shy + h * 0.24), (x - r * 1.3, shy + h * 0.24)], fill=WETH)
    # brazos
    aw = h * 0.042
    for s in (-1, 1):
        ax = x + s * (hw + aw * 0.3)
        if s > 0 and hand > 0:
            continue
        d.rounded_rectangle((ax - aw / 2, shy + h * 0.02, ax + aw / 2, T + h * 0.53), radius=int(aw * 0.4), fill=shade(PALE, 0.92))
        d.ellipse((ax - aw * 0.55, T + h * 0.51, ax + aw * 0.55, T + h * 0.58), fill=PALE)
    # camisón
    d.polygon([(x - hw, shy), (x + hw, shy), (x + hw * 1.5, gb), (x - hw * 1.5, gb)], fill=GOWN)
    for k in (-0.8, -0.3, 0.25, 0.7):
        d.line((x + k * hw * 0.6, shy + h * 0.15, x + k * hw * 1.3, gb), fill=shade(GOWN, 0.82), width=max(1, int(h * 0.006)))
    for k, (px, py) in enumerate([(-0.4, 0.45), (0.5, 0.62), (-0.2, 0.8), (0.3, 0.32)]):
        cx, cy = x + px * hw, T + py * h
        d.ellipse((cx - hw * 0.25, cy - h * 0.07, cx + hw * 0.25, cy + h * 0.07), fill=(208, 216, 220))
    d.chord((x - hw * 0.5, shy - h * 0.02, x + hw * 0.5, shy + h * 0.04), 0, 180, fill=shade(GOWN, 0.9))
    # pies descalzos
    for s in (-1, 1):
        fx = x + s * h * 0.035
        d.rectangle((fx - h * 0.018, gb, fx + h * 0.018, yf - h * 0.015), fill=shade(PALE, 0.9))
        d.ellipse((fx - h * 0.03, yf - h * 0.025, fx + h * 0.03, yf + h * 0.003), fill=PALE)
    # cabeza
    d.rectangle((x - r * 0.38, hy + r * 0.5, x + r * 0.38, shy + 2), fill=shade(PALE, 0.85))
    if view == "front":
        d.ellipse((x - r * 0.8, hy - r, x + r * 0.8, hy + r * 1.05), fill=PALE)
        d.ellipse((x + r * 0.18, hy - r * 0.02, x + r * 0.5, hy + r * 0.18), fill=(150, 158, 166))
        d.ellipse((x + r * 0.28, hy + r * 0.04, x + r * 0.4, hy + r * 0.14), fill=(24, 24, 28))
        d.line((x - r * 0.05, hy + r * 0.66, x + r * 0.3, hy + r * 0.66), fill=(150, 150, 156), width=max(1, int(r * 0.05)))
        d.chord((x - r * 0.95, hy - r * 1.12, x + r * 0.95, hy + r * 0.3), 180, 360, fill=WETH)
        # mechones mojados sobre la cara
        d.polygon([(x - r * 0.95, hy - r * 0.5), (x + r * 0.15, hy - r * 0.6), (x + r * 0.05, hy + r * 1.4), (x - r * 0.35, shy + h * 0.14),
                   (x - r * 1.2, shy + h * 0.16)], fill=WETH)
        d.polygon([(x + r * 0.55, hy - r * 0.6), (x + r * 0.95, hy - r * 0.4), (x + r * 1.2, shy + h * 0.15), (x + r * 0.7, shy + h * 0.12),
                   (x + r * 0.6, hy + r * 0.4)], fill=WETH)
        d.line((x + r * 0.15, hy - r * 0.6, x + r * 0.25, hy + r * 1.2), fill=WETH, width=max(1, int(r * 0.1)))
    else:
        d.ellipse((x - r * 0.95, hy - r * 1.1, x + r * 0.95, hy + r * 1.0), fill=WETH)
        d.polygon([(x - r * 1.0, hy), (x + r * 1.0, hy), (x + r * 1.25, shy + h * 0.25), (x - r * 1.25, shy + h * 0.25)], fill=WETH)
    if hand > 0:
        ax = x + hw + aw * 0.3
        ex, ey = lerp(ax, x + hw * 0.5, hand), lerp(T + h * 0.5, shy + h * 0.1, hand)
        d.line((ax, shy + h * 0.03, ex, ey), fill=shade(PALE, 0.9), width=int(aw * (1 + 0.6 * hand)))
        rr = aw * (0.6 + 0.9 * hand)
        d.ellipse((ex - rr, ey - rr * 1.1, ex + rr, ey + rr * 0.9), fill=PALE)
        d.arc((ex - rr * 0.8, ey - rr * 0.6, ex + rr * 0.8, ey + rr * 0.7), 200, 340, fill=shade(PALE, 0.75), width=max(1, int(rr * 0.12)))
    _cache[key] = im
    return im


def put_girl(img, x, yf, h, view="front", hand=0.0, lt=0.0, drips=True, puddle=0.0, alpha=1.0):
    sp = girl_sprite(h, view, hand)
    x0, y0 = int(x - sp.size[0] / 2), int(yf - h)
    if puddle > 0:
        ell_a(img, (x - h * 0.22 * puddle, yf - h * 0.02, x + h * 0.22 * puddle, yf + h * 0.035), (70, 92, 110), 0.85)
        ell_a(img, (x - h * 0.15 * puddle, yf - h * 0.01, x + h * 0.08 * puddle, yf + h * 0.02), (150, 180, 196), 0.5)
    if alpha >= 1:
        img.paste(sp, (x0, y0), sp)
    else:
        m = sp.split()[3].point(lambda v: int(v * alpha))
        img.paste(sp.convert("RGB"), (x0, y0), m)
    if drips:
        d = ImageDraw.Draw(img)
        rng = random.Random(int(h))
        for i in range(7):
            dx = rng.uniform(-0.16, 0.16) * h
            start = yf - h * rng.choice([0.07, 0.07, 0.62])
            ph = (lt * 1.6 + rng.random()) % 1
            yy = start + ph * h * 0.09
            d.line((x + dx, yy, x + dx, yy + h * 0.012), fill=(170, 200, 220), width=max(1, int(h * 0.004)))


def girl_silhouette(img, x, yf, h, col, alpha=1.0, view="front", hand=0.0):
    sp = girl_sprite(h, view, hand)
    m = sp.split()[3]
    if alpha < 1:
        m = m.point(lambda v: int(v * alpha))
    img.paste(col, (int(x - sp.size[0] / 2), int(yf - h)), m)


def seated(d, x, ys, h, f, top, hair, skin=TAN, pants=(50, 52, 58), coat=None, bun=False, band=False,
           arms="table", chair=(34, 36, 40), eye=1.0, write=0.0, talk=0.0, hair_side=None):
    r = h * 0.068
    if chair:
        d.rectangle((x - f * h * 0.11, ys - h * 0.33, x - f * h * 0.08, ys + h * 0.02), fill=chair)
        d.rectangle((x - f * h * 0.11, ys, x + f * h * 0.14, ys + h * 0.025), fill=chair)
        d.line((x - f * h * 0.09, ys, x - f * h * 0.09, ys + h * 0.27), fill=chair, width=int(h * 0.015))
        d.line((x + f * h * 0.12, ys, x + f * h * 0.12, ys + h * 0.27), fill=chair, width=int(h * 0.015))
    lw = int(h * 0.06)
    d.line((x, ys - lw * 0.3, x + f * h * 0.22, ys - lw * 0.3), fill=pants, width=lw)
    d.line((x + f * h * 0.22, ys - lw * 0.3, x + f * h * 0.24, ys + h * 0.25), fill=pants, width=lw)
    d.ellipse((x + f * h * 0.24 - lw * 0.4, ys + h * 0.245, x + f * h * 0.24 + lw * 0.4 + f * lw, ys + h * 0.275), fill=(20, 20, 22))
    shy = ys - h * 0.32
    dep = h * 0.08
    if coat:
        d.rounded_rectangle((x - dep * 1.1, shy, x + dep * 1.1, ys + h * 0.05), radius=int(h * 0.03), fill=coat)
        d.polygon([(x + f * dep * 0.6, shy + h * 0.02), (x + f * dep * 1.0, shy + h * 0.02), (x + f * dep * 1.0, ys - h * 0.05),
                   (x + f * dep * 0.7, ys - h * 0.05)], fill=top)
    else:
        d.rounded_rectangle((x - dep, shy, x + dep, ys), radius=int(h * 0.03), fill=top)
    hy = shy - r * 1.4
    d.rectangle((x - r * 0.4, hy + r * 0.5, x + r * 0.4, shy + 2), fill=shade(skin, 0.82))
    face_side(d, x + f * r * 0.15, hy, r, f, hair_side or hair, skin, eye=eye, bun=bun)
    if talk > 0:
        mx, my = x + f * r * 0.15 + f * r * 0.78, hy + r * 0.62
        d.ellipse((mx - r * 0.1, my - r * 0.05 * talk, mx + r * 0.02, my + r * 0.08 * talk), fill=(90, 44, 40))
    aw = int(h * 0.048)
    acol = shade(coat or top, 0.82)
    if arms == "table":
        ex, ey = x + f * h * 0.05, ys - h * 0.14
        hx_, hy_ = x + f * (h * 0.22 + write * h * 0.03), ys - h * 0.19 - write * h * 0.005
        d.line((x + f * dep * 0.2, shy + h * 0.03, ex, ey), fill=acol, width=aw)
        d.line((ex, ey, hx_, hy_), fill=acol, width=aw)
        d.ellipse((hx_ - aw * 0.55, hy_ - aw * 0.45, hx_ + aw * 0.6, hy_ + aw * 0.45), fill=skin)
        if band:
            d.rectangle((hx_ - f * aw * 0.9 - aw * 0.25, hy_ - aw * 0.45, hx_ - f * aw * 0.9 + aw * 0.25, hy_ + aw * 0.45), fill=(248, 248, 246))
        if write:
            d.line((hx_, hy_, hx_ + f * aw * 0.6, hy_ - aw * 1.2), fill=(20, 20, 30), width=max(2, aw // 5))
    elif arms == "lap":
        d.line((x + f * dep * 0.2, shy + h * 0.03, x + f * h * 0.06, ys - h * 0.12), fill=acol, width=aw)
        d.line((x + f * h * 0.06, ys - h * 0.12, x + f * h * 0.17, ys - h * 0.06), fill=acol, width=aw)
        d.ellipse((x + f * h * 0.17 - aw * 0.5, ys - h * 0.09, x + f * h * 0.17 + aw * 0.6, ys - h * 0.03), fill=skin)
        if band:
            d.rectangle((x + f * h * 0.14 - aw * 0.25, ys - h * 0.1, x + f * h * 0.14 + aw * 0.25, ys - h * 0.05), fill=(248, 248, 246))
    return x + f * r * 0.15, hy, r


# ================================================================ cine
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
    rim = (150, 190, 180)
    for i in range(5):
        x = 108 + i * 216
        if i == 2:
            bust_back(d, x, 1500, 173, (36, 34, 34), DARKHAIR, hood=MUSTARD, hairshape="fade", rim=rim)
            seat_back(d, x - 120, 1540, 60, shade(CRIMSON, 0.7))
        else:
            seat_back(d, x, 1470, 196, shade(CRIMSON, 0.75))
    for i in range(5):
        seat_back(d, 108 + i * 216 + 10, 1700, 206, shade(CRIMSON, 0.95))
    if dim < 1:
        im = Image.eval(im, lambda v: int(v * dim))
    return im


# ================================================================ celda acolchada (400 px/m, suelo 1500)
DOOR = (640, 700, 960, 1500)
WIN = (740, 790, 860, 910)


def cell_bg(night=False):
    key = ("cell", night)
    if key in _cache:
        return _cache[key]
    k = 0.42 if night else 1.0
    base = (214, 222, 214) if not night else (96, 118, 120)
    im = vgrad(W, H, [(0, shade(base, 0.55)), (0.14, shade(base, 0.8)), (0.78, base), (1, shade(base, 0.7))])
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, 250), fill=shade(base, 0.5))
    # acolchado
    for row in range(16):
        for col in range(10):
            x0, y0 = -40 + col * 120 + (60 if row % 2 else 0), 260 + row * 78
            if y0 > 1480:
                continue
            d.rounded_rectangle((x0 + 4, y0 + 4, x0 + 116, y0 + 74), radius=22, fill=shade(base, 1.04))
            d.ellipse((x0 + 54, y0 - 4, x0 + 66, y0 + 8), fill=shade(base, 0.7))
    d.rectangle((0, 1500, W, H), fill=shade(base, 0.78))
    d.line((0, 1500, W, 1500), fill=shade(base, 0.6), width=6)
    # puerta
    x0, y0, x1, y1 = DOOR
    d.rectangle((x0 - 14, y0 - 14, x1 + 14, y1), fill=shade(base, 0.55))
    d.rectangle(DOOR, fill=(150, 160, 160) if not night else (60, 72, 76))
    d.rectangle((x0 + 20, y0 + 20, x1 - 20, y1 - 20), outline=shade((150, 160, 160) if not night else (60, 72, 76), 0.8), width=6)
    d.rectangle((x1 - 50, 1080, x1 - 30, 1160), fill=(90, 96, 100))
    # catre (0,45 m)
    d.rectangle((60, 1320, 600, 1345), fill=(110, 116, 118) if not night else (50, 58, 62))
    for lx in (75, 580):
        d.rectangle((lx - 8, 1345, lx + 8, 1500), fill=(100, 106, 108) if not night else (44, 50, 54))
    d.rounded_rectangle((70, 1288, 595, 1325), radius=12, fill=(232, 236, 232) if not night else (110, 126, 130))
    d.rounded_rectangle((80, 1262, 210, 1292), radius=14, fill=(244, 246, 244) if not night else (120, 136, 140))
    # tubo fluorescente
    d.rectangle((300, 226, 780, 252), fill=(60, 66, 66))
    _cache[key] = im
    return im


def cell_world(lt, night=False, tube=1.0, door_open=0.0, girl=None, window_fog=0.0, win_girl=0.0):
    im = cell_bg(night).copy()
    d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = WIN
    if door_open > 0:
        # pasillo detrás de la puerta (luz fría a contraluz)
        dx0, dy0, dx1, dy1 = DOOR
        d.rectangle(DOOR, fill=(150, 190, 176) if night else (190, 220, 206))
        glow(im, (dx0 + dx1) / 2, 1100, 380, (60, 110, 90), 0.6 * door_open)
        if girl:
            put_girl(im, girl[0], girl[1], girl[2], hand=girl[3] if len(girl) > 3 else 0.0, lt=lt, puddle=0.8)
        wleaf = (dx1 - dx0) * (1 - 0.85 * door_open)
        col = (60, 72, 76) if night else (150, 160, 160)
        d.polygon([(dx1, dy0), (dx1 - wleaf, dy0 - 30 * door_open), (dx1 - wleaf, dy1 + 30 * door_open), (dx1, dy1)], fill=col)
        d.polygon([(dx1, dy0), (dx1 - wleaf, dy0 - 30 * door_open), (dx1 - wleaf, dy1 + 30 * door_open), (dx1, dy1)],
                  outline=shade(col, 0.7), width=5)
    else:
        d.rectangle(WIN, fill=(70, 110, 96) if not night else (22, 44, 40))
        if win_girl > 0:
            girl_silhouette(im, 805, 1060, 330, (6, 10, 12), alpha=win_girl)
            d = ImageDraw.Draw(im)
        if window_fog > 0:
            rect_a(im, WIN, (214, 224, 222), 0.85 * window_fog)
        d.rectangle(WIN, outline=(60, 64, 66), width=8)
        d.line(((x0 + x1) / 2, y0, (x0 + x1) / 2, y1), fill=(60, 64, 66), width=3)
    if tube > 0:
        d.rectangle((310, 232, 770, 246), fill=lerpc((90, 100, 96), (236, 255, 244), tube))
        glow(im, 540, 260, 520, (60, 110, 80) if not night else (30, 70, 60), 0.55 * tube)
    return im


def lying(d, hx=140, eye=0.0, mode="patient"):
    """mujer acostada en el catre (cabeza a la izquierda, mirando hacia arriba)."""
    col = PAT if mode == "patient" else BLOUSE
    d.rounded_rectangle((180, 1228, 470, 1292), radius=30, fill=col)
    d.rounded_rectangle((440, 1240, 590, 1290), radius=22, fill=PAT)
    d.ellipse((568, 1236, 598, 1288), fill=(24, 24, 26))
    r = 44
    hy = 1236
    d.ellipse((hx - r, hy - r, hx + r, hy + r), fill=TAN)
    d.chord((hx - r * 1.05, hy - r * 1.05, hx + r * 1.05, hy + r * 1.05), 90, 270, fill=DKB)
    d.ellipse((hx - r * 1.45, hy - r * 0.35, hx - r * 0.75, hy + r * 0.35), fill=DKB)
    d.polygon([(hx - r * 0.2, hy - r * 0.85), (hx + r * 0.25, hy - r * 1.18), (hx + r * 0.3, hy - r * 0.8)], fill=TAN)
    ex, ey = hx + r * 0.1, hy - r * 0.45
    if eye > 0.5:
        d.ellipse((ex - 6, ey - 7, ex + 6, ey + 5), fill=(30, 26, 24))
    else:
        d.line((ex - 9, ey, ex + 9, ey), fill=(30, 26, 24), width=3)
    # brazo con pulsera sobre el cuerpo
    d.line((230, 1240, 330, 1236), fill=shade(col, 0.85), width=26)
    d.ellipse((326, 1222, 356, 1250), fill=TAN)
    d.rectangle((308, 1224, 322, 1250), fill=(248, 248, 246))


def sitting_up(img, u, look=1, eye=1.0):
    """incorporarse en el catre: u=0 acostada, u=1 sentada; piernas sobre el catre."""
    d = ImageDraw.Draw(img)
    hip = (330, 1270)
    d.rounded_rectangle((300, 1240, 590, 1292), radius=22, fill=PAT)
    d.ellipse((568, 1236, 598, 1288), fill=(24, 24, 26))
    lay = Image.new("RGBA", (700, 700), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    px, py = 350, 600
    h = 660
    r = h * 0.068
    ld.rounded_rectangle((px - 56, py - 210, px + 56, py + 20), radius=30, fill=PAT)
    hy = py - 210 - r * 1.3
    ld.rectangle((px - r * 0.4, hy + r * 0.5, px + r * 0.4, py - 205), fill=shade(TAN, 0.82))
    face_side(ld, px + look * r * 0.1, hy, r, look, DKB, TAN, eye=eye, bun=True)
    ld.line((px + 10, py - 180, px + 60, py - 60), fill=shade(PAT, 0.85), width=30)
    ld.line((px + 60, py - 60, px + 130, py - 20), fill=shade(PAT, 0.85), width=30)
    ld.ellipse((px + 120, py - 38, px + 160, py - 4), fill=TAN)
    ld.rectangle((px + 104, py - 40, px + 120, py - 4), fill=(248, 248, 246))
    ang = 90 * (1 - u)
    lay = lay.rotate(ang, resample=Image.BICUBIC, center=(px, py))
    img.paste(lay, (hip[0] - px, hip[1] - py), lay)


# ================================================================ pasillo del hospital (330 px/m, suelo 1500)
CW = 2700


def corridor_bg(night=False):
    key = ("cor", night)
    if key in _cache:
        return _cache[key]
    wall = (150, 170, 158) if not night else (40, 58, 54)
    im = vgrad(CW, H, [(0, shade(wall, 0.4)), (0.3, shade(wall, 0.7)), (0.32, wall), (0.78, shade(wall, 0.9)), (1, shade(wall, 0.5))])
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, CW, 610), fill=shade(wall, 0.45))
    d.rectangle((0, 1500, CW, H), fill=(92, 100, 96) if not night else (30, 38, 36))
    for x in range(0, CW, 160):
        d.line((x, 1500, x - 120, H), fill=shade((92, 100, 96), 0.85) if not night else (24, 30, 28), width=3)
    d.rectangle((0, 1290, CW, 1300), fill=shade(wall, 0.8))   # zócalo
    # puertas metálicas
    for x0 in (40, 2060):
        d.rectangle((x0, 840, x0 + 250, 1500), fill=(110, 120, 122) if not night else (44, 52, 54))
        d.rectangle((x0 + 85, 900, x0 + 165, 980), fill=(40, 60, 56))
        d.rectangle((x0 + 210, 1150, x0 + 228, 1220), fill=(70, 74, 76))
    # puerta de madera (oficina del director)
    d.rectangle((750, 826, 1020, 1500), fill=(70, 44, 26))
    d.rectangle((760, 840, 1010, 1500), fill=(120, 76, 44) if not night else (60, 40, 26))
    for (a, b) in ((870, 1150), (1180, 1460)):
        d.rectangle((790, a, 980, b), outline=(96, 60, 34), width=8)
    d.ellipse((965, 1160, 990, 1185), fill=(200, 170, 90))
    d.rectangle((830, 780, 940, 806), fill=(176, 150, 90))   # placa sin texto
    # ventanal al patio
    x0, y0, x1, y1 = 1100, 880, 1520, 1250
    yard = vgrad(x1 - x0, y1 - y0, [(0, (176, 196, 196) if not night else (20, 30, 40)), (0.55, (150, 168, 170) if not night else (16, 24, 30)),
                                     (0.56, (120, 120, 112) if not night else (20, 22, 24)), (1, (104, 104, 98) if not night else (16, 18, 20))])
    yd = ImageDraw.Draw(yard)
    for i in range(0, x1 - x0, 24):
        yd.line((i, 150, i, 210), fill=(90, 96, 96), width=2)
    yd.line((0, 150, x1 - x0, 150), fill=(90, 96, 96), width=3)
    if not night:
        for k, xx in enumerate((60, 120, 210, 300, 360)):
            person_front(yd, xx, 330 - (k % 2) * 20, 120 - (k % 2) * 10, PAT, PAT, [DARKHAIR, BROWNHAIR, (60, 40, 30)][k % 3], SKIN if k % 2 else TAN,
                         hair_style=["long", "short", "curly"][k % 3])
    im.paste(yard, (x0, y0))
    d.rectangle((x0, y0, x1, y1), outline=(70, 76, 76), width=14)
    for xx in range(x0 + 60, x1, 60):
        d.line((xx, y0, xx, y1), fill=(80, 86, 86), width=6)
    # reloj
    d.ellipse((560, 700, 660, 800), fill=(236, 236, 230), outline=(40, 40, 40), width=6)
    for k in range(12):
        a = k * math.pi / 6
        d.line((610 + 40 * math.cos(a), 750 + 40 * math.sin(a), 610 + 46 * math.cos(a), 750 + 46 * math.sin(a)), fill=(40, 40, 40), width=3)
    # tubos de luz
    for x in range(200, CW, 520):
        d.rectangle((x, 600, x + 240, 616), fill=(220, 250, 230) if not night else (40, 60, 50))
    _cache[key] = im
    return im


GATE_X = 1680


def corridor_world(lt, night=False, gate_open=0.0, clock=True, lights=1.0):
    im = corridor_bg(night).copy()
    d = ImageDraw.Draw(im)
    if clock:
        a = lt * 0.5 - math.pi / 2
        d.line((610, 750, 610 + 38 * math.cos(a), 750 + 38 * math.sin(a)), fill=(150, 20, 20), width=2)
        d.line((610, 750, 610 + 26 * math.cos(-1.2), 750 + 26 * math.sin(-1.2)), fill=(30, 30, 30), width=5)
        d.line((610, 750, 610 + 34 * math.cos(0.7), 750 + 34 * math.sin(0.7)), fill=(30, 30, 30), width=4)
    if lights > 0 and not night:
        for x in range(200, CW, 520):
            glow(im, x + 120, 640, 300, (40, 80, 56), 0.5 * lights)
    # reja de seguridad (2,2 m) que se abre hacia la cámara
    gw = 260 * (1 - 0.8 * gate_open)
    gx0, gtop = GATE_X, 1500 - 726
    d.rectangle((gx0 - 16, gtop - 10, gx0, 1500), fill=(40, 44, 46))
    d.rectangle((gx0 + 260, gtop - 10, gx0 + 276, 1500), fill=(40, 44, 46))
    d.rectangle((gx0, gtop - 10, gx0 + 276, gtop), fill=(40, 44, 46))
    sk = 40 * gate_open
    d.polygon([(gx0, gtop), (gx0 + gw, gtop - sk), (gx0 + gw, 1500 + sk * 0.5), (gx0, 1500)], outline=(30, 32, 34), width=10)
    for k in range(1, 7):
        xx = gx0 + gw * k / 7
        d.line((xx, gtop - sk * k / 7, xx, 1500 + sk * 0.5 * k / 7), fill=(36, 38, 40), width=7)
    d.line((gx0, gtop + 360, gx0 + gw, gtop + 360 - sk * 0.3), fill=(36, 38, 40), width=10)
    return im


# ================================================================ sala de entrevistas (400 px/m, suelo 1500)
def room_bg():
    if "room" in _cache:
        return _cache["room"]
    wall = (120, 142, 128)
    im = vgrad(W, H, [(0, shade(wall, 0.45)), (0.3, shade(wall, 0.85)), (0.78, wall), (1, shade(wall, 0.5))])
    d = ImageDraw.Draw(im)
    d.rectangle((0, 1500, W, H), fill=(84, 90, 86))
    d.rectangle((0, 1240, W, 1250), fill=shade(wall, 0.8))
    # vidrio (espejo) en la pared del fondo
    d.rectangle((560, 640, 1040, 1100), fill=(30, 44, 46))
    for k in range(3):
        d.line((600 + k * 120, 1080, 720 + k * 120, 660), fill=(54, 72, 74), width=10)
    d.rectangle((560, 640, 1040, 1100), outline=(56, 60, 60), width=14)
    # lámpara colgante
    d.line((540, 0, 540, 520), fill=(30, 32, 32), width=4)
    d.polygon([(440, 560), (640, 560), (590, 515), (490, 515)], fill=(46, 50, 50))
    _cache["room"] = im
    return im


def table(d, x0=360, x1=720, top=1200):
    d.rectangle((x0, top, x1, top + 26), fill=(150, 140, 120))
    d.rectangle((x0, top + 26, x1, top + 40), fill=(110, 100, 86))
    for lx in (x0 + 20, x1 - 30):
        d.rectangle((lx, top + 40, lx + 12, 1500), fill=(70, 70, 70))


def room_world(lt, left, right, spect=False, light=1.0, write=0.0):
    """left/right: 'doc','col','pat','inm' para cada silla."""
    im = room_bg().copy()
    d = ImageDraw.Draw(im)
    if spect:
        bust_back(d, 800, 1000, 220, (40, 38, 36), DARKHAIR, hood=MUSTARD, hairshape="fade")
        rect_a(im, (566, 646, 1034, 1094), (30, 50, 52), 0.45)
        d = ImageDraw.Draw(im)
    if light > 0:
        glow(im, 540, 580, 500, (80, 120, 90), 0.5 * light)
        ell_a(im, (470, 548, 610, 566), (230, 255, 236), light)
    d = ImageDraw.Draw(im)
    ys = 1320

    def who(code, x, f):
        if code == "doc":
            return seated(d, x, ys, 660, f, BLOUSE, DKB, TAN, coat=COATW, bun=True, write=write)
        if code == "col":
            return seated(d, x, ys, 720, f, OLIVE, DBLOND, SKIN, coat=COATW, pants=(46, 48, 56), write=write)
        if code == "pat":
            return seated(d, x, ys, 660, f, PAT, DKB, TAN, pants=PAT, bun=True, band=True)
        if code == "inm":
            return seated(d, x, ys, 640, f, PAT, (70, 46, 30), SKIN, pants=PAT)
    who(left, 230, 1)
    who(right, 850, -1)
    table(d)
    # expediente sobre la mesa (lado izquierdo)
    d.polygon([(400, 1196), (520, 1196), (530, 1186), (410, 1186)], fill=(214, 190, 130))
    d.polygon([(420, 1186), (515, 1186), (522, 1180), (428, 1180)], fill=(240, 240, 234))
    return im


# ================================================================ escena 1
def cell_content(lt, mode="lying"):
    """versión apaisada para la pantalla del cine."""
    im = cell_world(lt)
    d = ImageDraw.Draw(im)
    if mode == "lying":
        lying(d, eye=0)
    crop = im.crop((0, 200, 1080, 1514)).resize((1080, 614))
    return crop


def corridor_cellside(lt, look=0.0):
    """fuera de la celda: dos guardias y un policía con la carpeta abierta (foto del esposo)."""
    if "cside" not in _cache:
        wall = (150, 170, 158)
        im = vgrad(W, H, [(0, shade(wall, 0.4)), (0.3, shade(wall, 0.75)), (1, shade(wall, 0.6))])
        d = ImageDraw.Draw(im)
        d.rectangle((0, 1500, W, H), fill=(86, 94, 90))
        d.rectangle((380, 700, 700, 1500), fill=(150, 160, 160))
        d.rectangle((476, 790, 596, 910), fill=(200, 214, 206))
        d.rectangle((476, 790, 596, 910), outline=(60, 64, 66), width=8)
        d.rectangle((420, 1080, 440, 1160), fill=(90, 96, 100))
        d.rectangle((150, 300, 550, 316), fill=(220, 250, 230))
        _cache["cside"] = im
    im = _cache["cside"].copy()
    glow(im, 350, 340, 420, (40, 80, 56), 0.5)
    d = ImageDraw.Draw(im)
    guard_side(d, 300, 1500, 700, 1, female=True, hair=(60, 40, 30))
    guard_side(d, 780, 1500, 720, -1)
    # policía con la carpeta
    x, yf, h = 900, 1560, 760
    person_side(d, x, yf, h, -1, POLICEC, DARKHAIR, SKIN, coatlen=0.4, arms="forward", pants=(20, 22, 26))
    r = h * 0.068
    d.chord((x - r * 1.1, yf - h - r * 0.05, x + r * 1.1, yf - h + r * 1.1), 180, 360, fill=(16, 18, 22))
    d.rectangle((x - r * 1.5, yf - h + r * 0.55, x + r * 0.2, yf - h + r * 0.7), fill=(16, 18, 22))
    folder(im, 720, 1150, 1.0)
    return im


def husband_photo(w, h):
    ph = vgrad(w, h, [(0, (150, 160, 170)), (1, (90, 96, 110))])
    pd = ImageDraw.Draw(ph)
    husband_front(pd, w / 2, h * 1.9, h * 1.9, expr="smile", legs=False)
    return ph


def folder(img, cx, cy, s):
    d = ImageDraw.Draw(img)
    w, h = 230 * s, 160 * s
    d.polygon([(cx - w, cy - h), (cx, cy - h * 0.92), (cx, cy + h), (cx - w, cy + h * 0.92)], fill=(214, 190, 130))
    d.polygon([(cx, cy - h * 0.92), (cx + w, cy - h), (cx + w, cy + h * 0.92), (cx, cy + h)], fill=(226, 204, 146))
    for k in range(6):
        yy = cy - h * 0.6 + k * h * 0.22
        d.line((cx - w * 0.85, yy, cx - w * 0.15, yy + 4), fill=(170, 160, 140), width=max(1, int(3 * s)))
    pw, ph_ = int(w * 0.55), int(h * 0.95)
    photo = husband_photo(pw, ph_)
    px, py = int(cx + w * 0.22), int(cy - h * 0.6)
    d.rectangle((px - 6 * s, py - 6 * s, px + pw + 6 * s, py + ph_ + 6 * s), fill=(244, 244, 240))
    img.paste(photo, (px, py))
    d.rounded_rectangle((px + pw * 0.4, py - 18 * s, px + pw * 0.55, py + 14 * s), radius=int(5 * s), outline=(170, 176, 184), width=max(2, int(5 * s)))
    return (px + pw / 2, py + ph_ / 2)


def photo_close(lt):
    im = Image.new("RGB", (W, H), (60, 56, 48))
    folder(im, 300, 960, 4.2)
    return im


def scene1(lt, dur):
    c = [3.0, 6.0]

    def a(t):
        im = cinema_world(t, cell_content(t))
        z = lerp(1.0, 1.12, sstep(0, 3.2, t))
        return camera(im, 540, lerp(980, 930, sstep(0, 3.2, t)), z)

    def b(t):
        u = t - c[0]
        if u < 0.9:
            im = cinema_world(t, cell_content(t))
            z = lerp(1.12, 3.4, sstep(-0.2, 0.9, u))
            out = camera(im, 540, lerp(930, 890, sstep(-0.2, 0.9, u)), z)
            if u > 0.6:
                inner = b_cell(t, u)
                out = blend(out, inner, sstep(0.6, 0.9, u))
            return out
        return b_cell(t, u)

    def b_cell(t, u):
        im = cell_world(t)
        sitting_up(im, sstep(0.9, 1.4, u), look=1 if (u < 2.0 or u > 2.6) else -1, eye=1.0)
        z = lerp(3.0, 1.25, sstep(0.6, 1.6, u))
        return camera(im, lerp(540, 520, sstep(0.6, 1.6, u)), lerp(1150, 1080, sstep(0.6, 1.6, u)), z)

    def cc(t):
        u = t - c[1]
        im = corridor_cellside(t)
        z = lerp(1.15, 3.6, sstep(0.8, dur - c[1] - 0.3, u))
        cx = lerp(560, 805, sstep(0.8, dur - c[1] - 0.3, u))
        cy = lerp(1060, 1100, sstep(0.8, dur - c[1] - 0.3, u))
        out = camera(im, cx, cy, z)
        k = sstep(dur - c[1] - 0.6, dur - c[1] - 0.1, u)
        if k > 0:
            pc = photo_close(t)
            out = blend(out, camera(pc, 760, 960, 1.0 + 0.2 * k), k)
        return out
    return pick(lt, c, [a, b, cc])


# ================================================================ escena 2
def scene2(lt, dur):
    c = [2.7, 5.4]

    def world(t, gate=0.0):
        im = corridor_world(t, gate_open=gate)
        return im, ImageDraw.Draw(im)

    def a(t):
        im, d = world(t)
        husband_front(d, 885, 1500, 578, expr="smile", hand_up=0.0)
        doc_side(d, lerp(380, 640, t / c[0]), 1500, 545, 1, arms="forward", step=math.sin(t * 7), file=True)
        cx, cy, z = cam_path(t, [(0, 885, 900, 2.6), (1.3, 800, 1150, 1.15), (3.0, 800, 1150, 1.15)])
        out = camera(im, cx, cy, z)
        if t < 2.4:
            days_text(out, t, cx, cy, z)
        return out

    def b(t):
        u = t - c[0]
        im, d = world(t)
        x = lerp(640, 1060, sstep(-0.3, 1.0, u))
        husband_front(d, 885, 1500, 578, expr="warm", hand_up=sstep(0.6, 1.0, u) * (1 - sstep(2.0, 2.4, u)))
        doc_side(d, x, 1500, 545, 1 if u < 1.2 else -1, arms="forward", step=math.sin(t * 7) * (1 - sstep(0.8, 1.0, u)),
                 file=True, smile=0.8 if u > 1.2 else 0)
        return camera(im, lerp(880, 1020, sstep(0, dur - c[0], u)), 1170, 1.25)

    def cc(t):
        u = t - c[1]
        L = dur - c[1]
        im, d = world(t, gate=sstep(0.0, 0.7, u))
        guard_side(d, GATE_X - 60, 1500, 580, 1, arms="forward" if u < 0.7 else "down")
        doc_side(d, lerp(1350, 2150, sstep(0.0, L + 0.6, u)), 1500, 545, 1, arms="forward", step=math.sin(t * 7), file=True)
        spect_back(d, 2420, 1500, 580)
        out = camera(im, lerp(1750, 1980, sstep(0, L, u)), 1170, lerp(1.15, 1.6, sstep(L - 1.0, L, u)))
        k = sstep(L - 0.5, L, u)
        if k > 0:
            out = blend(out, Image.new("RGB", (W, H), (12, 18, 28)), k * 0.85)
        return out
    return pick(lt, c, [a, b, cc])


def days_text(img, t, cx, cy, z):
    a = sstep(0.0, 0.3, t) * (1 - sstep(2.0, 2.4, t))
    if a <= 0:
        return
    sx = (610 - cx) * z + W / 2
    sy = (750 - cy) * z + H / 2
    f = font(FONT_N, 74)
    lay = Image.new("L", (W, 200), 0)
    ld = ImageDraw.Draw(lay)
    txt = "3 DÍAS ANTES"
    tw = ld.textlength(txt, font=f)
    x = clamp(sx + 70 * z, 40, W - tw - 40)
    y = clamp(sy - 60, 260, 1300)
    ld.text((0, 40), txt, font=f, fill=255)
    sh = lay.filter(ImageFilter.GaussianBlur(10))
    img.paste((0, 0, 0), (int(x), int(y)), sh.point(lambda v: int(v * 0.9 * a)))
    img.paste((246, 240, 220), (int(x), int(y)), lay.point(lambda v: int(v * a)))


# ================================================================ escena 3: tormenta
VP = (540, 640)


def car_interior(lt, girl_z=None, flash=0.0):
    im = Image.new("RGB", (W, H), (8, 10, 14))
    # exterior visto por el parabrisas
    out = vgrad(W, 1100, [(0, (8, 14, 26)), (0.55, (14, 22, 36)), (1, (10, 14, 20))])
    od = ImageDraw.Draw(out)
    od.polygon([(VP[0] - 20, VP[1]), (VP[0] + 20, VP[1]), (W + 400, 1100), (-400, 1100)], fill=(26, 30, 36))
    for k in range(8):
        z = ((k * 6 - lt * 22) % 48) + 2
        y0 = VP[1] + 1.2 * 600 / z
        y1 = VP[1] + 1.2 * 600 / (z + 2.5)
        od.polygon([(VP[0] - 6 * 600 / z * 0.02, y0), (VP[0] + 6 * 600 / z * 0.02, y0), (VP[0] + 6 * 600 / (z + 2.5) * 0.02, y1),
                    (VP[0] - 6 * 600 / (z + 2.5) * 0.02, y1)], fill=(150, 150, 130))
    for k in range(14):
        side = -1 if k % 2 else 1
        z = ((k * 3.4 - lt * 22) % 48) + 2
        tx = VP[0] + side * 5.0 * 600 / z
        th = 9 * 600 / z
        ty = VP[1] + 1.2 * 600 / z
        od.polygon([(tx, ty - th), (tx - th * 0.3, ty), (tx + th * 0.3, ty)], fill=(8, 16, 16))
    poly_a(out, [(VP[0] - 10, VP[1] + 10), (VP[0] + 10, VP[1] + 10), (W, 1100), (0, 1100)], (220, 220, 190), 0.12, blur=20)
    if girl_z is not None:
        z = girl_z
        gh = 1.62 * 600 / z
        gy = VP[1] + 1.2 * 600 / z
        glow(out, VP[0] + 20, gy - gh * 0.5, int(gh * 0.9), (180, 190, 170), 0.5)
        put_girl(out, VP[0] + 20, gy, gh, lt=lt, drips=False)
    rain(out, lt, n=180, slant=0.05, speed=1800, seed=4, ln=50)
    mask = Image.new("L", (W, 1100), 0)
    md = ImageDraw.Draw(mask)
    md.polygon([(140, 360), (940, 360), (1040, 1000), (40, 1000)], fill=255)
    im.paste(out, (0, 0), mask)
    d = ImageDraw.Draw(im)
    # gotas en el vidrio
    rng = random.Random(8)
    for i in range(70):
        x, y0 = rng.uniform(80, 1000), rng.uniform(380, 990)
        y = y0 + ((lt * rng.uniform(20, 70)) % 120)
        if y > 990:
            continue
        s = rng.uniform(3, 7)
        ell_a(im, (x - s, y - s * 1.3, x + s, y + s), (170, 190, 210), 0.35)
    d = ImageDraw.Draw(im)
    # limpiaparabrisas
    for px in (300, 720):
        a = math.radians(180 + 15 + 140 * (0.5 - 0.5 * math.cos(lt * 5.2)))
        d.line((px, 990, px + 460 * math.cos(a) * -1 * -1, 990 + 460 * math.sin(a)), fill=(10, 10, 12), width=12)
    d.polygon([(140, 360), (940, 360), (1040, 1000), (40, 1000)], outline=(16, 18, 22), width=26)
    # tablero y volante
    d.polygon([(0, 1000), (W, 1000), (W, H), (0, H)], fill=(16, 18, 22))
    glow(im, 340, 1060, 160, (40, 90, 110), 0.5)
    d.ellipse((150, 930, 510, 1230), outline=(10, 10, 12), width=30)
    # conductora de espaldas (moño bajo)
    bust_back(d, 330, 1260, 460, COATW, DKB, TAN)
    r = 460 * 0.27
    hy = 1260 - r * 0.9
    d.ellipse((330 - r * 0.45, hy + r * 0.3, 330 + r * 0.45, hy + r * 1.0), fill=shade(DKB, 0.85))
    d.line((160, 1330, 175, 1090), fill=shade(COATW, 0.8), width=62)
    d.line((500, 1330, 485, 1090), fill=shade(COATW, 0.8), width=62)
    d.ellipse((148, 1050, 208, 1110), fill=TAN)
    d.ellipse((452, 1050, 512, 1110), fill=TAN)
    # asiento del copiloto
    d.rounded_rectangle((680, 1150, 1000, 1920), radius=70, fill=(22, 24, 28))
    if flash > 0:
        rect_a(im, (0, 0, W, H), (230, 230, 210), flash)
    return im


def car_sprite(L, col=(52, 58, 66)):
    key = ("car", L, col)
    if key in _cache:
        return _cache[key]
    h = L * 0.34
    w = int(L * 1.05)
    im = Image.new("RGBA", (w, int(h * 1.6)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x, yg = w / 2, h * 1.5
    d.rounded_rectangle((x - L / 2, yg - h * 0.85, x + L / 2, yg - h * 0.2), radius=int(h * 0.2), fill=col)
    d.polygon([(x - L * 0.3, yg - h * 0.8), (x + L * 0.22, yg - h * 0.8), (x + L * 0.08, yg - h * 1.3), (x - L * 0.22, yg - h * 1.3)], fill=col)
    d.polygon([(x - L * 0.26, yg - h * 0.86), (x + L * 0.18, yg - h * 0.86), (x + L * 0.06, yg - h * 1.24), (x - L * 0.19, yg - h * 1.24)], fill=(20, 28, 40))
    d.line((x - L * 0.04, yg - h * 0.86, x - L * 0.05, yg - h * 1.25), fill=col, width=int(h * 0.06))
    for wx in (x - L * 0.32, x + L * 0.32):
        d.ellipse((wx - h * 0.3, yg - h * 0.5, wx + h * 0.3, yg + h * 0.1), fill=(12, 12, 14))
        d.ellipse((wx - h * 0.13, yg - h * 0.33, wx + h * 0.13, yg - h * 0.07), fill=(70, 72, 76))
    d.ellipse((x + L / 2 - h * 0.1, yg - h * 0.7, x + L / 2 + h * 0.04, yg - h * 0.52), fill=(255, 250, 220))
    d.rectangle((x - L / 2 - h * 0.02, yg - h * 0.7, x - L / 2 + h * 0.06, yg - h * 0.52), fill=(170, 20, 20))
    _cache[key] = im
    return im


def put_car(img, x, yg, L, ang=0.0, lights=True, hazard=0.0):
    sp = car_sprite(L)
    if ang:
        sp = sp.rotate(ang, resample=Image.BICUBIC, expand=False)
    w, hh = sp.size
    img.paste(sp, (int(x - w / 2), int(yg - hh * 1.5 / 1.6)), sp)
    h = L * 0.34
    ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    fx, fy = x + (L / 2) * ca, yg - h * 0.6 - (L / 2) * sa
    bx, by = x - (L / 2) * ca, yg - h * 0.6 + (L / 2) * sa
    if lights:
        glow(img, fx, fy, int(h * 1.2), (255, 240, 200), 0.8)
        poly_a(img, [(fx, fy - h * 0.08), (fx + L * 1.6 * ca, fy - h * 0.4 - L * 1.6 * sa), (fx + L * 1.6 * ca, fy + h * 0.6 - L * 1.6 * sa), (fx, fy + h * 0.08)],
               (255, 245, 210), 0.16, blur=12)
    if hazard > 0:
        for px, py in ((fx, fy), (bx, by)):
            glow(img, px, py, int(h * 1.4), (255, 160, 40), hazard)


def road_side(lt, rainy=True, embank=False):
    key = ("roadside", embank)
    if key not in _cache:
        im = vgrad(W, H, [(0, (6, 10, 20)), (0.5, (14, 22, 36)), (1, (8, 10, 14))])
        d = ImageDraw.Draw(im)
        rng = random.Random(3)
        for i in range(26):
            x = rng.uniform(-50, W + 50)
            s = rng.uniform(140, 260)
            d.polygon([(x, 1150 - s * 2.4), (x - s * 0.45, 1180), (x + s * 0.45, 1180)], fill=(8, 18, 18))
        d.rectangle((0, 1180, W, 1260), fill=(14, 22, 20))
        d.rectangle((0, 1260, W, 1560), fill=(30, 34, 40))
        for x in range(0, W, 200):
            d.rectangle((x, 1405, x + 110, 1415), fill=(130, 130, 116))
        d.rectangle((0, 1560, W, H), fill=(12, 18, 16))
        if embank:
            d.polygon([(560, 1560), (W, 1180), (W, H), (480, H)], fill=(36, 34, 26))
            d.polygon([(560, 1560), (W, 1180), (W, 1230), (610, 1590)], fill=(20, 30, 20))
        _cache[key] = im
    return _cache[key].copy()


def scene3(lt, dur):
    c = [snap(dur * 0.27), snap(dur * 0.52), snap(dur * 0.76)]

    def a(t):
        im = car_interior(t)
        z = lerp(1.9, 1.1, sstep(0, 1.2, t))
        return camera(im, 540, lerp(700, 900, sstep(0, 1.2, t)), z)

    def b(t):
        u = t - c[0]
        im = car_interior(t, girl_z=lerp(26, 5.5, sstep(-0.2, c[1] - c[0] + 0.2, u)))
        return camera(im, 540, lerp(900, 760, sstep(0, 2.2, u)), lerp(1.1, 1.5, sstep(0, 2.2, u)), shake=2, lt=t)

    def cc(t):
        u = t - c[1]
        L = c[2] - c[1]
        im = road_side(t)
        put_girl(im, 560, 1340, 440, lt=t)
        p = sstep(-0.2, L + 0.3, u)
        cx = lerp(-300, 900, p)
        ang = lerp(-4, 22, sstep(0.1, L, u))
        put_car(im, cx, 1500, 900, ang=ang)
        rng = random.Random(int(t * 30))
        d = ImageDraw.Draw(im)
        for i in range(40):  # salpicaduras
            sx = cx - 300 + rng.uniform(-150, 150)
            sy = 1500 - rng.uniform(0, 90)
            d.line((sx, sy, sx - rng.uniform(20, 60), sy - rng.uniform(10, 40)), fill=(160, 180, 200), width=3)
        rain(im, t, n=300, slant=0.12, speed=1700, seed=5)
        return camera(im, 540, 1280, 1.05, shake=4, lt=t)

    def dd(t):
        u = t - c[2]
        im = road_side(t, embank=True)
        haz = 1.0 if (u % 0.6) < 0.3 else 0.15
        put_car(im, 620, 1520, 900, ang=14, lights=True, hazard=haz)
        for i in range(10):  # vapor
            ph = (u * 0.5 + i / 10) % 1
            sx = 960 + 40 * math.sin(i * 2.1 + u)
            sy = 1240 - ph * 380
            s = 40 + ph * 110
            ell_a(im, (sx - s, sy - s, sx + s, sy + s), (200, 208, 214), 0.28 * (1 - ph), blur=18)
        rain(im, t, n=300, slant=0.12, speed=1700, seed=6)
        return camera(im, lerp(620, 420, sstep(0, dur - c[2], u)), 1330, lerp(1.1, 1.6, sstep(0, dur - c[2], u)))
    return pick(lt, c, [a, b, cc, dd])


# ================================================================ escena 4: llamas
def road_persp(lt):
    if "rp" not in _cache:
        im = vgrad(W, H, [(0, (6, 10, 20)), (0.45, (14, 22, 36)), (1, (10, 14, 20))])
        d = ImageDraw.Draw(im)
        hz = 900
        for k in range(18):
            side = -1 if k % 2 else 1
            z = 3 + k * 1.6
            tx = 540 + side * 6 * 700 / z
            th = 10 * 700 / z
            d.polygon([(tx, hz + 1.6 * 700 / z - th), (tx - th * 0.3, hz + 1.6 * 700 / z), (tx + th * 0.3, hz + 1.6 * 700 / z)], fill=(8, 16, 18))
        d.polygon([(520, hz), (560, hz), (W + 900, H), (-900, H)], fill=(30, 34, 42))
        for k in range(6):
            z = 2 + k * 3
            y0, y1 = hz + 1.6 * 700 / z, hz + 1.6 * 700 / (z + 1.4)
            d.polygon([(540 - 10 * 700 / z * 0.012, y0), (540 + 10 * 700 / z * 0.012, y0), (540 + 10 * 700 / (z + 1.4) * 0.012, y1),
                       (540 - 10 * 700 / (z + 1.4) * 0.012, y1)], fill=(130, 130, 116))
        _cache["rp"] = im
    return _cache["rp"].copy()


def scene4(lt, dur):
    c = [snap(1.8)]
    gx, gyf, gh = 640, 900 + 1.6 * 700 / 5.0, 1.62 * 700 / 5.0

    def a(t):
        im = road_persp(t)
        put_girl(im, gx, gyf, gh, view="back", lt=t)
        rain(im, t, n=300, slant=0.08, speed=1600, seed=9)
        d = ImageDraw.Draw(im)
        ext = sstep(0.2, 1.4, t)
        bust_back(d, 250, 1560, 560, COATW, DKB, TAN)
        r = 560 * 0.27
        hy = 1560 - r * 0.9
        d.ellipse((250 - r * 0.45, hy + r * 0.3, 250 + r * 0.45, hy + r * 1.0), fill=shade(DKB, 0.85))
        hx, hy2 = lerp(470, 560, ext), lerp(1700, 1330, ext)
        d.line((470, 1640, hx, hy2), fill=shade(COATW, 0.85), width=80)
        d.ellipse((hx - 42, hy2 - 50, hx + 42, hy2 + 30), fill=TAN)
        return camera(im, 520, lerp(1250, 1200, t / 2), lerp(1.15, 1.3, t / 2))

    def b(t):
        u = t - c[0]
        L = dur - c[0]
        fire = sstep(0.15, 0.6, u)
        im = road_persp(t)
        rain(im, t, n=300, slant=0.08, speed=1600, seed=9)
        if fire < 1:
            put_girl(im, gx, gyf, gh, view="front", lt=t)
        flick = 0.85 + 0.15 * math.sin(t * 37) * math.sin(t * 23)
        if fire > 0:
            glow(im, gx, gyf - gh * 0.5, int(gh * 2.2), FLAME, fire * flick)
            glow(im, gx, gyf - gh * 0.5, int(gh * 1.1), (255, 200, 120), fire * flick)
            girl_silhouette(im, gx, gyf, gh, (255, 226, 170), alpha=fire)
            # reflejo en el asfalto mojado
            poly_a(im, [(gx - gh * 0.14, gyf), (gx + gh * 0.14, gyf), (gx + gh * 0.4, H), (gx - gh * 0.4, H)], FLAME, 0.35 * fire, blur=30)
        d = ImageDraw.Draw(im)
        bust_back(d, 250, 1560, 560, COATW, DKB, TAN, rim=lerpc((150, 170, 190), (255, 170, 80), fire))
        r = 560 * 0.27
        hy = 1560 - r * 0.9
        d.ellipse((250 - r * 0.45, hy + r * 0.3, 250 + r * 0.45, hy + r * 1.0), fill=shade(DKB, 0.85))
        d.line((470, 1640, 560, 1330), fill=shade(COATW, 0.85), width=80)
        d.ellipse((518, 1280, 602, 1360), fill=lerpc(TAN, (255, 190, 120), fire * 0.6))
        out = camera(im, lerp(520, 600, sstep(0, L, u)), lerp(1200, 1150, sstep(0, L, u)), lerp(1.3, 1.9, sstep(0, L, u)))
        k = sstep(L - 1.0, L - 0.4, u)
        if k > 0:
            out = blend(out, Image.new("RGB", (W, H), (255, 150, 60)), k)
        if u > L - 0.35:
            out = Image.new("RGB", (W, H), (0, 0, 0))
        return out
    return pick(lt, c, [a, b])


# ================================================================ escena 5
def wrist_close(lt, lift):
    im = vgrad(W, H, [(0, (150, 170, 160)), (1, (200, 210, 204))])
    d = ImageDraw.Draw(im)
    for row in range(10):
        for col in range(5):
            x0, y0 = -60 + col * 260 + (130 if row % 2 else 0), row * 200
            d.rounded_rectangle((x0 + 8, y0 + 8, x0 + 252, y0 + 192), radius=50, fill=(210, 220, 212))
    y = lerp(1700, 1000, lift)
    d.polygon([(-100, y + 400), (420, y - 60), (560, y + 120), (40, y + 640)], fill=PAT)
    for k in range(4):
        d.line((60 + k * 90, y + 420 - k * 60, 150 + k * 90, y + 520 - k * 60), fill=shade(PAT, 0.85), width=6)
    d.polygon([(420, y - 60), (700, y - 300), (830, y - 140), (560, y + 120)], fill=TAN)
    d.polygon([(480, y + 10), (560, y - 60), (650, y + 60), (570, y + 130)], fill=(248, 248, 246))
    d.polygon([(500, y + 15), (560, y - 35), (575, y - 20), (515, y + 30)], fill=(220, 224, 228))
    d.ellipse((690, y - 380, 920, y - 120), fill=TAN)
    for k in range(4):
        d.rounded_rectangle((830 + k * 18, y - 440 + k * 50, 960 + k * 18, y - 380 + k * 50), radius=26, fill=shade(TAN, 0.96))
    glow(im, 540, 100, 600, (60, 110, 80), 0.4)
    return im


def scene5(lt, dur):
    c = [snap(dur * 0.5)]

    def a(t):
        flick = 0.0 if t < 0.25 else (1.0 if (t > 0.75 or int(t * 20) % 3) else 0.2)
        im = cell_world(t, tube=flick)
        d = ImageDraw.Draw(im)
        lying(d, eye=1.0 if t > 0.9 else 0.0)
        out = camera(im, 300, 1150, lerp(2.2, 2.0, t / c[0]))
        if flick < 1:
            out = Image.eval(out, lambda v: int(v * (0.12 + 0.88 * flick)))
        return out

    def b(t):
        u = t - c[0]
        return wrist_close(t, sstep(0.0, 0.9, u))
    return pick(lt, c, [a, b])


# ================================================================ escena 6
def stamp(img, t0, t1, t, txt, cx, cy, size=96, rot=8, col=(200, 30, 40)):
    a = sstep(t0, t0 + 0.15, t) * (1 - sstep(t1, t1 + 0.2, t))
    if a <= 0:
        return
    s = 1 + 0.25 * (1 - sstep(t0, t0 + 0.2, t))
    f = font(FONT_N, int(size * s))
    lay = Image.new("L", (1000, 400), 0)
    ld = ImageDraw.Draw(lay)
    tw = ld.textlength(txt, font=f)
    ld.rounded_rectangle((500 - tw / 2 - 36, 200 - size * s * 0.75, 500 + tw / 2 + 36, 200 + size * s * 0.75), radius=24, outline=255, width=12)
    ld.text((500 - tw / 2, 200 - size * s * 0.62), txt, font=f, fill=255)
    lay = lay.rotate(rot, resample=Image.BICUBIC)
    img.paste(col, (int(cx - 500), int(cy - 200)), lay.point(lambda v: int(v * a * 0.92)))


def scene6(lt, dur):
    c = [snap(dur * 0.36), snap(dur * 0.68)]

    def a(t):
        im = corridor_world(t, clock=False)
        d = ImageDraw.Draw(im)
        x = lerp(980, 1180, t / c[0])
        guard_side(d, x + 200, 1500, 580, 1, step=math.sin(t * 6))
        doc_side(d, x, 1500, 545, 1, mode="patient", step=math.sin(t * 6 + 1))
        z = 1.35
        cx, cy = 1180, 1250
        out = camera(im, cx, cy, z)
        od = ImageDraw.Draw(out)
        # internas en primer plano (detrás de las rejas), comentando entre ellas
        bust_back(od, 220, 1700, 300, PAT, (60, 40, 28), TAN, hairshape="bob")
        bust_back(od, 470, 1730, 290, PAT, DARKHAIR, SKIN)
        bust_back(od, 900, 1720, 300, PAT, (90, 64, 40), SKIN, hairshape="bob")
        for k in range(9):  # rejas
            xx = 40 + k * 125
            od.rectangle((xx, 0, xx + 22, H), fill=(26, 28, 30))
            od.line((xx + 6, 0, xx + 6, H), fill=(70, 76, 78), width=3)
        od.rectangle((0, 330, W, 352), fill=(26, 28, 30))
        od.rectangle((0, 1440, W, 1462), fill=(26, 28, 30))
        # pulsera en pantalla -> sello PACIENTE
        top = 1500 - 545
        wx = (x + 545 * 0.02 - cx) * z + W / 2
        wy = (top + 545 * 0.48 - cy) * z + H / 2
        stamp(out, B[5] + 0.3, B[5] + 2.2, B[5] + t, "PACIENTE", wx + 40, wy - 40, size=80)
        return out

    def b(t):
        u = t - c[0]
        im = room_world(t, "col", "pat", write=0.5 + 0.5 * math.sin(t * 9) if u > 0.6 else 0.0)
        return camera(im, 540, 1180, lerp(1.25, 1.4, sstep(0, c[1] - c[0], u)))

    def cc(t):
        u = t - c[1]
        L = dur - c[1]
        im = room_bg().copy()
        d = ImageDraw.Draw(im)
        bust_back(d, 800, 1000, 220, (40, 38, 36), DARKHAIR, hood=MUSTARD, hairshape="fade")
        rect_a(im, (566, 646, 1034, 1094), (30, 50, 52), 0.45)
        glow(im, 540, 580, 500, (80, 120, 90), 0.5)
        d = ImageDraw.Draw(im)
        doc_front(d, 420, 1900, 1450, mode="patient", expr="confused", arms="table", look=0.5 * math.sin(u * 2), legs=False)
        d.rectangle((0, 1160, W, H), fill=(150, 140, 120))
        d.rectangle((0, 1160, W, 1176), fill=(120, 110, 96))
        bust_back(d, 900, 1560, 560, COATW, DBLOND, SKIN)
        out = camera(im, lerp(560, 700, sstep(L - 0.8, L, u)), lerp(1150, 900, sstep(L - 0.8, L, u)), lerp(1.0, 1.8, sstep(L - 0.8, L, u)))
        return out
    return pick(lt, c, [a, b, cc])


# ================================================================ escena 7: pasillo de noche (perspectiva)
def night_hall(lt, lights_on, girl_z, puddle=1.0):
    im = Image.new("RGB", (W, H), (4, 6, 6))
    d = ImageDraw.Draw(im)
    f = 700
    cx, cy = 540, 860
    hwid, eyeh, ceil = 1.5, 1.6, 1.4

    def P(X, Y, z):
        return (cx + X * f / z, cy + Y * f / z)
    zs = [1.2 + k * 2.2 for k in range(12)]
    for i in range(len(zs) - 1, 0, -1):
        z0, z1 = zs[i - 1], zs[i]
        li = min(len(lights_on) - 1, (i - 1) // 2)
        on = lights_on[li]
        k = 0.25 + 0.75 * on
        k *= clamp(1.2 - z0 / 30, 0.3, 1)
        wall = shade((40, 84, 62), k)
        floor = shade((30, 52, 44), k)
        ceilc = shade((20, 36, 30), k)
        d.polygon([P(-hwid, eyeh, z0), P(hwid, eyeh, z0), P(hwid, eyeh, z1), P(-hwid, eyeh, z1)], fill=floor)
        d.polygon([P(-hwid, -ceil, z0), P(hwid, -ceil, z0), P(hwid, -ceil, z1), P(-hwid, -ceil, z1)], fill=ceilc)
        for s in (-1, 1):
            d.polygon([P(s * hwid, -ceil, z0), P(s * hwid, eyeh, z0), P(s * hwid, eyeh, z1), P(s * hwid, -ceil, z1)], fill=wall)
            if i % 2 == 0:  # puertas metálicas
                za, zb = z0 + 0.4, z0 + 1.3
                d.polygon([P(s * hwid, -0.4, za), P(s * hwid, eyeh, za), P(s * hwid, eyeh, zb), P(s * hwid, -0.4, zb)], fill=shade((30, 44, 40), k))
    zf = zs[-1]
    d.polygon([P(-hwid, -ceil, zf), P(hwid, -ceil, zf), P(hwid, eyeh, zf), P(-hwid, eyeh, zf)], fill=(6, 12, 10))
    for li, on in enumerate(lights_on):
        z = 2.2 + li * 4.4
        x0, y0 = P(-0.3, -ceil + 0.02, z)
        x1, y1 = P(0.3, -ceil + 0.06, z)
        d.rectangle((x0, y0, x1, y1), fill=lerpc((20, 30, 26), (140, 255, 170), on))
        if on > 0:
            glow(im, (x0 + x1) / 2, y1 + 20, int(2600 / z), (40, 140, 70), 0.6 * on)
    if girl_z is not None:
        gx, gy = P(0.1, eyeh, girl_z)
        put_girl(im, gx, gy, 1.62 * f / girl_z, lt=lt, puddle=puddle)
    return im


def door_close(lt, fog=0.0, girl=0.0, night=True):
    """ventanilla de la puerta vista desde dentro de la celda (plano cerrado)."""
    im = vgrad(W, H, [(0, (40, 50, 52)), (1, (26, 32, 34))])
    d = ImageDraw.Draw(im)
    wx0, wy0, wx1, wy1 = 190, 420, 890, 1180
    out = vgrad(wx1 - wx0, wy1 - wy0, [(0, (16, 40, 30)), (1, (8, 20, 16))])
    glow(out, 350, 60, 420, (40, 140, 70), 0.5)
    if girl > 0:
        gh = 1500
        put_girl(out, 360, 60 + gh, gh, lt=lt, drips=False)
        if girl < 1:
            out = Image.blend(vgrad(wx1 - wx0, wy1 - wy0, [(0, (16, 40, 30)), (1, (8, 20, 16))]), out, girl)
    if fog > 0:
        fogim = Image.new("RGB", out.size, (200, 214, 210))
        m = smooth_noise(out.size[0], out.size[1], 200, 4)
        m = Image.fromarray((np.clip(m * 1.4 * fog + fog * 0.35, 0, 0.92) * 255).astype(np.uint8))
        out.paste(fogim, (0, 0), m)
    im.paste(out, (wx0, wy0))
    d = ImageDraw.Draw(im)
    d.rectangle((wx0 - 30, wy0 - 30, wx1 + 30, wy1 + 30), outline=(70, 78, 80), width=40)
    d.line(((wx0 + wx1) / 2, wy0, (wx0 + wx1) / 2, wy1), fill=(70, 78, 80), width=10)
    for yy in (1500, 1700):
        d.line((0, yy, W, yy), fill=(34, 40, 42), width=8)
    return im


def scene7(lt, dur):
    c = [snap(dur * 0.33), snap(dur * 0.66)]

    def a(t):
        im = night_hall(t, [1, 1, 1, 1, 1, 1], 15.0, puddle=0.4 + 0.6 * sstep(0, c[0], t))
        return camera(im, 540, lerp(860, 840, t / c[0]), lerp(1.0, 1.25, t / c[0]))

    def b(t):
        u = t - c[0]
        L = c[1] - c[0]
        n_off = int(clamp(u / L * 6 + 0.5, 0, 5))
        lights = [0 if (5 - i) < n_off else 1 for i in range(6)]
        gz = [15, 11, 8, 6, 4.6, 3.6][n_off]
        im = night_hall(t, lights, gz, puddle=1.0)
        return camera(im, 540, 860, 1.25)

    def cc(t):
        u = t - c[1]
        L = dur - c[1]
        im = door_close(t, girl=1.0)
        z = lerp(1.0, 2.6, sstep(L - 0.6, L, u))
        return camera(im, 540, lerp(820, 760, sstep(0, L, u)), z)
    return pick(lt, c, [a, b, cc])


# ================================================================ escena 8: comedor
DW = 2200


def dining_bg():
    if "din" in _cache:
        return _cache["din"]
    wall = (170, 186, 176)
    im = vgrad(DW, H, [(0, shade(wall, 0.5)), (0.3, shade(wall, 0.85)), (0.8, wall), (1, shade(wall, 0.6))])
    d = ImageDraw.Draw(im)
    d.rectangle((0, 1560, DW, H), fill=(110, 116, 110))
    for x0 in (120, 760, 1400):
        d.rectangle((x0, 640, x0 + 420, 1000), fill=(210, 226, 228))
        for xx in range(x0 + 50, x0 + 420, 50):
            d.line((xx, 640, xx, 1000), fill=(60, 66, 66), width=7)
        d.rectangle((x0, 640, x0 + 420, 1000), outline=(80, 86, 86), width=12)
    for x in range(100, DW, 500):
        d.rectangle((x, 520, x + 260, 536), fill=(230, 250, 236))
    _cache["din"] = im
    return im


INMATES = [(200, "long", DARKHAIR, SKIN), (380, "curly", (60, 40, 28), TAN), (560, "short", BROWNHAIR, SKIN),
           (1600, "bob", (50, 36, 26), TAN), (1950, "long", (90, 64, 40), SKIN)]


def dining_world(lt, girl_x=None, you="seated", look=-1.0, watch=False, skip=()):
    im = dining_bg().copy()
    d = ImageDraw.Draw(im)
    # internas detrás de las mesas (de frente)
    for k, (x, st, hair, sk) in enumerate(INMATES):
        if k in skip:
            continue
        lk = look if watch else 0.4 * math.sin(lt * 0.8 + k)
        hs = "long" if st == "bob" else st
        person_front(d, x, 1560, 560, PAT, PAT, hair, sk, hair_style=hs, arms="table", legs=False, look=lk)
    # guardias de pie junto a la pared
    person_front(d, 70, 1560, 620, GUARD, shade(GUARD, 0.8), DARKHAIR, SKIN, look=0.5 if not watch else 1)
    for x0, x1 in ((100, 720), (1460, 2100)):
        d.rectangle((x0, 1290, x1, 1316), fill=(170, 160, 140))
        d.rectangle((x0 + 20, 1316, x0 + 36, 1560), fill=(80, 80, 80))
        d.rectangle((x1 - 36, 1316, x1 - 20, 1560), fill=(80, 80, 80))
        for k in range(3):
            tx = x0 + 60 + k * 210
            d.rectangle((tx, 1278, tx + 120, 1290), fill=(140, 146, 150))
    if girl_x is not None:
        put_girl(im, girl_x, 1560, 583, lt=lt, puddle=0.9)
        d = ImageDraw.Draw(im)
    if you == "seated":
        doc_front(d, 1780, 1560, 560, mode="patient", arms="table", legs=False, look=look, expr="confused")
    return im


def scene8(lt, dur):
    c = [snap(dur * 0.33), snap(dur * 0.66)]

    def a(t):
        im = dining_world(t, girl_x=1050, look=-1.0)
        d = ImageDraw.Draw(im)
        for x0, x1 in ((1460, 2100),):
            pass
        cx = lerp(900, 1250, sstep(0, c[0], t))
        return camera(im, cx, 1230, 1.15)

    def b(t):
        u = t - c[0]
        im = dining_world(t, girl_x=None, you=None, watch=True, skip=(3,))
        d = ImageDraw.Draw(im)
        put_girl(im, 1320, 1520, 560, lt=t, puddle=0.0)
        d = ImageDraw.Draw(im)
        guard_side(d, 1230, 1580, 620, -1)
        colleague_side(d, 1400, 1580, 640, -1)
        doc_side(d, 1700, 1580, 560, -1, mode="patient", arms="forward" if u > 0.2 else "down")
        talk = 0.5 + 0.5 * math.sin(t * 13)
        return camera(im, 1360, 1230, 1.2)

    def cc(t):
        u = t - c[1]
        L = dur - c[1]
        im = dining_world(t, girl_x=None, you=None, watch=True)
        d = ImageDraw.Draw(im)
        guard_side(d, 760, 1600, 640, 1 if u < L * 0.5 else -1)
        guard_side(d, 960, 1600, 620, -1, female=True, hair=(70, 46, 30))
        colleague_front(d, 1280, 1660, 760, legs=False, arms="table", look=0.6)
        # carpeta en la que escribe
        d.polygon([(1180, 1290), (1380, 1290), (1400, 1420), (1160, 1420)], fill=(214, 190, 130))
        d.polygon([(1195, 1300), (1365, 1300), (1380, 1410), (1180, 1410)], fill=(242, 242, 236))
        pen = 1230 + ((u * 90) % 120)
        for k in range(int(clamp(u * 4, 0, 8))):
            yy = 1320 + k * 11
            d.line((1210, yy, 1210 + (120 if k < int(u * 4) - 1 else pen - 1210), yy + 2), fill=(70, 76, 110), width=3)
        d.line((pen, 1320 + int(clamp(u * 4, 0, 8)) * 11, pen + 30, 1260), fill=(20, 20, 30), width=7)
        cx, cy, z = cam_path(u, [(0, 1100, 1250, 1.15), (L - 1.0, 1200, 1300, 1.3), (L, 1280, 1360, 4.0)])
        out = camera(im, cx, cy, z)
        k = sstep(L - 0.45, L, u)
        if k > 0:
            out = blend(out, page_close(t), k)
        return out
    return pick(lt, c, [a, b, cc])


def page_close(lt):
    im = vgrad(W, H, [(0, (226, 206, 150)), (1, (200, 180, 126))])
    d = ImageDraw.Draw(im)
    d.polygon([(110, 200), (980, 160), (1010, 1760), (80, 1800)], fill=(244, 244, 238))
    rng = random.Random(5)
    for k in range(22):
        y = 300 + k * 62
        x = 170
        while x < 900:
            w = rng.uniform(40, 140)
            pts = [(x + i * w / 8, y + 6 * math.sin(i * 1.7 + k)) for i in range(9)]
            d.line(pts, fill=(60, 70, 110), width=4)
            x += w + 24
    return im


# ================================================================ escena 9
def scene9(lt, dur):
    c = [snap(dur * 0.33), snap(dur * 0.66)]

    def a(t):
        im = room_world(t, "doc", "inm", write=0.5 + 0.5 * math.sin(t * 9))
        out = camera(im, 540, 1180, lerp(1.6, 1.3, sstep(0.0, 1.2, t)))
        k = 1 - sstep(0.0, 0.5, t)
        if k > 0:
            out = blend(out, page_close(t), k)
        return out

    def b(t):
        u = t - c[0]
        L = c[1] - c[0]
        A = camera(room_world(t, "doc", "inm"), 540, 1180, 1.3)
        Bm = camera(room_world(t, "col", "pat", write=0.5 + 0.5 * math.sin(t * 9)), 540, 1180, 1.3)
        return whip(A, Bm, sstep(0.1, L - 0.3, u))

    def cc(t):
        u = t - c[1]
        L = dur - c[1]
        im = room_bg().copy()
        d = ImageDraw.Draw(im)
        d.rectangle((40, 700, 300, 1500), fill=(40, 46, 44))
        d.rectangle((40, 700, 300, 1500), outline=(80, 90, 86), width=14)
        spect_back(d, 170, 1500, 600)
        tube = 1.0
        if u > L - 0.7:
            tube = 1.0 if int(u * 18) % 2 else 0.25
        if u > L - 0.2:
            tube = 0.0
        glow(im, 540, 580, 500, (80, 120, 90), 0.5 * tube)
        d = ImageDraw.Draw(im)
        up = sstep(0.3, 1.0, u)
        doc_front(d, 600, 1960, 1450, mode="patient", expr="determined" if up > 0.5 else "neutral", arms="table", legs=False, look=0.0)
        d.rectangle((0, 1222, W, H), fill=(150, 140, 120))
        d.rectangle((0, 1222, W, 1238), fill=(120, 110, 96))
        out = camera(im, 560, lerp(1150, 1080, up), 1.0)
        if tube < 1:
            out = Image.eval(out, lambda v: int(v * (0.1 + 0.9 * tube)))
        return out
    return pick(lt, c, [a, b, cc])


# ================================================================ escena 10
def scene10(lt, dur):
    c = [snap(dur * 0.25), snap(dur * 0.5), snap(dur * 0.75)]

    def cell_n(t, door=0.0, girl=None, fog=0.0, wg=0.0, eye=0.0, talk=0.0):
        im = cell_world(t, night=True, tube=0.0, door_open=door, girl=girl, window_fog=fog, win_girl=wg)
        glow(im, 540, 260, 520, (20, 50, 46), 0.4)
        d = ImageDraw.Draw(im)
        seated(d, 300, 1300, 660, 1, PAT, DKB, TAN, pants=PAT, bun=True, band=True, arms="lap", chair=None, eye=eye, talk=talk)
        return im

    def a(t):
        im = cell_n(t, talk=0.5 + 0.5 * math.sin(t * 11))
        return camera(im, 380, 1120, lerp(1.9, 1.7, t / c[0]))

    def b(t):
        u = t - c[0]
        L = c[1] - c[0]
        return door_close_fog_sil(t, sstep(0.0, L * 0.6, u), sstep(L * 0.3, L, u))

    def cc(t):
        u = t - c[1]
        L = c[2] - c[1]
        op = sstep(0.0, L, u)
        im = cell_n(t, door=op, girl=(800, 1500, 648, 0.0), eye=1.0)
        return camera(im, 560, 1150, 1.15)

    def dd(t):
        u = t - c[2]
        L = dur - c[2]
        hand = sstep(0.0, 0.9, u)
        im = cell_n(t, door=1.0, girl=(800, 1500, 648, hand), eye=1.0)
        hx, hy = 800 + 648 * 0.105 * 0.5, 852 + 648 * 0.1
        z = lerp(1.15, 2.4, sstep(0.3, L - 0.5, u))
        out = camera(im, lerp(560, hx, sstep(0.3, L - 0.5, u)), lerp(1150, hy + 100, sstep(0.3, L - 0.5, u)), z)
        k = sstep(L - 0.45, L, u)
        if k > 0:
            out = blend(out, Image.new("RGB", (W, H), (214, 224, 222)), k)
        return out
    return pick(lt, c, [a, b, cc, dd])


def door_close_fog_sil(t, fog, sil):
    im = door_close(t, fog=fog)
    if sil > 0:
        lay = Image.new("RGB", (W, H), (0, 0, 0))
        m = Image.new("L", (W, H), 0)
        sp = girl_sprite(1500)
        a = sp.split()[3].filter(ImageFilter.GaussianBlur(18)).point(lambda v: int(v * 0.75 * sil))
        m.paste(a, (int(540 - sp.size[0] / 2), 480), a)
        mask = Image.new("L", (W, H), 0)
        ImageDraw.Draw(mask).rectangle((190, 420, 890, 1180), fill=255)
        m = ImageChops.multiply(m, mask)
        im.paste((40, 54, 52), (0, 0), m)
        d = ImageDraw.Draw(im)
        d.rectangle((160, 390, 920, 1210), outline=(70, 78, 80), width=40)
        d.line((540, 420, 540, 1180), fill=(70, 78, 80), width=10)
    return im


# ================================================================ escenas 11-12: sala de cine
def door_content(lt, sil=1.0):
    w, h = 1020, 580
    im = vgrad(w, h, [(0, (20, 30, 30)), (1, (10, 14, 14))])
    d = ImageDraw.Draw(im)
    d.rectangle((420, 70, 640, 560), fill=(196, 226, 214))
    glow(im, 530, 320, 380, (60, 120, 100), 0.6)
    if sil > 0:
        girl_silhouette(im, 530, 552, 400, (8, 10, 12), alpha=sil)
    d = ImageDraw.Draw(im)
    d.polygon([(640, 70), (700, 40), (700, 590), (640, 560)], fill=(40, 50, 52))
    d.rectangle((0, 560, w, h), fill=(30, 36, 36))
    return im


def spect_profile(lt, light=1.0):
    im = vgrad(W, H, [(0, (10, 8, 12)), (1, (6, 4, 6))])
    d = ImageDraw.Draw(im)
    for i in range(4):
        seat_back(d, 120 + i * 300, 1560, 230, shade(CRIMSON, 0.4))
    x, hy, r = 620, 900, 150
    d.rounded_rectangle((x - 300, 1150, x + 260, H + 100), radius=140, fill=(40, 38, 36))
    d.ellipse((x - 250, 1060, x + 160, 1260), fill=MUSTARD)
    d.ellipse((x - 190, 1090, x + 100, 1220), fill=MUSTARD_D)
    d.rectangle((x - r * 0.45, hy + r * 0.5, x + r * 0.45, 1140), fill=SKIN_D)
    head_profile(d, x, hy, r, -1, DARKHAIR, SKIN, "short", beard=(46, 36, 30), smile=0.0)
    d.chord((x - r * 0.2, hy - r * 0.2, x + r * 1.02, hy + r * 0.85), 280, 350, fill=shade(DARKHAIR, 1.8))
    # mano en el mentón (pensativo)
    d.line((x - 60, 1500, x - 150, 1160), fill=(40, 38, 36), width=90)
    d.ellipse((x - 200, 1050, x - 90, 1170), fill=SKIN)
    glow(im, 0, 900, 900, (110, 140, 150), 0.45 * light)
    rim = lerpc((60, 70, 80), (200, 220, 230), light)
    d = ImageDraw.Draw(im)
    d.arc((x - r, hy - r, x + r, hy + r), 120, 250, fill=rim, width=6)
    return im


def scene11(lt, dur):
    im = cinema_world(lt, door_content(lt))
    cx, cy, z = cam_path(lt, [(0, 540, 890, 3.2), (dur * 0.7, 540, 950, 1.1), (dur, 540, 960, 1.05)])
    out = camera(im, cx, cy, z)
    k = 1 - sstep(0.0, 0.35, lt)
    if k > 0:
        out = blend(out, Image.new("RGB", (W, H), (214, 224, 222)), k)
    return out


def scene12(lt, dur):
    c = [snap(dur * 0.36), snap(dur * 0.68)]

    def a(t):
        A = camera(cinema_world(t, door_content(t)), 540, 960, 1.05)
        Bp = spect_profile(t)
        return whip(A, Bp, sstep(0.1, 1.0, t))

    def b(t):
        u = t - c[0]
        L = c[1] - c[0]
        sil = 1 - sstep(0.1, L, u)
        beam = 1.0 if int(u * 14) % 4 else 0.45
        im = cinema_world(t, door_content(t, sil), beam=beam)
        return camera(im, 540, 980, lerp(1.1, 1.05, u / L))

    def cc(t):
        u = t - c[1]
        L = dur - c[1]
        dim = 1 - 0.65 * sstep(0, L - 0.6, u)
        im = cinema_world(t, door_content(t, 0.0), beam=dim, dim=dim)
        out = camera(im, 540, 960, 1.05)
        k = sstep(L - 0.9, L - 0.05, u)
        if k > 0:
            out = Image.eval(out, lambda v: int(v * (1 - k)))
        return out
    return pick(lt, c, [a, b, cc])


# ================================================================ textos
def title_card(img, a):
    if a <= 0:
        return
    l1, l2 = "Espíritus ocultos:", "En compañía del miedo"
    size = 72
    while True:
        big = font(FONT_B, size)
        if ImageDraw.Draw(img).textlength(l2, font=big) <= 900:
            break
        size -= 2
    small = font(FONT_R, 40)
    layer = Image.new("L", (W, 460), 0)
    ld = ImageDraw.Draw(layer)
    for txt, y, f in ((l1, 70, big), (l2, 70 + size + 20, big), ("Gothika · 2003", 70 + 2 * size + 80, small)):
        tw = ld.textlength(txt, font=f)
        ld.text(((W - tw) / 2, y), txt, font=f, fill=255)
    y = 140
    band = Image.new("L", (W, 600), 0)
    ImageDraw.Draw(band).rounded_rectangle((60, 110, W - 60, 470), radius=60, fill=215)
    band = band.filter(ImageFilter.GaussianBlur(45))
    img.paste((8, 6, 8), (0, y - 60), band.point(lambda v: int(v * a)))
    sh = layer.filter(ImageFilter.GaussianBlur(8))
    img.paste((0, 0, 0), (0, y), sh.point(lambda v: int(v * 0.8 * a)))
    img.paste((240, 236, 226), (0, y), layer.point(lambda v: int(v * a)))
    ld2 = Image.new("L", (W, 460), 0)
    yl = 70 + 2 * size + 58
    ImageDraw.Draw(ld2).rectangle(((W - 220) / 2, yl, (W + 220) / 2, yl + 4), fill=255)
    img.paste(CRIMSON, (0, y), ld2.point(lambda v: int(v * a)))


def keyword(img, t, t0, t1, txt):
    a = sstep(t0, t0 + 0.2, t) * (1 - sstep(t1 - 0.2, t1, t))
    if a <= 0:
        return
    s = 1 + 0.12 * (1 - sstep(t0, t0 + 0.25, t))
    f = font(FONT_N, int(84 * s))
    lay = Image.new("L", (W, 300), 0)
    ld = ImageDraw.Draw(lay)
    tw = ld.textlength(txt, font=f)
    bx0, bx1 = (W - tw) / 2 - 40, (W + tw) / 2 + 40
    band = Image.new("L", (W, 300), 0)
    ImageDraw.Draw(band).rectangle((bx0, 70, bx1, 70 + 84 * s + 50), fill=255)
    y = 330
    img.paste(CRIMSON, (0, y), band.point(lambda v: int(v * 0.92 * a)))
    ld.text(((W - tw) / 2, 82), txt, font=f, fill=255)
    img.paste((246, 240, 228), (0, y), lay.point(lambda v: int(v * a)))


def overlays(img, t):
    keyword(img, t, B[0] + 3.9, B[0] + 6.4, "ACUSADA")
    keyword(img, t, B[7] + 2.3, B[7] + 4.6, "SOLO TÚ LA VES")


SCENES = [scene1, scene2, scene3, scene4, scene5, scene6, scene7, scene8, scene9, scene10, scene11, scene12]

FOG = {
    0: ((60, 60, 70), 0.08), 1: ((150, 190, 170), 0.10), 2: ((60, 80, 110), 0.18), 3: ((60, 80, 110), 0.14),
    4: ((170, 210, 190), 0.08), 5: ((150, 190, 170), 0.10), 6: ((40, 90, 60), 0.18), 7: ((170, 200, 186), 0.10),
    8: ((150, 190, 170), 0.10), 9: ((40, 70, 66), 0.16), 10: ((60, 60, 70), 0.08), 11: ((60, 60, 70), 0.08),
}
