# Biblioteca de dibujo procedural (pintura digital estilizada)
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops

PW, PH = 864, 1536  # tamaño de plancha (1,2x el cuadro 720x1280)

def C(h):
    h = h.lstrip('#'); return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def mix(a, b, t): return tuple(int(a[i]*(1-t)+b[i]*t) for i in range(3))

def grad(top, bot, w=PW, h=PH, mid=None):
    top, bot = np.array(top, float), np.array(bot, float)
    y = np.linspace(0, 1, h)[:, None, None]
    if mid is not None:
        m = np.array(mid, float)
        arr = np.where(y < .5, top*(1-y*2)+m*(y*2), m*(1-(y-.5)*2)+bot*((y-.5)*2))
    else:
        arr = top*(1-y)+bot*y
    arr = np.repeat(arr, w, axis=1)
    return Image.fromarray(arr.astype(np.uint8), 'RGB')

def glow(img, xy, r, color, strength=1.0):
    """Luz aditiva radial."""
    w, h = img.size
    x0, y0 = xy
    yy, xx = np.mgrid[0:h, 0:w]
    d = np.sqrt((xx-x0)**2+(yy-y0)**2)/r
    m = np.clip(1-d, 0, 1)**2*strength
    a = np.asarray(img).astype(float)
    a += m[..., None]*np.array(color, float)[None, None, :]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))

def cone(img, apex, p1, p2, color, strength=0.7, blur=25):
    """Haz de luz (faros, linternas, proyector)."""
    m = Image.new('L', img.size, 0)
    ImageDraw.Draw(m).polygon([apex, p1, p2], fill=int(255*strength))
    m = m.filter(ImageFilter.GaussianBlur(blur))
    a = np.asarray(img).astype(float)
    mm = np.asarray(m).astype(float)/255
    a += mm[..., None]*np.array(color, float)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))

def tint_rect(img, box, color, alpha):
    ov = Image.new('RGB', img.size, color)
    m = Image.new('L', img.size, 0)
    ImageDraw.Draw(m).rectangle(box, fill=int(255*alpha))
    return Image.composite(ov, img, m)

def paint(img, blur=1.1, tex=10, seed=0):
    """Acabado pictórico: suavizado + textura de pincel + polvo."""
    img = img.filter(ImageFilter.GaussianBlur(blur))
    rng = np.random.default_rng(seed)
    n = rng.normal(0, 1, (PH//6+1, PW//6+1))
    n = np.asarray(Image.fromarray(((n+3)*40).clip(0, 255).astype(np.uint8)).resize(img.size, Image.BICUBIC)).astype(float)/255-.5
    a = np.asarray(img).astype(float)+n[..., None]*tex
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))

# ---------------- paisaje ----------------
def mountains(d, base, amp, color, seed, snowcap=None, w=PW, step=36):
    rng = random.Random(seed)
    pts = [(0, base)]
    x = -20
    peaks = []
    while x < w+60:
        y = base-amp*(0.45+0.55*rng.random())
        pts.append((x, y)); peaks.append((x, y))
        x += step+rng.randint(0, step)
        pts.append((x, base-amp*0.25*rng.random()))
        x += step//2
    pts += [(w+60, base), (w+60, PH), (0, PH)]
    d.polygon(pts, fill=color)
    if snowcap:
        for (px, py) in peaks:
            d.polygon([(px, py), (px-18, py+28), (px-4, py+22), (px+6, py+32), (px+16, py+24)], fill=snowcap)

def trees(d, y, n, color, seed, hmin=60, hmax=140, x0=0, x1=PW, snow=None):
    rng = random.Random(seed)
    for _ in range(n):
        x = rng.uniform(x0, x1); h = rng.uniform(hmin, hmax); yy = y+rng.uniform(-10, 10)
        for k in range(3):
            ww = h*(0.32-k*0.07); top = yy-h+k*h*0.22
            d.polygon([(x, top), (x-ww, yy-k*h*0.25), (x+ww, yy-k*h*0.25)], fill=color)
            if snow:
                d.polygon([(x, top), (x-ww*0.4, top+h*0.12), (x+ww*0.4, top+h*0.12)], fill=snow)

