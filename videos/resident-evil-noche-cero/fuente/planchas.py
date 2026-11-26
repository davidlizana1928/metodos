from arte import *

NIGHT_TOP, NIGHT_BOT = (8, 14, 30), (40, 60, 92)

def screen_city(w, h, monsters=False, seed=1):
    img = grad((10, 16, 34), (54, 70, 96), w, h)
    d = ImageDraw.Draw(img)
    mountains(d, int(h*0.62), h*0.38, (36, 46, 66), seed, snowcap=(170, 186, 210), w=w, step=max(20, w//14))
    mountains(d, int(h*0.75), h*0.22, (26, 34, 50), seed+4, snowcap=(140, 158, 186), w=w, step=max(16, w//18))
    city(d, int(h*0.86), w*0.12, w*0.88, seed, scale=w/420)
    d.rectangle([0, int(h*0.86), w, h], fill=(120, 138, 168))
    for k, sx in enumerate((0.3, 0.55, 0.72)):
        img = smoke_column(img, w*sx, h*0.8, h*0.6, k+seed, alpha=0.5)
    d = ImageDraw.Draw(img)
    if monsters:
        for k in range(6):
            creature(d, w*(0.2+k*0.12), h*0.95, h*0.1, k, color=(10, 14, 12))
    return img

def cine(content, title_dim=False):
    img = grad((10, 6, 8), (26, 12, 14))
    d = ImageDraw.Draw(img)
    # pantalla
    sx0, sy0, sx1, sy1 = 34, 300, PW-34, 760
    d.rectangle([sx0-10, sy0-10, sx1+10, sy1+10], fill=(6, 4, 4))
    c = content.resize((sx1-sx0, sy1-sy0), Image.LANCZOS)
    img.paste(c, (sx0, sy0))
    # cortinas
    d = ImageDraw.Draw(img)
    for x0, x1 in ((0, 34), (PW-34, PW)):
        for k in range(0, 34, 6):
            d.rectangle([x0+k, 200, x0+k+3, 900], fill=(90, 14, 22))
    # haz del proyector (arriba izquierda)
    img = cone(img, (40, 120), (sx0+60, sy0), (sx1-60, sy1-40), (70, 66, 56), strength=0.35, blur=40)
    d = ImageDraw.Draw(img)
    d.rectangle([14, 96, 70, 140], fill=(18, 14, 14)); d.ellipse([52, 108, 70, 126], fill=(255, 240, 200))
    # luz reflejada de la pantalla
    img = glow(img, (PW//2, 760), 700, (24, 30, 40), 0.8)
    d = ImageDraw.Draw(img)
    # filas de butacas carmesí (4 a 5 por fila en primer plano)
    rows = [(900, 120, 7), (1040, 150, 6), (1200, 185, 5), (1390, 215, 4)]
    for ri, (y, sw, n) in enumerate(rows):
        x0 = (PW-n*sw)/2-sw*0.25*(ri % 2)
        for k in range(n+1):
            x = x0+k*sw
            d.rounded_rectangle([x+4, y, x+sw-4, y+sw*1.1], radius=int(sw*0.22), fill=(110, 16, 28))
            d.rounded_rectangle([x+10, y+8, x+sw-10, y+sw*0.7], radius=int(sw*0.2), fill=(140, 24, 38))
        if ri == 1:
            # el Espectador, sentado de espaldas en la segunda fila: hombros ≈ 0,8 ancho de butaca
            ex = x0+2.5*sw
            sh = sw*0.8
            d.rounded_rectangle([ex-sh/2, y-sw*0.25, ex+sh/2, y+sw*0.5], radius=int(sh*0.3), fill=(22, 22, 28))
            d.ellipse([ex-sh*0.22, y-sw*0.62, ex+sh*0.22, y-sw*0.12], fill=(24, 20, 18))
            d.rectangle([ex-sh*0.1, y-sw*0.2, ex+sh*0.1, y-sw*0.1], fill=(24, 20, 18))
    return img

# ---------------- escenas ----------------
def p1a(): return cine(screen_city(800, 460))
def p1b(): return cine(screen_city(800, 460, monsters=True))

def road_scene(car_x=420, car_y=1060, cw=300, heavy=False, sign=False, espect=False, seed=2):
    img = grad(NIGHT_TOP, (60, 80, 110))
    d = ImageDraw.Draw(img)
    mountains(d, 700, 300, (34, 44, 64), seed, snowcap=(160, 176, 204))
    city(d, 760, 520, 760, seed+1, scale=0.8)
    img = smoke_column(img, 640, 740, 260, 3)
    d = ImageDraw.Draw(img)
    mountains(d, 840, 160, (26, 34, 50), seed+5, snowcap=(130, 150, 180))
    snow_ground(d, 900, seed=seed)
    trees(d, 930, 14, (18, 30, 34), seed, 120, 240, snow=(170, 186, 210))
    # carretera en curva
    d.polygon([(-50, 1536), (360, 1000), (520, 960), (900, 1000), (900, 1120), (560, 1060), (420, 1100), (200, 1536)], fill=(48, 54, 66))
    d.line([(60, 1536), (380, 1060), (520, 1010), (880, 1050)], fill=(150, 150, 120), width=4)
    # barandas
    d.line([(0, 1280), (300, 1050), (500, 990), (900, 1010)], fill=(140, 146, 156), width=6)
    for k in range(8):
        px = k*120; py = 1280-k*35 if k < 3 else 1020
        d.line([(px, py), (px, py+30)], fill=(110, 116, 126), width=5)
    if sign:
        d.rectangle([150, 880, 158, 1060], fill=(90, 94, 100))
        d.rectangle([90, 840, 260, 920], fill=(30, 90, 60)); d.rectangle([90, 840, 260, 862], fill=(220, 226, 234))
        d.polygon([(240, 880), (268, 880), (254, 868)], fill=(220, 226, 234))
    car(d, car_x, car_y, cw)
    img = cone(img, (car_x+cw*0.5, car_y-cw*0.1), (car_x+cw*2.0, car_y-cw*0.6), (car_x+cw*2.2, car_y+cw*0.25), (200, 196, 160), 0.6)
    d = ImageDraw.Draw(img)
    if espect:
        # Espectador de pie en la orilla, un poco más alto que el auto (~0,36·w·1,15)
        person(d, 120, 1300, cw*0.36*1.2/0.83*0.83+60, ESPECT, view='back')
    return img

def p2a(): return road_scene()
def p2b():
    img = grad((10, 14, 24), (20, 26, 40))
    d = ImageDraw.Draw(img)
    # ventana / parabrisas con nieve nocturna
    d.polygon([(0, 260), (PW, 200), (PW, 760), (0, 800)], fill=(30, 42, 64))
    mountains(d, 700, 180, (24, 32, 48), 9, snowcap=(110, 128, 160))
    d.polygon([(0, 800), (PW, 760), (PW, PH), (0, PH)], fill=(16, 18, 26))
    d.polygon([(0, 140), (PW, 120), (PW, 220), (0, 270)], fill=(12, 14, 20))
    # repartidor de perfil al volante (ocupa la mitad superior de la ventana)
    person(d, 250, 1500, 1100, REP, view='side', pose='sit')
    d.ellipse([340, 830, 560, 1240], outline=(30, 30, 34), width=26)  # volante
    # mochila médica en el copiloto con cinturón
    d.rounded_rectangle([580, 940, 800, 1260], radius=30, fill=(232, 236, 238))
    d.rectangle([580, 940, 800, 975], fill=(22, 22, 24))
    d.rectangle([675, 1060, 705, 1160], fill=(196, 40, 46)); d.rectangle([640, 1095, 740, 1125], fill=(196, 40, 46))
    d.line([(840, 860), (560, 1320)], fill=(40, 40, 44), width=22)
    img = glow(img, (450, 1200), 420, (40, 60, 90), 0.6)
    return img

def p3a():
    img = grad((200, 214, 206), (150, 166, 160))
    d = ImageDraw.Draw(img)
    # pasillo en perspectiva
    d.polygon([(0, 1100), (300, 760), (564, 760), (PW, 1100), (PW, PH), (0, PH)], fill=(170, 182, 176))
    d.polygon([(0, 0), (300, 520), (564, 520), (PW, 0)], fill=(226, 232, 228))
    for k in range(4):
        y = 80+k*110; d.rectangle([300-200/(k+1), y, 564+200/(k+1), y+16], fill=(255, 255, 246))
    d.rectangle([300, 520, 564, 760], fill=(190, 204, 198))
    d.rectangle([330, 560, 420, 600], fill=(60, 140, 110)); d.rectangle([450, 560, 540, 600], fill=(200, 200, 190))  # carteles sin texto
    d.rectangle([330, 690, 470, 720], fill=(236, 236, 236)); d.rectangle([330, 720, 340, 760], fill=(120, 120, 120)); d.rectangle([460, 720, 470, 760], fill=(120, 120, 120))  # camilla
    # mostrador a la cintura
    d.rectangle([420, 1100, PW, 1240], fill=(110, 130, 140)); d.rectangle([420, 1090, PW, 1110], fill=(220, 226, 228))
    person(d, 640, 1420, 520, ENF, view='side', flip=-1)
    d = ImageDraw.Draw(img)
    d.rectangle([420, 1100, PW, 1240], fill=(110, 130, 140)); d.rectangle([420, 1090, PW, 1110], fill=(220, 226, 228))
    person(d, 260, 1520, 560, REP, view='side', pose='give')
    d.rounded_rectangle([390, 1080, 470, 1150], radius=10, fill=(244, 246, 248)); d.rectangle([390, 1080, 470, 1092], fill=(196, 40, 46))
    return img

def p3b():
    img = grad((10, 14, 26), (30, 40, 56))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 300, PW, 1000], fill=(44, 52, 62))
    d.rectangle([300, 560, 560, 1000], fill=(220, 230, 222))  # puerta de urgencias iluminada
    d.rectangle([300, 480, 560, 540], fill=(170, 30, 36))  # franja roja sin texto
    d.rectangle([0, 1000, PW, PH], fill=(54, 58, 66))
    for k in range(6):
        d.line([(k*170, 1100), (k*170+80, 1536)], fill=(200, 200, 160), width=4)
    img = glow(img, (430, 800), 500, (60, 70, 60), 0.9)
    d = ImageDraw.Draw(img)
    person(d, 660, 1000, 380, dict(coat=(30, 34, 40), pants=(30, 30, 34), skin=(170, 130, 100), hair=(30, 26, 24), hat=(26, 26, 30)), view='front')  # guardia
    person(d, 360, 1360, 470, REP, view='back')
    car(d, 120, 1240, 260, lights=False)
    return img

def p3c():
    img = grad((6, 8, 14), (14, 16, 24))
    d = ImageDraw.Draw(img)
    d.polygon([(0, 0), (PW, 0), (PW, 520), (0, 600)], fill=(18, 26, 40))
    d.polygon([(0, 640), (PW, 560), (PW, 760), (0, 820)], fill=(22, 24, 30))  # tablero
    for k in range(5):
        d.ellipse([140+k*60, 650, 170+k*60, 680], fill=(40, 140, 170))
    d.rounded_rectangle([0, 980, PW, PH], radius=60, fill=(30, 30, 36))  # asiento
    # consola portátil sobre el asiento
    d.rounded_rectangle([230, 1120, 640, 1320], radius=60, fill=(40, 42, 48))
    d.rounded_rectangle([330, 1150, 540, 1290], radius=10, fill=(90, 170, 210))
    d.ellipse([255, 1195, 305, 1245], fill=(20, 20, 24)); d.ellipse([570, 1180, 600, 1210], fill=(180, 40, 50)); d.ellipse([590, 1220, 620, 1250], fill=(40, 120, 200))
    img = glow(img, (435, 1220), 300, (40, 80, 100), 0.8)
    img = glow(img, (300, 680), 400, (20, 50, 60), 0.6)
    return img

def phone(img, box, content):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    d.rounded_rectangle([x0-14, y0-30, x1+14, y1+30], radius=34, fill=(14, 14, 16))
    if content is not None:
        img.paste(content.resize((x1-x0, y1-y0)), (x0, y0))
    else:
        d.rectangle(box, fill=(4, 4, 6))
    return img

def kitchen(w, h):
    k = grad((230, 160, 90), (150, 90, 50), w, h)
    dk = ImageDraw.Draw(k)
    dk.rectangle([0, int(h*0.55), w, h], fill=(170, 110, 70))
    dk.rectangle([int(w*0.62), int(h*0.12), int(w*0.95), int(h*0.42)], fill=(40, 50, 80))
    dk.rectangle([int(w*0.05), int(h*0.15), int(w*0.4), int(h*0.3)], fill=(200, 140, 80))
    for i in range(3):
        dk.ellipse([int(w*(0.1+i*0.1)), int(h*0.2), int(w*(0.16+i*0.1)), int(h*0.27)], fill=(240, 230, 200))
    k = glow(k, (int(w*0.3), int(h*0.1)), w, (60, 40, 10), 0.8)
    return k

def novia_call(w, h):
    k = kitchen(w, h)
    dk = ImageDraw.Draw(k)
    person(dk, w*0.5, h*1.25, h*1.15, NOVIA, view='side', flip=-1)
    # mano sobre el vientre (embarazo temprano)
    dk.ellipse([w*0.38, h*0.88, w*0.58, h*1.02], fill=(232, 220, 196))
    dk.ellipse([w*0.42, h*0.9, w*0.5, h*0.96], fill=(214, 172, 146))
    return k

def cabin(phone_content):
    img = grad((6, 8, 14), (16, 18, 26))
    d = ImageDraw.Draw(img)
    d.polygon([(0, 0), (PW, 0), (PW, 620), (0, 700)], fill=(16, 22, 34))
    mountains(d, 620, 120, (12, 16, 24), 4)
    d.polygon([(0, 700), (PW, 620), (PW, 900), (0, 980)], fill=(22, 24, 30))
    img = phone(img, (250, 420, 620, 1080), phone_content)
    d = ImageDraw.Draw(img)
    d.rectangle([410, 1110, 460, 1240], fill=(24, 24, 28))  # soporte
    return img

def p4a(): return cabin(novia_call(370, 660))
def p4b():
    img = cabin(None)
    d = ImageDraw.Draw(img)
    person(d, 120, 1900, 1500, REP, view='side')
    # pulgar sobre la pantalla
    d.polygon([(200, 900), (560, 760), (600, 800), (240, 980)], fill=(28, 40, 74))
    d.ellipse([540, 740, 620, 820], fill=(206, 160, 130))
    return img

def medical_lot(with_desp=False):
    img = grad((12, 16, 30), (34, 40, 56))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 360, PW, 1000], fill=(70, 76, 86))
    d.rectangle([0, 340, PW, 370], fill=(50, 54, 60))
    d.rectangle([90, 470, 330, 680], fill=(230, 200, 130))  # ventana con reloj
    d.ellipse([170, 500, 250, 580], fill=(240, 240, 236), outline=(30, 30, 30), width=4)
    d.line([(210, 540), (210, 510)], fill=(20, 20, 20), width=4); d.line([(210, 540), (232, 552)], fill=(20, 20, 20), width=3)
    d.rectangle([560, 640, 700, 1000], fill=(40, 46, 56)); d.rectangle([566, 646, 694, 1000], fill=(250, 220, 150) if with_desp else (60, 66, 76))  # puerta lateral 2 m
    d.rectangle([0, 1000, PW, PH], fill=(46, 50, 58))
    for k in range(5):
        d.line([(k*190-40, 1060), (k*190+60, 1536)], fill=(190, 190, 150), width=4)
    img = glow(img, (630, 560), 180, (90, 80, 50), 0.9)
    img = glow(img, (210, 560), 300, (70, 50, 20), 0.6)
    d = ImageDraw.Draw(img)
    car(d, 250, 1300, 380, lights=False)
    return img

def p5a():
    img = medical_lot()
    d = ImageDraw.Draw(img)
    person(d, 560, 1360, 460, REP, view='side', flip=-1)
    d.line([(495, 1095), (485, 1120)], fill=(210, 210, 200), width=4)  # llaves
    return img

def p5b():
    img = medical_lot(True)
    d = ImageDraw.Draw(img)
    person(d, 700, 1340, 430, DESP, view='side', pose='give', flip=-1)
    person(d, 360, 1360, 440, REP, view='side', pose='give')
    # caja térmica metálica (como caja de zapatos)
    d.rounded_rectangle([450, 1040, 600, 1110], radius=8, fill=(170, 178, 188))
    d.rectangle([450, 1040, 600, 1056], fill=(210, 216, 224)); d.line([(460, 1075), (590, 1075)], fill=(120, 126, 136), width=3)
    return img

def p6a(): return road_scene(car_x=360, car_y=1080, cw=320, seed=6)
def p6b(): return road_scene(car_x=560, car_y=1100, cw=260, sign=True, espect=True, seed=8)

def p7a():
    img = grad((4, 6, 12), (14, 18, 28))
    d = ImageDraw.Draw(img)
    d.polygon([(0, 900), (PW, 900), (PW, PH), (0, PH)], fill=(30, 34, 44))
    img = cone(img, (200, 1500), (300, 820), (520, 820), (210, 206, 180), 0.8, 40)
    img = cone(img, (660, 1500), (380, 820), (600, 820), (210, 206, 180), 0.8, 40)
    d = ImageDraw.Draw(img)
    person(d, 440, 990, 300, dict(MUJER, coat=(70, 20, 30)), view='front')
    # marco del parabrisas y tablero
    d.polygon([(0, 0), (PW, 0), (PW, 160), (0, 220)], fill=(8, 8, 10))
    d.polygon([(0, 1240), (PW, 1200), (PW, PH), (0, PH)], fill=(14, 14, 18))
    d.ellipse([120, 1150, 520, 1700], outline=(26, 26, 30), width=30)
    return img

def p7b():
    img = grad(NIGHT_TOP, (50, 66, 92))
    d = ImageDraw.Draw(img)
    trees(d, 860, 20, (16, 26, 30), 4, 140, 280, snow=(160, 176, 200))
    snow_ground(d, 860, seed=7)
    d.polygon([(0, 1000), (PW, 960), (PW, 1300), (0, 1360)], fill=(80, 92, 112))
    for k in range(3):
        d.arc([100+k*30, 1020+k*30, 900+k*30, 1500+k*30], 190, 260, fill=(40, 46, 58), width=8)  # marcas de neumáticos
    car(d, 470, 1200, 380)
    img = glow(img, (290, 1150), 380, (180, 10, 10), 0.9)  # luces de freno tiñen la nieve
    return img

def p7c():
    img = grad(NIGHT_TOP, (50, 66, 92))
    d = ImageDraw.Draw(img)
    trees(d, 860, 20, (16, 26, 30), 5, 140, 280, snow=(160, 176, 200))
    snow_ground(d, 860, seed=9)
    d.polygon([(0, 1000), (PW, 960), (PW, 1300), (0, 1360)], fill=(80, 92, 112))
    car(d, 260, 1180, 330)
    img = cone(img, (420, 1150), (860, 980), (860, 1260), (200, 196, 160), 0.5)
    d = ImageDraw.Draw(img)
    person(d, 640, 1340, 300, MUJER, pose='lie', flip=-1)  # tendida, de espaldas a cámara
    person(d, 470, 1290, 330, REP, view='side', pose='run')
    return img

def patrol(d, x, yf, w, flip=1):
    car(d, x, yf, w, color=(30, 36, 52), flip=flip)
    d.rectangle([x-0.18*w, yf-0.36*w*0.97, x+0.18*w, yf-0.36*w*0.9], fill=(40, 40, 46))
    d.rectangle([x-0.18*w, yf-0.36*w*0.99, x-0.01*w, yf-0.36*w*0.92], fill=(230, 40, 40))
    d.rectangle([x+0.01*w, yf-0.36*w*0.99, x+0.18*w, yf-0.36*w*0.92], fill=(40, 80, 240))

def p8a():
    img = grad(NIGHT_TOP, (44, 60, 86))
    d = ImageDraw.Draw(img)
    trees(d, 860, 22, (16, 26, 30), 11, 140, 280, snow=(160, 176, 200))
    snow_ground(d, 860, seed=11)
    d.polygon([(0, 1000), (PW, 960), (PW, 1300), (0, 1360)], fill=(80, 92, 112))
    car(d, 700, 1180, 300, lights=False)
    patrol(d, 250, 1240, 420)
    d = ImageDraw.Draw(img)
    person(d, 560, 1400, 420, POLI, view='side', pose='flash', flip=-1)
    img = cone(img, (450, 1110), (200, 1300), (330, 1400), (220, 220, 190), 0.5, 20)
    d = ImageDraw.Draw(img)
    person(d, 440, 1420, 380, dict(MUJER, coat=(120, 100, 70)), view='side', flip=-1)  # envuelta en manta
    d.line([(424, 1080), (430, 1110)], fill=(70, 150, 90), width=3)  # venas verdosas apenas visibles
    return img

def p8b():
    img = grad(NIGHT_TOP, (44, 60, 86))
    d = ImageDraw.Draw(img)
    trees(d, 900, 26, (16, 26, 30), 12, 160, 320, snow=(160, 176, 200))
    snow_ground(d, 900, seed=12)
    d.polygon([(330, 900), (530, 900), (PW, PH), (0, PH)], fill=(70, 80, 98))
    car(d, 430, 1250, 340, color=(30, 36, 52), view='back')
    d.rectangle([430-60, 1250-180, 430-5, 1250-165], fill=(230, 40, 40)); d.rectangle([435, 1250-180, 490, 1250-165], fill=(40, 80, 240))
    return img

def p8c():
    img = grad((4, 8, 16), (20, 30, 46))
    d = ImageDraw.Draw(img)
    mountains(d, 760, 220, (20, 28, 40), 13, snowcap=(110, 126, 150))
    snow_ground(d, 900, color=(110, 126, 156), seed=13)
    trees(d, 980, 40, (8, 14, 16), 13, 180, 380, snow=(120, 136, 160))
    d.line([(0, 1100), (300, 1020), (560, 1000), (900, 1060)], fill=(60, 66, 80), width=24)
    return img

def p9a():
    img = grad((6, 10, 22), (30, 40, 56))
    d = ImageDraw.Draw(img)
    mountains(d, 700, 200, (20, 28, 40), 14, snowcap=(110, 126, 150))
    snow_ground(d, 1150, seed=14)
    bx0, bx1, top = 220, 640, 380
    d.rectangle([bx0, top, bx1, 1160], fill=(58, 66, 78))
    fh = (1160-top)/10
    for k in range(10):
        y = top+k*fh
        d.rectangle([bx0+10, y+10, bx1-10, y+fh-12], fill=(30, 50, 64) if k != 2 else (20, 30, 30))
        d.line([(bx0, y), (bx1, y)], fill=(80, 88, 100), width=3)
    for wx in (260, 360, 470, 560):  # ventanas rotas en piso alto
        d.polygon([(wx, top+2*fh+10), (wx+40, top+2*fh+30), (wx+20, top+2*fh+60), (wx+50, top+3*fh-12), (wx, top+3*fh-12)], fill=(8, 10, 10))
    for ax in (bx0+10, bx1-10):
        d.rectangle([ax-8, top-30, ax+8, top], fill=(80, 70, 40))
    return img

def p9b():
    img = grad((6, 10, 22), (30, 40, 56))
    d = ImageDraw.Draw(img)
    mountains(d, 640, 200, (20, 28, 40), 15, snowcap=(110, 126, 150))
    snow_ground(d, 900, seed=15)
    d.rectangle([520, 260, 864, 1000], fill=(58, 66, 78))
    for k in range(8):
        d.rectangle([540, 290+k*90, 860, 350+k*90], fill=(30, 50, 64))
    d.polygon([(560, 380), (620, 400), (600, 440), (650, 440), (560, 440)], fill=(8, 10, 10))
    rng = random.Random(15)
    for k in range(18):  # casas del valle
        x = rng.uniform(20, 480); y = rng.uniform(1100, 1400); s = rng.uniform(40, 70)
        d.rectangle([x, y-s*0.6, x+s, y], fill=(40, 46, 58)); d.polygon([(x-6, y-s*0.6), (x+s/2, y-s), (x+s+6, y-s*0.6)], fill=(150, 166, 190))
        d.rectangle([x+s*0.3, y-s*0.4, x+s*0.5, y-s*0.2], fill=(240, 200, 120))
    return img

def town_street(seed=16, lamps=True):
    img = grad((6, 10, 22), (26, 34, 48))
    d = ImageDraw.Draw(img)
    for k, x in enumerate((0, 200, 520, 700)):
        hgt = 400+(k*97 % 180)
        d.rectangle([x, 900-hgt, x+180, 1060], fill=(36+k*4, 38, 50))
        for wy in range(920-hgt, 1000, 90):
            d.rectangle([x+30, wy, x+70, wy+50], fill=(30, 36, 44)); d.rectangle([x+110, wy, x+150, wy+50], fill=(50, 46, 40) if (wy+k) % 3 else (180, 150, 90))
    d.polygon([(0, 1060), (PW, 1060), (PW, PH), (0, PH)], fill=(140, 156, 182))
    d.polygon([(300, 1060), (560, 1060), (PW, PH), (0, PH)], fill=(86, 96, 116))
    return img

def lamp(img, x, yb, h):
    d = ImageDraw.Draw(img)
    d.rectangle([x-5, yb-h, x+5, yb], fill=(30, 30, 34)); d.rectangle([x-5, yb-h, x+40, yb-h+8], fill=(30, 30, 34))
    d.ellipse([x+26, yb-h+4, x+50, yb-h+20], fill=(255, 220, 150))
    return glow(img, (x+38, yb-h+40), h*0.7, (90, 70, 30), 0.9)

def p9c():
    img = town_street()
    for x, yb in ((140, 1200), (700, 1260)):
        img = lamp(img, x, yb, 420)
    d = ImageDraw.Draw(img)
    car(d, 640, 1240, 300, lights=False)
    d.polygon([(640+20, 1240-80), (640+90, 1240-150), (640+100, 1240-110)], fill=(50, 54, 62))  # puerta abierta
    d.rectangle([60, 1080, 330, 1180], fill=(160, 150, 120)); d.ellipse([90, 1140, 150, 1200], fill=(14, 14, 16)); d.ellipse([240, 1140, 300, 1200], fill=(14, 14, 16))  # camión volcado
    for k, (x, y) in enumerate(((330, 1180), (440, 1150), (520, 1210))):
        creature(d, x, y, 210, k+20)  # siluetas de altura adulta, el farol duplica su altura
    return img

def p10a():
    img = grad((8, 12, 24), (40, 54, 78))
    d = ImageDraw.Draw(img)
    mountains(d, 700, 160, (24, 32, 46), 17, snowcap=(120, 136, 162))
    trees(d, 760, 30, (12, 20, 22), 17, 90, 180, snow=(130, 146, 170))
    snow_ground(d, 760, seed=17)
    for k in range(10):
        d.ellipse([300+k*50, 1300-k*12, 316+k*50, 1308-k*12], fill=(120, 136, 166))
    person(d, 560, 1360, 460, REP, view='side', pose='run')
    d.rounded_rectangle([590, 1040, 680, 1090], radius=6, fill=(170, 178, 188))
    dog(d, 190, 1250, 150, flip=1)  # a media distancia, a la cintura del repartidor
    return img

def farmhouse(open_door=False):
    img = grad((8, 12, 24), (40, 54, 78))
    d = ImageDraw.Draw(img)
    snow_ground(d, 1000, seed=18)
    d.rectangle([20, 620, 330, 1010], fill=(120, 30, 30)); d.polygon([(0, 620), (175, 470), (350, 620)], fill=(140, 150, 170))  # granero rojo
    d.rectangle([130, 800, 230, 1010], fill=(80, 20, 20)); d.line([(130, 800), (230, 1010)], fill=(160, 140, 120), width=5); d.line([(230, 800), (130, 1010)], fill=(160, 140, 120), width=5)
    d.rectangle([360, 640, 840, 1020], fill=(96, 80, 64)); d.polygon([(340, 640), (600, 470), (860, 640)], fill=(150, 160, 180))
    d.rectangle([420, 720, 520, 820], fill=(250, 200, 110)); d.rectangle([700, 720, 800, 820], fill=(250, 200, 110))
    dx0, dx1 = 560, 660
    d.rectangle([dx0, 790, dx1, 1020], fill=(255, 214, 130) if open_door else (60, 40, 30))
    img = glow(img, (610, 880), 360, (90, 70, 20), 0.8)
    d = ImageDraw.Draw(img)
    for k in range(9):  # cerca
        d.rectangle([k*100, 1180, k*100+12, 1300], fill=(70, 56, 44))
    d.rectangle([0, 1210, PW, 1222], fill=(70, 56, 44)); d.rectangle([0, 1260, PW, 1272], fill=(70, 56, 44))
    return img

def p10b():
    img = farmhouse()
    d = ImageDraw.Draw(img)
    person(d, 530, 1030, 240, REP, view='side', pose='knock')
    person(d, 140, 1480, 520, ESPECT, view='back')  # Espectador junto a la cerca
    return img

def p10c():
    img = grad((120, 90, 40), (60, 40, 20))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, PW, PH], fill=(30, 22, 18))
    d.rectangle([170, 160, 700, 1400], fill=(255, 210, 120))  # umbral a contraluz
    d.rectangle([600, 500, 640, 580], fill=(60, 50, 40)); d.line([(620, 580), (612, 640)], fill=(60, 50, 40), width=3)  # teléfono fijo en la pared
    img = glow(img, (430, 600), 700, (90, 60, 10), 0.8)
    d = ImageDraw.Draw(img)
    person(d, 420, 1400, 1180, dict(GRANJ, coat=(60, 20, 20), pants=(26, 34, 50)), view='front')  # llena casi toda la puerta
    rng = random.Random(4)
    for _ in range(9):  # brazo deformado
        x = 560+rng.uniform(-30, 40); y = 750+rng.uniform(0, 300); r = rng.uniform(18, 46)
        d.ellipse([x-r, y-r, x+r, y+r], fill=(26, 34, 28))
    d.rectangle([0, 1400, PW, PH], fill=(150, 166, 190))
    return img

