"""Las 18 escenas del guion visual. Cada escena: f(t, dur, ev) -> Image RGB 720x1280.
t = segundos desde el inicio de la escena; ev = tiempos locales de los 'Cambios'."""
import math
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from base import *
from escala import ppm, ancho, altura, BUTACA_ANCHO, BUTACA_ALTO_RESPALDO, PANTALLA_PX, AUTO_ANCHO, AUTO_ALTO, \
    PERSONA_ALTO, PERSONA_HOMBROS, CAMIONETA_ANCHO, CAMIONETA_ALTO, MOSTRADOR_ALTO, CAJA_ANCHO, CAJA_ALTO, \
    MUJER_ALTO, PATRULLA_ANCHO, BUZON_ALTO

# Sala de cine: pantalla de 640x360 (16:9) centrada arriba; filas de butacas segun su distancia.
PANTALLA_BOX = (40, 170, 40 + PANTALLA_PX, 170 + PANTALLA_PX * 9 // 16)
FILAS_FONDO = [780, 880, 1000]   # filas de atras hacia adelante; la fila del espectador es la 1000
FILA_ESPECTADOR = 1000
FILA_FRENTE = 1130


# ============================================================ fondos comunes
@lru_cache(maxsize=4)
def bg_road(variant=0):
    """Carretera de montaña nevada de noche, bosque de pinos (vista desde atras del auto)."""
    img = vgrad(W, H, [(0, (6, 12, 24)), (0.35, (22, 40, 58)), (0.42, (40, 62, 78)), (1, (70, 84, 96))])
    d = ImageDraw.Draw(img)
    rng = np.random.default_rng(11 + variant)
    # montañas lejanas
    pts = [(0, 520)]
    for x in range(0, W + 40, 40):
        pts.append((x, 430 + 60 * math.sin(x * 0.011 + variant) + rng.uniform(-18, 18)))
    pts.append((W, 520))
    d.polygon(pts, fill=(36, 54, 70))
    d.polygon([(p[0], p[1] + 8) for p in pts[1:-1]] + [(W, 520), (0, 520)], fill=(30, 46, 60))
    img = img.filter(ImageFilter.GaussianBlur(3))
    d = ImageDraw.Draw(img)
    # suelo nevado
    d.polygon([(0, 520), (W, 520), (W, H), (0, H)], fill=(120, 140, 155))
    # carretera con hielo
    vx, vy = 360, 520
    d.polygon([(vx - 8, vy), (vx + 8, vy), (W + 120, H), (-120, H)], fill=(52, 64, 76))
    d.polygon([(vx - 3, vy), (vx + 3, vy), (W * 0.62, H), (W * 0.38, H)], fill=(78, 98, 112))  # brillo de hielo
    for k in range(8):  # linea central discontinua
        a, b = (k / 8) ** 2, ((k + 0.45) / 8) ** 2
        ya, yb = vy + (H - vy) * a, vy + (H - vy) * b
        wa, wb = 1 + 10 * a, 1 + 10 * b
        d.polygon([(vx - wa, ya), (vx + wa, ya), (vx + wb, yb), (vx - wb, yb)], fill=(170, 150, 90))
    # bordes de nieve
    d.polygon([(vx - 8, vy), (-120, H), (-200, H), (0, vy + 5)], fill=(150, 166, 178))
    d.polygon([(vx + 8, vy), (W + 120, H), (W + 200, H), (W, vy + 5)], fill=(150, 166, 178))
    # pinos a ambos lados (de atras hacia adelante)
    for i in range(26):
        f = (i / 26) ** 1.6
        y = vy + 6 + (H - vy) * f * 0.75
        hh = 70 + 760 * f
        for side in (-1, 1):
            x = vx + side * (40 + 640 * f + rng.uniform(0, 40) * (1 + 3 * f))
            col = lerpc((34, 52, 64), (8, 18, 24), f)
            pine(d, x, y, hh, col=col, snowk=0.45)
    return img


@lru_cache(maxsize=2)
def bg_cinema():
    img = vgrad(W, H, [(0, (20, 6, 10)), (0.5, (36, 10, 16)), (1, (14, 4, 8))])
    d = ImageDraw.Draw(img)
    # paredes con cortinas
    for x in range(0, W, 26):
        d.rectangle([x, 120, x + 12, 760], fill=(46, 10, 18))
    d.rectangle([0, 0, W, 120], fill=(12, 4, 8))
    # pantalla: ocupa casi todo el ancho (PANTALLA_BOX), con marco
    d.rectangle([PANTALLA_BOX[0] - 8, PANTALLA_BOX[1] - 8, PANTALLA_BOX[2] + 8, PANTALLA_BOX[3] + 8],
                fill=(60, 40, 44))
    d.rectangle(list(PANTALLA_BOX), fill=(10, 8, 10))
    img = img.filter(ImageFilter.GaussianBlur(2))
    d = ImageDraw.Draw(img)
    # proyector arriba a la izquierda (ventanita de cabina)
    d.rectangle([0, 96, 120, 200], fill=(8, 4, 6))
    d.rectangle([44, 128, 100, 168], fill=(30, 26, 26))
    # butacas de terciopelo carmesi: pocas y grandes en primer plano, pequenas al fondo
    for y in FILAS_FONDO:
        butacas_fila(d, y, (112, 14, 28))
    return img


def butacas_fila(d, y, col, cuerpo=(150, 26, 40)):
    """Una fila de butacas a la altura y del suelo; el ancho sale de la escala (escala.py)."""
    bw = int(ancho(y, BUTACA_ANCHO))
    bh = int(altura(y, BUTACA_ALTO_RESPALDO))
    gap = max(3, int(bw * 0.12))
    paso = bw + gap
    n = int(W / paso) + 2
    off = (y * 7) % paso
    for i in range(-1, n):
        x = -off + i * paso
        rrect(d, [x, y - bh, x + bw, y], max(3, int(bw * 0.3)), col)
        rrect(d, [x + bw * 0.08, y - bh + bw * 0.08, x + bw * 0.92, y - bh * 0.45], max(2, int(bw * 0.25)), cuerpo)
    d.rectangle([0, y - 4, W, y + 40], fill=(26, 4, 10))


def screen_content(kind, t=0.0):
    """Imagen que aparece en la pantalla del cine (ocupa PANTALLA_BOX)."""
    bw, bh = PANTALLA_BOX[2] - PANTALLA_BOX[0], PANTALLA_BOX[3] - PANTALLA_BOX[1]
    if kind == "road":
        src = bg_road(0).copy()
        d = ImageDraw.Draw(src)
        # auto de reparto en el plano de la pantalla: su tamano sale de la misma escala de metros
        auto_at(d, src, 360, 960, 0.0, t)
        snow_layer(src, t, n=120, seed=5, speed=200)
        return src.resize((bw, bh), Image.BILINEAR, box=(0, 420, W, 420 + W * bh / bw))
    if kind == "hospital_dark":
        src = scene17(10.0, 3.5, [1.9])
        return src.resize((bw, bh), Image.BILINEAR, box=(0, 260, W, 260 + W * bh / bw))
    return Image.new("RGB", (bw, bh), (210, 212, 206))


def auto_at(d, img, x, y, skid=0.0, t=0.0, brake=0.0):
    """Auto de reparto visto de atras, con medidas reales. (x, y) = centro del suelo bajo el auto.
    El tamano sale de ppm(y): asi el auto siempre guarda proporcion con las personas del mismo plano."""
    p = ppm(y)
    w, h = AUTO_ANCHO * p, AUTO_ALTO * p
    car_rear(d, img, x, y, w, h, brake)


def car_rear(d, img, x, y, w, h, brake=0.0):
    """Dibuja el auto de atras. w, h en pixeles (ya escalados). (x, y) = centro del suelo."""
    u = w / AUTO_ANCHO          # px por metro en este plano
    # sombra
    d.ellipse([x - w * 0.55, y - 0.08 * u, x + w * 0.55, y + 0.08 * u], fill=(30, 36, 44))
    # ruedas (0,65 m de diametro, a 0,35 m del ancho exterior)
    for sx in (-1, 1):
        cx = x + sx * (w * 0.5 - 0.3 * u)
        d.rectangle([cx - 0.11 * u, y - 0.6 * u, cx + 0.11 * u, y], fill=(14, 14, 16))
    # carroceria: de 0,25 m a 1,0 m del suelo; techo hasta AUTO_ALTO
    top_cuerpo = y - 1.0 * u
    body = [(x - w / 2, y - 0.25 * u), (x + w / 2, y - 0.25 * u), (x + w / 2, top_cuerpo),
            (x + w * 0.42, y - h), (x - w * 0.42, y - h), (x - w / 2, top_cuerpo)]
    d.polygon(body, fill=(132, 138, 128))
    # vidrio trasero
    d.polygon([(x - w * 0.36, y - h * 0.94), (x + w * 0.36, y - h * 0.94), (x + w * 0.4, y - 1.02 * u),
               (x - w * 0.4, y - 1.02 * u)], fill=(28, 40, 52))
    # portaequipaje y patente (0,5 m de ancho)
    d.rectangle([x - w / 2, y - 1.0 * u, x + w / 2, y - 0.6 * u], fill=(70, 74, 72))
    d.rectangle([x - 0.25 * u, y - 0.5 * u, x + 0.25 * u, y - 0.36 * u], fill=(220, 216, 200))
    # calaveras a 0,7 m del suelo
    for sx in (-1, 1):
        lx = x + sx * w * 0.38
        d.rectangle([lx - 0.14 * u, y - 0.82 * u, lx + 0.14 * u, y - 0.68 * u], fill=(200, 30, 30))
        add_glow(img, lx, y - 0.75 * u, 0.5 * u * (1 + brake), (255, 40, 30), 0.7 + 0.5 * brake)
    # haz de los focos hacia adelante
    add_poly_light(img, [(x - w * 0.3, y - 0.5 * u), (x + w * 0.3, y - 0.5 * u),
                         (x + 1.2 * u, y - 4.0 * u), (x - 1.2 * u, y - 4.0 * u)], (255, 220, 150), 0.22, 22)


# ============================================================ escena 1: la sala
def cinema_frame(t, beam_on, content, turn=0.0, flicker=1.0, ct=0.0):
    img = bg_cinema().copy()
    d = ImageDraw.Draw(img)
    scr = screen_content(content, ct)
    if not beam_on:
        scr = Image.blend(scr, Image.new("RGB", scr.size, (40, 40, 44)), 0.75)
    img.paste(scr, (PANTALLA_BOX[0], PANTALLA_BOX[1]))
    x0, y0, x1, y1 = PANTALLA_BOX
    if beam_on:
        k = beam_on * flicker
        haz = [(98, 138), (x0, y0), (x1, y0), (x1, y1), (x0, y1), (100, 160)]
        add_poly_light(img, [(98, 138), (x1, y0), (x1, y1), (100, 160)], (255, 226, 160), 0.18 * k, 26)
        add_poly_light(img, [(98, 138), (470, 300), (470, 520), (100, 160)], (255, 236, 190), 0.12 * k, 14)
        add_glow(img, 100, 148, 70, (255, 230, 170), 0.9 * k)
        add_glow(img, 470, 410, 330, (90, 110, 130), 0.25 * k, sx=1.2, sy=0.9)
        dust_in_beam(img, t, [(98, 138), (x1, y0), (x1, y1), (100, 160)], n=110)
    # Espectador sentado de espaldas, en su fila: hombros = 0,45 m, como una butaca de 0,55 m
    s_esp = PERSONA_HOMBROS * ppm(FILA_ESPECTADOR) / 3.1   # spectator_seated dibuja hombros de 3,1 * s
    spectator_seated(d, img, 380, FILA_ESPECTADOR - 40, s_esp, turn)
    # primera fila, la mas cercana: butacas grandes
    d.rectangle([0, FILA_FRENTE - 90, W, FILA_FRENTE - 60], fill=(22, 4, 8))
    butacas_fila(d, FILA_FRENTE, (100, 12, 26), (136, 22, 36))
    return img


def scene1(t, dur, ev):
    beam = ramp(t, ev[0] - 0.15, ev[0] + 0.15)
    img = cinema_frame(t, beam, "road" if beam > 0.5 else "blank", ct=t)
    z = 1.0 + 0.35 * ramp(t, ev[1], dur - 0.45)
    fx, fy = lerp(360, 470, ramp(t, ev[1], dur)), lerp(640, 470, ramp(t, ev[1], dur))
    zz = ramp(t, dur - 0.5, dur)  # atraviesa la pantalla (centro de PANTALLA_BOX)
    z = z * (1 + 3.2 * zz * zz)
    fy = lerp(fy, (PANTALLA_BOX[1] + PANTALLA_BOX[3]) / 2, zz)
    return cam(img, z, fx, fy)


# ============================================================ escena 2 / 7: interior del auto
def car_interior(t, wipe=1.0, snow_k=1.0, phone=None, box=True, clock="00:47"):
    img = Image.new("RGB", (W, H), (8, 10, 14))
    # vista exterior por el parabrisas
    out = bg_road(1).resize((W, int(H * 0.62)), Image.BILINEAR, box=(0, 300, W, 1140))
    ws = Image.new("RGB", (W, H), 0)
    ws.paste(out, (0, 250))
    add_poly_light(ws, [(300, 560), (420, 560), (720, 760), (0, 760)], (255, 215, 150), 0.22, 30)
    snow_layer(ws, t, n=160, seed=21, speed=260 * snow_k, size=(1, 3.5), wind=0, streak=2)
    # parabrisas cubierto de nieve -> limpiaparabrisas
    cover = Image.new("RGB", (W, H), (150, 160, 166))
    cover = Image.blend(cover, ws, 0.25)
    m = Image.new("L", (W, H), 0)
    if wipe > 0:
        md = ImageDraw.Draw(m)
        for px in (230, 520):
            md.pieslice([px - 330, 760 - 330, px + 330, 760 + 330], 180, 180 + 180 * wipe, fill=255)
        m = m.filter(ImageFilter.GaussianBlur(8))
    ws = Image.composite(ws, cover, m)
    wmask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(wmask).polygon([(70, 250), (650, 250), (720, 760), (0, 760)], fill=255)
    img.paste(ws, (0, 0), wmask)
    d = ImageDraw.Draw(img)
    # techo y pilares
    d.polygon([(0, 0), (W, 0), (W, 240), (650, 250), (70, 250), (0, 240)], fill=(18, 20, 26))
    d.polygon([(0, 240), (70, 250), (0, 760)], fill=(14, 16, 20))
    d.polygon([(W, 240), (650, 250), (W, 760)], fill=(14, 16, 20))
    d.rectangle([330, 250, 390, 290], fill=(20, 22, 26))  # espejo
    # limpiaparabrisas
    for px in (230, 520):
        a = math.radians(180 + 180 * (wipe if 0 < wipe < 1 else 0.02))
        d.line([(px, 755), (px + 320 * math.cos(a), 755 + 320 * math.sin(a))], fill=(10, 10, 12), width=7)
    # tablero
    d.polygon([(0, 740), (W, 740), (W, 880), (0, 900)], fill=(24, 26, 30))
    d.polygon([(0, 735), (W, 735), (W, 760), (0, 760)], fill=(34, 36, 42))
    # GPS
    d.rounded_rectangle([300, 770, 470, 860], 8, fill=(10, 30, 30))
    d.line([(318, 845), (350, 830), (372, 812), (400, 805), (420, 790), (450, 782)], fill=(120, 230, 160), width=4)
    d.polygon([(420, 800), (436, 778), (452, 800)], fill=(60, 90, 90))
    d.polygon([(436, 802), (450, 784), (464, 802)], fill=(50, 80, 80))
    d.text((318, 778), "148 km", font=font(FONT_MED, 15), fill=(160, 240, 190))
    add_glow(img, 385, 815, 110, (40, 120, 90), 0.45)
    d.text((488, 780), clock, font=font(FONT_MONO, 26), fill=(240, 120, 60))
    add_glow(img, 530, 795, 50, (180, 70, 20), 0.5)
    # celular en el soporte
    if phone is not None:
        ring, flip = phone
        px, py = 560, 650
        hgt = 150 * abs(math.cos(flip * math.pi / 2)) if flip < 1 else 150
        d.rectangle([px - 8, py + 70, px + 8, py + 100], fill=(30, 30, 34))
        if flip < 0.5:
            d.rounded_rectangle([px - 45, py - hgt / 2, px + 45, py + hgt / 2], 10, fill=(18, 18, 20))
            d.rounded_rectangle([px - 40, py - hgt / 2 + 5, px + 40, py + hgt / 2 - 5], 8,
                                fill=lerpc((20, 30, 40), (90, 140, 170), ring))
            if hgt > 100:
                d.text((px, py - 30), "Casa", font=font(FONT_BOLD, 22), fill=(250, 250, 250), anchor="mm")
                d.text((px, py - 8), "llamando...", font=font(FONT_MED, 12), fill=(220, 230, 240), anchor="mm")
                d.ellipse([px - 32, py + 30, px - 10, py + 52], fill=(220, 50, 50))
                d.ellipse([px + 10, py + 30, px + 32, py + 52], fill=(60, 200, 90))
            add_glow(img, px, py, 160, (120, 170, 220), 0.55 * ring * (1 - flip * 2))
        else:
            d.rounded_rectangle([px - 45, py - hgt / 2, px + 45, py + hgt / 2], 10, fill=(26, 26, 30))
    # asiento del copiloto + caja termica
    if box:
        thermal_box(d, 470, 800, 200, 130)
    d.polygon([(450, 900), (700, 890), (720, 1280), (440, 1280)], fill=(36, 38, 44))
    d.rounded_rectangle([480, 860, 680, 960], 30, fill=(42, 44, 50))
    # conductor de espaldas (grande, a la izquierda)
    person(d, 210, 2150, 1750, jacket=JACKET, hat=BEANIE, skin=(28, 28, 32), arm=(-0.06, 0.25, 0.03, 0.24))
    # volante
    d.arc([60, 700, 330, 900], 200, 340, fill=(12, 12, 14), width=16)
    return img


def scene2(t, dur, ev):
    wipe = ramp(t, ev[0], ev[0] + 0.6)
    img = car_interior(t, wipe=wipe)
    if t < ev[0]:
        return cam(img, 1.6 + 0.08 * t, 570, 860)
    return cam(img, 1.08 - 0.03 * (t - ev[0]), 360, 640)


# ============================================================ escena 3: estacionamiento
@lru_cache(maxsize=1)
def bg_hospital_lot():
    img = vgrad(W, H, [(0, (8, 14, 26)), (0.45, (26, 40, 54)), (1, (60, 70, 80))])
    d = ImageDraw.Draw(img)
    # hospital pequeño de pueblo
    d.rectangle([60, 360, 660, 640], fill=(70, 80, 88))
    d.polygon([(40, 360), (680, 360), (660, 330), (60, 330)], fill=(52, 60, 66))
    for r in range(3):
        for c in range(9):
            x, y = 90 + c * 62, 390 + r * 76
            lit = (c * 3 + r) % 4 != 0
            d.rectangle([x, y, x + 36, y + 44], fill=(200, 210, 170) if lit else (36, 44, 52))
    d.rectangle([300, 540, 420, 640], fill=(160, 200, 190))  # puerta iluminada
    d.rectangle([250, 290, 470, 330], fill=(230, 235, 235))
    d.text((360, 310), "HOSPITAL", font=font(FONT_BOLD, 28), fill=(170, 20, 30), anchor="mm")
    d.rectangle([215, 296, 241, 324], fill=(200, 30, 36))
    img = img.filter(ImageFilter.GaussianBlur(1.5))
    for r in range(3):
        for c in range(9):
            if (c * 3 + r) % 4 != 0:
                add_glow(img, 108 + c * 62, 412 + r * 76, 40, (90, 100, 70), 0.5)
    add_glow(img, 360, 590, 150, (60, 110, 100), 0.6)
    d = ImageDraw.Draw(img)
    d.polygon([(0, 640), (W, 640), (W, H), (0, H)], fill=(118, 128, 136))
    for k in range(5):  # lineas de estacionamiento bajo la nieve
        d.line([(80 + k * 140, 700), (20 + k * 170, 900)], fill=(150, 156, 150), width=4)
    # faroles mostaza
    for x in (40, 690):
        d.rectangle([x - 5, 300, x + 5, 760], fill=(20, 22, 26))
        d.rectangle([x - 24, 296, x + 24, 306], fill=(20, 22, 26))
        add_glow(img, x, 312, 160, MUSTARD, 0.8)
        add_poly_light(img, [(x - 20, 306), (x + 20, 306), (x + 160, 780), (x - 160, 780)], MUSTARD, 0.16, 30)
    return img


def scene3(t, dur, ev):
    img = bg_hospital_lot().copy()
    d = ImageDraw.Draw(img)
    # auto viejo de reparto, con abolladura, apoyado en el suelo a la altura y=940 (ppm 207):
    # 1,75 m de ancho y 1,45 m de alto, junto a una persona de 1,75 m que esta en y=1180.
    auto_at(d, img, 520, 940)
    u = ppm(940)
    dent = [(520 + 0.25 * u, 940 - 0.85 * u), (520 + 0.55 * u, 940 - 0.8 * u), (520 + 0.5 * u, 940 - 0.6 * u),
            (520 + 0.22 * u, 940 - 0.66 * u)]
    d.polygon(dent, fill=(96, 80, 62))  # abolladura en la puerta trasera
    d = ImageDraw.Draw(img)
    # guardias y enfermeros que pasan sin mirarlo
    for i, (col, sp, y0, h) in enumerate([((40, 44, 60), 70, 720, 260), ((90, 150, 170), -60, 690, 230),
                                          ((70, 130, 150), 55, 700, 240)]):
        x = (100 + i * 260 + sp * t) % (W + 200) - 100
        person(d, x, y0, h, jacket=col, pants=lerpc(col, (0, 0, 0), 0.3), hair=(40, 30, 24),
               walk=math.sin(t * 5 + i) * 0.8, front=(sp < 0))
    # repartidor: delgado y cansado, carga cajas al auto (de espaldas, chaleco REPARTO)
    rub = ramp(t, ev[0], ev[0] + 0.2) * (1 - ramp(t, ev[0] + 1.2, ev[0] + 1.5))
    x, y, h = 250, 1180, 620
    tilt = rub * 0.25 * math.sin(t * 20)
    person(d, x, y, h, jacket=JACKET, hat=BEANIE, vest=True, lean=-0.03,
           arm=(0.07 + rub * 0.05, 0.12 + rub * 0.05, 0.05 + rub * 0.08, 0.14 + rub * 0.06))
    d.text((x, y - h * 0.72), "REPARTO", font=font(FONT_BLACK, 30), fill=(30, 34, 30), anchor="mm")
    # caja en brazos
    bx, by = x + 40 + rub * 30, y - h * 0.5 - rub * 20 + rub * 24 * abs(math.sin(t * 9))
    box = Image.new("RGBA", (180, 160), (0, 0, 0, 0))
    thermal_box(ImageDraw.Draw(box), 10, 40, 150, 100, label=False)
    box = box.rotate(-25 * rub * math.sin(t * 7) - 8 * rub, Image.BILINEAR, expand=False)
    img.paste(box, (int(bx - 90), int(by - 80)), box)
    if rub > 0.2:
        for s in (-1, 1):  # vaho de las manos por el frio
            add_glow(img, bx - 30 + s * 30, by + 30, 40, (120, 130, 140), 0.35 * rub)
    snow_layer(img, t, n=200, seed=31, speed=120)
    z = 1.0 + 0.04 * t + 0.12 * ramp(t, ev[0], ev[0] + 0.4)
    return cam(img, z, 300, 900)


# ============================================================ escena 4: mostrador
@lru_cache(maxsize=1)
def bg_counter():
    img = vgrad(W, H, [(0, (60, 84, 80)), (0.55, (84, 104, 98)), (1, (40, 50, 50))])
    d = ImageDraw.Draw(img)
    for x in range(0, W, 120):  # tubos fluorescentes
        d.rectangle([x + 20, 40, x + 100, 52], fill=(220, 240, 230))
    img2 = img.copy()
    for x in range(0, W, 120):
        add_glow(img2, x + 60, 46, 120, (110, 140, 120), 0.6)
    d = ImageDraw.Draw(img2)
    d.rectangle([0, 520, W, 560], fill=(50, 66, 64))
    # tablero de corcho / carteles
    d.rectangle([60, 240, 250, 400], fill=(150, 120, 80))
    for i in range(5):
        d.rectangle([75 + (i % 3) * 58, 255 + (i // 3) * 70, 120 + (i % 3) * 58, 310 + (i // 3) * 70],
                    fill=(230, 230, 220))
    # reloj de pared: fin del turno (23:58)
    cx, cy, r = 560, 270, 70
    d.ellipse([cx - r - 6, cy - r - 6, cx + r + 6, cy + r + 6], fill=(30, 34, 36))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(236, 236, 226))
    for i in range(12):
        a = i * math.pi / 6
        d.line([(cx + r * 0.82 * math.sin(a), cy - r * 0.82 * math.cos(a)),
                (cx + r * 0.95 * math.sin(a), cy - r * 0.95 * math.cos(a))], fill=(30, 30, 30), width=4)
    for a, l, wd in ((math.radians(-5), 0.5, 7), (math.radians(-12), 0.8, 4)):
        d.line([(cx, cy), (cx + r * l * math.sin(a), cy - r * l * math.cos(a))], fill=(20, 20, 20), width=wd)
    # mostrador
    d.rectangle([0, 760, W, 1280], fill=(120, 130, 122))
    d.rectangle([0, 740, W, 790], fill=(196, 200, 188))
    d.rectangle([0, 790, W, 806], fill=(90, 98, 92))
    return img2


def nurse(d, x, y, s):
    """Enfermera adulta tras el mostrador, estilizada, sin rasgos detallados."""
    scrub = (70, 140, 150)
    d.polygon([(x - 1.6 * s, y + 3 * s), (x - 1.4 * s, y - 0.3 * s), (x - 0.4 * s, y - 0.7 * s),
               (x + 0.4 * s, y - 0.7 * s), (x + 1.4 * s, y - 0.3 * s), (x + 1.6 * s, y + 3 * s)], fill=scrub)
    d.polygon([(x - 0.35 * s, y - 0.68 * s), (x + 0.35 * s, y - 0.68 * s), (x, y - 0.1 * s)], fill=SKIN)
    d.rectangle([x - 0.2 * s, y - 1.0 * s, x + 0.2 * s, y - 0.6 * s], fill=SKIN2)
    d.polygon(ell(x, y - 1.55 * s, 0.62 * s, 0.75 * s, 24), fill=(60, 34, 24))  # pelo tomado
    d.polygon(ell(x, y - 1.45 * s, 0.48 * s, 0.62 * s, 24), fill=SKIN)
    d.polygon(ell(x, y - 1.95 * s, 0.5 * s, 0.25 * s, 18), fill=(60, 34, 24))
    for sd in (-1, 1):  # ojos simples mirando hacia abajo
        d.line([(x + sd * 0.26 * s - 0.08 * s, y - 1.45 * s), (x + sd * 0.26 * s + 0.08 * s, y - 1.45 * s)],
               fill=(50, 30, 24), width=max(2, int(s * 0.06)))
    d.line([(x - 0.1 * s, y - 1.12 * s), (x + 0.1 * s, y - 1.12 * s)], fill=(150, 80, 70), width=max(2, int(s * 0.05)))
    d.rectangle([x + 0.6 * s, y + 0.2 * s, x + 1.0 * s, y + 0.7 * s], fill=(230, 230, 230))  # credencial


def scene4(t, dur, ev):
    base = bg_counter()
    img = base.copy()
    d = ImageDraw.Draw(img)
    # Mostrador: su borde superior (1,0 m) esta en y=740 -> el suelo tras el mostrador esta en y=960 (ppm 220).
    # La enfermera de 1,7 m esta detras del mostrador: a esa profundidad mide 374 px, no mas.
    p = ppm(960)
    nurse(d, 470, 960, s=PERSONA_ALTO * p / 2.2)
    # el mostrador tapa las piernas de la enfermera
    img.paste(base.crop((0, 740, W, H)), (0, 740))
    d = ImageDraw.Draw(img)
    # brazos de la enfermera entregando
    k = ramp(t, ev[0] - 0.6, ev[0])
    bx = lerp(430, 250, k)
    d.polygon([(400, 640), (480, 640), (bx + 70, 720), (bx + 20, 740)], fill=(70, 140, 150))
    # caja termica de 0,50 m (110 px a esta profundidad) con etiqueta roja de prioridad maxima
    box = Image.new("RGBA", (150, 100), (0, 0, 0, 0))
    bd = ImageDraw.Draw(box)
    thermal_box(bd, 20, 30, ancho(960, CAJA_ANCHO), altura(960, CAJA_ALTO))
    img.paste(box, (int(bx - 75), 740 - 96), box)
    # repartidor en primer plano (izq), chaqueta a medio quitar
    person(d, 120, 2050, 1500, jacket=JACKET, hat=BEANIE, vest=False, arm=(0.02, 0.05, 0.1, 0.2))
    d.polygon([(-40, 1060), (60, 1000), (90, 1280), (-40, 1280)], fill=lerpc(JACKET, (0, 0, 0), 0.4))  # manga caida
    d.polygon([(130, 950), (230, 960), (260, 1280), (150, 1280)], fill=(150, 150, 140))  # polera debajo
    z = lerp(1.05, 1.18, t / dur)
    return cam(img, z, 360, 700)


# ============================================================ escena 5: vista aerea
@lru_cache(maxsize=1)
def bg_aerial():
    HH = 2200
    img = vgrad(W, HH, [(0, (8, 12, 22)), (0.18, (24, 34, 50)), (0.32, (60, 72, 86)), (0.45, (98, 112, 124)),
                        (1, (150, 162, 170))])
    d = ImageDraw.Draw(img)
    rng = np.random.default_rng(5)
    # ciudad lejana en el valle (arriba del lienzo)
    d.polygon([(0, 560), (180, 420), (300, 500), (460, 380), (720, 520), (720, 700), (0, 700)], fill=(40, 52, 66))
    for i in range(260):
        x = rng.uniform(100, 640); y = rng.uniform(560, 650)
        d.rectangle([x, y, x + 2, y + 2], fill=(255, 200, 120))
    img = img.filter(ImageFilter.GaussianBlur(1.5))
    add_glow(img, 370, 600, 260, (160, 110, 60), 0.5, sx=1.4, sy=0.5)
    d = ImageDraw.Draw(img)
    # ladera con pinos
    for i in range(900):
        x = rng.uniform(-20, 740); y = rng.uniform(760, HH)
        hh = 16 + (y - 760) / 1440 * 40
        pine(d, x, y, hh, col=(20, 36, 40), snowk=0.6)
    # pueblo abajo
    for i in range(40):
        x, y = rng.uniform(80, 640), rng.uniform(1980, 2160)
        d.rectangle([x, y, x + 26, y + 18], fill=(50, 46, 44))
        d.polygon([(x - 3, y), (x + 29, y), (x + 13, y - 12)], fill=(200, 205, 210))
    for i in range(40):
        add_glow(img, rng.uniform(80, 640), rng.uniform(1980, 2160), 30, MUSTARD, 0.6)
    return img


def road_path():
    pts = [(360, 2200), (360, 2050), (560, 1900), (180, 1650), (560, 1400), (200, 1150), (420, 900), (380, 760)]
    out = []
    for i in range(len(pts) - 1):
        for k in range(20):
            a = k / 20
            out.append((lerp(pts[i][0], pts[i + 1][0], a), lerp(pts[i][1], pts[i + 1][1], a)))
    return out


def scene5(t, dur, ev):
    img = bg_aerial().copy()
    d = ImageDraw.Draw(img)
    path = road_path()
    d.line(path, fill=(170, 176, 180), width=16, joint="curve")
    d.line(path, fill=(60, 68, 76), width=10, joint="curve")
    p = clamp(0.05 + 0.32 * t / dur, 0, 0.99)
    i = int(p * (len(path) - 1))
    cx, cy = path[i]
    nx, ny = path[min(i + 3, len(path) - 1)]
    a = math.atan2(ny - cy, nx - cx)
    d.polygon([(cx + 9 * math.cos(a + s), cy + 9 * math.sin(a + s)) for s in (0.5, -0.5, math.pi + 0.5, math.pi - 0.5)],
              fill=(200, 200, 190))
    add_poly_light(img, [(cx, cy), (cx + 120 * math.cos(a - 0.3), cy + 120 * math.sin(a - 0.3)),
                         (cx + 120 * math.cos(a + 0.3), cy + 120 * math.sin(a + 0.3))], (255, 220, 150), 0.5, 10)
    snow_layer(img, t, n=500, seed=51, speed=220, size=(1.5, 4), wind=-80)
    # la camara sube y revela la ciudad; al final baja hacia el auto
    up = ramp(t, ev[1], dur - 0.6)
    top = lerp(cy - 700, 0, up)
    top = clamp(top, 0, 2200 - H)
    frame = img.crop((0, int(top), W, int(top) + H))
    dive = ramp(t, dur - 0.55, dur)
    if dive > 0:
        frame = cam(frame, 1 + 3 * dive * dive, W / 2, 900)
    # plano breve de la etiqueta URGENTE
    if ev[0] <= t < ev[1]:
        frame = urgent_insert(t - ev[0])
    return frame


def urgent_insert(t):
    img = vgrad(W, H, [(0, (18, 22, 28)), (1, (40, 44, 50))])
    d = ImageDraw.Draw(img)
    thermal_box(d, -200, 380, 1100, 700)
    add_glow(img, 500, 600, 400, (255, 200, 140), 0.25)
    return cam(img, 1.0 + 0.08 * t, 520, 640)


# ============================================================ escena 6: recuerdo
@lru_cache(maxsize=1)
def bg_bedroom():
    img = vgrad(W, H, [(0, (70, 44, 24)), (0.6, (110, 74, 38)), (1, (60, 36, 20))])
    d = ImageDraw.Draw(img)
    # ventana con noche nevada
    d.rectangle([420, 240, 640, 520], fill=(30, 30, 30))
    d.rectangle([430, 250, 630, 510], fill=(30, 50, 70))
    d.line([(530, 250), (530, 510)], fill=(40, 30, 20), width=8)
    d.line([(430, 380), (630, 380)], fill=(40, 30, 20), width=8)
    # cama
    d.rectangle([200, 720, 720, 900], fill=(170, 150, 120))
    d.rectangle([200, 690, 720, 740], fill=(210, 196, 170))
    d.rectangle([180, 600, 220, 900], fill=(80, 50, 30))
    d.polygon([(0, 900), (W, 900), (W, H), (0, H)], fill=(80, 54, 34))
    # lampara
    d.rectangle([90, 560, 150, 640], fill=(60, 40, 20))
    d.polygon([(70, 500), (170, 500), (150, 560), (90, 560)], fill=(240, 200, 120))
    add_glow(img, 120, 540, 380, MUSTARD, 0.55)
    return img


def woman_sitting(d, x, y, s, look=1.0):
    """Mujer adulta sentada al borde de la cama, de frente; sostiene una prueba de embarazo."""
    dress = (120, 60, 70)
    d.polygon([(x - 1.2 * s, y + 3.0 * s), (x - 1.0 * s, y + 0.2 * s), (x + 1.0 * s, y + 0.2 * s),
               (x + 1.2 * s, y + 3.0 * s)], fill=(60, 60, 80))  # piernas
    d.polygon([(x - 0.9 * s, y + 0.4 * s), (x - 1.0 * s, y - 1.7 * s), (x + 1.0 * s, y - 1.7 * s),
               (x + 0.9 * s, y + 0.4 * s)], fill=dress)
    d.rectangle([x - 0.2 * s, y - 2.1 * s, x + 0.2 * s, y - 1.6 * s], fill=SKIN)
    d.polygon(ell(x, y - 2.55 * s, 0.75 * s, 0.95 * s, 24), fill=(70, 30, 20))  # pelo largo
    d.polygon([(x - 0.75 * s, y - 2.5 * s), (x + 0.75 * s, y - 2.5 * s), (x + 0.9 * s, y - 1.3 * s),
               (x - 0.9 * s, y - 1.3 * s)], fill=(70, 30, 20))
    d.polygon(ell(x, y - 2.5 * s, 0.5 * s, 0.65 * s, 24), fill=SKIN)
    d.polygon(ell(x, y - 3.0 * s, 0.55 * s, 0.28 * s, 18), fill=(70, 30, 20))
    for sd in (-1, 1):
        d.ellipse([x + sd * 0.22 * s - 0.06 * s, y - 2.58 * s, x + sd * 0.22 * s + 0.06 * s, y - 2.46 * s],
                  fill=(40, 26, 20))
    d.arc([x - 0.15 * s, y - 2.3 * s, x + 0.15 * s, y - 2.1 * s], 20, 160, fill=(140, 70, 60), width=3)
    # manos con la prueba
    d.polygon([(x - 0.9 * s, y - 1.4 * s), (x - 0.3 * s, y - 0.2 * s), (x, y - 0.3 * s)], fill=dress)
    d.polygon([(x + 0.9 * s, y - 1.4 * s), (x + 0.3 * s, y - 0.2 * s), (x, y - 0.3 * s)], fill=dress)
    d.ellipse([x - 0.22 * s, y - 0.45 * s, x + 0.22 * s, y - 0.1 * s], fill=SKIN)
    tx, ty = x + 0.05 * s, y - 0.95 * s
    d.rounded_rectangle([tx - 0.1 * s, ty, tx + 0.1 * s, ty + 0.65 * s], int(0.08 * s), fill=(245, 245, 245))
    d.rectangle([tx - 0.06 * s, ty + 0.12 * s, tx + 0.06 * s, ty + 0.32 * s], fill=(210, 220, 225))
    for yy in (0.17, 0.25):
        d.line([(tx - 0.05 * s, ty + yy * s), (tx + 0.05 * s, ty + yy * s)], fill=(220, 60, 110), width=max(2, int(s * 0.03)))
    return tx, ty + 0.3 * s


def scene6(t, dur, ev):
    img = bg_bedroom().copy()
    d = ImageDraw.Draw(img)
    snow_layer(img, t, n=40, seed=61, speed=60, region=[(430, 250), (630, 250), (630, 510), (430, 510)])
    tx, ty = woman_sitting(d, 420, 760, 62)
    # el, de pie en la puerta, de espaldas, con la chaqueta del trabajo
    d.rectangle([0, 0, 40, H], fill=(40, 26, 14))
    person(d, 140, 1500, 1050, jacket=JACKET, hat=BEANIE, vest=True)
    if t < ev[0]:
        z, fx, fy = 1.0 + 0.03 * t, 360, 640
    else:
        k = ramp(t, ev[0], ev[0] + 0.35)
        z, fx, fy = lerp(1.05, 2.6, k), lerp(360, tx, k), lerp(640, ty, k)
    out = cam(img, z, fx, fy)
    tr = ramp(t, dur - 0.45, dur)  # el reflejo de la ventana se convierte en parabrisas
    if tr > 0:
        win = cam(img, 3.2, 530, 380)
        out = Image.blend(out, win, tr)
    return out


def scene7(t, dur, ev):
    ring = 0.6 + 0.4 * math.sin(t * 12)
    flip = ramp(t, ev[0], ev[0] + 0.35)
    img = car_interior(t + 3, wipe=1.0, snow_k=1.0 + t * 0.4, phone=(ring, flip), box=True, clock="01:12")
    d = ImageDraw.Draw(img)
    if ev[0] - 0.3 < t < ev[0] + 0.5:  # mano que gira el celular
        k = ramp(t, ev[0] - 0.3, ev[0])
        hx, hy = lerp(380, 540, k), lerp(900, 700, k)
        d.polygon([(hx - 30, hy), (hx + 30, hy), (hx - 20, hy + 300), (hx - 90, hy + 300)], fill=JACKET)
        d.ellipse([hx - 30, hy - 40, hx + 34, hy + 20], fill=SKIN)
    snow_layer(img, t, n=int(60 + 80 * t), seed=71, speed=300, size=(1, 3), wind=-40,
               region=[(70, 250), (650, 250), (720, 740), (0, 740)])
    return cam(img, 1.25 + 0.05 * t, 470, 700)


# ============================================================ escena 8: carretera con hielo
def scene8(t, dur, ev):
    img = bg_road(0).copy()
    d = ImageDraw.Draw(img)
    # mujer en la carretera (lejos, entra a la luz de los focos)
    wk = ramp(t, ev[1] - 0.6, ev[1] + 0.4)
    if t > ev[1] - 1.2:
        wy = lerp(640, 800, wk)   # esta delante del auto: entre mas cerca, mas grande (1,65 m con ppm(y))
        creature(d, 360 + 30 * math.sin(t), wy, altura(wy, MUJER_ALTO), t, seed=2,
                 color=lerpc((10, 14, 20), (64, 60, 66), wk))
    # Espectador de espaldas al costado del camino, como testigo: 1,75 m a la profundidad de sus pies (y=1090)
    person(d, 70, 1090, altura(1090), jacket=MUSTARD_HOOD, pants=(36, 36, 44),
           hood=lerpc(MUSTARD_HOOD, (0, 0, 0), 0.2))
    # el auto avanza; patina sobre el hielo
    sk = ramp(t, ev[0], ev[0] + 0.5)
    yaw = sk * 7 * math.sin((t - ev[0]) * 6) * (1 - ramp(t, ev[1], dur)) if t > ev[0] else 0
    car = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(car)
    cx = 380 + sk * 50 * math.sin((t - ev[0]) * 3) if t > ev[0] else 380
    auto_at(cd, car, cx, 1060 - 60 * (t / dur), 0.0, t, brake=sk)   # medidas reales a la profundidad del auto
    car = car.rotate(yaw, Image.BILINEAR, center=(cx, 1000))
    img.paste(car, (0, 0), car)
    add_poly_light(img, [(cx - 90, 960), (cx + 90, 960), (cx + 200, 560), (cx - 200, 560)], (255, 220, 160), 0.12, 30)
    snow_layer(img, t, n=260, seed=81, speed=200, size=(1, 3.5), wind=-60)
    shake = (6 * math.sin(t * 40) * sk, 4 * math.cos(t * 37) * sk) if t > ev[0] else (0, 0)
    z = 1.0 + 0.25 * ramp(t, ev[1], dur)
    return cam(img, z * 1.02, 360, 720, shake=shake)


# ============================================================ escena 9: parabrisas agrietado
def scene9(t, dur, ev):
    img = car_interior(t + 10, wipe=1.0, box=False, clock="01:31")
    img = Image.blend(img, Image.new("RGB", (W, H), (20, 24, 30)), 0.35)
    d = ImageDraw.Draw(img)
    rng = np.random.default_rng(9)
    cx, cy = 380, 500
    for i in range(26):
        a = rng.uniform(0, 2 * math.pi)
        x, y = cx, cy
        pts = [(x, y)]
        for k in range(6):
            a += rng.uniform(-0.4, 0.4)
            l = rng.uniform(25, 70)
            x, y = x + l * math.cos(a), y + l * math.sin(a)
            pts.append((x, y))
        d.line(pts, fill=(220, 230, 235), width=2)
    for r in (40, 90, 150):
        d.arc([cx - r, cy - r * 0.8, cx + r, cy + r * 0.8], 0, 360, fill=(200, 210, 215), width=1)
    snow_layer(img, t, n=200, seed=91, speed=600, size=(1.5, 4), wind=200)
    k = 1 - t / max(dur, 0.01)
    return cam(img, 1.15, 380, 560, shake=(18 * k * math.sin(t * 70), 14 * k * math.cos(t * 63)))


# ============================================================ escena 10: la mujer en la nieve
def scene10(t, dur, ev):
    img = vgrad(W, H, [(0, (6, 10, 18)), (0.4, (20, 30, 42)), (1, (110, 120, 130))])
    d = ImageDraw.Draw(img)
    for i in range(12):
        pine(d, 30 + i * 62, 560, 300 + (i % 3) * 60, col=(10, 22, 26))
    d.polygon([(0, 560), (W, 560), (W, H), (0, H)], fill=(130, 140, 150))
    # auto detenido con luces de freno rojas
    auto_at(d, img, 220, 760, 0.0, t, brake=1.0)   # auto lejano: el mismo ppm que su profundidad
    add_glow(img, 220, 700, 700, (220, 30, 20), 0.55, sx=1.2, sy=0.9)
    d = ImageDraw.Draw(img)
    # mujer tendida en la nieve
    wx, wy = 440, 1050
    d.ellipse([wx - 230, wy + 10, wx + 230, wy + 60], fill=(100, 106, 116))
    d.polygon([(wx - 200, wy + 30), (wx + 120, wy - 10), (wx + 130, wy + 40), (wx - 200, wy + 60)], fill=(120, 96, 104))
    d.polygon([(wx + 110, wy - 5), (wx + 190, wy - 5), (wx + 190, wy + 30), (wx + 110, wy + 40)], fill=(80, 70, 80))
    d.ellipse([wx + 180, wy - 40, wx + 260, wy + 30], fill=(60, 30, 24))
    d.ellipse([wx + 190, wy - 30, wx + 250, wy + 25], fill=(170, 160, 160))
    d.rectangle([wx + 150, wy - 10, wx + 190, wy + 20], fill=(170, 160, 160))
    # venas oscuras en el cuello (sin sangre)
    rng = np.random.default_rng(4)
    for i in range(7):
        x, y = wx + 165 + rng.uniform(-10, 10), wy + rng.uniform(-6, 16)
        pts = [(x, y)]
        for k in range(4):
            x += rng.uniform(-14, 6); y += rng.uniform(-8, 8); pts.append((x, y))
        d.line(pts, fill=(40, 30, 60), width=2)
    # mano crispada que se aferra a la chaqueta
    g = ramp(t, ev[0], ev[0] + 0.3)
    hx, hy = lerp(wx + 40, wx - 30, g), lerp(wy + 20, wy - 140, g)
    d.line([(wx + 60, wy + 10), (hx, hy)], fill=(70, 60, 70), width=22)
    d.ellipse([hx - 18, hy - 18, hx + 18, hy + 18], fill=(160, 150, 150))
    for f in range(4):
        a = -2.2 + f * 0.35 + 0.2 * math.sin(t * 30 + f) * (1 - g * 0.5)
        d.line([(hx, hy), (hx + 26 * math.cos(a), hy + 26 * math.sin(a))], fill=(150, 140, 140), width=6)
    # repartidor arrodillado a su lado (de espaldas, iluminado en rojo)
    person(d, 250, 1090, altura(1090), jacket=lerpc(JACKET, (120, 20, 20), 0.25), hat=BEANIE, vest=True, hip=0.2,
           lean=0.22, arm=(0.05, 0.15, 0.12, 0.2 - 0.1 * g))
    add_glow(img, 300, 900, 300, (200, 20, 20), 0.25)
    snow_layer(img, t, n=200, seed=101, speed=120)
    z = lerp(1.0, 1.35, ramp(t, ev[0], ev[0] + 0.4))
    return cam(img, z, 360 + 30 * ramp(t, ev[0], dur), 960)


# ============================================================ escena 11: siluetas en la carretera
def scene11(t, dur, ev):
    img = bg_road(2).copy()
    d = ImageDraw.Draw(img)
    pos = [(360, 640, 160, 0), (240, 600, 110, 1), (470, 610, 120, 2), (150, 580, 90, 3), (560, 590, 95, 4),
           (300, 575, 75, 5)]
    for i, (x, y, h, sd) in enumerate(pos):
        a = 1.0 if i == 0 else ramp(t, ev[0] + 0.1 * i, ev[0] + 0.1 * i + 0.3)
        if a <= 0:
            continue
        adv = t * 12
        creature(d, x + (360 - x) * t * 0.02, y + adv, h * (1 + t * 0.06), t, seed=sd,
                 color=lerpc((120, 136, 150), (12, 16, 22), a))
    add_poly_light(img, [(200, 1280), (520, 1280), (460, 600), (260, 600)], (255, 220, 160), 0.18, 30)
    # el repartidor en primer plano, de espaldas, mirando hacia adelante
    person(d, 360, 1700, 1100, jacket=JACKET, hat=BEANIE, vest=True)
    snow_layer(img, t, n=260, seed=111, speed=200, wind=-60)
    up = ramp(t, dur - 0.6, dur)
    return cam(img, 1.05 + 0.2 * up, 360, lerp(700, 300, up))


# ============================================================ escena 12: la ciudad
@lru_cache(maxsize=1)
def bg_city():
    img = vgrad(W, H, [(0, (8, 10, 20)), (0.4, (24, 30, 44)), (1, (60, 66, 76))])
    d = ImageDraw.Draw(img)
    vx, vy = 360, 560
    rng = np.random.default_rng(12)
    # edificios a ambos lados en perspectiva
    for side in (-1, 1):
        for i in range(7):
            f0, f1 = (i / 7) ** 1.5, ((i + 1) / 7) ** 1.5
            xa, xb = vx + side * (30 + 420 * f0), vx + side * (30 + 420 * f1)
            top_a, top_b = vy - 60 - 700 * f0, vy - 60 - 700 * f1
            bot_a, bot_b = vy + 10 + 700 * f0, vy + 10 + 700 * f1
            col = lerpc((40, 44, 56), (22, 24, 32), f0)
            d.polygon([(xa, top_a + rng.uniform(-20, 20)), (xb, top_b), (xb, bot_b), (xa, bot_a)], fill=col)
            for k in range(6):
                for j in range(2):
                    if rng.uniform() < 0.45:
                        u = (j + 0.3) / 2.2
                        xx = lerp(xa, xb, u)
                        yy = lerp(lerp(top_a, bot_a, 0.15 + k * 0.1), lerp(top_b, bot_b, 0.15 + k * 0.1), u)
                        s = 4 + 16 * f0
                        d.rectangle([xx - s / 2, yy - s / 2, xx + s / 2, yy + s / 2], fill=(200, 170, 100))
    d.polygon([(vx - 30, vy + 10), (vx + 30, vy + 10), (W + 200, H), (-200, H)], fill=(70, 76, 86))
    d.polygon([(vx - 30, vy + 10), (vx + 30, vy + 10), (W * 0.7, H), (W * 0.3, H)], fill=(96, 100, 108))
    # huellas en la nieve, barreras caidas
    for i in range(60):
        x, y = rng.uniform(150, 570), rng.uniform(800, 1250)
        d.ellipse([x, y, x + 8, y + 4], fill=(60, 62, 70))
    for x, y, a in ((140, 1040, 0.2), (520, 1100, -0.3)):
        pts = [(x - 90, y), (x + 90, y + 90 * a), (x + 90, y + 90 * a + 22), (x - 90, y + 22)]
        d.polygon(pts, fill=(230, 230, 220))
        for k in range(4):
            xx = x - 70 + k * 45
            d.polygon([(xx, y + (xx - x + 90) * a / 2), (xx + 20, y + (xx - x + 110) * a / 2),
                       (xx + 20, y + 22 + (xx - x + 110) * a / 2), (xx, y + 22 + (xx - x + 90) * a / 2)],
                      fill=(200, 40, 40))
    # cartel HOSPITAL 5 KM
    d.rectangle([566, 640, 574, 820], fill=(30, 30, 34))
    d.rectangle([500, 600, 690, 660], fill=(30, 90, 60))
    d.text((595, 630), "HOSPITAL 5 KM", font=font(FONT_BOLD, 22), fill=(240, 240, 230), anchor="mm")
    # vitrina con televisores (izquierda)
    d.rectangle([20, 760, 250, 960], fill=(16, 18, 22))
    # autos abandonados con puertas abiertas
    for x, y, s in ((470, 900, 1.0), (180, 1150, 1.4)):
        d.rounded_rectangle([x - 110 * s, y - 50 * s, x + 110 * s, y + 20 * s], int(20 * s), fill=(60, 64, 70))
        d.polygon([(x - 70 * s, y - 50 * s), (x - 40 * s, y - 95 * s), (x + 50 * s, y - 95 * s),
                   (x + 80 * s, y - 50 * s)], fill=(40, 46, 54))
        d.polygon([(x + 110 * s, y - 50 * s), (x + 170 * s, y - 80 * s), (x + 170 * s, y - 10 * s),
                   (x + 110 * s, y + 10 * s)], fill=(70, 74, 80))  # puerta abierta
        for sx in (-0.7, 0.7):
            d.ellipse([x + sx * 110 * s - 22 * s, y, x + sx * 110 * s + 22 * s, y + 40 * s], fill=(14, 14, 16))
    return img


def scene12(t, dur, ev):
    img = bg_city().copy()
    d = ImageDraw.Draw(img)
    # patrulla con la sirena girando
    px, py = 330, 760
    d.rounded_rectangle([px - 90, py - 40, px + 90, py + 16], 16, fill=(220, 222, 226))
    d.rectangle([px - 90, py - 14, px + 90, py + 2], fill=(20, 30, 70))
    d.polygon([(px - 60, py - 40), (px - 36, py - 74), (px + 40, py - 74), (px + 64, py - 40)], fill=(30, 34, 44))
    d.rectangle([px - 26, py - 84, px + 26, py - 74], fill=(60, 60, 60))
    for sx in (-0.7, 0.7):
        d.ellipse([px + sx * 90 - 18, py, px + sx * 90 + 18, py + 32], fill=(14, 14, 16))
    ph = (t * 3) % 1
    red_on = ph < 0.5
    add_glow(img, px - 14, py - 80, 260, RED if red_on else (40, 0, 0), 0.8 if red_on else 0.2)
    add_glow(img, px + 14, py - 80, 260, BLUE if not red_on else (0, 0, 40), 0.8 if not red_on else 0.2)
    add_glow(img, 360, 900, 600, RED if red_on else BLUE, 0.18, sx=1.2, sy=0.6)
    # farmacia: letrero luminoso que parpadea
    on = (math.sin(t * 17) > -0.3) and not (1.3 < t % 2.1 < 1.45)
    fx, fy = 640, 470
    d.rectangle([fx - 46, fy - 46, fx + 46, fy + 46], fill=(20, 26, 22))
    gc = (60, 230, 120) if on else (20, 60, 34)
    d.rectangle([fx - 32, fy - 11, fx + 32, fy + 11], fill=gc)
    d.rectangle([fx - 11, fy - 32, fx + 11, fy + 32], fill=gc)
    if on:
        add_glow(img, fx, fy, 160, (40, 200, 100), 0.6)
    d.text((fx, fy + 66), "FARMACIA", font=font(FONT_BOLD, 18), fill=gc, anchor="mm")
    # televisores en la vitrina con alerta sanitaria
    for i, (tx, ty) in enumerate(((40, 780), (140, 780), (40, 870), (140, 870))):
        d.rectangle([tx, ty, tx + 90, ty + 72], fill=(18, 18, 20))
        bl = (math.sin(t * 8 + i) > -0.6)
        d.rectangle([tx + 5, ty + 5, tx + 85, ty + 67], fill=(190, 40, 30) if bl else (120, 20, 20))
        cx, cy = tx + 45, ty + 32
        d.ellipse([cx - 13, cy - 13, cx + 13, cy + 13], outline=(250, 230, 200), width=3)
        for k in range(8):
            a = k * math.pi / 4
            d.line([(cx + 13 * math.cos(a), cy + 13 * math.sin(a)), (cx + 21 * math.cos(a), cy + 21 * math.sin(a))],
                   fill=(250, 230, 200), width=3)
        d.rectangle([tx + 8, ty + 56, tx + 82, ty + 63], fill=(250, 220, 60))
        add_glow(img, cx, cy, 90, (200, 50, 30), 0.35)
    d.text((140, 975), "ALERTA SANITARIA", font=font(FONT_BOLD, 18), fill=(250, 220, 60), anchor="mm")
    # gente corriendo y siluetas que persiguen
    for i in range(5):
        sp = 160 + 40 * i
        x = 280 + (i * 90 + sp * t * (1 if i % 2 else -1)) % 520
        y = 820 + (i % 3) * 70
        h = altura(y)   # persona de 1,75 m a la profundidad de sus pies
        col = (52, 60, 80) if i % 2 == 0 else (90, 70, 60)
        person(d, x, y, h, jacket=col, walk=math.sin(t * 12 + i), lean=0.12 * (1 if i % 2 else -1))
        if i % 2 == 0:
            creature(d, x + (90 if i % 2 else -90) * -1, y + 10, h, t * 2, seed=i)
    snow_layer(img, t, n=200, seed=121, speed=140)
    # una silueta deformada cruza corriendo frente a la camara
    if t > ev[1]:
        k = (t - ev[1]) / 0.6
        if k < 1.2:
            ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            od = ImageDraw.Draw(ov)
            creature(od, lerp(-300, 1000, k), 1700, 1500, t * 3, seed=7, color=(6, 8, 10))
            ov = ov.filter(ImageFilter.GaussianBlur(6))
            img.paste(ov, (0, 0), ov)
    if t < ev[0]:
        return cam(img, 1.0 + 0.02 * t, 360, 700)
    k = ramp(t, ev[0], ev[0] + 0.4)
    return cam(img, lerp(1.0, 2.3, k), lerp(360, 140, k), lerp(700, 880, k))


# ============================================================ escena 13: la casa aislada
def scene13(t, dur, ev):
    if t < ev[0]:
        img = vgrad(W, H, [(0, (6, 10, 20)), (0.5, (30, 40, 56)), (1, (130, 140, 150))])
        d = ImageDraw.Draw(img)
        for i in range(14):
            pine(d, i * 56, 700, 380 + (i * 37) % 120, col=(10, 22, 26))
        d.polygon([(0, 700), (W, 700), (W, H), (0, H)], fill=(140, 150, 160))
        d.rectangle([150, 520, 570, 800], fill=(60, 50, 44))
        d.polygon([(120, 530), (600, 530), (360, 360)], fill=(200, 210, 216))
        d.polygon([(140, 530), (580, 530), (360, 380)], fill=(80, 60, 50))
        d.rectangle([330, 660, 400, 800], fill=(30, 22, 18))
        d.rectangle([200, 600, 270, 670], fill=(20, 24, 30))
        d.rectangle([450, 600, 520, 670], fill=(20, 24, 30))
        d.rectangle([290, 640, 440, 650], fill=(40, 30, 24))
        add_glow(img, 365, 640, 200, MUSTARD, 0.9)
        add_glow(img, 365, 640, 40, (255, 230, 160), 1.0)
        d = ImageDraw.Draw(img)
        p13 = ppm(1060)
        person(d, 380, 1060, altura(1060), jacket=JACKET, hat=BEANIE, vest=True, walk=math.sin(t * 6) * 0.6,
               arm=(0, 0, 0.06, 0.12))
        # caja de 0,50 x 0,30 m a la altura del pecho (1,1 m), en la mano derecha
        thermal_box(d, 400, 1060 - 1.1 * p13, ancho(1060, CAJA_ANCHO), altura(1060, CAJA_ALTO), label=False)
        snow_layer(img, t, n=260, seed=131, speed=160)
        return cam(img, 1.05 + 0.05 * t, 360, 760)
    lt = t - ev[0]
    img = vgrad(W, H, [(0, (14, 14, 16)), (1, (34, 32, 30))])
    d = ImageDraw.Draw(img)
    vx, vy = 360, 620
    d.polygon([(0, 0), (vx - 90, vy - 150), (vx - 90, vy + 120), (0, H)], fill=(44, 40, 34))
    d.polygon([(W, 0), (vx + 90, vy - 150), (vx + 90, vy + 120), (W, H)], fill=(38, 34, 30))
    d.polygon([(0, H), (vx - 90, vy + 120), (vx + 90, vy + 120), (W, H)], fill=(52, 44, 36))
    d.rectangle([vx - 90, vy - 150, vx + 90, vy + 120], fill=(56, 52, 46))  # pared del fondo
    # comoda con cajones revueltos
    d.polygon([(40, 900), (200, 820), (200, 1000), (40, 1120)], fill=(70, 50, 34))
    for k in range(3):
        y = 860 + k * 70
        d.polygon([(60, y + 40), (190, y - 20), (230, y), (100, y + 60)], fill=(96, 70, 46))
    for i in range(6):
        d.rectangle([90 + i * 20, 1150 + (i % 2) * 20, 120 + i * 20, 1165 + (i % 2) * 20], fill=(200, 196, 180))
    # puerta con candado (derecha)
    d.polygon([(560, 380), (660, 300), (660, 1000), (560, 880)], fill=(60, 46, 34))
    d.rectangle([586, 600, 616, 636], fill=(150, 140, 120))
    d.arc([588, 574, 614, 610], 180, 360, fill=(150, 140, 120), width=5)
    # luz de linterna / pasillo
    add_glow(img, vx, vy - 20, 260, (120, 110, 90), 0.4)
    # sombra del perro en la pared del fondo
    g = ramp(lt, ev[1] - ev[0], ev[1] - ev[0] + 0.6)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    s = lerp(1.0, 1.9, g)
    bx, by = vx + 10, vy + 110
    body = [(bx - 70 * s, by - 50 * s), (bx - 30 * s, by - 80 * s), (bx + 40 * s, by - 74 * s), (bx + 64 * s, by - 100 * s),
            (bx + 92 * s, by - 96 * s), (bx + 104 * s, by - 80 * s), (bx + 80 * s, by - 60 * s), (bx + 60 * s, by - 30 * s),
            (bx + 64 * s, by), (bx + 52 * s, by), (bx + 40 * s, by - 34 * s), (bx - 40 * s, by - 36 * s),
            (bx - 50 * s, by), (bx - 62 * s, by), (bx - 64 * s, by - 34 * s), (bx - 100 * s, by - 70 * s)]
    for i in range(5):  # columna deforme
        sd.polygon([(bx - 40 * s + i * 18 * s, by - 76 * s), (bx - 32 * s + i * 18 * s, by - 100 * s - 6 * i * s),
                    (bx - 24 * s + i * 18 * s, by - 76 * s)], fill=(0, 0, 0, 230))
    sd.polygon(body, fill=(0, 0, 0, 230))
    sh = sh.filter(ImageFilter.GaussianBlur(5))
    img.paste(sh, (0, 0), sh)
    d = ImageDraw.Draw(img)
    # el repartidor entrando con la caja bajo el brazo
    person(d, 230, 1500, 900, jacket=JACKET, hat=BEANIE, vest=True, arm=(0, 0, 0.08, 0.1))
    thermal_box(d, 330, 1030, 150, 90, label=True)
    return cam(img, 1.0 + 0.05 * lt + 0.15 * g, 360, 640)


# ============================================================ escena 14: escondido
def scene14(t, dur, ev):
    img = vgrad(W, H, [(0, (16, 22, 26)), (1, (28, 34, 34))])
    d = ImageDraw.Draw(img)
    d.polygon([(0, 0), (360, 200), (360, 1000), (0, H)], fill=(30, 38, 40))
    d.polygon([(360, 1000), (0, H), (W, H), (W, 1000)], fill=(40, 42, 40))
    add_poly_light(img, [(620, 0), (720, 0), (520, 1280), (380, 1280)], (120, 150, 170), 0.18, 20)  # rendija de luz
    d = ImageDraw.Draw(img)
    # repartidor sentado en el rincon, rodillas arriba, abrazando la caja (cabeza gacha)
    cx, cy = 340, 900
    d.polygon([(cx - 200, cy + 300), (cx - 160, cy - 120), (cx + 160, cy - 120), (cx + 200, cy + 300)], fill=JACKET)
    for s in (-1, 1):
        d.polygon([(cx + s * 40, cy + 300), (cx + s * 150, cy - 60), (cx + s * 230, cy - 40), (cx + s * 210, cy + 320)],
                  fill=(36, 38, 48))
    d.polygon(ell(cx, cy - 210, 105, 120, 24), fill=SKIN2)
    d.polygon(ell(cx, cy - 250, 112, 95, 24, math.pi, 2 * math.pi), fill=BEANIE)
    d.rectangle([cx - 112, cy - 260, cx + 112, cy - 222], fill=lerpc(BEANIE, (0, 0, 0), 0.25))
    d.polygon(ell(cx, cy - 170, 90, 50, 20), fill=lerpc(SKIN2, (0, 0, 0), 0.35))  # cara en sombra
    thermal_box(d, cx - 150, cy - 30, 300, 210)
    # etiqueta con codigo y logotipo hexagonal
    lx, ly = cx + 15, cy + 22
    d.rectangle([lx, ly, lx + 120, ly + 90], fill=(205, 30, 38))
    hex_logo(d, lx + 30, ly + 34, 20, (250, 240, 240))
    d.text((lx + 58, ly + 26), "UX-0417", font=font(FONT_MONO, 15), fill=(255, 240, 240))
    d.text((lx + 58, ly + 46), "BIO-PRIO", font=font(FONT_MONO, 12), fill=(255, 220, 220))
    # brazos que abrazan
    for s in (-1, 1):
        d.polygon([(cx + s * 170, cy - 100), (cx + s * 200, cy + 40), (cx - s * 20, cy + 190), (cx - s * 60, cy + 150)],
                  fill=lerpc(JACKET, (0, 0, 0), 0.15))
    breathe = 0.01 * math.sin(t * 5)
    if t < ev[0]:
        return cam(img, 1.05 + breathe + 0.03 * t, 360, 800)
    k = ramp(t, ev[0], ev[0] + 0.35)
    z = lerp(1.1, 4.2, k)
    zz = ramp(t, dur - 0.4, dur)
    return cam(img, z * (1 + 2.5 * zz * zz), lerp(360, lx + 30, k), lerp(800, ly + 34, k))


# ============================================================ escena 15: la empresa
@lru_cache(maxsize=1)
def bg_corp():
    img = vgrad(W, H, [(0, (6, 8, 16)), (0.5, (20, 26, 40)), (1, (50, 56, 66))])
    d = ImageDraw.Draw(img)
    rng = np.random.default_rng(15)
    for i in range(10):  # ciudad de fondo
        x = i * 80 - 20
        hh = rng.uniform(300, 600)
        d.rectangle([x, 900 - hh, x + 70, 900], fill=(18, 22, 32))
    # rascacielos corporativo (desde abajo, convergente)
    d.polygon([(170, 1000), (550, 1000), (450, 40), (270, 40)], fill=(30, 36, 50))
    d.polygon([(360, 1000), (550, 1000), (450, 40), (360, 40)], fill=(24, 28, 40))
    for k in range(40):
        y = 60 + k * 23
        f = (y - 40) / 960
        xl, xr = lerp(270, 170, f), lerp(450, 550, f)
        for j in range(8):
            if rng.uniform() < 0.6:
                x = lerp(xl, xr, (j + 0.2) / 8)
                d.rectangle([x, y, x + (xr - xl) / 8 * 0.55, y + 10], fill=(150, 180, 200))
    img = img.filter(ImageFilter.GaussianBlur(1))
    d = ImageDraw.Draw(img)
    hex_logo(d, 360, 150, 62, (230, 60, 60), bg=(30, 36, 50))
    add_glow(img, 360, 150, 220, (200, 30, 40), 0.7)
    d = ImageDraw.Draw(img)
    d.polygon([(0, 960), (W, 960), (W, H), (0, H)], fill=(84, 90, 100))
    return img


def tactical(d, x, y, h, t, i):
    """Hombre adulto con equipo tactico y mascara de gas; arma apuntando al suelo."""
    person(d, x, y, h, jacket=(26, 28, 32), pants=(30, 32, 36), skin=(40, 42, 46), hair=(20, 22, 24),
           front=True, walk=0.3 * math.sin(t * 4 + i), arm=(0.0, 0.05, 0.08, 0.12))
    hx, hy = x, y - h * 0.9
    d.ellipse([hx - h * 0.07, hy - h * 0.085, hx + h * 0.07, hy + h * 0.07], fill=(30, 32, 36))
    for s in (-1, 1):
        d.ellipse([hx + s * h * 0.03 - h * 0.022, hy - h * 0.03, hx + s * h * 0.03 + h * 0.022, hy + h * 0.01],
                  fill=(90, 110, 120))
    d.ellipse([hx - h * 0.035, hy + h * 0.02, hx + h * 0.035, hy + h * 0.08], fill=(60, 64, 70))
    # arma hacia el suelo (diagonal hacia abajo)
    d.line([(x - h * 0.08, y - h * 0.6), (x + h * 0.12, y - h * 0.28)], fill=(10, 10, 12), width=max(3, int(h * 0.03)))


def camioneta_at(d, img, x, y, k=1.0):
    """Camioneta negra vista de frente, con medidas reales (1,95 m de ancho, 1,9 m de alto) a la profundidad y."""
    p = ppm(y)
    w, h = CAMIONETA_ANCHO * p, CAMIONETA_ALTO * p
    d.rounded_rectangle([x - w / 2, y - h, x + w / 2, y - 0.25 * p], int(0.15 * p), fill=(10, 10, 12))
    d.rectangle([x - w * 0.4, y - h * 0.92, x + w * 0.4, y - h * 0.62], fill=(30, 40, 52))  # parabrisas
    for sx in (-1, 1):  # ruedas de 0,8 m de diametro
        cx = x + sx * w * 0.38
        d.ellipse([cx - 0.4 * p, y - 0.8 * p, cx + 0.4 * p, y], fill=(4, 4, 6))
    add_glow(img, x + w * 0.4, y - h * 0.55, 0.25 * p, (230, 230, 255), 0.6 * k)


def scene15(t, dur, ev):
    img = bg_corp().copy()
    d = ImageDraw.Draw(img)
    # camionetas negras que llegan
    k = ramp(t, ev[0], ev[0] + 0.8)
    for j, (x0, y) in enumerate(((-300, 985), (W + 300, 1010))):
        x = lerp(x0, 170 if j == 0 else 560, k)
        camioneta_at(d, img, x, y, k)
    # hombres tacticos instalando barreras: 1,75 m con ppm de sus pies (y=1120 y 1140)
    for i in range(4):
        yy = 1120 + (i % 2) * 20
        tactical(d, 120 + i * 160, yy, altura(yy), t, i)
    # barrera con cinta de cuarentena
    c = ramp(t, ev[1], ev[1] + 0.5)
    d.rectangle([20, 1150, 30, 1260], fill=(40, 40, 40))
    tx = lerp(40, 700, c)
    for k2 in range(int((tx - 30) / 36) + 1):
        x = 30 + k2 * 36
        d.polygon([(x, 1170), (x + 18, 1170), (x + 36, 1190), (x + 18, 1190)], fill=(240, 200, 30))
        d.polygon([(x + 18, 1170), (x + 36, 1170), (x + 54, 1190), (x + 36, 1190)], fill=(20, 20, 20))
    if c > 0.95:
        d.text((360, 1215), "CUARENTENA", font=font(FONT_BOLD, 20), fill=(240, 200, 30), anchor="mm")
    # el Espectador observa de espaldas desde una esquina
    d.rectangle([0, 700, 80, 1280], fill=(16, 18, 24))
    person(d, 110, 1330, altura(1330), jacket=MUSTARD_HOOD, pants=(36, 36, 44), hood=lerpc(MUSTARD_HOOD, (0, 0, 0), 0.2))
    snow_layer(img, t, n=200, seed=151, speed=150)
    # entra desde el hexagono (zoom out)
    zin = 1 - ramp(t, 0, 0.6)
    if t < ev[0]:
        z = 1.25 + 4 * zin * zin
        return cam(img, z, 360, lerp(560, 150, zin))
    return cam(img, lerp(1.25, 1.05, ramp(t, ev[0], ev[0] + 0.8)), 360, lerp(560, 760, ramp(t, ev[0], ev[0] + 0.8)))


# ============================================================ escena 16: la pistola y las balas
def scene16(t, dur, ev):
    if t < ev[0]:  # guantera de la patrulla
        img = vgrad(W, H, [(0, (14, 16, 22)), (1, (30, 32, 38))])
        d = ImageDraw.Draw(img)
        add_glow(img, 600, 200, 400, RED if (t * 3) % 1 < 0.5 else BLUE, 0.3)
        d.polygon([(0, 500), (W, 440), (W, 1000), (0, 1100)], fill=(36, 38, 44))
        op = ramp(t, 0.2, 0.7)
        d.rectangle([200, 640, 560, 820], fill=(48, 50, 58))
        add_glow(img, 380, 730, 260, (150, 170, 190), 0.35 * op)
        d = ImageDraw.Draw(img)
        d.polygon([(200, 820), (560, 820), (560 + 40 * op, 820 + 180 * op), (200 - 40 * op, 820 + 180 * op)],
                  fill=(46, 48, 54))
        d.rectangle([250, 726, 430, 762], fill=(14, 14, 16))  # pistola (apuntando a la pared)
        d.line([(250, 727), (430, 727)], fill=(120, 126, 134), width=3)
        d.polygon([(380, 760), (430, 760), (440, 810), (396, 812)], fill=(14, 14, 16))
        d.line([(430, 760), (440, 810)], fill=(110, 116, 124), width=3)
        hx = lerp(-60, 300, ramp(t, 0.6, 1.4))
        d.polygon([(hx - 200, 1280), (hx - 60, 1280), (hx + 40, 800), (hx - 20, 790)], fill=JACKET)
        d.ellipse([hx - 30, 770, hx + 50, 840], fill=SKIN)
        return cam(img, 1.1 + 0.04 * t, 380, 760)
    if t < ev[1]:  # balas alineadas sobre el asiento
        lt = t - ev[0]
        img = vgrad(W, H, [(0, (30, 26, 28)), (1, (54, 46, 44))])
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([-40, 380, 760, 1100], 60, fill=(60, 50, 48))
        for i in range(-2, 12):
            d.line([(0, 420 + i * 60), (W, 400 + i * 60)], fill=(52, 44, 42), width=4)
        n = min(4, int(lt / 0.3) + 1)
        for i in range(n):
            x = 170 + i * 95
            d.rounded_rectangle([x, 640, x + 36, 760], 6, fill=(180, 140, 60))
            d.polygon(ell(x + 18, 640, 18, 34, 12, math.pi, 2 * math.pi), fill=(170, 110, 70))
            d.rectangle([x, 740, x + 36, 760], fill=(150, 110, 50))
            add_glow(img, x + 18, 690, 50, (200, 160, 80), 0.3)
        d = ImageDraw.Draw(img)
        d.polygon([(0, 1280), (80, 1280), (150, 820), (90, 800)], fill=JACKET)
        d.ellipse([90, 770, 170, 840], fill=SKIN)
        return cam(img, 1.0 + 0.05 * lt, 360, 700)
    # afuera: practica contra una lata sobre un buzon, sin personas en la linea de tiro
    lt = t - ev[1]
    img = vgrad(W, H, [(0, (8, 12, 22)), (0.5, (30, 40, 54)), (1, (130, 140, 150))])
    d = ImageDraw.Draw(img)
    for i in range(14):
        pine(d, i * 56, 720, 280 + (i * 31) % 100, col=(10, 22, 26))
    d.polygon([(0, 720), (W, 720), (W, H), (0, H)], fill=(140, 150, 160))
    d.rectangle([586, 760, 598, 900], fill=(40, 30, 24))
    d.rounded_rectangle([548, 700, 636, 770], 20, fill=(40, 70, 110))
    shot = lt > 0.25
    can_y = 676 if not shot else 676 - 300 * (lt - 0.25)
    can_x = 592 if not shot else 592 + 400 * (lt - 0.25)
    d.rectangle([can_x - 14, can_y - 20, can_x + 14, can_y + 24], fill=(170, 176, 180))
    d.rectangle([can_x - 14, can_y - 6, can_x + 14, can_y + 10], fill=(190, 40, 40))
    # repartidor de perfil, brazos extendidos hacia la lata
    rec = 0
    if 0.2 < lt < 0.5:
        rec = math.sin((lt - 0.2) / 0.3 * math.pi)
    x, y, h = 170 - 14 * rec, 1180, 620
    d.polygon([(x - 50, y), (x - 10, y), (x, y - h * 0.48), (x - 60, y - h * 0.48)], fill=(32, 32, 40))
    d.polygon([(x + 10, y), (x + 50, y), (x + 20, y - h * 0.48), (x - 30, y - h * 0.48)], fill=(30, 30, 38))
    d.polygon([(x - 70, y - h * 0.46), (x + 40, y - h * 0.46), (x + 50, y - h * 0.8), (x - 60, y - h * 0.82)], fill=JACKET)
    d.polygon([(x - 50, y - h * 0.47), (x + 30, y - h * 0.47), (x + 38, y - h * 0.79), (x - 44, y - h * 0.8)],
              fill=(178, 196, 60))
    ay = y - h * 0.72 - 18 * rec
    d.polygon([(x + 20, y - h * 0.78), (x + 30, y - h * 0.7), (x + 260, ay + 6), (x + 260, ay - 18)], fill=JACKET)
    d.ellipse([x + 250, ay - 22, x + 290, ay + 10], fill=SKIN)
    d.rectangle([x + 270, ay - 22, x + 320, ay - 8], fill=(14, 14, 16))
    d.polygon(ell(x - 4, y - h * 0.9, 50, 58, 20), fill=SKIN2)
    d.polygon(ell(x - 10, y - h * 0.93, 54, 40, 20, math.pi, 2 * math.pi), fill=BEANIE)
    d.polygon([(x + 44, y - h * 0.9), (x + 60, y - h * 0.87), (x + 44, y - h * 0.84)], fill=SKIN2)
    if 0.22 < lt < 0.32:
        add_glow(img, x + 330, ay - 15, 90, (255, 220, 120), 1.0)
    snow_layer(img, t, n=180, seed=161, speed=140)
    sh = (10 * rec * math.sin(t * 60), 6 * rec)
    return cam(img, 1.05, 380, 820, shake=sh)


# ============================================================ escena 17: el hospital a lo lejos
def scene17(t, dur, ev):
    img = vgrad(W, H, [(0, (6, 10, 20)), (0.45, (30, 40, 56)), (1, (120, 130, 140))])
    d = ImageDraw.Draw(img)
    off = ramp(t, ev[0], ev[0] + 0.08)
    # ciudad entre la tormenta y hospital iluminado al fondo
    for i in range(12):
        x = i * 64 - 10
        d.rectangle([x, 560 - (i * 47) % 140, x + 56, 720], fill=(30, 36, 48))
    d.rectangle([230, 380, 490, 720], fill=(60, 68, 80))
    d.rectangle([300, 330, 420, 380], fill=(56, 62, 74))
    d.rectangle([346, 288, 374, 330], fill=(200, 30, 36) if off < 0.5 else (60, 20, 24))
    d.rectangle([334, 300, 386, 318], fill=(200, 30, 36) if off < 0.5 else (60, 20, 24))
    rng = np.random.default_rng(17)
    for r in range(8):
        for c in range(6):
            flick = (math.sin(t * 9 + r * 3 + c * 7) > -0.7)
            lit = (1 - off) * (1 if flick else 0.4)
            col = lerpc((30, 34, 40), (230, 230, 190), lit)
            d.rectangle([250 + c * 40, 400 + r * 38, 272 + c * 40, 422 + r * 38], fill=col)
    if off < 1:
        add_glow(img, 360, 520, 300, (140, 150, 120), 0.5 * (1 - off))
        add_glow(img, 360, 309, 90, (220, 40, 40), 0.8 * (1 - off))
    d = ImageDraw.Draw(img)
    # calle nevada en bajada
    d.polygon([(0, 720), (W, 720), (W, H), (0, H)], fill=(130, 140, 150))
    d.polygon([(300, 720), (420, 720), (W, H), (0, H)], fill=(100, 108, 118))
    # sombras en las calles entre el y el hospital
    for i in range(7):
        x = 200 + i * 55 + 20 * math.sin(t * 0.8 + i)
        creature(d, x, 760 + (i % 3) * 30, 50 + (i % 3) * 14, t, seed=i)
    snow_layer(img, t, n=420, seed=171, speed=220, size=(1, 4), wind=-90)
    # repartidor en lo alto de la calle, de espaldas, con la caja en el brazo
    person(d, 250, 1700, 1100, jacket=JACKET, hat=BEANIE, vest=True, arm=(0, 0, 0.06, 0.08))
    thermal_box(d, 360, 1000, 200, 130)
    return cam(img, 1.0 + 0.03 * t, 360, 640)


# ============================================================ escena 18: la sala, final
def scene18(t, dur, ev):
    flick = 1.0
    if t > ev[1]:
        flick = 0.35 + 0.65 * (1 if math.sin((t - ev[1]) * 40) > 0 or (t - ev[1]) > 0.6 else 0)
    turn = ramp(t, ev[0], ev[0] + 0.6)
    img = cinema_frame(t, 1.0, "hospital_dark", turn=turn, flicker=flick)
    k = 1 - ramp(t, 0, 0.9)  # sale de la pantalla
    z = 1.0 + 3.6 * k * k
    return cam(img, z + 0.03 * t, lerp(360, 470, k), lerp(640, 410, k))


SCENES = [scene1, scene2, scene3, scene4, scene5, scene6, scene7, scene8, scene9, scene10, scene11, scene12,
          scene13, scene14, scene15, scene16, scene17, scene18]
