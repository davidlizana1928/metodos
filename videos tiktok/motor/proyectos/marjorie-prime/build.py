#!/usr/bin/env python3
"""Genera index.html de Marjorie Prime desde escenas.json, tiempos de la voz y la biblioteca svgkit.

Uso: python3 -I build.py   (desde esta carpeta)
Escenas construidas: ver ESCENAS. Las que faltan se muestran como pendiente (solo en revisión).
"""
import json
import pathlib
import sys

AQUI = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent.parent / "biblioteca"))
from svgkit import (Defs, persona, sillon, lampara_pie, planta, sala_cine, mulberry32, tono, espectador_pie, sofa, mesa, lluvia, silla)  # noqa: E402

ESC = json.load(open(AQUI / "escenas.json"))
TIEMPOS = json.load(open(AQUI.parent.parent.parent / "instrucciones/2026-11-28-marjorie-prime/voz/tiempos.json"))
TOTAL = ESC[-1]["fin"]
d = Defs("m")
F = d.filtros()


def palabra(n_frase, texto):
    for w in TIEMPOS[n_frase - 1]["palabras"]:
        if w["p"].lower().startswith(texto.lower()):
            return w["inicio"]
    raise KeyError(texto)


# ------------------------------------------------------------ personajes del video
ANCIANA = dict(falda="#1d6f86", torso="#1d6f86", chal="#d4d4cf", pelo="moño_blanco", pelo_color="#f2f2ee", piel="#e8b898")
ESPOSO = dict(torso="#1e2f6e", piernas="#6b6f78", pelo="ondulado", pelo_color="#b0844f", piel="#e6ae86")
HIJA = dict(torso="#6f8a2a", piernas="#3b3f4a", pelo="corto_flequillo", pelo_color="#b5b5b5", anteojos=True, piel="#dca47e")
YERNO = dict(torso="#8a1f33", piernas="#40444d", pelo="rapado", pelo_color="#888888", barba="#c8c8c0", piel="#cf9470")
JOVEN_ELLA = dict(falda="#f1e4c8", torso="#f1e4c8", pelo="moño_castaño", pelo_color="#7a4a26", piel="#eab792")


# ------------------------------------------------------------ fondos
def living(noche=False, mar_id="olas", lampara_id="lampLuz"):
    r = mulberry32(5)
    if noche:
        muro = d.lineal("muroN", [(0, "#6f92ea", 1), (1, "#0c143a", 1)])
        cielo = d.lineal("cieloN", [(0, "#050a26", 1), (1, "#3a6cc8", 1)])
        mar = d.lineal("marN", [(0, "#1a5a9a", 1), (1, "#061a33", 1)])
        piso = d.lineal("pisoN", [(0, "#8a4a26", 1), (1, "#1a0d08", 1)])
    else:
        muro = d.lineal("muroD", [(0, "#ffd79a", 1), (1, "#e9935a", 1)])
        cielo = d.lineal("cieloD", [(0, "#8fd0ee", 1), (1, "#d8f0f6", 1)])
        mar = d.lineal("marD", [(0, "#14a3a8", 1), (1, "#0b6f86", 1)])
        piso = d.lineal("pisoD", [(0, "#b8672e", 1), (1, "#6a3416", 1)])
    olas = "".join(
        f'<path d="M{-60 + k * 140 + (i % 2) * 70} {840 + i * 34} q35 -10 70 0" stroke="{"#bfefff" if not noche else "#6fa8d8"}" stroke-width="5" fill="none" opacity=".55"/>'
        for i in range(10) for k in range(9))
    nubes = "" if noche else "".join(
        f'<ellipse cx="{150 + i * 210 + r() * 60:.0f}" cy="{470 + r() * 120:.0f}" rx="{90 + r() * 60:.0f}" ry="{22 + r() * 12:.0f}" fill="#fff" opacity=".75"/>' for i in range(5))
    luna = '<circle cx="760" cy="520" r="46" fill="#fdf3c8"/><ellipse cx="760" cy="900" rx="30" ry="120" fill="#fdf3c8" opacity=".25"/>' if noche else ""
    tablas = "".join(f'<path d="M0 {1400 + i * 70} H1080" stroke="#000" stroke-opacity=".18" stroke-width="3"/>' for i in range(8))
    return (f'<rect width="1080" height="1920" fill="{muro}"/>'
            f'<rect x="0" y="1180" width="1080" height="220" fill="{tono("#7a3a1a" if not noche else "#1a1f3a", 0)}" opacity=".35"/>'
            # ventanal
            f'<rect x="120" y="360" width="860" height="840" fill="{cielo}"/>{nubes}{luna}'
            f'<rect x="120" y="820" width="860" height="380" fill="{mar}"/>'
            f'<svg x="120" y="360" width="860" height="840" viewBox="120 360 860 840"><g id="{mar_id}">{olas}</g></svg>'
            '<path d="M120 360 H980 V1200 H120 Z M550 360 V1200" stroke="#3a2012" stroke-width="22" fill="none"/>'
            '<rect x="100" y="1196" width="900" height="26" fill="#4a2814"/>'
            f'<rect x="0" y="1380" width="1080" height="540" fill="{piso}"/>{tablas}'
            f'<ellipse cx="540" cy="1640" rx="470" ry="120" fill="{"#a8323c" if not noche else "#8a2a4a"}" opacity=".85"/>'
            f'<ellipse cx="540" cy="1640" rx="400" ry="92" fill="none" stroke="#f0c86a" stroke-width="6" opacity=".6"/>'
            + lampara_pie(d, 70, 1450, 520, encendida=True, gid=lampara_id)
            + planta(d, 1010, 1470, 300, seed=3))


def mesa_emisor():
    cono = d.lineal("cono", [(0, "#7fe8ff", .0), (1, "#7fe8ff", .45)])
    return ('<g id="emisor"><rect x="430" y="1470" width="220" height="26" rx="8" fill="#6a3a1e"/>'
            '<path d="M450 1496 L440 1590 M630 1496 L640 1590" stroke="#4a2814" stroke-width="12"/>'
            '<ellipse cx="540" cy="1468" rx="54" ry="14" fill="#cfefff"/><ellipse cx="540" cy="1466" rx="40" ry="9" fill="#7fe8ff"/>'
            f'<path id="conoLuz" d="M520 1462 L760 980 L900 1080 L560 1462 Z" fill="{cono}"/></g>')


def escena_living_dia(con_holograma=True):
    s = living(False)
    s += sillon(d, 250, 1590, 290, "#c0462e")
    s += persona(d, 250, 1590, 600, pose="sentada", brazo="regazo", **ANCIANA)
    s += mesa_emisor()
    s += sillon(d, 840, 1590, 290, "#c0462e", mira="izq")
    s += f'<g id="holo">{persona(d, 840, 1590, 690, pose="sentada", mira="izq", brazo="adelante", holograma=F["halo"], **ESPOSO)}</g>'
    return s


