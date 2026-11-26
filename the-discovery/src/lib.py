import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageFont

W, H = 1080, 1920
FPS = 30

MUSTARD = (214, 150, 40)
MUSTARD_D = (160, 105, 25)
CRIMSON = (140, 24, 38)
CRIMSON_D = (80, 12, 22)
COAT = (38, 42, 50)
SKIN = (196, 156, 128)
SKIN_D = (150, 112, 92)
DARKHAIR = (28, 24, 22)
WHITEHAIR = (226, 226, 220)
SWEATER = (122, 124, 128)
GREEN = (38, 74, 58)
BROWNHAIR = (98, 64, 40)
WORK = (98, 82, 56)
FOLLOW = (118, 120, 124)

FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
FONT_R = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
FONT_N = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
_fonts = {}


def font(path, size):
    k = (path, size)
    if k not in _fonts:
        _fonts[k] = ImageFont.truetype(path, size)
    return _fonts[k]


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def sstep(a, b, x):
    if b == a:
        return 1.0 if x >= b else 0.0
    t = clamp((x - a) / (b - a))
    return t * t * (3 - 2 * t)


def lerp(a, b, t):
    return a + (b - a) * t


def lerpc(c1, c2, t):
    return tuple(int(lerp(a, b, t)) for a, b in zip(c1, c2))


def shade(c, k):
    return tuple(int(clamp(v * k, 0, 255)) for v in c)


def vgrad(w, h, stops):
    """stops: list of (pos, color)"""
    ys = np.linspace(0, 1, h)
    out = np.zeros((h, 3))
    ps = [p for p, _ in stops]
    for ch in range(3):
        out[:, ch] = np.interp(ys, ps, [c[ch] for _, c in stops])
    arr = np.repeat(out[:, None, :], w, axis=1).astype(np.uint8)
    return Image.fromarray(arr, "RGB")


_glow_cache = {}


def glow_sprite(r, color, strength=1.0, power=2.0):
    k = (int(r), color, round(strength, 2), power)
    if k in _glow_cache:
        return _glow_cache[k]
    r = int(max(2, r))
    y, x = np.mgrid[-r:r + 1, -r:r + 1]
    d = np.sqrt(x * x + y * y) / r
    f = np.clip(1 - d, 0, 1) ** power * strength
    arr = np.zeros((2 * r + 1, 2 * r + 1, 3))
    for i in range(3):
        arr[..., i] = f * color[i]
    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")
    if len(_glow_cache) > 400:
        _glow_cache.clear()
    _glow_cache[k] = im
    return im


def glow(img, x, y, r, color, strength=1.0, power=2.0):
    sp = glow_sprite(r, color, strength, power)
    r = sp.size[0] // 2
    x0, y0 = int(x) - r, int(y) - r
    box = (x0, y0, x0 + sp.size[0], y0 + sp.size[1])
    bx = (max(0, box[0]), max(0, box[1]), min(img.size[0], box[2]), min(img.size[1], box[3]))
    if bx[2] <= bx[0] or bx[3] <= bx[1]:
        return
    reg = img.crop(bx)
    spc = sp.crop((bx[0] - x0, bx[1] - y0, bx[2] - x0, bx[3] - y0))
    img.paste(ImageChops.add(reg, spc), bx[:2])


def poly_a(img, pts, color, alpha, blur=0):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    pad = int(blur * 3) + 2
    x0, y0 = int(min(xs)) - pad, int(min(ys)) - pad
    x1, y1 = int(max(xs)) + pad, int(max(ys)) + pad
    m = Image.new("L", (x1 - x0, y1 - y0), 0)
    ImageDraw.Draw(m).polygon([(p[0] - x0, p[1] - y0) for p in pts], fill=int(255 * clamp(alpha)))
    if blur:
        m = m.filter(ImageFilter.GaussianBlur(blur))
    img.paste(color, (x0, y0), m)


def ell_a(img, box, color, alpha, blur=0):
    pad = int(blur * 3) + 2
    x0, y0 = int(box[0]) - pad, int(box[1]) - pad
    x1, y1 = int(box[2]) + pad, int(box[3]) + pad
    m = Image.new("L", (x1 - x0, y1 - y0), 0)
    ImageDraw.Draw(m).ellipse((box[0] - x0, box[1] - y0, box[2] - x0, box[3] - y0), fill=int(255 * clamp(alpha)))
    if blur:
        m = m.filter(ImageFilter.GaussianBlur(blur))
    img.paste(color, (x0, y0), m)