def barn():
    img = grad((24, 18, 14), (40, 30, 22))
    d = ImageDraw.Draw(img)
    for k in range(0, PW, 70):
        d.rectangle([k, 0, k+64, PH], fill=(54+(k % 3)*6, 40, 28))
    d.rectangle([0, 1250, PW, PH], fill=(60, 52, 40))
    for k in range(5):  # herramientas
        x = 80+k*70; d.rectangle([x, 300, x+8, 640], fill=(110, 86, 60)); d.rectangle([x-14, 620, x+22, 660], fill=(120, 124, 130))
    img = glow(img, (600, 200), 600, (80, 60, 30), 0.7)
    return img

def p11a():
    img = barn()
    d = ImageDraw.Draw(img)
    d.rectangle([520, 420, 820, 440], fill=(70, 56, 40))
    person(d, 450, 1460, 800, REP, view='back')
    # escopeta sostenida torpemente, horizontal, sin apuntar a nadie
    d.line([(400, 860), (800, 820)], fill=(30, 30, 32), width=14); d.polygon([(380, 850), (300, 890), (310, 920), (420, 875)], fill=(110, 70, 40))
    return img

def p11b():
    img = barn()
    d = ImageDraw.Draw(img)
    d.rectangle([60, 900, 820, 960], fill=(96, 70, 46)); d.rectangle([90, 960, 120, 1400], fill=(70, 50, 34)); d.rectangle([760, 960, 790, 1400], fill=(70, 50, 34))
    d.rectangle([260, 770, 520, 900], fill=(60, 80, 52)); d.rectangle([260, 770, 520, 800], fill=(80, 100, 66))
    for k in range(6):
        d.rounded_rectangle([290+k*36, 815, 314+k*36, 890], radius=6, fill=(180, 40, 36)); d.rectangle([290+k*36, 870, 314+k*36, 890], fill=(200, 170, 90))
    d.polygon([(560, 980), (700, 900), (760, 940), (620, 1020)], fill=(28, 40, 74))
    d.ellipse([530, 870, 600, 940], fill=(206, 160, 130)); d.rounded_rectangle([548, 860, 566, 920], radius=6, fill=(180, 40, 36))
    img = glow(img, (400, 800), 400, (70, 50, 20), 0.8)
    return img

