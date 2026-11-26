import sys, json, math, subprocess, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import planchas as P
from arte import paint, PW, PH

S = sys.argv[1]; OUT = sys.argv[2]; PREVIEW = len(sys.argv) > 3
W, H, FPS = 720, 1280, 30
SR = 44100
vz = json.load(open(S+'/build/voz.json')); VSR = vz['sr']
voices = np.load(S+'/build/voz.npy', allow_pickle=True)
GAP = 0.22
BEAT = 60/105

# ---------- línea de tiempo (voz primero) ----------
starts, durs = [], []
t = 0.0
for i, d in enumerate(vz['durs']):
    starts.append(t)
    dd = d+GAP if i < 13 else d+1.0
    durs.append(dd); t += dd
TOTAL = t
print('total', round(TOTAL, 2), [round(s, 2) for s in starts])

# escenas: (planchas, [(zoom0, zoom1, cx0, cy0, cx1, cy1)], fx por sub-momento, transición)
SC = [
 (['p1a', 'p1b'], [(1.0, 1.15, .5, .45, .5, .4), (1.15, 1.9, .5, .4, .5, .33)], [['dust'], ['dust']], 'through'),
 (['p2a', 'p2b'], [(1.05, 1.3, .45, .65, .52, .7), (1.1, 1.2, .5, .62, .5, .6)], [['snow'], ['snowwin']], 'white'),
 (['p3a', 'p3b', 'p3c'], [(1.0, 1.15, .5, .7, .5, .72), (1.1, 1.0, .5, .65, .5, .6), (1.0, 1.3, .5, .75, .55, .78)], [[], ['snow'], ['screenglow']], 'fade'),
 (['p4a', 'p4b'], [(1.05, 1.3, .5, .5, .5, .48), (1.0, 1.12, .5, .5, .55, .5)], [[], []], 'notify'),
 (['p5a', 'p5b'], [(1.0, 1.12, .5, .7, .55, .72), (1.1, 1.35, .55, .72, .6, .7)], [['snow'], ['snow', 'x2']], 'through'),
 (['p6a', 'p6b'], [(1.0, 1.2, .45, .68, .5, .7), (1.05, 1.0, .4, .7, .5, .7)], [['blizzard'], ['blizzard']], 'whiteout'),
 (['p7a', 'p7b', 'p7c'], [(1.0, 1.4, .5, .6, .5, .6), (1.15, 1.0, .55, .75, .5, .75), (1.0, 1.15, .55, .8, .55, .8)], [['snowfast', 'shake'], ['snow', 'shake'], ['snow']], 'redblue'),
 (['p8a', 'p8b', 'p8c'], [(1.0, 1.1, .5, .8, .5, .8), (1.0, 1.2, .5, .75, .5, .72), (1.0, 1.25, .5, .65, .6, .66)], [['snow', 'siren'], ['snow', 'siren'], ['snow', 'patrolpath']], 'fade'),
 (['p9a', 'p9b', 'p9c'], [(1.0, 1.15, .5, .5, .5, .45), (1.05, 1.2, .55, .55, .45, .6), (1.0, 1.15, .5, .75, .5, .75)], [['amber'], ['mist'], ['flicker', 'snow']], 'green'),
 (['p10a', 'p10b', 'p10c'], [(1.0, 1.15, .45, .78, .55, .78), (1.0, 1.1, .45, .75, .5, .72), (1.0, 1.2, .5, .5, .5, .45)], [['snow', 'shake'], ['snow'], []], 'whip'),
 (['p11a', 'p11b', 'p11c'], [(1.0, 1.15, .5, .6, .5, .58), (1.1, 1.3, .5, .6, .5, .6), (1.0, 1.2, .5, .55, .5, .5)], [['dust'], ['dust'], ['breath', 'flashlight']], 'white'),
 (['p12a', 'p12b', 'p12c'], [(1.0, 1.1, .5, .75, .5, .72), (1.05, 1.3, .5, .55, .5, .56), (1.0, 1.12, .5, .75, .55, .72)], [['snowsoft'], ['veins'], ['snowsoft']], 'beams'),
 (['p13a', 'p13b'], [(1.2, 1.35, .5, .68, .5, .68), (1.0, 1.05, .5, .72, .5, .72)], [['snow'], ['snow']], 'back'),
 (['p14a', 'p14b', 'p14c'], [(1.9, 1.0, .5, .33, .5, .45), (1.15, 1.25, .5, .4, .5, .38), (1.0, 1.05, .5, .5, .5, .5)], [['dust'], ['dust'], ['dust']], None),
]
assert len(SC) == 14