def escena_exterior():
    r = mulberry32(9)
    cielo = d.lineal("cieloE", [(0, "#5aa6d8", 1), (.6, "#bfe3f0", 1), (1, "#f4e2c4", 1)])
    mar = d.lineal("marE", [(0, "#0f9aa2", 1), (1, "#0a6f84", 1)])
    arena = d.lineal("arena", [(0, "#f3d08e", 1), (1, "#d99a52", 1)])
    nubes = "".join(f'<ellipse cx="{r() * 1080:.0f}" cy="{180 + r() * 380:.0f}" rx="{120 + r() * 120:.0f}" ry="{30 + r() * 20:.0f}" fill="#fff" opacity="{.55 + r() * .35:.2f}"/>' for _ in range(9))
    olas = "".join(f'<path d="M{-80 + k * 160 + (i % 2) * 80} {900 + i * 26} q40 -10 80 0" stroke="#d6fbff" stroke-width="4" fill="none" opacity=".6"/>' for i in range(8) for k in range(9))
    vidrio = d.lineal("vidrio", [(0, "#cfeefc", 1), (.5, "#7fc3e6", 1), (1, "#3a7fa8", 1)])
    madera = d.vol("#b8662c", "h", .12)
    tablas = "".join(f'<path d="M430 {560 + i * 46} H1080" stroke="#7a3a14" stroke-width="4" opacity=".6"/>' for i in range(16))
    pasto = "".join(f'<path d="M{x} 1500 q{-10 + (x % 7) * 3} -60 {-4 + (x % 5) * 4} -110" stroke="#7a9a3a" stroke-width="5" fill="none"/>' for x in range(20, 400, 23))
    return (f'<rect width="1080" height="1920" fill="{cielo}"/><g id="nubes">{nubes}</g>'
            f'<rect y="880" width="1080" height="320" fill="{mar}"/><g id="olasE">{olas}</g>'
            f'<path d="M0 1150 Q300 1110 600 1150 T1080 1140 V1920 H0Z" fill="{arena}"/>'
            # casa
            f'<rect x="430" y="520" width="650" height="780" fill="{madera}"/>{tablas}'
            '<path d="M400 520 L1080 470 L1080 520 L430 540 Z" fill="#3a2012"/>'
            f'<rect x="470" y="600" width="250" height="380" fill="{vidrio}"/><rect x="760" y="600" width="280" height="380" fill="{vidrio}"/>'
            f'<rect x="470" y="1010" width="570" height="260" fill="{vidrio}"/>'
            '<path d="M470 600 h250 v380 h-250z M760 600 h280 v380 h-280z M470 1010 h570 v260 h-570z M755 1010 v260" stroke="#2a160a" stroke-width="10" fill="none"/>'
            '<path d="M500 640 L600 940 M800 640 L900 940" stroke="#fff" stroke-width="18" opacity=".25"/>'
            # terraza
            '<rect x="300" y="1300" width="780" height="40" fill="#8a4a20"/><rect x="300" y="1340" width="780" height="22" fill="#5a2a10"/>'
            '<path d="M300 1220 H1080 M300 1220 V1300 M480 1220 V1300 M660 1220 V1300 M840 1220 V1300 M1020 1220 V1300" stroke="#e8d8c0" stroke-width="7"/>'
            f'{pasto}'
            f'<g id="caminante">{persona(d, 0, 0, 300, brazo="bastón", bastón=True, encorvada=8, **ANCIANA)}</g>')


def escena_living_noche(dormida=True):
    s = living(True, mar_id="olasN", lampara_id="lampN")
    repisa = ('<rect x="150" y="300" width="380" height="18" fill="#5a3a22"/>'
              '<rect x="170" y="210" width="70" height="90" fill="#c9a24a"/><rect x="178" y="218" width="54" height="74" fill="#8fb0d0"/>'
              '<rect x="260" y="230" width="60" height="70" fill="#a8743a"/><rect x="267" y="237" width="46" height="56" fill="#d0a080"/>'
              '<rect x="420" y="220" width="64" height="80" fill="#c9a24a"/><rect x="427" y="227" width="50" height="66" fill="#9ac0a0"/>'
              '<g id="marcoAbajo"><rect x="335" y="288" width="72" height="12" fill="#6a4a2a"/><rect x="335" y="284" width="72" height="5" fill="#3a2414"/></g>')
    # la repisa va sobre el muro izquierdo, arriba del ventanal (repisa alta)
    s = s.replace('<rect x="120" y="360"', repisa + '<rect x="120" y="360"', 1)
    s += sillon(d, 250, 1590, 290, "#6a2a3a")
    if dormida:
        s += persona(d, 250, 1590, 600, pose="sentada", brazo="regazo", ojos="cerrados", encorvada=-6, **ANCIANA)
    s += '<rect x="840" y="980" width="170" height="420" fill="#0a0f24"/><rect x="840" y="980" width="170" height="420" fill="none" stroke="#3a2a1a" stroke-width="14"/>'
    s += f'<g id="holoN">{persona(d, 925, 1400, 520, mira="izq", holograma=F["halo"], **ESPOSO)}</g>'
    return s


def escena_calle_noche():
    r = mulberry32(21)
    cielo = d.lineal("cieloC", [(0, "#120a3a", 1), (1, "#3a1a6a", 1)])
    edif = "".join(
        f'<rect x="{x}" y="{y}" width="{w}" height="{1300 - y}" fill="{c}"/>' + "".join(
            f'<rect x="{x + 18 + i * 44}" y="{y + 24 + j * 58}" width="22" height="30" fill="#ffcf6a" opacity="{.35 + r() * .6:.2f}"/>'
            for i in range(int((w - 30) / 44)) for j in range(int((1250 - y) / 58)) if r() > .35)
        for x, y, w, c in [(0, 380, 230, "#2a1a4a"), (850, 340, 230, "#2a1a4a")])
    bombillas = "".join(f'<circle class="bomb" cx="{240 + i * 30}" cy="{c}" r="8" fill="#ffe9a8"/>' for i in range(21) for c in (700, 860))
    carteles = "".join(f'<rect class="cartel" id="cartel{i}" x="{262 + i * 190}" y="900" width="160" height="230" rx="6" fill="{c}"/>'
                       for i, c in enumerate(["#e0384f", "#2ab0c8", "#f0a526"]))
    acera = d.lineal("acera", [(0, "#3a2a4a", 1), (1, "#1a1028", 1)])
    reflejo = d.lineal("refl", [(0, "#ffcf6a", .45), (1, "#ffcf6a", 0)])
    farol = lambda x: (f'<path d="M{x} 1500 V880" stroke="#1a1a24" stroke-width="12"/><circle cx="{x}" cy="870" r="22" fill="#ffd98a"/>'
                       f'<circle cx="{x}" cy="870" r="70" fill="#ffd98a" opacity=".35" filter="{F["brillo"]}"/>')
    return (f'<rect width="1080" height="1920" fill="{cielo}"/>{edif}'
            # cine
            '<rect x="230" y="560" width="620" height="740" fill="#5a1a2a"/>'
            '<rect x="210" y="680" width="660" height="200" rx="10" fill="#1a0a14"/>'
            f'<g id="bombillas">{bombillas}</g>'
            '<rect x="250" y="720" width="580" height="120" fill="#f7e6b8"/>'
            f'<g id="carteles">{carteles}</g>'
            '<rect x="420" y="1150" width="240" height="150" fill="#2a0a14"/><rect x="430" y="1160" width="105" height="140" fill="#ffcf6a" opacity=".7"/><rect x="545" y="1160" width="105" height="140" fill="#ffcf6a" opacity=".7"/>'
            f'<rect y="1300" width="1080" height="620" fill="{acera}"/>'
            f'<rect x="230" y="1300" width="620" height="400" fill="{reflejo}"/>'
            + farol(110) + farol(970)
            + persona(d, 690, 1660, 640, mira="izq", brazo="abajo", **JOVEN_ELLA)
            + persona(d, 400, 1660, 690, pose="arrodillado", brazo="adelante",
                      extra='<circle cx="{mx}" cy="{my}" r="9" fill="#ffd84a" stroke="#fff" stroke-width="2"/>', **ESPOSO))