def p11c():
    img = grad((4, 6, 8), (16, 18, 20))
    d = ImageDraw.Draw(img)
    d.polygon([(0, 0), (330, 600), (534, 600), (PW, 0)], fill=(44, 46, 48))
    d.polygon([(0, PH), (330, 860), (534, 860), (PW, PH)], fill=(52, 54, 56))
    d.polygon([(0, 0), (330, 600), (330, 860), (0, PH)], fill=(36, 38, 40))
    d.polygon([(PW, 0), (534, 600), (534, 860), (PW, PH)], fill=(36, 38, 40))
    d.rectangle([330, 600, 534, 860], fill=(4, 4, 6))
    img = cone(img, (500, 1060), (330, 760), (480, 880), (200, 196, 170), 0.8, 20)
    d = ImageDraw.Draw(img)
    person(d, 440, 1500, 760, REP, view='back', pose='flash')
    d.line([(380, 1050), (470, 1260)], fill=(28, 28, 30), width=12)  # arma apuntando al suelo
    return img

def p12a():
    img = town_street(19)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 200, 330, 1400], fill=(110, 50, 40))
    for y in range(200, 1400, 30):
        for x in range((y//30 % 2)*30, 330, 60):
            d.rectangle([x, y, x+56, y+26], outline=(80, 36, 30), width=2)
    img = lamp(img, 720, 1300, 500)
    d = ImageDraw.Draw(img)
    person(d, 430, 1420, 560, REP, view='side', flip=-1)
    return img

def p12b():
    img = grad((14, 18, 30), (30, 36, 50))
    d = ImageDraw.Draw(img)
    # plano medio: antebrazo con mordida (sin sangre explícita)
    d.polygon([(0, 1100), (PW, 700), (PW, 1000), (0, 1400)], fill=(28, 40, 74))
    d.polygon([(120, 1000), (700, 700), (760, 860), (180, 1160)], fill=(206, 160, 130))
    for k in range(8):
        a = k*0.8; d.ellipse([430+math.cos(a)*40-8, 860+math.sin(a)*24-8, 430+math.cos(a)*40+8, 860+math.sin(a)*24+8], fill=(110, 60, 60))
    return img

def p12c():
    img = town_street(20)
    d = ImageDraw.Draw(img)
    c = screen_city(500, 300, seed=5)
    img.paste(c.resize((360, 200)), (480, 820))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 200, 300, 1400], fill=(110, 50, 40))
    person(d, 360, 1400, 600, REP, view='side')
    d.rounded_rectangle([420, 1320, 560, 1400], radius=8, fill=(232, 236, 238)); d.rectangle([420, 1320, 560, 1336], fill=(196, 40, 46))  # botiquín abierto
    d.rounded_rectangle([600, 1330, 720, 1395], radius=6, fill=(170, 178, 188))  # caja metálica intacta
    d.rectangle([330, 1000, 400, 1040], fill=(240, 240, 236))  # venda
    return img