def city(d, base, x0, x1, seed, scale=1.0, lit=0.45, smoke=True, win=(255, 214, 140)):
    rng = random.Random(seed)
    x = x0
    while x < x1:
        bw = rng.randint(14, 34)*scale; bh = rng.randint(30, 120)*scale
        col = mix((22, 30, 44), (34, 44, 58), rng.random())
        d.rectangle([x, base-bh, x+bw, base], fill=col)
        dark_block = rng.random() < 0.35  # barrios sin luz
        for wy in np.arange(base-bh+4*scale, base-4*scale, 7*scale):
            for wx in np.arange(x+3*scale, x+bw-3*scale, 6*scale):
                if not dark_block and rng.random() < lit:
                    d.rectangle([wx, wy, wx+2.4*scale, wy+3*scale], fill=mix(win, (255, 120, 60), rng.random()*0.3))
        x += bw+rng.randint(0, 4)*scale

def smoke_column(img, x, ybot, h, seed, color=(70, 70, 72), alpha=0.55):
    rng = random.Random(seed)
    m = Image.new('L', img.size, 0); dm = ImageDraw.Draw(m)
    for k in range(26):
        t = k/25; r = 10+t*h*0.25
        cx = x+math.sin(t*3+seed)*h*0.12+t*h*0.25; cy = ybot-t*h
        dm.ellipse([cx-r, cy-r*0.8, cx+r, cy+r*0.8], fill=int(255*alpha*(1-t*0.6)))
    m = m.filter(ImageFilter.GaussianBlur(9))
    return Image.composite(Image.new('RGB', img.size, color), img, m)

def snow_ground(d, y, color=(178, 196, 222), shade=(120, 140, 175), seed=0, w=PW):
    d.rectangle([0, y, w, PH], fill=color)
    rng = random.Random(seed)
    for _ in range(40):
        x = rng.uniform(0, w); yy = rng.uniform(y, PH); r = rng.uniform(20, 120)
        d.ellipse([x-r, yy-r*0.12, x+r, yy+r*0.12], fill=mix(color, shade, rng.uniform(.2, .6)))

# ---------------- personas (adultos, sin rasgos reales) ----------------
REP = dict(coat=(28, 40, 74), stripe=(150, 158, 168), pants=(40, 40, 48), skin=(206, 160, 130), hair=(96, 64, 40), hat=(120, 122, 128), pack=True)
NOVIA = dict(coat=(232, 220, 196), pants=(70, 60, 60), skin=(214, 172, 146), hair=(16, 14, 16), hat=None, longhair=True)
MUJER = dict(coat=(98, 24, 40), pants=(40, 30, 30), skin=(214, 206, 196), hair=(196, 170, 110), hat=None, longhair=True, longcoat=True)
POLI = dict(coat=(24, 32, 56), pants=(24, 30, 50), skin=(200, 150, 120), hair=(140, 140, 140), hat=(90, 70, 52), stache=True)
GRANJ = dict(coat=(150, 34, 34), pants=(52, 70, 100), skin=(150, 150, 140), hair=(220, 220, 220), hat=None, beard=True)
EMP1 = dict(coat=(176, 180, 182), pants=(160, 164, 166), skin=(196, 150, 120), hair=(30, 26, 24), hat=None, glasses=True, mask=True)
EMP2 = dict(coat=(176, 180, 182), pants=(160, 164, 166), skin=(204, 164, 136), hair=(14, 14, 16), hat=None, braid=True, mask=True)
DESP = dict(coat=(226, 110, 30), pants=(46, 46, 56), skin=(180, 130, 100), hair=(30, 26, 22), hat=None)
ENF = dict(coat=(120, 176, 170), pants=(120, 176, 170), skin=(210, 168, 140), hair=(50, 34, 26), hat=None, bun=True)
ESPECT = dict(coat=(30, 30, 36), pants=(26, 26, 30), skin=(170, 130, 110), hair=(26, 22, 20), hat=None)

def _P(x, yf, h, pts, flip=1):
    return [(x+px*h*flip, yf+py*h) for px, py in pts]