print('pintando planchas...')
PL = {}
for sc in SC:
    for n in sc[0]:
        PL[n] = paint(getattr(P, n)(), seed=hash(n) % 1000)

# sub-momentos alineados al tiempo fuerte más cercano
SUBS = []  # (escena, sub, t0, t1)
for i, sc in enumerate(SC):
    n = len(sc[0]); s0 = starts[i]; s1 = s0+durs[i]
    cuts = [s0]
    for k in range(1, n):
        c = s0+(s1-s0)*k/n
        c = round(c/BEAT)*BEAT
        c = min(max(c, cuts[-1]+1.2), s1-1.0)
        cuts.append(c)
    cuts.append(s1)
    for k in range(n):
        SUBS.append((i, k, cuts[k], cuts[k+1]))

# ---------- recursos de efectos ----------
rng = np.random.default_rng(7)
GRAIN = [rng.normal(0, 7, (H//2, W//2)).astype(np.float32) for _ in range(6)]
GRAIN = [np.asarray(Image.fromarray(g).resize((W, H)), dtype=np.float32) for g in GRAIN]
yy, xx = np.mgrid[0:H, 0:W]
VIG = (1-0.55*np.clip(((xx-W/2)/(W*0.75))**2+((yy-H/2)/(H*0.72))**2, 0, 1)).astype(np.float32)[..., None]
SNOW = rng.random((420, 4))  # x, y, tamaño, fase
fog = rng.normal(0, 1, (40, 24))
FOG = np.asarray(Image.fromarray(((fog-fog.min())/(fog.max()-fog.min())*255).astype(np.uint8)).resize((W*2, H), Image.BICUBIC), dtype=np.float32)/255
FONT_T = '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'
FONT_S = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
FONT_B = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

def ease(x): return x*x*(3-2*x)

def camera(img, z, cx, cy, shake=(0, 0)):
    cw, ch = PW/z/1.2, PH/z/1.2
    x0 = cx*PW-cw/2+shake[0]; y0 = cy*PH-ch/2+shake[1]
    x0 = min(max(x0, 0), PW-cw); y0 = min(max(y0, 0), PH-ch)
    return img.resize((W, H), Image.BILINEAR, box=(x0, y0, x0+cw, y0+ch))

def snow_layer(fr, t, n=200, speed=1.0, slant=0.0, size=1.0, alpha=200):
    d = ImageDraw.Draw(fr, 'RGBA')
    for k in range(n):
        x, y, s, ph = SNOW[k]
        sp = (0.5+s)*speed
        py = (y*H+t*sp*260) % (H+20)-10
        px = (x*W+t*sp*260*slant+math.sin(t*1.3+ph*6)*12) % (W+20)-10
        r = (0.8+s*2.2)*size
        if slant > 0.5:
            d.line([(px, py), (px-r*4*slant, py-r*4)], fill=(235, 240, 255, alpha), width=max(1, int(r)))
        else:
            d.ellipse([px-r, py-r, px+r, py+r], fill=(235, 240, 255, int(alpha*(0.5+s/2))))

def apply_fx(fr, fx, t, lt, ld, si):
    """fr: PIL RGB; t: tiempo global; lt: tiempo local del sub-momento; ld: su duración."""
    a = None
    for f in fx:
        if f == 'snow': snow_layer(fr, t, 160, 0.8, 0.15)
        elif f == 'snowsoft': snow_layer(fr, t, 110, 0.45, 0.05, 1.1, 170)
        elif f == 'snowfast': snow_layer(fr, t, 260, 2.2, 0.3, 1.0)
        elif f == 'snowwin': snow_layer(fr, t, 120, 1.4, 0.6, 0.8, 120)
        elif f == 'blizzard': snow_layer(fr, t, 420, 2.0, 1.1, 1.0, 210)
        elif f == 'dust':
            d = ImageDraw.Draw(fr, 'RGBA')
            for k in range(90):
                x, y, s, ph = SNOW[k]
                px = (x*W+math.sin(t*0.4+ph*9)*30) % W; py = (y*H*0.7+math.cos(t*0.3+ph*7)*30) % H
                d.ellipse([px-1.2, py-1.2, px+1.2, py+1.2], fill=(255, 236, 200, int(60+90*s)))
    arr = np.asarray(fr, dtype=np.float32).copy()
    for f in fx:
        if f == 'siren':
            ph = (t*3.2) % 1
            col = np.array([255, 30, 30], np.float32) if ph < .5 else np.array([30, 70, 255], np.float32)
            arr += col*0.18*(0.6+0.4*math.sin(t*20))
        elif f == 'amber':
            k = 0.5+0.5*math.sin(t*6)
            m = np.exp(-(((xx-W*(0.3+0.4*k))/(W*0.35))**2+((yy-H*0.25)/(H*0.2))**2))[..., None]
            arr += m*np.array([255, 150, 20], np.float32)*0.55
        elif f == 'mist':
            sh = int(lt*80) % W
            m = np.roll(FOG, -sh, axis=1)[:, :W]
            prog = np.clip(lt/ld*1.4, 0, 1)
            mask = np.clip((xx < W*0.9)*(1-(xx/W))*1.6*prog, 0, 1)*m
            arr = arr*(1-mask[..., None]*0.6)+mask[..., None]*np.array([90, 200, 120], np.float32)*0.6
        elif f == 'flicker':
            arr *= (0.85+0.15*(random.Random(int(t*12)).random() > 0.3))
        elif f == 'screenglow':
            fade = 1-np.clip((lt-(ld-0.6))/0.4, 0, 1)
            arr *= (0.75+0.25*fade)
        elif f == 'breath':
            pass
        elif f == 'flashlight':
            pulse = np.clip((lt-(ld-0.5))/0.5, 0, 1)
            arr += pulse*255*0.9
        elif f == 'patrolpath':
            p = np.clip(lt/ld, 0, 1)
            px = W*(0.15+0.55*p)+(math.sin(lt*30)*25 if p > 0.55 else 0); py = H*0.62-(H*0.05*p)
            vis = 1.0 if p < 0.75 else max(0, 1-(p-0.75)*6)
            col = [255, 30, 30] if (t*4) % 1 < .5 else [40, 80, 255]
            m = np.exp(-(((xx-px)/40)**2+((yy-py)/30)**2))[..., None]*vis
            arr += m*np.array(col, np.float32)*1.4
        elif f == 'veins':
            p = np.clip(lt/ld, 0, 1)
            ov = Image.new('L', (W, H), 0); d = ImageDraw.Draw(ov)
            r = random.Random(3)
            cx, cy = W*0.49, H*0.55
            for k in range(9):
                ang = r.uniform(-3.1, 0.6); L = (60+r.uniform(0, 160))*p
                pts = [(cx, cy)]
                for s in range(6):
                    pts.append((pts[-1][0]+math.cos(ang+math.sin(s+k)*0.6)*L/6, pts[-1][1]+math.sin(ang+math.sin(s+k)*0.6)*L/6))
                d.line(pts, fill=230, width=3)
            m = np.asarray(ov.filter(ImageFilter.GaussianBlur(1.5)), np.float32)[..., None]/255
            arr = arr*(1-m)+m*np.array([70, 170, 90], np.float32)
        elif f == 'x2':
            pass
    return arr

def stamp_x2(arr, a):
    """«x2» en formato sello sobre la caja, rotado -8°, fuera del 20% inferior."""
    if a <= 0: return arr
    im = Image.new('RGBA', (300, 200), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([10, 10, 290, 190], radius=26, outline=(200, 30, 40, 255), width=12)
    d.text((150, 100), 'x2', font=ImageFont.truetype(FONT_B, 130), fill=(210, 30, 42, 255), anchor='mm')
    im = im.rotate(8, expand=True, resample=Image.BICUBIC)  # positivo en PIL = antihorario = -8° visual
    sc = 0.9+0.4*max(0, 1-a*3)  # golpe de sello
    im = im.resize((int(im.width*sc*0.8), int(im.height*sc*0.8)))
    al = np.asarray(im, np.float32)
    x0 = int(W*0.52-im.width/2); y0 = int(H*0.42-im.height/2)
    reg = arr[y0:y0+im.height, x0:x0+im.width]
    m = al[..., 3:4]/255*min(1, a*3)
    arr[y0:y0+im.height, x0:x0+im.width] = reg*(1-m)+al[..., :3]*m
    return arr

TITLE = None
def title_card(arr, a):
    global TITLE
    if TITLE is None:
        im = Image.new('RGBA', (W, 360), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        f1 = ImageFont.truetype(FONT_T, 62); f2 = ImageFont.truetype(FONT_T, 74); f3 = ImageFont.truetype(FONT_S, 30)
        for dx, dy in ((3, 3), (0, 0)):
            c = (0, 0, 0, 200) if dx else None
            d.text((W/2+dx, 90+dy), 'Resident Evil:', font=f1, fill=c or (236, 230, 214, 255), anchor='mm')
            d.text((W/2+dx, 175+dy), 'Noche Cero', font=f2, fill=c or (200, 36, 48, 255), anchor='mm')
            d.text((W/2+dx, 250+dy), 'Resident Evil, 2026', font=f3, fill=c or (214, 206, 190, 255), anchor='mm')
        TITLE = np.asarray(im, np.float32)
    if a <= 0: return arr
    y0 = 130
    m = TITLE[..., 3:4]/255*a
    arr[y0:y0+360] = arr[y0:y0+360]*(1-m)+TITLE[..., :3]*m
    return arr

def grade(arr, i):
    # bruma verde azulada, acentos mostaza y carmesí
    arr = arr*np.array([0.95, 1.0, 1.04], np.float32)+np.array([2, 6, 8], np.float32)
    return arr

def render_sub(idx, t, punch=True):
    i, k, t0, t1 = SUBS[idx]
    sc = SC[i]; ld = t1-t0
    lt = np.clip(t-t0, -0.5, ld+0.5)
    p = ease(float(np.clip(lt/ld, 0, 1)))
    z0, z1, cx0, cy0, cx1, cy1 = sc[1][k]
    z = z0+(z1-z0)*p
    if punch: z *= 1+0.035*math.exp(-max(lt, 0)*10)  # micro-zoom en el corte
    sh = (0, 0)
    if 'shake' in sc[2][k]:
        sh = (math.sin(t*37)*6*math.exp(-max(lt, 0)*2.5), math.cos(t*41)*5*math.exp(-max(lt, 0)*2.5))
    fr = camera(PL[sc[0][k]], z, cx0+(cx1-cx0)*p, cy0+(cy1-cy0)*p, sh)
    arr = apply_fx(fr, sc[2][k], t, lt, ld, idx)
    return arr

def frame(t):
    idx = max(j for j in range(len(SUBS)) if SUBS[j][2] <= t+1e-6)
    i, k, t0, t1 = SUBS[idx]
    arr = render_sub(idx, t)
    # transición de escena (últimos 0,35 s del último sub-momento)
    TD = 0.35
    if k == len(SC[i][0])-1 and SC[i][3] and t > t1-TD and idx+1 < len(SUBS):
        q = (t-(t1-TD))/TD; typ = SC[i][3]
        nxt = render_sub(idx+1, t1, punch=False)
        if typ == 'through':
            i_, k_, a0, a1 = SUBS[idx]
            z = 1+q*1.2
            cur = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
            cw, ch = W/z, H/z
            arr = np.asarray(cur.resize((W, H), Image.BILINEAR, box=(W/2-cw/2, max(0, min(H-ch, H*0.45-ch/2)), W/2+cw/2, max(0, min(H-ch, H*0.45-ch/2))+ch)), np.float32)
            arr = arr*(1-ease(q))+nxt*ease(q)
        elif typ in ('white', 'notify', 'whiteout', 'beams'):
            col = {'white': 255, 'notify': 210, 'whiteout': 240, 'beams': 255}[typ]
            if q < .5: arr = arr*(1-q*2)+col*(q*2)
            else: arr = col*(1-(q-.5)*2)+nxt*((q-.5)*2)
        elif typ == 'redblue':
            c = np.array([255, 20, 30] if (t*8) % 1 < .5 else [30, 60, 255], np.float32)
            arr = (arr*(1-q)+nxt*q)*0.7+c*0.35*math.sin(q*math.pi)
        elif typ == 'green':
            g = np.array([70, 190, 110], np.float32)
            m = math.sin(q*math.pi)
            arr = (arr*(1-q)+nxt*q)*(1-m*0.7)+g*m*0.7*FOG[:, :W, None]
        elif typ == 'whip':
            sh = int(q*W*0.6)
            a2 = np.roll(arr, -sh, axis=1); n2 = np.roll(nxt, int((1-q)*W*0.6), axis=1)
            mix = a2*(1-q)+n2*q
            arr = np.asarray(Image.fromarray(np.clip(mix, 0, 255).astype(np.uint8)).filter(ImageFilter.BoxBlur(int(6+10*math.sin(q*math.pi)))), np.float32)
        elif typ == 'back':
            z = 1-q*0.45
            cur = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).resize((int(W*z), int(H*z)))
            base = nxt.copy()
            ox, oy = (W-cur.width)//2, int(H*0.33-cur.height/2)
            base[max(oy, 0):oy+cur.height, ox:ox+cur.width] = np.asarray(cur, np.float32)[max(-oy, 0):]
            arr = base*q+arr*(1-q) if q > 0.7 else base
        else:
            arr = arr*(1-q)+nxt*q
    # textos en pantalla
    if i == 4 and k == 1:
        arr = stamp_x2(arr, t-max(t0, 21.0))
    if i == 13:
        arr = title_card(arr, np.clip((t-starts[13])/0.6, 0, 1))
    arr = grade(arr, i)
    arr = arr*VIG+GRAIN[int(t*FPS) % 6][..., None]
    return np.clip(arr, 0, 255).astype(np.uint8)

# ---------- música (synth de terror ochentero, ~105 BPM) ----------
def music():
    n = int(TOTAL*SR)+SR; tt = np.arange(n)/SR
    out = np.zeros(n, np.float32)
    def saw(fq, t): return 2*((t*fq) % 1)-1
    def lp(x, a):
        y = np.empty_like(x); acc = 0.0
        # filtro de un polo vectorizado aproximado por convolución exponencial
        k = np.exp(-np.arange(0, 400)/a).astype(np.float32); k /= k.sum()
        return np.convolve(x, k, 'same')
    chords = [(55.0, [220, 261.6, 329.6]), (43.65, [174.6, 220, 261.6]), (65.41, [196, 261.6, 329.6]), (49.0, [196, 246.9, 293.7])]
    bar = BEAT*4
    sec = [0, 18, 39, 67.5, TOTAL+1]
    def section(t):
        for j in range(4):
            if t < sec[j+1]: return j
        return 3
    # pad
    pad = np.zeros(n, np.float32)
    for b in range(int(TOTAL/bar)+2):
        s = int(b*bar*SR); e = min(n, int((b+1)*bar*SR)+SR//4)
        if s >= n: break
        root, notes = chords[b % 4]
        seg = tt[s:e]-tt[s]
        env = np.minimum(1, seg/0.8)*np.minimum(1, (tt[e-1]-tt[s]+0.25-seg)/0.5)
        v = sum(saw(f*0.5, seg)+saw(f*0.5*1.006, seg) for f in notes)
        if section(b*bar) == 2:
            v += 0.7*(saw(notes[0]*0.5*1.0595, seg))  # disonancia
        pad[s:e] += v*env*0.05
    pad = lp(pad, 30)
    out += pad
    # bajo pulsante (corcheas) desde el tramo 2
    bass = np.zeros(n, np.float32)
    for q in range(int(TOTAL/(BEAT/2))+2):
        st = q*BEAT/2
        j = section(st)
        if j in (0, 3) and q % 2: continue
        root = chords[int(st/bar) % 4][0]
        s = int(st*SR); e = min(n, s+int(BEAT/2*SR*0.9))
        seg = tt[s:e]-tt[s]
        bass[s:e] += saw(root, seg)*np.exp(-seg*6)*(0.18 if j in (1, 2) else 0.08)
    out += lp(bass, 12)
    # percusión ligera en tramos 2 y 3
    for q in range(int(TOTAL/BEAT)+1):
        st = q*BEAT; j = section(st)
        if j not in (1, 2): continue
        s = int(st*SR); e = min(n, s+int(0.25*SR)); seg = tt[s:e]-tt[s]
        out[s:e] += np.sin(2*np.pi*(50+90*np.exp(-seg*30))*seg)*np.exp(-seg*14)*0.45
        hs = int((st+BEAT/2)*SR); he = min(n, hs+int(0.05*SR))
        out[hs:he] += np.random.default_rng(q).normal(0, 1, he-hs)*np.exp(-np.arange(he-hs)/SR*80)*0.05*(2 if j == 2 else 1)
    # arpegio frío en el tramo 3
    for q in range(int(TOTAL/(BEAT/4))):
        st = q*BEAT/4
        if section(st) != 2: continue
        notes = chords[int(st/bar) % 4][1]
        f = notes[q % 3]*2
        s = int(st*SR); e = min(n, s+int(0.12*SR)); seg = tt[s:e]-tt[s]
        out[s:e] += np.sign(np.sin(2*np.pi*f*seg))*np.exp(-seg*25)*0.025
    return out

def build_audio():
    n = int(TOTAL*SR)+SR
    voice = np.zeros(n, np.float32)
    for i, v in enumerate(voices):
        v = np.asarray(v, np.float32)
        v = np.interp(np.arange(0, len(v), VSR/SR), np.arange(len(v)), v)
        s = int(starts[i]*SR); voice[s:s+len(v)] += v[:n-s]
    voice /= np.abs(voice).max()+1e-6; voice *= 0.9
    mus = music(); mus /= np.abs(mus).max()+1e-6
    env = np.convolve(np.abs(voice), np.ones(4410)/4410, 'same')
    duck = 1-0.6*np.clip(env/0.05, 0, 1)
    mus *= 0.32*duck
    # fade final; 1 s de silencio de voz al cierre, la música se apaga
    fe = int((TOTAL-1.2)*SR); mus[fe:] *= np.linspace(1, 0, n-fe)
    mix = voice+mus
    mix = mix[:int(TOTAL*SR)]
    mix /= max(1, np.abs(mix).max()/0.97)
    import wave
    with wave.open(S+'/build/mix.wav', 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((mix*32767).astype(np.int16).tobytes())

if PREVIEW:
    for tp in [float(x) for x in sys.argv[3].split(',')]:
        Image.fromarray(frame(tp)).save(f'{S}/build/f_{tp:05.2f}.png')
    sys.exit()

build_audio()
print('audio ok')
nf = int(TOTAL*FPS)
cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
       '-i', S+'/build/mix.wav', '-vf', 'scale=1080:1920:flags=lanczos', '-c:v', 'libx264', '-preset', 'medium', '-crf', '19',
       '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', OUT]
pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
for fi in range(nf):
    pr.stdin.write(frame(fi/FPS).tobytes())
    if fi % 300 == 0: print('frame', fi, '/', nf, flush=True)
pr.stdin.close(); pr.wait()
print('listo', OUT)