# ------------------------------------------------------------ fondos nuevos (escenas 3 a 13)
def frase(n):
    t = TIEMPOS[n - 1]
    return t["inicio"], t["fin"]


def interior_vitrina():
    s = living(False, mar_id="olas3", lampara_id="lamp3")
    vid = d.lineal("vitr", [(0, "#dff6ff", .55), (1, "#9fd6f0", .25)])
    s += ('<g id="vitrina"><rect x="640" y="1010" width="300" height="470" fill="#5a2e14"/>'
          f'<rect x="660" y="1030" width="260" height="420" fill="#2a1a12"/>'
          '<g transform="translate(790 1240) rotate(-12)">'
          '<ellipse cx="0" cy="60" rx="62" ry="78" fill="#c2581c"/><ellipse cx="0" cy="-40" rx="50" ry="62" fill="#c2581c"/>'
          '<rect x="-20" y="-10" width="40" height="20" fill="#c2581c"/><rect x="-8" y="-200" width="16" height="200" fill="#2a1408"/>'
          '<ellipse cx="0" cy="-210" rx="14" ry="22" fill="#2a1408"/><path d="M-4 -190 V120 M4 -190 V120" stroke="#f2e6c0" stroke-width="2"/>'
          '<path d="M-22 20 q-8 10 0 20 M22 20 q8 10 0 20" stroke="#2a1408" stroke-width="5" fill="none"/></g>'
          f'<rect x="660" y="1030" width="260" height="420" fill="{vid}"/>'
          '<path d="M690 1050 L760 1430" stroke="#fff" stroke-width="16" opacity=".3"/></g>'
          '<path d="M980 1480 L1000 1130 M960 1130 h80" stroke="#2a1a10" stroke-width="8"/>')
    s += persona(d, 470, 1560, 560, brazo="bastón", bastón=True, encorvada=8, **ANCIANA)
    return s


def pared_fotos():
    r = mulberry32(31)
    muro = d.lineal("muroF", [(0, "#f6c98c", 1), (1, "#d98850", 1)])
    s = f'<rect width="1080" height="1920" fill="{muro}"/><rect y="1500" width="1080" height="420" fill="{d.lineal("pisoF", [(0, "#a85a26", 1), (1, "#5a2a10", 1)])}"/>'
    fotos = []
    for i, (x, y, w, h) in enumerate([(130, 420, 220, 280), (400, 380, 260, 200), (710, 430, 220, 280), (170, 760, 260, 200), (480, 650, 200, 260), (740, 780, 230, 200)]):
        c1, c2 = ["#3a6ea8", "#a84a3a", "#4a8a5a", "#8a5aa8", "#c08a3a", "#3a8a9a"][i], ["#f0c8a0", "#e8b090", "#f2d0b0"][i % 3]
        fotos.append(
            f'<g><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#3a2010"/>'
            f'<g id="foto{i}"><rect x="{x+14}" y="{y+14}" width="{w-28}" height="{h-28}" fill="{c1}"/>'
            f'<circle cx="{x+w/2-25}" cy="{y+h*0.42}" r="{h*0.13:.0f}" fill="{c2}"/><circle cx="{x+w/2+28}" cy="{y+h*0.45}" r="{h*0.12:.0f}" fill="{c2}"/>'
            f'<path d="M{x+30} {y+h-14} Q{x+w/2} {y+h*0.55} {x+w-30} {y+h-14}Z" fill="{tono(c1,-.15)}"/></g>'
            f'<rect class="blanco" id="blanco{i}" x="{x+14}" y="{y+14}" width="{w-28}" height="{h-28}" fill="#fffdf6" opacity="0"/></g>')
    s += "".join(fotos)
    s += f'<ellipse cx="540" cy="900" rx="600" ry="500" fill="{d.radial("lzF", [(0, "#fff3c8", .35), (1, "#000", 0)])}"/>'
    s += persona(d, 860, 1800, 760, mira="izq", brazo="adelante", bastón=False, encorvada=6, **ANCIANA)
    return s