def person(d, x, yf, h, P, view='back', pose='stand', flip=1, rim=None):
    """Adulto de ~7,5 cabezas. view: back | side | front (contraluz, sin rasgos)."""
    coat, pants, skin = P['coat'], P['pants'], P['skin']
    dk = mix(coat, (0, 0, 0), .35)
    # piernas
    if pose == 'run':
        legs = [[(-0.02, -0.47), (0.04, -0.47), (0.17, -0.06), (0.12, -0.02)],
                [(-0.04, -0.47), (0.02, -0.47), (-0.10, -0.24), (-0.20, -0.10), (-0.22, -0.14), (-0.13, -0.26)]]
    elif pose == 'lie':
        d.polygon(_P(x, yf, h, [(-0.5, -0.03), (0.38, -0.07), (0.42, 0), (-0.5, 0.02)], flip), fill=coat)
        d.ellipse([x+0.38*h*flip-0.06*h, yf-0.10*h, x+0.38*h*flip+0.08*h, yf+0.02*h], fill=P['hair'])
        d.polygon(_P(x, yf, h, [(-0.3, -0.06), (0.25, -0.09), (0.28, -0.05), (-0.3, -0.02)], flip), fill=mix(coat, (255, 255, 255), .12))
        return
    elif pose == 'sit':
        legs = []
    else:
        legs = [[(-0.075, -0.47), (-0.01, -0.47), (-0.012, 0), (-0.07, 0)],
                [(0.01, -0.47), (0.075, -0.47), (0.07, 0), (0.012, 0)]]
    for L in legs:
        d.polygon(_P(x, yf, h, L, flip), fill=pants)
    if legs:
        for sx in ((-0.045, 0.045) if pose != 'run' else (0.15, -0.21)):
            if pose == 'run':
                pass
            d.ellipse([x+(sx-0.04)*h*flip-0.01*h, yf-0.03*h, x+(sx+0.04)*h*flip, yf+0.005*h], fill=(20, 20, 22)) if pose != 'run' else None
    # torso
    hem = -0.20 if P.get('longcoat') else -0.42
    if view == 'side':
        torso = [(-0.07, -0.82), (0.07, -0.82), (0.09, -0.6), (0.08, hem), (-0.08, hem), (-0.09, -0.6)]
    else:
        torso = [(-0.13, -0.81), (0.13, -0.81), (0.12, -0.6), (0.11, hem), (-0.11, hem), (-0.12, -0.6)]
    d.polygon(_P(x, yf, h, torso, flip), fill=coat)
    # mochila médica blanca (vista de espaldas o perfil)
    if P.get('pack') and view in ('back', 'side'):
        if view == 'back':
            d.rounded_rectangle([x-0.10*h, yf-0.79*h, x+0.10*h, yf-0.54*h], radius=0.03*h, fill=(232, 236, 238))
            d.rectangle([x-0.10*h, yf-0.79*h, x+0.10*h, yf-0.765*h], fill=(20, 20, 22))
            d.rectangle([x-0.02*h, yf-0.71*h, x+0.02*h, yf-0.61*h], fill=(196, 40, 46)); d.rectangle([x-0.05*h, yf-0.68*h, x+0.05*h, yf-0.64*h], fill=(196, 40, 46))
        else:
            bx = x-0.17*h*flip
            d.rounded_rectangle([min(bx, bx+0.1*h*flip), yf-0.80*h, max(bx, bx+0.1*h*flip), yf-0.55*h], radius=0.02*h, fill=(232, 236, 238))
    # brazos
    if pose == 'give':
        arms = [[(0.05, -0.80), (0.11, -0.80), (0.33, -0.62), (0.30, -0.57)]]
    elif pose == 'run':
        arms = [[(0.03, -0.80), (0.09, -0.78), (0.22, -0.66), (0.18, -0.62)], [(-0.06, -0.8), (0.0, -0.8), (-0.14, -0.6), (-0.19, -0.62)]]
    elif pose == 'knock':
        arms = [[(0.04, -0.80), (0.10, -0.80), (0.24, -0.88), (0.22, -0.93)]]
    elif pose == 'flash':
        arms = [[(0.05, -0.80), (0.11, -0.80), (0.30, -0.72), (0.28, -0.67)]]
    elif view == 'side' or pose == 'sit':
        arms = [[(-0.03, -0.80), (0.04, -0.80), (0.05, -0.50), (-0.01, -0.50)]]
    else:
        arms = [[(-0.16, -0.80), (-0.10, -0.80), (-0.11, -0.49), (-0.17, -0.49)], [(0.10, -0.80), (0.16, -0.80), (0.17, -0.49), (0.11, -0.49)]]
    for A in arms:
        d.polygon(_P(x, yf, h, A, flip), fill=dk)
        if P.get('stripe'):
            (ax, ay), (bx2, by), (cx, cy), (ddx, ddy) = A
            t = .55
            s = [(ax+(ddx-ax)*t, ay+(ddy-ay)*t), (bx2+(cx-bx2)*t, by+(cy-by)*t), (bx2+(cx-bx2)*(t+.08), by+(cy-by)*(t+.08)), (ax+(ddx-ax)*(t+.08), ay+(ddy-ay)*(t+.08))]
            d.polygon(_P(x, yf, h, s, flip), fill=P['stripe'])
        hx, hy = A[2]
        d.ellipse([x+hx*h*flip-0.025*h, yf+hy*h-0.025*h, x+hx*h*flip+0.025*h, yf+hy*h+0.025*h], fill=skin if view != 'front' else mix(skin, (0, 0, 0), .5))
    # cuello y cabeza
    hc = (x, yf-0.895*h)
    rx, ry = 0.058*h, 0.068*h
    d.rectangle([x-0.025*h, yf-0.85*h, x+0.025*h, yf-0.80*h], fill=mix(skin, (0, 0, 0), .2))
    if view == 'back':
        d.ellipse([hc[0]-rx, hc[1]-ry, hc[0]+rx, hc[1]+ry], fill=P['hair'])
        if P.get('longhair'):
            d.polygon([(x-rx, hc[1]), (x+rx, hc[1]), (x+rx*1.2, yf-0.66*h), (x-rx*1.2, yf-0.66*h)], fill=P['hair'])
        if P.get('braid'):
            d.rectangle([x-0.012*h, hc[1], x+0.012*h, yf-0.62*h], fill=P['hair'])
    elif view == 'side':
        fs = mix(skin, (0, 0, 0), .05)
        d.ellipse([hc[0]-rx, hc[1]-ry, hc[0]+rx, hc[1]+ry], fill=fs)
        d.polygon([(x+rx*0.8*flip, hc[1]-ry*0.1), (x+rx*1.28*flip, hc[1]+ry*0.25), (x+rx*0.85*flip, hc[1]+ry*0.35)], fill=fs)  # nariz
        d.pieslice([hc[0]-rx, hc[1]-ry, hc[0]+rx, hc[1]+ry], 180 if flip > 0 else 270, 270 if flip > 0 else 360, fill=P['hair'])
        d.rectangle([min(x, x-rx*flip), hc[1]-ry*0.2, max(x, x-rx*flip), hc[1]+ry*0.5], fill=P['hair'])
        if P.get('stubble') or P is REP:
            d.chord([hc[0]-rx*0.2, hc[1]+ry*0.1, hc[0]+rx*1.1, hc[1]+ry*1.0], 0, 180, fill=mix(fs, P['hair'], .45))
        if P.get('beard'):
            d.chord([hc[0]-rx*0.5, hc[1]-ry*0.1, hc[0]+rx*1.1, hc[1]+ry*1.25], 0, 180, fill=P['hair'])
        if P.get('stache'):
            d.rectangle([x+rx*0.55*flip-3, hc[1]+ry*0.42, x+rx*1.05*flip, hc[1]+ry*0.55], fill=P['hair'])
        if P.get('longhair'):
            d.polygon([(x-rx*flip, hc[1]-ry*0.5), (x+rx*0.2*flip, hc[1]-ry), (x-rx*1.25*flip, yf-0.66*h), (x-rx*0.2*flip, yf-0.66*h)], fill=P['hair'])
    else:  # front: contraluz, sin rasgos faciales
        d.ellipse([hc[0]-rx, hc[1]-ry, hc[0]+rx, hc[1]+ry], fill=mix(skin, (0, 0, 0), .55))
        d.chord([hc[0]-rx, hc[1]-ry, hc[0]+rx, hc[1]+ry*0.3], 180, 360, fill=P['hair'])
        if P.get('beard'):
            d.chord([hc[0]-rx, hc[1]-ry*0.3, hc[0]+rx, hc[1]+ry*1.25], 0, 180, fill=mix(P['hair'], (0, 0, 0), .3))
        if P.get('glasses'):
            d.line([hc[0]-rx*0.8, hc[1], hc[0]+rx*0.8, hc[1]], fill=(20, 20, 20), width=max(1, int(0.01*h)))
        if P.get('mask'):
            d.rectangle([x-rx*0.7, yf-0.82*h, x+rx*0.7, yf-0.80*h], fill=(220, 224, 226))
        if P.get('braid'):
            d.rectangle([x+rx*0.7, hc[1], x+rx*0.95, yf-0.68*h], fill=P['hair'])
    if P.get('hat'):
        d.chord([hc[0]-rx*1.05, hc[1]-ry*1.15, hc[0]+rx*1.05, hc[1]+ry*0.35], 180, 360, fill=P['hat'])
    if P.get('bun') and view != 'front':
        d.ellipse([x-0.03*h-rx*0.6*flip, hc[1]-ry*1.2, x+0.03*h-rx*0.6*flip, hc[1]-ry*0.5], fill=P['hair'])
    if rim:
        pass