def p13a():
    img = town_street(21)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([290, 900, 580, 1090], radius=20, fill=(220, 224, 228))  # camioneta blanca sin logos
    d.rectangle([310, 920, 560, 990], fill=(40, 50, 66)); d.ellipse([340, 1050, 390, 1100], fill=(14, 14, 16)); d.ellipse([490, 1050, 540, 1100], fill=(14, 14, 16))
    for x, P in ((370, EMP1), (500, EMP2)):
        person(d, x, 1140, 200, P, view='front')
        d.line([(x-30, 1040), (x-50, 1130)], fill=(26, 26, 28), width=6)  # armas al suelo
    img = cone(img, (340, 990), (100, 1500), (420, 1500), (220, 220, 200), 0.5, 30)
    img = cone(img, (530, 990), (440, 1500), (800, 1500), (220, 220, 200), 0.5, 30)
    return img

def p13b():
    img = p13a()
    d = ImageDraw.Draw(img)
    person(d, 430, 1300, 230, REP, view='back')
    person(d, 700, 1700, 860, ESPECT, view='back')  # en primer plano, desde la esquina
    return img

def street_far():
    img = town_street(22)
    d = ImageDraw.Draw(img)
    c = screen_city(500, 300, seed=7)
    img.paste(c.resize((400, 220)), (240, 840))
    d = ImageDraw.Draw(img)
    person(d, 430, 1300, 160, REP, view='back')
    return img

def p14a(): return cine(street_far())
def split_screen():
    a = screen_city(400, 460, seed=9)
    k = kitchen(400, 460)
    dk = ImageDraw.Draw(k)
    dk.rectangle([60, 60, 340, 400], fill=(255, 196, 110)); dk.line([(200, 60), (200, 400)], fill=(120, 70, 40), width=10); dk.line([(60, 230), (340, 230)], fill=(120, 70, 40), width=10)
    k = glow(k, (200, 230), 260, (60, 40, 0), 1.0)
    out = Image.new('RGB', (800, 460)); out.paste(a, (0, 0)); out.paste(k, (400, 0))
    ImageDraw.Draw(out).rectangle([396, 0, 404, 460], fill=(0, 0, 0))
    return out
def p14b(): return cine(split_screen())
def p14c(): return cine(split_screen())