def comedor(catalogo=False):
    muro = d.lineal("muroC", [(0, "#ffd08a", 1), (1, "#e07a4a", 1)])
    s = (f'<rect width="1080" height="1920" fill="{muro}"/><rect y="1380" width="1080" height="540" fill="{d.lineal("pisoC", [(0, "#a85a26", 1), (1, "#4a200a", 1)])}"/>'
         '<rect x="620" y="300" width="380" height="560" fill="#9ad6ee"/><rect x="620" y="640" width="380" height="220" fill="#14a3a8"/>'
         '<path d="M620 300 h380 v560 h-380z M810 300 v560" stroke="#3a2012" stroke-width="18" fill="none"/>'
         '<path d="M540 0 V520" stroke="#2a2018" stroke-width="6"/><path d="M450 600 L630 600 L590 520 L490 520 Z" fill="#2a6a5a"/>'
         f'<ellipse cx="540" cy="640" rx="260" ry="160" fill="{d.radial("colg", [(0, "#ffe0a0", .55), (1, "#000", 0)])}"/>')
    s += silla(d, 210, 1560, 240) + persona(d, 210, 1560, 620, pose="sentada", brazo="adelante", **HIJA)
    s += silla(d, 870, 1560, 240, mira="izq") + persona(d, 870, 1560, 660, pose="sentada", mira="izq", brazo="adelante", **YERNO)
    s += mesa(d, 540, 1600, 560, 330, "#8a4a24")
    # tablet translúcida
    s += ('<g id="tablet"><rect x="470" y="1255" width="140" height="18" rx="4" fill="#bff0ff" opacity=".85"/>'
          f'<ellipse cx="540" cy="1250" rx="140" ry="40" fill="{d.radial("tabl", [(0, "#7fe8ff", .5), (1, "#7fe8ff", 0)])}"/></g>')
    # catálogo de siluetas holográficas sobre la mesa
    sil = []
    for i, x in enumerate([400, 470, 540, 610, 680]):
        sil.append(f'<g transform="translate({x} 1262) scale(1.15)"><g class="sil" id="sil{i}">'
                   '<ellipse cx="0" cy="-90" rx="13" ry="16" fill="#bff6ff" opacity=".85"/><path d="M-18 -72 Q0 -80 18 -72 L14 -30 L8 0 L-8 0 L-14 -30Z" fill="#bff6ff" opacity=".85"/></g></g>')
    s += f'<g id="catalogo" opacity="{1 if catalogo else 0}" filter="{F["halo"]}">{"".join(sil)}</g>'
    # silueta que se llena de color (el esposo)
    s += (f'<g id="silLlena" opacity="0" transform="translate(540 1262) scale(.32)">'
          f'{persona(d, 0, 0, 690, mira="izq", **ESPOSO)}</g>')
    s += f'<g id="ondas" opacity="0" stroke="#7fe8ff" stroke-width="6" fill="none">' + "".join(
        f'<path d="M{760 - k * 50} {1000 + k * 20} q-20 30 0 60"/>' for k in range(4)) + '</g>'
    return s


def eleccion():
    s = living(False, mar_id="olas5", lampara_id="lamp5")
    s += sillon(d, 280, 1590, 300, "#c0462e")
    marco = ('<g transform="translate({mx} {my}) rotate(-10)"><rect x="-6" y="-120" width="110" height="140" fill="#c9a24a"/>'
             '<rect x="4" y="-110" width="90" height="120" fill="#8fb0c8"/>'
             '<circle cx="49" cy="-70" r="22" fill="#e0b090"/><path d="M30 -82 q19 -18 38 0" fill="#d8d8d8"/>'
             '<path d="M18 10 Q49 -40 80 10Z" fill="#1e2f6e"/></g>')
    s += persona(d, 280, 1590, 600, pose="sentada", brazo="adelante", extra=marco, **ANCIANA)
    s += f'<g id="holo5" opacity="0">{persona(d, 830, 1600, 700, mira="izq", holograma=F["halo"], **ESPOSO)}</g>'
    return s


def cuentas_vida():
    s = living(False, mar_id="olas6", lampara_id="lamp6")
    refl = ('<g id="recuerdos" opacity="0" style="mix-blend-mode:screen">'
            # violinista en un escenario
            '<rect x="170" y="420" width="330" height="340" fill="#ffe8a8" opacity=".35"/>'
            f'<g transform="translate(330 740)">{persona(d, 0, 0, 280, brazo="arriba", sombra=False, **JOVEN_ELLA)}</g>'
            # boda
            '<rect x="600" y="420" width="330" height="340" fill="#fff" opacity=".3"/>'
            f'<g transform="translate(700 740)">{persona(d, 0, 0, 270, sombra=False, **JOVEN_ELLA)}</g>'
            f'<g transform="translate(820 740)">{persona(d, 0, 0, 300, mira="izq", sombra=False, **ESPOSO)}</g></g>')
    s += refl
    s += sillon(d, 840, 1590, 290, "#c0462e", mira="izq")
    s += f'<g id="holo6">{persona(d, 840, 1590, 690, pose="sentada", mira="izq", brazo="adelante", holograma=F["halo"], **ESPOSO)}</g>'
    # la anciana en primer plano, por sobre el hombro (grande, cortada abajo)
    s += sillon(d, 170, 2050, 520, "#c0462e")
    s += persona(d, 170, 2050, 1080, pose="sentada", brazo="adelante", **ANCIANA)
    return s


def cocina():
    muro = d.lineal("muroK", [(0, "#2aa6a0", 1), (1, "#146a6e", 1)])
    azul = "".join(f'<rect x="{x}" y="{y}" width="56" height="56" fill="none" stroke="#7fd6cc" stroke-width="3" opacity=".35"/>'
                   for x in range(0, 1080, 60) for y in range(880, 1200, 60))
    s = (f'<rect width="1080" height="1920" fill="{muro}"/>{azul}'
         f'<rect y="1380" width="1080" height="540" fill="{d.lineal("pisoK", [(0, "#c8b090", 1), (1, "#7a6040", 1)])}"/>'
         # puerta al living (luminosa) con la madre y el holograma al fondo
         '<rect x="430" y="520" width="420" height="880" fill="#ffd79a"/>'
         '<rect x="430" y="520" width="420" height="300" fill="#9ad6ee"/><rect x="430" y="740" width="420" height="80" fill="#14a3a8"/>'
         f'<g>{sillon(d, 540, 1360, 150, "#c0462e")}{persona(d, 540, 1360, 300, pose="sentada", brazo="regazo", **ANCIANA)}</g>'
         f'<g id="holo7a">{sillon(d, 760, 1360, 150, "#c0462e", mira="izq")}{persona(d, 760, 1360, 345, pose="sentada", mira="izq", brazo="adelante", holograma=F["halo"], **ESPOSO)}</g>'
         f'<g id="holo7b" opacity="0">{persona(d, 760, 1360, 345, pose="sentada", mira="izq", brazo="arriba", holograma=F["halo"], **ESPOSO)}</g>'
         '<path d="M430 520 h420 v880 h-420z" stroke="#5a3418" stroke-width="26" fill="none"/>'
         # mesón de la cocina
         f'<rect x="0" y="1260" width="380" height="300" fill="{d.vol("#e8e0d0", "v", .1)}"/><rect x="0" y="1240" width="400" height="30" fill="#5a4a3a"/>'
         '<rect x="60" y="1180" width="60" height="60" rx="8" fill="#c0462e"/><rect x="200" y="1200" width="90" height="40" rx="6" fill="#f2f2ee"/>')
    s += f'<g id="hija7">{persona(d, 300, 1700, 680, mira="der", brazo="abajo", **HIJA)}</g>'
    s += espectador_pie(d, 960, 1980, 780)
    return s