def creature(d, x, yf, h, seed, color=(14, 22, 20)):
    """Silueta encorvada con crecimientos irregulares (sin sangre)."""
    rng = random.Random(seed)
    lean = 0.18
    d.polygon(_P(x, yf, h, [(-0.07, -0.47), (-0.01, -0.47), (-0.05, 0), (-0.10, 0)]), fill=color)
    d.polygon(_P(x, yf, h, [(0.01, -0.47), (0.07, -0.47), (0.09, -0.02), (0.03, 0)]), fill=color)
    d.polygon(_P(x, yf, h, [(-0.11, -0.47), (0.10, -0.47), (0.16+lean, -0.76), (-0.04+lean, -0.82)]), fill=color)
    d.ellipse([x+(0.13+lean)*h, yf-0.80*h, x+(0.25+lean)*h, yf-0.68*h], fill=color)
    d.polygon(_P(x, yf, h, [(0.08+lean, -0.76), (0.13+lean, -0.74), (0.12, -0.40), (0.08, -0.40)]), fill=color)
    d.polygon(_P(x, yf, h, [(-0.02+lean, -0.8), (0.03+lean, -0.8), (-0.12, -0.45), (-0.17, -0.47)]), fill=color)
    for _ in range(7):
        px = x+(rng.uniform(-0.1, 0.25))*h; py = yf-rng.uniform(0.55, 0.85)*h; r = rng.uniform(0.025, 0.07)*h
        d.ellipse([px-r, py-r, px+r, py+r*0.8], fill=mix(color, (30, 60, 40), rng.random()*.5))
    for _ in range(3):
        sx = x+rng.uniform(0, 0.2)*h; sy = yf-rng.uniform(0.6, 0.8)*h
        pts = [(sx+math.sin(k*0.7+seed)*0.03*h+k*0.02*h*rng.choice([-1, 1]), sy-k*0.03*h) for k in range(6)]
        d.line(pts, fill=color, width=max(2, int(0.015*h)))

