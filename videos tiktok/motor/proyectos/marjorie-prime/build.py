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
from svgkit import (Defs, persona, sillon, lampara_pie, planta, sala_cine, sello_svg, mulberry32, tono)  # noqa: E402

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


def escena_living_noche():
    s = living(True, mar_id="olasN", lampara_id="lampN")
    repisa = ('<rect x="150" y="300" width="380" height="18" fill="#5a3a22"/>'
              '<rect x="170" y="210" width="70" height="90" fill="#c9a24a"/><rect x="178" y="218" width="54" height="74" fill="#8fb0d0"/>'
              '<rect x="260" y="230" width="60" height="70" fill="#a8743a"/><rect x="267" y="237" width="46" height="56" fill="#d0a080"/>'
              '<rect x="420" y="220" width="64" height="80" fill="#c9a24a"/><rect x="427" y="227" width="50" height="66" fill="#9ac0a0"/>'
              '<g id="marcoAbajo"><rect x="335" y="288" width="72" height="12" fill="#6a4a2a"/><rect x="335" y="284" width="72" height="5" fill="#3a2414"/></g>'
              + sello_svg("sSecreto", 371, 262, "SECRETO", 300, tam=50))
    # la repisa va sobre el muro izquierdo, arriba del ventanal (repisa alta)
    s = s.replace('<rect x="120" y="360"', repisa + '<rect x="120" y="360"', 1)
    s += sillon(d, 250, 1590, 290, "#6a2a3a")
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
            + sello_svg("sEditado", 540, 785, "EDITADO", 360) +
            f'<g id="carteles">{carteles}</g>'
            '<rect x="420" y="1150" width="240" height="150" fill="#2a0a14"/><rect x="430" y="1160" width="105" height="140" fill="#ffcf6a" opacity=".7"/><rect x="545" y="1160" width="105" height="140" fill="#ffcf6a" opacity=".7"/>'
            f'<rect y="1300" width="1080" height="620" fill="{acera}"/>'
            f'<rect x="230" y="1300" width="620" height="400" fill="{reflejo}"/>'
            + farol(110) + farol(970)
            + persona(d, 690, 1660, 640, mira="izq", brazo="abajo", **JOVEN_ELLA)
            + persona(d, 400, 1660, 690, pose="arrodillado", brazo="adelante",
                      extra='<circle cx="{mx}" cy="{my}" r="9" fill="#ffd84a" stroke="#fff" stroke-width="2"/>', **ESPOSO))


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
.banner-wrap{position:absolute;left:0;right:0;top:330px;display:flex;justify-content:center}
.banner{background:var(--carmesi);color:var(--crema);font-family:"Archivo Black";font-size:104px;padding:14px 44px 6px;box-shadow:0 12px 40px rgba(0,0,0,.45)}
.sello{position:absolute;font-family:"Archivo Black";color:#ff4a4a;font-size:78px;border:8px solid #ff4a4a;padding:4px 22px 0;transform:rotate(-8deg);background:rgba(20,0,0,.25)}
.tarjeta-wrap{position:absolute;left:120px;right:192px;top:300px}
.tarjeta{background:rgba(8,16,18,.72);padding:34px 40px 30px;text-align:center;border-top:6px solid var(--mostaza)}
.tarjeta .titulo{font-family:"Archivo Black";color:var(--crema);font-size:84px;line-height:1}
.tarjeta .sub{font-family:"Oswald";color:var(--mostaza);font-size:40px;margin-top:14px;letter-spacing:.08em}
.pendiente{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-family:"Oswald";font-size:48px;color:#888;background:#111}
"""


def lienzo(contenido, cid, pintura=False):
    filtro = f' filter="{F["pintura"]}"' if pintura else ""
    return (f'<svg class="lienzo" viewBox="0 0 1080 1920"><g id="{cid}" style="transform-origin:540px 960px">'
            f'<g{filtro}>{contenido}</g></g><rect width="1080" height="1920" filter="{F["grano"]}"/></svg>')


def clip(e, cuerpo, extra=""):
    return (f'<div id="e{e["n"]}" class="clip esc" data-start="{e["inicio"]}" data-duration="{e["dur"]}" '
            f'data-track-index="0">{cuerpo}</div>{extra}')


def build():
    E = {e["slug"]: e for e in ESC}
    html, tw = [], []
    # 1 · sala con el living en la pantalla
    e = E["sala-entrada"]
    html.append(clip(e, lienzo(sala_cine(d, escena_living_dia().replace('id="', 'id="p1'), polvo_id="polvo1"), "cam1")
                     + '<div class="gancho-wrap"><div class="gancho" id="gancho">Imagina que tu esposo, muerto hace <em>15 años</em>, está frente a ti…</div></div>'))
    tw += [f'tl.fromTo("#cam1",{{svgOrigin:"540 960",scale:1}},{{scale:1.05,duration:{e["dur"]-1.3},ease:"none"}},{e["inicio"]});',
           f'tl.to("#cam1",{{svgOrigin:"540 960",scale:2.6,y:520,duration:1.3,ease:"power2.in"}},{e["fin"]-1.3});',
           f'tl.fromTo("#polvo1",{{x:0}},{{x:-30,duration:{e["dur"]},ease:"none"}},{e["inicio"]});',
           f'tl.fromTo("#gancho",{{opacity:0,y:30}},{{opacity:1,y:0,duration:.3,ease:"power3.out"}},0);',
           f'tl.to("#gancho",{{opacity:0,duration:.25}},{e["fin"]-1.6});']
    # 2 · el holograma
    e = E["holograma"]
    t_holo = palabra(3, "holograma")
    html.append(clip(e, lienzo(escena_living_dia(), "cam2", pintura=True)
                     + f'<div id="cBanner" class="banner-wrap clip" data-start="{t_holo:.3f}" data-duration="{e["fin"]-t_holo-.1:.3f}" data-track-index="1"><div class="banner" id="bHolo">HOLOGRAMA</div></div>'))
    tw += [f'tl.fromTo("#cam2",{{svgOrigin:"540 960",scale:1.12,x:-60}},{{scale:1.22,x:-140,duration:{e["dur"]},ease:"none"}},{e["inicio"]});',
           f'tl.fromTo("#holo",{{opacity:.95}},{{opacity:.55,duration:.18,repeat:9,yoyo:true,ease:"steps(2)"}},{e["inicio"]+.2});',
           f'tl.fromTo("#olas",{{x:0}},{{x:-70,duration:{e["dur"]},ease:"none"}},{e["inicio"]});',
           f'tl.fromTo("#conoLuz",{{opacity:.4}},{{opacity:1,duration:.6,repeat:5,yoyo:true,ease:"sine.inOut"}},{e["inicio"]});',
           f'tl.fromTo("#bHolo",{{opacity:0,scale:1.15}},{{opacity:1,scale:1,duration:.15,ease:"power2.out"}},{t_holo:.3f});']
    # 3 · la casa frente al mar
    e = E["casa-mar"]
    html.append(clip(e, lienzo(escena_exterior(), "cam3", pintura=True)))
    tw += [f'tl.fromTo("#cam3",{{svgOrigin:"540 960",scale:1.18,x:-60,y:150}},{{scale:1.26,x:-110,y:170,duration:{e["dur"]},ease:"none"}},{e["inicio"]});',
           f'tl.fromTo("#caminante",{{x:360,y:1300}},{{x:620,y:1300,duration:{e["dur"]},ease:"none"}},{e["inicio"]});',
           f'tl.fromTo("#nubes",{{x:0}},{{x:-120,duration:{e["dur"]},ease:"none"}},{e["inicio"]});',
           f'tl.fromTo("#olasE",{{x:0}},{{x:-80,duration:{e["dur"]},ease:"none"}},{e["inicio"]});']
    # 9 · lo que nadie menciona
    e = E["secreto"]
    t_sec = palabra(20, "tragedia")
    html.append(clip(e, lienzo(escena_living_noche(), "cam9", pintura=True)))
    tw += [f'tl.fromTo("#cam9",{{svgOrigin:"540 960",scale:1.5,x:250,y:420}},{{scale:1.15,x:60,y:60,duration:{e["dur"]},ease:"power1.inOut"}},{e["inicio"]});',
           f'tl.fromTo("#holoN",{{opacity:.9}},{{opacity:.6,duration:.4,repeat:7,yoyo:true,ease:"sine.inOut"}},{e["inicio"]});',
           f'tl.to("#lampN",{{opacity:0,duration:.25}},{e["fin"]-1.2});',
           f'tl.fromTo("#sSecreto",{{scale:1.25,opacity:0,transformOrigin:"50% 50%"}},{{scale:1,opacity:1,duration:.2,ease:"power2.out"}},{t_sec:.3f});',
           f'tl.to("#sSecreto",{{opacity:0,duration:.2}},{t_sec+2.2:.3f});']
    # 12 · la noche de la propuesta
    e = E["propuesta"]
    t_ed = palabra(27, "versión")
    html.append(clip(e, lienzo(escena_calle_noche(), "cam12", pintura=True)))
    tw += [f'tl.fromTo("#cam12",{{svgOrigin:"540 960",scale:1.0,y:0}},{{scale:1.12,y:-60,duration:{e["dur"]},ease:"none"}},{e["inicio"]});',
           f'tl.fromTo("#e12 .bomb",{{opacity:1}},{{opacity:.35,duration:.25,repeat:{int(e["dur"]/.25)-1},yoyo:true,stagger:{{each:.04,from:"random"}},ease:"none"}},{e["inicio"]});',
           f'tl.to("#cartel0",{{fill:"#7a3ad8",duration:.4}},{t_ed:.3f});',
           f'tl.to("#cartel1",{{fill:"#f06a2a",duration:.4}},{t_ed+.2:.3f});',
           f'tl.to("#cartel2",{{fill:"#2ad88a",duration:.4}},{t_ed+.4:.3f});',
           f'tl.fromTo("#sEditado",{{scale:1.25,opacity:0,transformOrigin:"50% 50%"}},{{scale:1,opacity:1,duration:.2,ease:"power2.out"}},{t_ed:.3f});',
           f'tl.to("#sEditado",{{opacity:0,duration:.2}},{min(t_ed+2.0, e["fin"]-.1):.3f});']
    # 14 · regreso a la sala
    e = E["sala-final"]
    t_se = palabra(30, "Se")
    pant = escena_living_noche().replace('id="', 'id="p14')
    html.append(clip(e, lienzo(sala_cine(d, pant, polvo_id="polvo14"), "cam14")
                     + f'<div id="cTarjeta" class="tarjeta-wrap clip" data-start="{t_se:.3f}" data-duration="{TOTAL-t_se:.3f}" data-track-index="1"><div class="tarjeta" id="tarjeta"><div class="titulo">MARJORIE PRIME</div><div class="sub">2017</div></div></div>'))
    tw += [f'tl.fromTo("#cam14",{{svgOrigin:"540 960",scale:2.6,y:520}},{{scale:1.0,y:0,duration:1.3,ease:"power2.out"}},{e["inicio"]});',
           f'tl.fromTo("#cam14",{{svgOrigin:"540 960",scale:1.0}},{{scale:1.06,duration:{e["dur"]-1.3},ease:"none",immediateRender:false}},{e["inicio"]+1.3});',
           f'tl.fromTo("#polvo14",{{x:0,y:0}},{{x:-40,y:10,duration:{e["dur"]},ease:"none"}},{e["inicio"]});',
           f'tl.fromTo("#tarjeta",{{opacity:0}},{{opacity:1,duration:.4,ease:"power1.out"}},{t_se:.3f});']
    # escenas aún no construidas: pendiente (solo para la revisión de fotogramas)
    hechas = {"sala-entrada", "holograma", "casa-mar", "secreto", "propuesta", "sala-final"}
    for e in ESC:
        if e["slug"] not in hechas:
            html.append(clip(e, f'<div class="pendiente">Escena {e["n"]} · pendiente</div>'))
    audio = f'<audio id="voz" src="assets/audio/voz.mp3" data-start="0" data-duration="{TOTAL}" data-track-index="9"></audio>'
    page = f"""<!doctype html>
<html lang="es" data-resolution="portrait">
<head><meta charset="UTF-8"/><meta name="viewport" content="width=1080, height=1920"/>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
<style>{CSS}</style></head>
<body>
<svg width="0" height="0" style="position:absolute"><defs>{d.render()}</defs></svg>
<div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1080" data-height="1920">
{''.join(html)}
{audio}
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(tw)}
window.__timelines["main"] = tl;
tl.seek(0);
</script>
</body></html>
"""
    (AQUI / "index.html").write_text(page, encoding="utf-8")
    print("index.html:", len(page) // 1024, "KB ·", TOTAL, "s")


if __name__ == "__main__":
    build()