def terraza_noche():
    cielo = d.lineal("cieloT", [(0, "#10163a", 1), (1, "#3a5490", 1)])
    s = (f'<rect width="1080" height="1920" fill="{cielo}"/>'
         + "".join(f'<circle cx="{(i*137)%1080}" cy="{(i*251)%700+60}" r="{1+(i%3)}" fill="#fff" opacity=".8"/>' for i in range(60))
         + '<rect y="900" width="1080" height="300" fill="#0f3a6a"/>'
         + "".join(f'<path d="M{-40 + k * 150 + (i % 2) * 75} {930 + i * 30} q36 -10 72 0" stroke="#6fa8d8" stroke-width="4" fill="none" opacity=".5"/>' for i in range(8) for k in range(9))
         # casa con ventana iluminada y la anciana dormida
         + f'<rect x="560" y="420" width="520" height="980" fill="{d.vol("#6a3a1c", "h", .1)}"/>'
         + '<rect x="640" y="560" width="360" height="420" fill="#ffcf7a"/>'
         + f'<g transform="translate(700 960) scale(.5)">{sillon(d, 0, 0, 290, "#a83a2a")}{persona(d, 0, 0, 600, pose="sentada", brazo="regazo", ojos="cerrados", **ANCIANA)}</g>'
         + '<path d="M640 560 h360 v420 h-360z M820 560 v420" stroke="#2a160a" stroke-width="14" fill="none"/>'
         + f'<rect y="1400" width="1080" height="520" fill="{d.lineal("deck", [(0, "#7a4420", 1), (1, "#2a140a", 1)])}"/>'
         + "".join(f'<path d="M0 {1430 + i * 60} H1080" stroke="#000" stroke-opacity=".25" stroke-width="3"/>' for i in range(8)))
    taza = '<g transform="translate({mx} {my})"><rect x="-4" y="-38" width="44" height="46" rx="6" fill="#f2efe6"/><path d="M40 -28 q18 6 0 22" stroke="#f2efe6" stroke-width="7" fill="none"/></g>'
    s += mesa(d, 300, 1640, 180, 300, "#5a3a22")
    s += silla(d, 230, 1640, 250, "#4a2a16")
    s += f'<g id="yerno8">{persona(d, 230, 1640, 660, pose="sentada", brazo="adelante", encorvada=10, extra=taza, **YERNO)}</g>'
    s += f'<g id="holo8">{persona(d, 690, 1640, 720, mira="izq", holograma=F["halo"], **ESPOSO)}</g>'
    return s


def terraza_dia(recuerdo=False):
    cielo = d.lineal("cieloTD", [(0, "#4aa6e0", 1), (1, "#cfeefa", 1)])
    s = (f'<rect width="1080" height="1920" fill="{cielo}"/>'
         + '<rect y="900" width="1080" height="320" fill="#11a0a8"/>'
         + f'<g id="olas10">' + "".join(f'<path d="M{-40 + k * 150 + (i % 2) * 75} {930 + i * 30} q36 -10 72 0" stroke="#dffaff" stroke-width="4" fill="none" opacity=".6"/>' for i in range(9) for k in range(9)) + '</g>'
         # ventanal detrás (a la izquierda) con el recuerdo reflejado
         + '<rect x="0" y="380" width="430" height="1020" fill="#d6f0fb"/>')
    s += (f'<g id="reflejo" opacity="{0}" style="mix-blend-mode:multiply">{calle_reflejo("r10")}</g>')
    s += ('<path d="M0 380 h430 v1020 h-430z M215 380 v1020" stroke="#3a2012" stroke-width="20" fill="none"/>'
          f'<rect y="1400" width="1080" height="520" fill="{d.lineal("deckD", [(0, "#d88a42", 1), (1, "#1e0a02", 1)])}"/>'
          + "".join(f'<path d="M0 {1430 + i * 60} H1080" stroke="#000" stroke-opacity=".2" stroke-width="3"/>' for i in range(8)))
    s += sillon(d, 560, 1660, 280, "#e0a526") + persona(d, 560, 1660, 600, pose="sentada", brazo="regazo", **ANCIANA)
    s += sillon(d, 840, 1660, 280, "#e0a526") + f'<g id="holo10">{persona(d, 840, 1660, 690, pose="sentada", brazo="regazo", holograma=F["halo"], **ESPOSO)}</g>'
    return s


def calle_reflejo(pref, lluvia_on=True):
    """El recuerdo: la pareja joven caminando por una calle de noche (para reflejos y para la escena 11)."""
    cielo = d.lineal(pref + "cielo", [(0, "#1a1a3a", 1), (1, "#4a3a6a", 1)])
    s = (f'<rect x="0" y="380" width="430" height="1020" fill="{cielo}"/>'
         '<rect x="0" y="600" width="140" height="800" fill="#2a2440"/><rect x="300" y="560" width="130" height="840" fill="#2a2440"/>'
         + "".join(f'<rect x="{x}" y="{y}" width="20" height="28" fill="#ffcf6a" opacity=".7"/>' for x in (30, 80, 320, 370) for y in range(640, 1300, 70))
         + f'<g transform="translate(190 1330)">{persona(d, 0, 0, 380, brazo="abajo", sombra=False, **JOVEN_ELLA)}</g>'
         + f'<g transform="translate(270 1330)">{persona(d, 0, 0, 420, sombra=False, **ESPOSO)}</g>')
    return s


def recuerdo_grande():
    """Escena 11: el recuerdo dentro del ventanal, a pantalla completa, con lluvia que se va."""
    cieloG = d.lineal("cieloG", [(0, "#1a2a4a", 1), (1, "#4a5a7a", 1)])
    cieloC = d.lineal("cieloCal", [(0, "#2a1a5a", 1), (.6, "#c2326e", 1), (1, "#ffb35a", 1)])
    s = (f'<rect width="1080" height="1920" fill="{cieloG}"/><rect id="cieloCalido" width="1080" height="1920" fill="{cieloC}" opacity="0"/>'
         '<rect x="0" y="500" width="300" height="1100" fill="#2a2440"/><rect x="780" y="440" width="300" height="1160" fill="#2a2440"/>'
         + "".join(f'<rect class="ventC" x="{x}" y="{y}" width="40" height="56" fill="#ffd36a" opacity=".85"/>' for x in (40, 130, 220, 820, 910, 1000) for y in range(560, 1500, 110))
         + f'<rect y="1600" width="1080" height="320" fill="{d.lineal("veredaG", [(0, "#3a3a5a", 1), (1, "#141428", 1)])}"/>'
         + '<path d="M540 1600 V820" stroke="#1a1a24" stroke-width="16"/><circle cx="540" cy="810" r="30" fill="#ffd98a"/>'
         + f'<circle id="faroG" cx="540" cy="810" r="170" fill="#ffe3a0" opacity=".5" filter="{F["brillo"]}"/>'
         + f'<g id="parejaG"><g transform="translate(400 1700)">{persona(d, 0, 0, 640, brazo="abajo", torso="#8a8a90", falda="#8a8a90", pelo="moño_castaño", pelo_color="#7a4a26", piel="#eab792")}</g>'
         + f'<g id="abrigoCrema" opacity="0"><g transform="translate(400 1700)">{persona(d, 0, 0, 640, brazo="abajo", **JOVEN_ELLA)}</g></g>'
         + f'<g transform="translate(560 1700)">{persona(d, 0, 0, 700, **ESPOSO)}</g></g>'
         + lluvia("lluviaG", n=160)
         # marco del ventanal y la mano de la anciana que señala
         + '<path d="M0 0 h1080 v1920 h-1080z" stroke="#3a2012" stroke-width="60" fill="none"/>'
         + f'<g id="mano"><path d="M-40 1460 L240 1330" stroke="#d4d4cf" stroke-width="110" stroke-linecap="round"/>'
           f'<circle cx="260" cy="1322" r="48" fill="{d.vol("#e8b898", "h", .1)}"/><path d="M290 1300 L360 1262" stroke="#e8b898" stroke-width="26" stroke-linecap="round"/></g>')
    return s