def dog(d, x, yf, h, seed=3, color=(16, 22, 20), flip=1):
    """Perro grande deforme: boca abierta antinatural con tentáculos oscuros."""
    rng = random.Random(seed)
    L = h*1.6
    f = flip
    d.ellipse([x-L*0.45, yf-h*0.95, x+L*0.35, yf-h*0.45], fill=color)
    for lx in (-0.35, -0.2, 0.15, 0.28):
        d.polygon([(x+lx*L*f, yf-h*0.6), (x+(lx+0.07)*L*f, yf-h*0.6), (x+(lx+0.1)*L*f, yf), (x+(lx+0.02)*L*f, yf)], fill=color)
    hx = x+0.42*L*f; hy = yf-h*0.92
    d.ellipse([hx-h*0.25, hy-h*0.22, hx+h*0.2, hy+h*0.18], fill=color)
    d.polygon([(hx, hy-h*0.05), (hx+h*0.55*f, hy-h*0.35), (hx+h*0.5*f, hy-h*0.15)], fill=color)
    d.polygon([(hx, hy+h*0.05), (hx+h*0.55*f, hy+h*0.32), (hx+h*0.48*f, hy+h*0.14)], fill=color)
    d.polygon([(hx+h*0.05*f, hy-h*0.02), (hx+h*0.48*f, hy-h*0.15), (hx+h*0.45*f, hy+h*0.12)], fill=(46, 70, 52))
    for k in range(5):
        a = -0.6+k*0.3
        pts = []
        for s in range(8):
            r = s*h*0.09
            pts.append((hx+h*0.3*f+math.cos(a+math.sin(s*0.9+k)*0.5)*r*f, hy+math.sin(a+math.sin(s*0.9+k)*0.5)*r))
        d.line(pts, fill=color, width=max(2, int(h*0.04*(1-k*0.1))))
    for _ in range(5):
        px = x+rng.uniform(-0.4, 0.3)*L; py = yf-h*rng.uniform(0.75, 1.0); r = h*rng.uniform(0.05, 0.12)
        d.ellipse([px-r, py-r, px+r, py+r], fill=mix(color, (30, 50, 36), .4))
    d.polygon([(x-0.43*L*f, yf-h*0.8), (x-0.6*L*f, yf-h*1.05), (x-0.55*L*f, yf-h*0.75)], fill=color)