def rect_a(img, box, color, alpha):
    poly_a(img, [(box[0], box[1]), (box[2], box[1]), (box[2], box[3]), (box[0], box[3])], color, alpha)


def smooth_noise(w, h, scale, seed):
    rng = np.random.default_rng(seed)
    acc = np.zeros((h, w))
    amp = 1.0
    tot = 0
    for o in range(4):
        sw, sh = max(2, int(w / scale * 2 ** o)), max(2, int(h / scale * 2 ** o))
        n = rng.random((sh, sw))
        im = Image.fromarray((n * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
        acc += np.asarray(im, dtype=np.float32) / 255 * amp
        tot += amp
        amp *= 0.5
    acc /= tot
    acc = (acc - acc.min()) / (acc.max() - acc.min())
    return acc.astype(np.float32)


# ---------------------------------------------------------------- figures

def person_back(d, x, yf, h, coat, hair, skin=SKIN, hood=None, pants=(28, 28, 34), coatlen=0.55,
                step=0.0, legs=True, hairshape="short", arm_out=0.0, rim=None, collar=None):
    r = h * 0.068
    top = yf - h
    hy = top + r
    hw = h * 0.125
    shy = top + h * 0.185
    # legs
    if legs:
        lw = h * 0.055
        for s in (-1, 1):
            off = s * h * 0.045 + s * step * h * 0.03
            lift = max(0, s * step) * h * 0.03
            d.polygon([(x + off - lw / 2, top + h * 0.5), (x + off + lw / 2, top + h * 0.5),
                       (x + off + lw / 2 + step * s * h * 0.01, yf - lift), (x + off - lw / 2 + step * s * h * 0.01, yf - lift)],
                      fill=pants)
            d.ellipse((x + off - lw * 0.7, yf - lift - lw * 0.35, x + off + lw * 0.7, yf - lift + lw * 0.25), fill=(20, 20, 22))
    # arms
    aw = h * 0.05
    for s in (-1, 1):
        ax = x + s * (hw + aw * 0.35)
        ex = ax + s * arm_out * h * 0.12
        d.polygon([(ax - aw / 2, shy + h * 0.02), (ax + aw / 2, shy + h * 0.02),
                   (ex + aw / 2, top + h * 0.52), (ex - aw / 2, top + h * 0.52)], fill=shade(coat, 0.85))
        d.ellipse((ex - aw * 0.5, top + h * 0.5, ex + aw * 0.5, top + h * 0.56), fill=skin)
    # torso
    bot = top + h * (0.18 + coatlen)
    d.rounded_rectangle((x - hw, shy, x + hw, bot), radius=int(h * 0.05), fill=coat)
    d.polygon([(x - hw, shy + h * 0.1), (x - hw * 1.12, bot), (x + hw * 1.12, bot), (x + hw, shy + h * 0.1)], fill=coat)
    if collar:
        d.rounded_rectangle((x - hw * 0.55, shy - h * 0.01, x + hw * 0.55, shy + h * 0.05), radius=int(h * 0.02), fill=collar)
    if hood:
        d.ellipse((x - hw * 0.8, shy - h * 0.03, x + hw * 0.8, shy + h * 0.1), fill=hood)
        d.ellipse((x - hw * 0.55, shy - h * 0.0, x + hw * 0.55, shy + h * 0.07), fill=shade(hood, 0.72))
        d.line((x, shy + h * 0.1, x, bot), fill=shade(hood, 0.6), width=max(1, int(h * 0.006)))
    # neck
    d.rectangle((x - r * 0.45, hy + r * 0.6, x + r * 0.45, shy + h * 0.01), fill=SKIN_D)
    # head (back view)
    d.ellipse((x - r * 1.08, hy - r * 0.35, x - r * 0.82, hy + r * 0.25), fill=skin)
    d.ellipse((x + r * 0.82, hy - r * 0.35, x + r * 1.08, hy + r * 0.25), fill=skin)
    d.ellipse((x - r * 0.92, hy - r, x + r * 0.92, hy + r * 0.95), fill=hair)
    if hairshape == "bob":
        d.rounded_rectangle((x - r * 1.05, hy - r * 0.6, x + r * 1.05, hy + r * 1.05), radius=int(r * 0.5), fill=hair)
    if hairshape == "fade":
        d.ellipse((x - r * 0.92, hy + r * 0.1, x + r * 0.92, hy + r * 0.95), fill=shade(hair, 1.6))
        d.ellipse((x - r * 0.8, hy - r, x + r * 0.8, hy + r * 0.55), fill=hair)
    if rim:
        d.arc((x - r * 0.92, hy - r, x + r * 0.92, hy + r * 0.95), 200, 340, fill=rim, width=max(1, int(r * 0.12)))
        d.arc((x - hw, shy - h * 0.01, x + hw, shy + h * 0.2), 190, 350, fill=rim, width=max(1, int(r * 0.12)))
    return (x, hy, r)


def head_profile(d, x, hy, r, f, hair, skin=SKIN, style="short", beard=None, smile=0.0, wind=0.0, eye=True):
    d.ellipse((x - r, hy - r, x + r, hy + r), fill=skin)
    # nose
    d.polygon([(x + f * r * 0.85, hy - r * 0.2), (x + f * r * 1.18, hy + r * 0.22), (x + f * r * 0.86, hy + r * 0.3)], fill=skin)
    # jaw
    d.polygon([(x + f * r * 0.7, hy + r * 0.45), (x + f * r * 0.35, hy + r * 1.08), (x - f * r * 0.3, hy + r * 0.9)], fill=skin)
    if beard:
        d.polygon([(x + f * r * 0.75, hy + r * 0.5), (x + f * r * 0.35, hy + r * 1.12), (x - f * r * 0.45, hy + r * 0.8),
                   (x - f * r * 0.4, hy + r * 0.3)], fill=beard)
    if f > 0:
        a0, a1 = 95, 335
    else:
        a0, a1 = 205, 445
    d.chord((x - r * 1.03, hy - r * 1.06, x + r * 1.03, hy + r * 1.0), a0, a1, fill=hair)
    if style == "bob":
        bx = x - f * r * 0.15
        d.rounded_rectangle((bx - r * 1.0 - (wind * r * 0.3 if f > 0 else 0), hy - r * 0.4,
                             bx + r * 0.75 + (wind * r * 0.3 if f < 0 else 0), hy + r * 1.05),
                            radius=int(r * 0.4), fill=hair)
        d.ellipse((x - r * 0.25 + f * r * 0.1, hy - r * 0.05, x + r * 0.25 + f * r * 0.1, hy + r * 0.45), fill=skin)
        if wind > 0:
            for i in range(4):
                sx = x - f * r * (0.6 + 0.1 * i)
                d.line((sx, hy - r * (0.6 - 0.3 * i), sx - f * r * (0.5 + 0.3 * wind), hy - r * (0.7 - 0.35 * i) - wind * r * 0.2),
                       fill=hair, width=max(2, int(r * 0.12)))
    if eye:
        ex = x + f * r * 0.48
        d.ellipse((ex - r * 0.08, hy - r * 0.15, ex + r * 0.08, hy + r * 0.0), fill=(30, 26, 24))
        d.line((ex - r * 0.18, hy - r * 0.3, ex + r * 0.15 * f, hy - r * 0.28), fill=shade(hair, 0.8), width=max(1, int(r * 0.07)))
    # mouth
    mx = x + f * r * 0.78
    my = hy + r * 0.62
    d.line((mx - f * r * 0.22, my - smile * r * 0.08, mx, my), fill=SKIN_D, width=max(1, int(r * 0.06)))
    # ear
    d.ellipse((x - f * r * 0.15 - r * 0.15, hy - r * 0.05, x - f * r * 0.15 + r * 0.15, hy + r * 0.35), fill=SKIN_D)


def person_side(d, x, yf, h, f, coat, hair, skin=SKIN, style="short", pants=(28, 28, 34), coatlen=0.55,
                arms="down", step=0.0, beard=None, smile=0.0, wind=0.0, head_off=0.0, lean=0.0):
    r = h * 0.068
    top = yf - h
    hx = x + f * lean * h * 0.08
    hy = top + r + head_off
    shy = top + h * 0.185
    dep = h * 0.075
    # legs
    lw = h * 0.055
    for s in (-1, 1):
        ang = s * step * 0.45
        hipx, hipy = x, top + h * 0.5
        fx = hipx + math.sin(ang) * h * 0.5 * f
        d.line((hipx, hipy, fx, yf), fill=pants, width=int(lw))
        d.ellipse((fx - lw * 0.4, yf - lw * 0.4, fx + lw * 0.4 + f * lw * 0.9, yf + lw * 0.2), fill=(20, 20, 22))
    bot = top + h * (0.18 + coatlen)
    d.polygon([(x - dep + f * lean * h * 0.06, shy), (x + dep + f * lean * h * 0.06, shy),
               (x + dep * 1.15, bot), (x - dep * 1.15, bot)], fill=coat)
    d.ellipse((x - dep + f * lean * h * 0.06, shy - h * 0.02, x + dep + f * lean * h * 0.06, shy + h * 0.06), fill=coat)
    aw = int(h * 0.048)
    sx, sy = x + f * lean * h * 0.06, shy + h * 0.03
    if arms == "down":
        d.line((sx, sy, x + f * h * 0.02, top + h * 0.5), fill=shade(coat, 0.8), width=aw)
        d.ellipse((x + f * h * 0.02 - aw * 0.5, top + h * 0.49, x + f * h * 0.02 + aw * 0.5, top + h * 0.55), fill=skin)
    elif arms == "crossed":
        d.line((sx, sy, sx + f * h * 0.05, top + h * 0.36), fill=shade(coat, 0.8), width=aw)
        d.line((sx + f * h * 0.05, top + h * 0.36, sx + f * h * 0.1, top + h * 0.32), fill=shade(coat, 0.7), width=aw)
    elif arms == "rail":
        d.line((sx, sy, sx + f * h * 0.1, top + h * 0.38), fill=shade(coat, 0.8), width=aw)
        d.line((sx + f * h * 0.1, top + h * 0.38, sx + f * h * 0.2, top + h * 0.41), fill=shade(coat, 0.8), width=aw)
        d.ellipse((sx + f * h * 0.2 - aw * 0.5, top + h * 0.39, sx + f * h * 0.2 + aw * 0.5, top + h * 0.44), fill=skin)
    elif arms == "forward":
        d.line((sx, sy, sx + f * h * 0.17, top + h * 0.42), fill=shade(coat, 0.8), width=aw)
        d.ellipse((sx + f * h * 0.17 - aw * 0.5, top + h * 0.40, sx + f * h * 0.17 + aw * 0.5, top + h * 0.45), fill=skin)
    d.rectangle((hx - r * 0.4, hy + r * 0.5, hx + r * 0.4, shy + 2), fill=SKIN_D)
    head_profile(d, hx, hy, r, f, hair, skin, style, beard, smile, wind)
    return (hx, hy, r)


def seated_side(d, x, ys, h, f, top_col, hair, skin=SKIN, pants=(40, 40, 46), beard=None, smile=0.0, chair=(30, 30, 34)):
    """ys = seat height y. h = full standing height scale."""
    r = h * 0.068
    # chair
    d.rectangle((x - f * h * 0.1, ys - h * 0.33, x - f * h * 0.07, ys + h * 0.02), fill=chair)
    d.rectangle((x - f * h * 0.1, ys, x + f * h * 0.15, ys + h * 0.025), fill=chair)
    d.line((x - f * h * 0.08, ys, x - f * h * 0.08, ys + h * 0.25), fill=chair, width=int(h * 0.015))
    d.line((x + f * h * 0.13, ys, x + f * h * 0.13, ys + h * 0.25), fill=chair, width=int(h * 0.015))
    lw = int(h * 0.06)
    d.line((x, ys - lw * 0.3, x + f * h * 0.22, ys - lw * 0.3), fill=pants, width=lw)
    d.line((x + f * h * 0.22, ys - lw * 0.3, x + f * h * 0.24, ys + h * 0.25), fill=pants, width=lw)
    d.ellipse((x + f * h * 0.24 - lw * 0.4, ys + h * 0.24, x + f * h * 0.24 + lw * 0.4 + f * lw, ys + h * 0.27), fill=(20, 20, 22))
    shy = ys - h * 0.32
    dep = h * 0.08
    d.rounded_rectangle((x - dep, shy, x + dep, ys), radius=int(h * 0.03), fill=top_col)
    aw = int(h * 0.048)
    d.line((x + f * dep * 0.2, shy + h * 0.03, x + f * h * 0.08, ys - h * 0.12), fill=shade(top_col, 0.8), width=aw)
    d.line((x + f * h * 0.08, ys - h * 0.12, x + f * h * 0.2, ys - h * 0.08), fill=shade(top_col, 0.8), width=aw)
    d.ellipse((x + f * h * 0.2 - aw * 0.5, ys - h * 0.1, x + f * h * 0.2 + aw * 0.6, ys - h * 0.05), fill=skin)
    hy = shy - r * 1.4
    d.rectangle((x - r * 0.4, hy + r * 0.5, x + r * 0.4, shy + 2), fill=SKIN_D)
    head_profile(d, x + f * r * 0.15, hy, r, f, hair, skin, "short", beard, smile)


def bust_back(d, x, y, s, top_col, hair, skin=SKIN, hood=None, nod=0.0, rim=None, hairshape="short"):
    """head + shoulders from behind. y = shoulder line, s = shoulder width."""
    r = s * 0.27
    d.rounded_rectangle((x - s / 2, y, x + s / 2, y + s * 1.2), radius=int(s * 0.25), fill=top_col)
    if hood:
        d.ellipse((x - s * 0.33, y - s * 0.08, x + s * 0.33, y + s * 0.3), fill=hood)
        d.ellipse((x - s * 0.22, y - s * 0.02, x + s * 0.22, y + s * 0.2), fill=shade(hood, 0.72))
    hy = y - r * 0.9 + nod * r * 0.35
    d.rectangle((x - r * 0.45, hy, x + r * 0.45, y + 2), fill=SKIN_D)
    d.ellipse((x - r * 1.08, hy - r * 0.3, x - r * 0.82, hy + r * 0.3), fill=skin)
    d.ellipse((x + r * 0.82, hy - r * 0.3, x + r * 1.08, hy + r * 0.3), fill=skin)
    d.ellipse((x - r * 0.95, hy - r * 1.05, x + r * 0.95, hy + r * 0.85), fill=hair)
    if hairshape == "bob":
        d.rounded_rectangle((x - r * 1.05, hy - r * 0.6, x + r * 1.05, hy + r * 0.95), radius=int(r * 0.4), fill=hair)
    if hairshape == "fade":
        d.ellipse((x - r * 0.95, hy - r * 0.1, x + r * 0.95, hy + r * 0.85), fill=shade(hair, 1.7))
        d.ellipse((x - r * 0.85, hy - r * 1.05, x + r * 0.85, hy + r * 0.4), fill=hair)
    if rim:
        d.arc((x - r * 0.95, hy - r * 1.05, x + r * 0.95, hy + r * 0.85), 200, 340, fill=rim, width=max(2, int(r * 0.1)))
        d.arc((x - s / 2, y, x + s / 2, y + s * 0.6), 185, 355, fill=rim, width=max(2, int(r * 0.1)))


def seat_back(d, x, y, w, col=CRIMSON):
    d.rounded_rectangle((x - w / 2, y, x + w / 2, y + w * 1.1), radius=int(w * 0.25), fill=col)
    d.rounded_rectangle((x - w / 2 + w * 0.08, y + w * 0.08, x + w / 2 - w * 0.08, y + w * 1.0), radius=int(w * 0.2),
                        fill=shade(col, 1.18))


def _norm(b):
    if len(b) == 4 and not isinstance(b[0], (tuple, list)):
        x0, y0, x1, y1 = b
        return (min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))
    if len(b) == 2 and isinstance(b[0], (tuple, list)):
        (x0, y0), (x1, y1) = b
        return (min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))
    return b


def _wrap(name):
    orig = getattr(ImageDraw.ImageDraw, name)
    def f(self, xy, *a, **k):
        return orig(self, _norm(xy), *a, **k)
    setattr(ImageDraw.ImageDraw, name, f)


for _n in ("rectangle", "rounded_rectangle", "ellipse", "chord", "pieslice", "arc"):
    _wrap(_n)