def recuerdo_vuelve(con_espectador=True):
    s = escena_living_noche(dormida=False).replace('id="', 'id="r13')
    s += sillon(d, 760, 1600, 260, "#3a5a8a", mira="izq") + persona(d, 760, 1600, 600, pose="sentada", mira="izq", brazo="adelante", **HIJA)
    s += sillon(d, 960, 1600, 260, "#3a5a8a", mira="izq") + persona(d, 960, 1600, 640, pose="sentada", mira="izq", brazo="adelante", **YERNO)
    s += f'<g id="camina13">{persona(d, 0, 0, 560, mira="izq", brazo="bastón", bastón=True, encorvada=8, **ANCIANA)}</g>'
    s += f'<g id="alcanza13" opacity="0">{persona(d, 0, 0, 560, mira="izq", brazo="arriba", encorvada=4, **ANCIANA)}</g>'
    if con_espectador:
        s += espectador_pie(d, 120, 2050, 820)
    return s

# ------------------------------------------------------------ HTML
CSS = """
:root{--mostaza:#e0a526;--carmesi:#7a1020;--crema:#f4ead2}
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:1920px;overflow:hidden;background:#0a0608}
#root{position:relative;width:100%;height:100%;overflow:hidden}
.esc{position:absolute;inset:0;overflow:hidden}
.esc svg.lienzo{position:absolute;inset:0;width:1080px;height:1920px}
.gancho-wrap{position:absolute;left:120px;right:330px;top:930px}
.gancho{font-family:"Archivo Black";color:var(--crema);font-size:68px;line-height:1.04;text-shadow:0 6px 30px rgba(0,0,0,.75)}
.gancho em{font-style:normal;color:var(--mostaza)}
.banner-wrap{position:absolute;left:0;right:0;display:flex;justify-content:center}
.banner{background:var(--carmesi);color:var(--crema);font-family:"Archivo Black";font-size:104px;padding:14px 44px 6px;box-shadow:0 12px 40px rgba(0,0,0,.45)}
.tarjeta-wrap{position:absolute;left:120px;right:192px;top:300px}
.tarjeta{background:rgba(8,16,18,.72);padding:34px 40px 30px;text-align:center;border-top:6px solid var(--mostaza)}
.tarjeta .titulo{font-family:"Archivo Black";color:var(--crema);font-size:84px;line-height:1}
.tarjeta .sub{font-family:"Oswald";color:var(--mostaza);font-size:40px;margin-top:14px;letter-spacing:.08em}
"""
FUNDIDO = 0.35  # cada plano entra con un fundido sobre el anterior


def lienzo(contenido, cid, pintura=True):
    filtro = f' filter="{F["pintura"]}"' if pintura else ""
    return (f'<svg class="lienzo" viewBox="0 0 1080 1920"><g id="{cid}">'
            f'<g{filtro}>{contenido}</g></g><rect width="1080" height="1920" filter="{F["grano"]}"/></svg>')


PLANOS, TW = [], []


def plano(pid, ini, fin, contenido, cam_de, cam_a, pintura=True, extra_html="", ease="none", cam_dur=None):
    """Un plano: clip desde ini hasta fin (+ fundido de salida), con movimiento de cámara."""
    dur = fin - ini + (FUNDIDO if fin < TOTAL - 0.01 else 0)
    PLANOS.append(f'<div id="{pid}" class="clip esc" data-start="{ini:.3f}" data-duration="{dur:.3f}" data-track-index="0">'
                  f'{lienzo(contenido, "c" + pid, pintura)}{extra_html}</div>')
    de = ",".join(f"{k}:{v}" for k, v in cam_de.items())
    a = ",".join(f"{k}:{v}" for k, v in cam_a.items())
    TW.append(f'tl.fromTo("#c{pid}",{{svgOrigin:"540 960",{de}}},{{{a},duration:{(cam_dur or dur):.3f},ease:"{ease}"}},{ini:.3f});')
    if ini > 0:
        TW.append(f'tl.fromTo("#{pid}",{{opacity:0}},{{opacity:1,duration:{FUNDIDO},ease:"none"}},{ini:.3f});')


def banner(bid, texto, n_frase, palabra_txt, top, hasta):
    t = palabra(n_frase, palabra_txt)
    TW.append(f'tl.fromTo("#{bid}",{{opacity:0,scale:1.15}},{{opacity:1,scale:1,duration:.15,ease:"power2.out"}},{t:.3f});')
    TW.append(f'tl.to("#{bid}",{{opacity:0,duration:.15}},{hasta:.3f});')
    return f'<div class="banner-wrap" style="top:{top}px"><div class="banner" id="{bid}" style="opacity:0">{texto}</div></div>'


def tw(s):
    TW.append(s)