# ---------------- vehículos ----------------
def car(d, x, yf, w, color=(128, 132, 138), view='side', flip=1, lights=True):
    h = w*0.36
    if view == 'side':
        body = [(-0.5, -0.12), (-0.48, -0.5), (0.5, -0.5), (0.52, -0.15), (0.52, -0.05), (-0.5, -0.05)]
        cab = [(-0.32, -0.5), (-0.2, -0.92), (0.2, -0.92), (0.36, -0.5)]
        d.polygon([(x+px*w*f(flip), yf+py*h) for px, py in cab], fill=mix(color, (0, 0, 0), .15))
        d.polygon([(x+px*w*f(flip), yf+py*h) for px, py in [(-0.27, -0.52), (-0.18, -0.86), (-0.02, -0.86), (-0.02, -0.52)]], fill=(40, 52, 70))
        d.polygon([(x+px*w*f(flip), yf+py*h) for px, py in [(0.02, -0.52), (0.02, -0.86), (0.18, -0.86), (0.31, -0.52)]], fill=(40, 52, 70))
        d.polygon([(x+px*w*f(flip), yf+py*h) for px, py in body], fill=color)
        d.line([(x-0.45*w, yf-0.33*h), (x+0.48*w, yf-0.33*h)], fill=mix(color, (255, 255, 255), .3), width=2)
        for wx in (-0.3, 0.3):
            r = 0.13*w
            d.ellipse([x+wx*w-r, yf-r*1.1, x+wx*w+r, yf+r*0.9], fill=(16, 16, 18))
            d.ellipse([x+wx*w-r*0.5, yf-r*0.6, x+wx*w+r*0.5, yf+r*0.4], fill=(90, 94, 100))
        fx = x+0.5*w*flip
        if lights:
            d.ellipse([fx-6, yf-0.38*h, fx+6, yf-0.24*h], fill=(255, 250, 220))
        bx = x-0.5*w*flip
        d.rectangle([bx-4, yf-0.42*h, bx+4, yf-0.28*h], fill=(220, 30, 30))
    else:  # trasera
        d.rounded_rectangle([x-w/2, yf-h*1.5, x+w/2, yf-h*0.05], radius=w*0.08, fill=color)
        d.rounded_rectangle([x-w*0.38, yf-h*1.42, x+w*0.38, yf-h*0.95], radius=w*0.05, fill=(36, 44, 58))
        d.rectangle([x-w*0.48, yf-h*0.8, x-w*0.34, yf-h*0.62], fill=(230, 40, 36))
        d.rectangle([x+w*0.34, yf-h*0.8, x+w*0.48, yf-h*0.62], fill=(230, 40, 36))
        d.rectangle([x-w*0.5, yf-h*0.2, x-w*0.36, yf+h*0.05], fill=(14, 14, 16))
        d.rectangle([x+w*0.36, yf-h*0.2, x+w*0.5, yf+h*0.05], fill=(14, 14, 16))

def f(flip): return flip

# normaliza cajas invertidas (por espejado con flip=-1)
def _norm(fn):
    def w(self, xy, *a, **k):
        if isinstance(xy, (list, tuple)) and len(xy) == 4 and not isinstance(xy[0], (list, tuple)):
            x0, y0, x1, y1 = xy; xy = [min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)]
        return fn(self, xy, *a, **k)
    return w
for _m in ('ellipse', 'rectangle', 'rounded_rectangle', 'chord', 'pieslice', 'arc'):
    setattr(ImageDraw.ImageDraw, _m, _norm(getattr(ImageDraw.ImageDraw, _m)))