def build():
    f = frase
    # 1 · la sala; en la pantalla, el living con el holograma (frases 1-2)
    ini, fin = 0.0, f(3)[0]
    plano("p01", ini, fin, sala_cine(d, escena_living_dia().replace('id="', 'id="p1'), polvo_id="polvo1"),
          {"scale": 1}, {"scale": 1.05}, pintura=False, cam_dur=fin - 1.3,
          extra_html='<div class="gancho-wrap"><div class="gancho" id="gancho">Imagina que tu esposo, muerto hace <em>15 años</em>, está frente a ti…</div></div>')
    tw('tl.fromTo("#gancho",{opacity:0,y:30},{opacity:1,y:0,duration:.3,ease:"power3.out"},0);')
    tw(f'tl.to("#gancho",{{opacity:0,duration:.25}},{fin-1.7:.3f});')
    tw(f'tl.fromTo("#cp01",{{svgOrigin:"540 960",scale:1.05,y:0}},{{scale:2.6,y:520,duration:1.3,ease:"power2.in",immediateRender:false}},{fin-1.3:.3f});')
    tw(f'tl.fromTo("#polvo1",{{x:0}},{{x:-30,duration:{fin:.3f},ease:"none"}},0);')

    # 2 · el holograma (frases 3-4)
    ini, fin = f(3)[0], f(5)[0]
    plano("p02", ini, fin, escena_living_dia(), {"scale": 1.12, "x": -60}, {"scale": 1.22, "x": -140},
          extra_html=banner("bHolo", "HOLOGRAMA", 3, "holograma", 330, fin - 0.2))
    tw(f'tl.fromTo("#holo",{{opacity:.95}},{{opacity:.55,duration:.18,repeat:9,yoyo:true,ease:"steps(2)"}},{ini+.2:.3f});')
    tw(f'tl.fromTo("#olas",{{x:0}},{{x:-70,duration:{fin-ini:.3f},ease:"none"}},{ini:.3f});')
    tw(f'tl.fromTo("#conoLuz",{{opacity:.4}},{{opacity:1,duration:.6,repeat:5,yoyo:true,ease:"sine.inOut"}},{ini:.3f});')

    # 3a · más de ochenta años, violinista (frase 5)
    ini, fin = f(5)[0], f(6)[0]
    plano("p03a", ini, fin, interior_vitrina(), {"scale": 1.25, "x": 60, "y": -120}, {"scale": 1.32, "x": -40, "y": -140},
          extra_html=banner("b80", "80 AÑOS", 5, "ochenta", 330, fin - 0.2))
    tw(f'tl.fromTo("#olas3",{{x:0}},{{x:-50,duration:{fin-ini:.3f},ease:"none"}},{ini:.3f});')
    # 3b · frente al mar (frase 6)
    ini, fin = f(6)[0], f(7)[0]
    plano("p03b", ini, fin, escena_exterior(), {"scale": 1.18, "x": -60, "y": 150}, {"scale": 1.26, "x": -110, "y": 170})
    tw(f'tl.fromTo("#caminante",{{x:420,y:1300}},{{x:600,y:1300,duration:{fin-ini+FUNDIDO:.3f},ease:"none"}},{ini:.3f});')
    tw(f'tl.fromTo("#nubes",{{x:0}},{{x:-90,duration:{fin-ini:.3f},ease:"none"}},{ini:.3f});')
    tw(f'tl.fromTo("#olasE",{{x:0}},{{x:-60,duration:{fin-ini:.3f},ease:"none"}},{ini:.3f});')
    # 3c · la memoria se borra (frase 7)
    ini, fin = f(7)[0], f(8)[0]
    plano("p03c", ini, fin, pared_fotos(), {"scale": 1.0, "y": 0}, {"scale": 1.08, "y": 40})
    for i in range(6):
        tw(f'tl.to("#blanco{i}",{{opacity:1,duration:.9,ease:"sine.in"}},{ini + 0.2 + i * 0.22:.3f});')

    # 4 · el servicio (frases 8-10)
    ini, fin = f(8)[0], f(11)[0]
    plano("p04", ini, fin, comedor(), {"scale": 1.0, "y": 0}, {"scale": 1.06, "y": 0}, cam_dur=f(9)[0] - 0.4 - ini)
    tw(f'tl.fromTo("#cp04",{{svgOrigin:"540 960",scale:1.06,x:0,y:0}},{{scale:1.8,y:-430,duration:1.2,ease:"power2.inOut",immediateRender:false}},{f(9)[0]-0.4:.3f});')
    tw(f'tl.to("#catalogo",{{opacity:1,duration:.4}},{f(9)[0]:.3f});')
    tw(f'tl.fromTo("#cp04 .sil",{{y:6}},{{y:-6,duration:.5,repeat:7,yoyo:true,stagger:.1,ease:"sine.inOut"}},{f(9)[0]:.3f});')
    tw(f'tl.fromTo("#cp04",{{svgOrigin:"540 960",scale:1.8,x:0,y:-430}},{{scale:1.25,y:-150,x:-60,duration:1.0,ease:"power2.inOut",immediateRender:false}},{f(10)[0]-0.2:.3f});')
    tw(f'tl.to("#catalogo",{{opacity:.25,duration:.4}},{f(10)[0]:.3f});')
    tw(f'tl.fromTo("#ondas",{{opacity:0,x:0}},{{opacity:1,x:-60,duration:.6,repeat:3,yoyo:true,ease:"sine.inOut"}},{f(10)[0]:.3f});')
    tw(f'tl.to("#silLlena",{{opacity:1,duration:1.6,ease:"sine.in"}},{f(10)[0]+0.3:.3f});')

    # 5 · la elección (frases 11-13)
    ini, fin = f(11)[0], f(14)[0]
    plano("p05", ini, fin, eleccion(), {"scale": 1.15, "x": 40}, {"scale": 1.28, "x": -60})
    tw(f'tl.to("#holo5",{{opacity:1,duration:.5}},{palabra(12, "joven"):.3f});')
    tw(f'tl.fromTo("#holo5",{{y:0}},{{y:-8,duration:.6,repeat:3,yoyo:true,ease:"sine.inOut"}},{f(12)[0]+.5:.3f});')
    tw(f'tl.fromTo("#olas5",{{x:0}},{{x:-60,duration:{fin-ini:.3f},ease:"none"}},{ini:.3f});')

    # 6 · le cuentas tu vida (frase 14)
    ini, fin = f(14)[0], f(15)[0]
    plano("p06", ini, fin, cuentas_vida(), {"scale": 1.05, "x": 0}, {"scale": 1.14, "x": -40})
    tw(f'tl.to("#recuerdos",{{opacity:.75,duration:.6}},{ini+.3:.3f});')
    tw(f'tl.to("#recuerdos",{{opacity:1,duration:.4}},{palabra(14, "repite"):.3f});')
    tw(f'tl.fromTo("#holo6",{{opacity:.7}},{{opacity:1,duration:.3,repeat:3,yoyo:true}},{palabra(14, "repite"):.3f});')

    # 7 · la hija (frases 15-17)
    ini, fin = f(15)[0], f(18)[0]
    plano("p07", ini, fin, cocina(), {"scale": 1.1, "x": 40}, {"scale": 1.18, "x": -30})
    tw(f'tl.to("#holo7a",{{opacity:0,duration:.2}},{f(16)[0]+.6:.3f});')
    tw(f'tl.to("#holo7b",{{opacity:1,duration:.2}},{f(16)[0]+.6:.3f});')
    tw(f'tl.to("#hija7",{{x:-520,duration:{f(18)[0]-f(17)[0]:.3f},ease:"power1.in"}},{f(17)[0]:.3f});')

    # 8 · el yerno y el holograma, de noche (frases 18-19)
    ini, fin = f(18)[0], f(20)[0]
    plano("p08", ini, fin, terraza_noche(), {"scale": 1.1, "x": 30}, {"scale": 1.22, "x": -20},
          extra_html=banner("bSecreto", "SECRETO", 19, "secreto", 330, fin - 0.2))
    tw(f'tl.to("#yerno8",{{x:20,duration:.8,ease:"sine.inOut"}},{f(19)[0]:.3f});')
    tw(f'tl.fromTo("#holo8",{{opacity:.95}},{{opacity:.65,duration:.4,repeat:9,yoyo:true,ease:"sine.inOut"}},{ini:.3f});')

    # 9 · lo que nadie menciona (frases 20-21)
    ini, fin = f(20)[0], f(22)[0]
    plano("p09", ini, fin, escena_living_noche(), {"scale": 1.5, "x": 250, "y": 420}, {"scale": 1.15, "x": 60, "y": 60}, ease="power1.inOut")
    tw(f'tl.fromTo("#holoN",{{opacity:.9}},{{opacity:.6,duration:.4,repeat:7,yoyo:true,ease:"sine.inOut"}},{ini:.3f});')
    tw(f'tl.to("#lampN",{{opacity:0,duration:.25}},{fin-1.2:.3f});')

    # 10 · compañía (frases 22-23)
    ini, fin = f(22)[0], f(24)[0]
    plano("p10", ini, fin, terraza_dia(), {"scale": 1.08, "x": -40}, {"scale": 1.2, "x": 120})
    tw(f'tl.fromTo("#olas10",{{x:0}},{{x:-60,duration:{fin-ini:.3f},ease:"none"}},{ini:.3f});')
    tw(f'tl.to("#reflejo",{{opacity:.85,duration:.8}},{palabra(23, "reescribiendo"):.3f});')

    # 11 · detalles nuevos (frases 24-25)
    ini, fin = f(24)[0], f(26)[0]
    plano("p11", ini, fin, recuerdo_grande(), {"scale": 1.0}, {"scale": 1.08})
    tw(f'tl.fromTo("#lluviaG",{{y:-60}},{{y:60,duration:.3,repeat:{int((f(25)[0]-ini)/.3)},ease:"none"}},{ini:.3f});')
    t25 = f(25)[0]
    tw(f'tl.to("#lluviaG",{{opacity:0,duration:.6}},{t25:.3f});')
    tw(f'tl.to("#cieloCalido",{{opacity:1,duration:1.2}},{t25:.3f});')
    tw(f'tl.to("#abrigoCrema",{{opacity:1,duration:1.0}},{t25+.4:.3f});')
    tw(f'tl.to("#cp11 .ventC",{{opacity:1,fill:"#ffb84a",duration:.8,stagger:.03}},{t25:.3f});')
    tw(f'tl.fromTo("#mano",{{x:0}},{{x:20,duration:.5,repeat:3,yoyo:true,ease:"sine.inOut"}},{ini:.3f});')

    # 12 · la noche de la propuesta (frases 26-27)
    ini, fin = f(26)[0], f(28)[0]
    plano("p12", ini, fin, escena_calle_noche(), {"scale": 1.0, "y": 0}, {"scale": 1.12, "y": -60})
    t_v = palabra(27, "versión")
    tw(f'tl.fromTo("#cp12 .bomb",{{opacity:1}},{{opacity:.35,duration:.25,repeat:{int((fin-ini)/.25)-1},yoyo:true,stagger:{{each:.04,from:"random"}},ease:"none"}},{ini:.3f});')
    tw(f'tl.to("#cartel0",{{fill:"#7a3ad8",duration:.4}},{t_v:.3f});')
    tw(f'tl.to("#cartel1",{{fill:"#f06a2a",duration:.4}},{t_v+.25:.3f});')
    tw(f'tl.to("#cartel2",{{fill:"#2ad88a",duration:.4}},{t_v+.5:.3f});')

    # 13 · el recuerdo que vuelve (frases 28-29)
    ini, fin = f(28)[0], f(30)[0]
    plano("p13", ini, fin, recuerdo_vuelve(), {"scale": 1.05, "x": 40}, {"scale": 1.35, "x": 260, "y": 330}, ease="power1.in")
    tw(f'tl.fromTo("#camina13",{{x:640,y:1600}},{{x:470,y:1600,duration:{f(29)[1]-ini-0.9:.3f},ease:"none"}},{ini:.3f});')
    tw(f'tl.set("#alcanza13",{{x:470,y:1600}},{ini:.3f});')
    t_esc = palabra(29, "esconde")
    tw(f'tl.to("#camina13",{{opacity:0,duration:.15}},{t_esc-0.6:.3f});')
    tw(f'tl.to("#alcanza13",{{opacity:1,duration:.15}},{t_esc-0.6:.3f});')
    tw(f'tl.fromTo("#r13holoN",{{opacity:.9}},{{opacity:.6,duration:.4,repeat:7,yoyo:true}},{ini:.3f});')

    # 14 · regreso a la sala (frases 30-32 + 1 s de silencio)
    ini, fin = f(30)[0], TOTAL
    pant = recuerdo_vuelve(con_espectador=False).replace('id="', 'id="p14')
    pant = pant.replace('id="p14alcanza13" opacity="0"', 'id="p14alcanza13" opacity="1" transform="translate(470 1600)"')
    pant = pant.replace('id="p14camina13"', 'id="p14camina13" opacity="0"')
    t_se = palabra(30, "Se")
    plano("p14", ini, fin, sala_cine(d, pant, polvo_id="polvo14"), {"scale": 2.6, "y": 520}, {"scale": 1.0, "y": 0},
          pintura=False, ease="power2.out", cam_dur=1.3,
          extra_html='<div class="tarjeta-wrap"><div class="tarjeta" id="tarjeta" style="opacity:0"><div class="titulo">MARJORIE PRIME</div><div class="sub">2017</div></div></div>')
    tw(f'tl.fromTo("#cp14",{{svgOrigin:"540 960",scale:1.0,y:0}},{{scale:1.06,duration:{fin-ini-1.3:.3f},ease:"none",immediateRender:false}},{ini+1.3:.3f});')  # …y sigue avanzando lento
    tw(f'tl.fromTo("#polvo14",{{x:0,y:0}},{{x:-40,y:10,duration:{fin-ini:.3f},ease:"none"}},{ini:.3f});')
    tw(f'tl.fromTo("#tarjeta",{{opacity:0}},{{opacity:1,duration:.4,ease:"power1.out"}},{t_se:.3f});')

    audio = f'<audio id="voz" src="assets/audio/voz.mp3" data-start="0" data-duration="{TOTAL}" data-track-index="9"></audio>'
    page = f"""<!doctype html>
<html lang="es" data-resolution="portrait">
<head><meta charset="UTF-8"/><meta name="viewport" content="width=1080, height=1920"/>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
<style>{CSS}</style></head>
<body>
<svg width="0" height="0" style="position:absolute"><defs>{d.render()}</defs></svg>
<div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1080" data-height="1920">
{''.join(PLANOS)}
{audio}
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(TW)}
window.__timelines = window.__timelines || {{}};
window.__timelines["main"] = tl;
tl.seek(0);
</script>
</body></html>
"""
    (AQUI / "index.html").write_text(page, encoding="utf-8")
    print("index.html:", len(page) // 1024, "KB ·", TOTAL, "s ·", len(PLANOS), "planos")


if __name__ == "__main__":
    build()
