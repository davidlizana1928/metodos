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


# ------------------------------------------------------------ escenas · acabado mixto (v3)
# Fondos en pintura digital (assets/fondos/*.jpg, generados con motor/fondos.py) + personajes 2D con volumen (svgkit).

def frase(n):
    t = TIEMPOS[n - 1]
    return t["inicio"], t["fin"]


def fondo(nombre, gid=None):
    g = f' id="{gid}"' if gid else ""
    return (f'<g{g}><image href="assets/fondos/{nombre}.jpg" x="-40" y="-40" width="1160" height="2000" '
            f'preserveAspectRatio="xMidYMid slice"/></g>')


def velo(color, opacidad, modo="multiply"):
    """Luz de la escena sobre todo el cuadro: une personajes y fondo en un mismo ambiente."""
    return f'<rect width="1080" height="1920" fill="{color}" opacity="{opacidad}" style="mix-blend-mode:{modo}"/>'


def luz_ventana(x, y, r, color="#fff4d0", op=.35):
    return f'<ellipse cx="{x}" cy="{y}" rx="{r}" ry="{r*0.7:.0f}" fill="{d.radial("lv" + color[1:] + str(int(op*100)), [(0, color, op), (1, color, 0)])}"/>'


def emisor(x, y):
    cono = d.lineal("cono", [(0, "#7fe8ff", .0), (1, "#7fe8ff", .45)])
    return (f'<g id="emisor"><g transform="translate({x} {y})">{mesa(d, 0, 0, 240, 170, "#6a3a1e")}'
            f'<ellipse cx="0" cy="-172" rx="54" ry="14" fill="#cfefff"/><ellipse cx="0" cy="-174" rx="40" ry="9" fill="#7fe8ff"/>'
            f'<path id="conoLuz" d="M-20 -178 L200 -640 L330 -560 L20 -178 Z" fill="{cono}"/></g></g>')


def escena_living_dia():
    s = fondo("living_dia", "bgLD") + luz_ventana(540, 1300, 600)
    s += sillon(d, 250, 1730, 300, "#b8402c")
    s += persona(d, 250, 1730, 640, pose="sentada", brazo="regazo", **ANCIANA)
    s += emisor(560, 1760)
    s += sillon(d, 850, 1730, 300, "#b8402c", mira="izq")
    s += f'<g id="holo">{persona(d, 850, 1730, 730, pose="sentada", mira="izq", brazo="adelante", holograma=F["halo"], **ESPOSO)}</g>'
    return s


def interior_vitrina():
    s = fondo("vitrina", "bgV") + luz_ventana(700, 1100, 500)
    s += persona(d, 720, 1860, 980, mira="izq", brazo="bastón", bastón=True, encorvada=8, **ANCIANA)
    return s


def escena_exterior():
    s = fondo("exterior", "bgE")
    s += f'<g id="caminante">{persona(d, 0, 0, 600, brazo="bastón", bastón=True, encorvada=8, **ANCIANA)}</g>'
    return s


def pared_fotos():
    s = fondo("pared", "bgP") + luz_ventana(200, 700, 700, "#fff0c8", .3)
    for i, (x, y, w, h) in enumerate([(110, 380, 230, 290), (390, 330, 270, 210), (710, 400, 230, 290), (150, 740, 270, 210), (470, 620, 210, 270), (730, 760, 240, 210)]):
        c1, c2 = ["#3a6ea8", "#a84a3a", "#4a8a5a", "#8a5aa8", "#c08a3a", "#3a8a9a"][i], ["#f0c8a0", "#e8b090", "#f2d0b0"][i % 3]
        s += (f'<g><rect x="{x+10}" y="{y+14}" width="{w}" height="{h}" fill="#000" opacity=".25"/>'
              f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{d.vol("#5a3418", "h", .18)}"/>'
              f'<g id="foto{i}"><rect x="{x+14}" y="{y+14}" width="{w-28}" height="{h-28}" fill="{d.vol(c1, "v", .15)}"/>'
              f'<circle cx="{x+w/2-25}" cy="{y+h*0.42}" r="{h*0.13:.0f}" fill="{c2}"/><circle cx="{x+w/2+28}" cy="{y+h*0.45}" r="{h*0.12:.0f}" fill="{c2}"/>'
              f'<path d="M{x+30} {y+h-14} Q{x+w/2} {y+h*0.55} {x+w-30} {y+h-14}Z" fill="{tono(c1,-.15)}"/></g>'
              f'<rect class="blanco" id="blanco{i}" x="{x+14}" y="{y+14}" width="{w-28}" height="{h-28}" fill="#fffdf6" opacity="0"/></g>')
    s += persona(d, 860, 1860, 920, mira="izq", brazo="adelante", encorvada=6, **ANCIANA)
    return s


def comedor():
    s = fondo("living_vacio", "bgC") + luz_ventana(540, 900, 700)
    s += ('<path d="M540 0 V560" stroke="#2a2018" stroke-width="6"/><path d="M450 640 L630 640 L590 560 L490 560 Z" fill="#2a8a5a"/>'
          f'<ellipse cx="540" cy="700" rx="300" ry="180" fill="{d.radial("colg", [(0, "#ffe0a0", .5), (1, "#000", 0)])}"/>')
    g = [silla(d, 210, 1560, 240) + persona(d, 210, 1560, 640, pose="sentada", brazo="adelante", **HIJA),
         silla(d, 870, 1560, 240, mira="izq") + persona(d, 870, 1560, 680, pose="sentada", mira="izq", brazo="adelante", **YERNO),
         mesa(d, 540, 1600, 580, 330, "#7a4424"),
         '<g id="tablet"><rect x="470" y="1255" width="140" height="18" rx="4" fill="#bff0ff" opacity=".85"/>'
         f'<ellipse cx="540" cy="1250" rx="140" ry="40" fill="{d.radial("tabl", [(0, "#7fe8ff", .5), (1, "#7fe8ff", 0)])}"/></g>']
    sil = "".join(f'<g transform="translate({x} 1262) scale(1.15)"><g class="sil" id="sil{i}">'
                  '<ellipse cx="0" cy="-90" rx="13" ry="16" fill="#bff6ff" opacity=".85"/><path d="M-18 -72 Q0 -80 18 -72 L14 -30 L8 0 L-8 0 L-14 -30Z" fill="#bff6ff" opacity=".85"/></g></g>'
                  for i, x in enumerate([400, 470, 540, 610, 680]))
    g.append(f'<g id="catalogo" opacity="0" filter="{F["halo"]}">{sil}</g>')
    g.append(f'<g id="silLlena" opacity="0" transform="translate(540 1262) scale(.32)">{persona(d, 0, 0, 690, mira="izq", **ESPOSO)}</g>')
    g.append('<g id="ondas" opacity="0" stroke="#7fe8ff" stroke-width="6" fill="none">' + "".join(
        f'<path d="M{760 - k * 50} {1000 + k * 20} q-20 30 0 60"/>' for k in range(4)) + '</g>')
    s += f'<g transform="translate(0 150)">{"".join(g)}</g>'
    s += velo("#ff9a40", .24)
    return s


def eleccion():
    s = fondo("living_dia", "bgEl") + luz_ventana(540, 1300, 600)
    marco = ('<g transform="translate({mx} {my}) rotate(-10)"><rect x="-6" y="-120" width="110" height="140" fill="#c9a24a"/>'
             '<rect x="4" y="-110" width="90" height="120" fill="#8fb0c8"/>'
             '<circle cx="49" cy="-70" r="22" fill="#e0b090"/><path d="M30 -82 q19 -18 38 0" fill="#d8d8d8"/>'
             '<path d="M18 10 Q49 -40 80 10Z" fill="#1e2f6e"/></g>')
    s += sillon(d, 280, 1760, 320, "#b8402c")
    s += persona(d, 280, 1760, 660, pose="sentada", brazo="adelante", extra=marco, **ANCIANA)
    s += f'<g id="holo5" opacity="0">{persona(d, 830, 1770, 760, mira="izq", holograma=F["halo"], **ESPOSO)}</g>'
    return s


def cuentas_vida():
    s = fondo("living_dia", "bgCV") + luz_ventana(540, 1100, 600)
    s += ('<g id="recuerdos" opacity="0">'
          '<rect x="140" y="500" width="360" height="380" rx="8" fill="#fff3c8" opacity=".3"/>'
          f'<g transform="translate(320 860)" opacity=".8">{persona(d, 0, 0, 320, brazo="arriba", sombra=False, **JOVEN_ELLA)}</g>'
          '<rect x="580" y="500" width="360" height="380" rx="8" fill="#ffffff" opacity=".3"/>'
          f'<g transform="translate(700 860)" opacity=".8">{persona(d, 0, 0, 300, sombra=False, **JOVEN_ELLA)}</g>'
          f'<g transform="translate(830 860)" opacity=".8">{persona(d, 0, 0, 330, mira="izq", sombra=False, **ESPOSO)}</g></g>')
    s += sillon(d, 850, 1730, 300, "#b8402c", mira="izq")
    s += f'<g id="holo6">{persona(d, 850, 1730, 730, pose="sentada", mira="izq", brazo="adelante", holograma=F["halo"], **ESPOSO)}</g>'
    s += sillon(d, 170, 2080, 540, "#b8402c")
    s += persona(d, 170, 2080, 1120, pose="sentada", brazo="adelante", **ANCIANA)
    return s


def escena_hija():
    """Escena 7: en el living; la madre y el holograma al fondo, la hija adelante, el Espectador de testigo."""
    s = fondo("living_dia", "bgH") + luz_ventana(600, 1250, 500)
    s += f'<g>{sillon(d, 520, 1520, 190, "#b8402c")}{persona(d, 520, 1520, 410, pose="sentada", brazo="regazo", **ANCIANA)}</g>'
    s += f'<g id="holo7a">{sillon(d, 800, 1520, 190, "#b8402c", mira="izq")}{persona(d, 800, 1520, 470, pose="sentada", mira="izq", brazo="adelante", holograma=F["halo"], **ESPOSO)}</g>'
    s += f'<g id="holo7b" opacity="0">{persona(d, 800, 1520, 470, pose="sentada", mira="izq", brazo="arriba", holograma=F["halo"], **ESPOSO)}</g>'
    s += f'<g id="hija7">{persona(d, 230, 1960, 1000, mira="der", brazo="abajo", **HIJA)}</g>'
    s += espectador_pie(d, 1000, 2060, 960)
    return s


def terraza_noche():
    s = fondo("terraza_noche", "bgTN")
    taza = '<g transform="translate({mx} {my})"><rect x="-4" y="-38" width="44" height="46" rx="6" fill="#f2efe6"/><path d="M40 -28 q18 6 0 22" stroke="#f2efe6" stroke-width="7" fill="none"/></g>'
    s += mesa(d, 330, 1720, 190, 310, "#5a3a22") + silla(d, 250, 1720, 250, "#4a2a16")
    s += f'<g id="yerno8">{persona(d, 250, 1720, 680, pose="sentada", brazo="adelante", encorvada=10, extra=taza, **YERNO)}</g>'
    s += f'<g id="holo8">{persona(d, 720, 1720, 760, mira="izq", holograma=F["halo"], **ESPOSO)}</g>'
    s += velo("#2a3a8a", .25)
    return s


def escena_living_noche(dormida=True):
    s = fondo("living_noche", "bgLN")
    s += ('<rect x="60" y="300" width="460" height="22" fill="#5a3a22"/><rect x="60" y="322" width="460" height="10" fill="#2a1a10"/>'
          '<rect x="90" y="196" width="80" height="104" fill="#c9a24a"/><rect x="99" y="205" width="62" height="86" fill="#8fb0d0"/>'
          '<rect x="190" y="220" width="70" height="80" fill="#a8743a"/><rect x="198" y="228" width="54" height="64" fill="#d0a080"/>'
          '<rect x="390" y="206" width="76" height="94" fill="#c9a24a"/><rect x="398" y="214" width="60" height="78" fill="#9ac0a0"/>'
          '<g id="marcoAbajo"><rect x="285" y="286" width="84" height="14" fill="#6a4a2a"/><rect x="285" y="282" width="84" height="6" fill="#3a2414"/></g>')
    s += lampara_pie(d, 70, 1740, 560, encendida=True, gid="lampN")
    if dormida:
        s += sillon(d, 300, 1780, 300, "#6a2a3a")
        s += persona(d, 300, 1780, 640, pose="sentada", brazo="regazo", ojos="cerrados", encorvada=-6, **ANCIANA)
    s += f'<g id="holoN">{persona(d, 930, 1620, 640, mira="izq", holograma=F["halo"], **ESPOSO)}</g>'
    s += velo("#1a2a6a", .2)
    return s


def calle_reflejo():
    """El recuerdo como imagen translúcida en el cielo: la pareja joven en la calle de noche."""
    return (f'<g transform="translate(330 0)"><rect x="0" y="300" width="430" height="700" rx="20" fill="#1a1a3a" opacity=".7"/>'
            f'<g transform="translate(150 980)">{persona(d, 0, 0, 360, brazo="abajo", sombra=False, **JOVEN_ELLA)}</g>'
            f'<g transform="translate(240 980)">{persona(d, 0, 0, 400, sombra=False, **ESPOSO)}</g></g>')


def terraza_dia():
    s = fondo("terraza_dia", "bgTD")
    s += f'<g id="reflejo" opacity="0"><g opacity=".55">{calle_reflejo()}</g></g>'
    s += sillon(d, 520, 1760, 300, "#e0a526") + persona(d, 520, 1760, 640, pose="sentada", brazo="regazo", **ANCIANA)
    s += sillon(d, 820, 1760, 300, "#e0a526") + f'<g id="holo10">{persona(d, 820, 1760, 730, pose="sentada", brazo="regazo", holograma=F["halo"], **ESPOSO)}</g>'
    return s


def recuerdo_grande():
    cieloC = d.lineal("cieloCal", [(0, "#2a1a5a", 1), (.6, "#c2326e", 1), (1, "#ffb35a", 1)])
    return (fondo("calle_lluvia", "bgCL")
            + f'<rect id="cieloCalido" width="1080" height="1920" fill="{cieloC}" opacity="0" style="mix-blend-mode:soft-light"/>'
            + f'<g id="parejaG"><g transform="translate(420 1760)">{persona(d, 0, 0, 660, brazo="abajo", torso="#8a8a90", falda="#8a8a90", pelo="moño_castaño", pelo_color="#7a4a26", piel="#eab792")}</g>'
            + f'<g id="abrigoCrema" opacity="0"><g transform="translate(420 1760)">{persona(d, 0, 0, 660, brazo="abajo", **JOVEN_ELLA)}</g></g>'
            + f'<g transform="translate(580 1760)">{persona(d, 0, 0, 720, **ESPOSO)}</g></g>'
            + lluvia("lluviaG", n=170)
            + '<path d="M0 0 h1080 v1920 h-1080z" stroke="#3a2012" stroke-width="60" fill="none"/>'
            + f'<g id="mano"><path d="M-40 1460 L240 1330" stroke="#d4d4cf" stroke-width="110" stroke-linecap="round"/>'
              f'<circle cx="260" cy="1322" r="48" fill="{d.vol("#e8b898", "h", .1)}"/><path d="M290 1300 L360 1262" stroke="#e8b898" stroke-width="26" stroke-linecap="round"/></g>')


def escena_calle_noche():
    """Escena 12: entrada del cine antiguo; la marquesina en código tapa las letras que inventó la IA."""
    bombillas = "".join(f'<circle class="bomb" cx="{40 + i * 50}" cy="{c}" r="10" fill="#ffe9a8"/>' for i in range(21) for c in (345, 505))
    return (fondo("cine", "bgCi")
            + '<rect x="0" y="320" width="1080" height="210" fill="#1a0a14"/>'
            + f'<g id="bombillas">{bombillas}</g>'
            + '<rect id="tablero" x="40" y="370" width="1000" height="110" fill="#f7e6b8"/>'
            + f'<rect x="40" y="370" width="1000" height="110" fill="{d.lineal("marq", [(0, "#fff", .45), (1, "#fff", 0)])}"/>'
            + f'<ellipse cx="540" cy="430" rx="700" ry="260" fill="{d.radial("marqLuz", [(0, "#ffd98a", .35), (1, "#ffd98a", 0)])}"/>'
            + f'<rect y="1560" width="1080" height="360" fill="{d.lineal("reflC", [(0, "#ffcf6a", .3), (1, "#ffcf6a", 0)])}"/>'
            + persona(d, 700, 1800, 700, mira="izq", brazo="abajo", **JOVEN_ELLA)
            + persona(d, 400, 1800, 750, pose="arrodillado", brazo="adelante",
                      extra='<circle cx="{mx}" cy="{my}" r="9" fill="#ffd84a" stroke="#fff" stroke-width="2"/>', **ESPOSO)
            + velo("#b03a8a", .24))


def recuerdo_vuelve(con_espectador=True):
    s = escena_living_noche(dormida=False).replace('id="', 'id="r13')
    s += sillon(d, 760, 1720, 270, "#3a5a8a", mira="izq") + persona(d, 760, 1720, 620, pose="sentada", mira="izq", brazo="adelante", **HIJA)
    s += sillon(d, 960, 1720, 270, "#3a5a8a", mira="izq") + persona(d, 960, 1720, 660, pose="sentada", mira="izq", brazo="adelante", **YERNO)
    s += f'<g id="camina13">{persona(d, 0, 0, 640, mira="izq", brazo="bastón", bastón=True, encorvada=8, **ANCIANA)}</g>'
    s += f'<g id="alcanza13" opacity="0">{persona(d, 0, 0, 640, mira="izq", brazo="arriba", encorvada=4, **ANCIANA)}</g>'
    if con_espectador:
        s += espectador_pie(d, 120, 2100, 900)
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


def lienzo(contenido, cid, pintura=False):
    filtro = f' filter="{F["pintura"]}"' if pintura else ""
    return (f'<svg class="lienzo" viewBox="0 0 1080 1920"><g id="{cid}">'
            f'<g{filtro}>{contenido}</g></g><rect width="1080" height="1920" filter="{F["grano"]}"/></svg>')


PLANOS, TW = [], []


def plano(pid, ini, fin, contenido, cam_de, cam_a, pintura=False, extra_html="", ease="none", cam_dur=None):
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
    tw(f'tl.fromTo("#bgLD",{{x:0}},{{x:30,duration:{fin-ini:.3f},ease:"none"}},{ini:.3f});')
    tw(f'tl.fromTo("#conoLuz",{{opacity:.4}},{{opacity:1,duration:.6,repeat:5,yoyo:true,ease:"sine.inOut"}},{ini:.3f});')

    # 3a · más de ochenta años, violinista (frase 5)
    ini, fin = f(5)[0], f(6)[0]
    plano("p03a", ini, fin, interior_vitrina(), {"scale": 1.25, "x": 60, "y": -120}, {"scale": 1.32, "x": -40, "y": -140},
          extra_html=banner("b80", "80 AÑOS", 5, "ochenta", 330, fin - 0.2))
    tw(f'tl.fromTo("#bgV",{{x:0}},{{x:25,duration:{fin-ini:.3f},ease:"none"}},{ini:.3f});')
    # 3b · frente al mar (frase 6)
    ini, fin = f(6)[0], f(7)[0]
    plano("p03b", ini, fin, escena_exterior(), {"scale": 1.18, "x": -60, "y": 150}, {"scale": 1.26, "x": -110, "y": 170})
    tw(f'tl.fromTo("#caminante",{{x:180,y:1720}},{{x:470,y:1720,duration:{fin-ini+FUNDIDO:.3f},ease:"none"}},{ini:.3f});')
    tw(f'tl.fromTo("#bgE",{{x:0}},{{x:30,duration:{fin-ini:.3f},ease:"none"}},{ini:.3f});')
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
    tw(f'tl.fromTo("#bgEl",{{x:0}},{{x:25,duration:{fin-ini:.3f},ease:"none"}},{ini:.3f});')

    # 6 · le cuentas tu vida (frase 14)
    ini, fin = f(14)[0], f(15)[0]
    plano("p06", ini, fin, cuentas_vida(), {"scale": 1.05, "x": 0}, {"scale": 1.14, "x": -40})
    tw(f'tl.to("#recuerdos",{{opacity:.75,duration:.6}},{ini+.3:.3f});')
    tw(f'tl.to("#recuerdos",{{opacity:1,duration:.4}},{palabra(14, "repite"):.3f});')
    tw(f'tl.fromTo("#holo6",{{opacity:.7}},{{opacity:1,duration:.3,repeat:3,yoyo:true}},{palabra(14, "repite"):.3f});')

    # 7 · la hija (frases 15-17)
    ini, fin = f(15)[0], f(18)[0]
    plano("p07", ini, fin, escena_hija(), {"scale": 1.1, "x": 40}, {"scale": 1.18, "x": -30})
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
    tw(f'tl.fromTo("#bgTD",{{x:0}},{{x:-30,duration:{fin-ini:.3f},ease:"none"}},{ini:.3f});')
    tw(f'tl.to("#reflejo",{{opacity:.85,duration:.8}},{palabra(23, "reescribiendo"):.3f});')

    # 11 · detalles nuevos (frases 24-25)
    ini, fin = f(24)[0], f(26)[0]
    plano("p11", ini, fin, recuerdo_grande(), {"scale": 1.0}, {"scale": 1.08})
    tw(f'tl.fromTo("#lluviaG",{{y:-60}},{{y:60,duration:.3,repeat:{int((f(25)[0]-ini)/.3)},ease:"none"}},{ini:.3f});')
    t25 = f(25)[0]
    tw(f'tl.to("#lluviaG",{{opacity:0,duration:.6}},{t25:.3f});')
    tw(f'tl.to("#cieloCalido",{{opacity:1,duration:1.2}},{t25:.3f});')
    tw(f'tl.to("#abrigoCrema",{{opacity:1,duration:1.0}},{t25+.4:.3f});')
    tw(f'tl.fromTo("#bgCL",{{x:0}},{{x:-25,duration:{fin-ini:.3f},ease:"none"}},{ini:.3f});')
    tw(f'tl.fromTo("#mano",{{x:0}},{{x:20,duration:.5,repeat:3,yoyo:true,ease:"sine.inOut"}},{ini:.3f});')

    # 12 · la noche de la propuesta (frases 26-27)
    ini, fin = f(26)[0], f(28)[0]
    plano("p12", ini, fin, escena_calle_noche(), {"scale": 1.0, "y": 0}, {"scale": 1.12, "y": -60})
    t_v = palabra(27, "versión")
    tw(f'tl.fromTo("#cp12 .bomb",{{opacity:1}},{{opacity:.35,duration:.25,repeat:{int((fin-ini)/.25)-1},yoyo:true,stagger:{{each:.04,from:"random"}},ease:"none"}},{ini:.3f});')
    tw(f'tl.to("#tablero",{{fill:"#9ee8d0",duration:.35}},{t_v:.3f});')
    tw(f'tl.to("#tablero",{{fill:"#ffb0c8",duration:.35}},{t_v+.5:.3f});')
    tw(f'tl.to("#tablero",{{fill:"#ffe08a",duration:.35}},{t_v+1.0:.3f});')
    tw(f'tl.fromTo("#bgCi",{{x:0}},{{x:20,duration:{fin-ini:.3f},ease:"none"}},{ini:.3f});')

    # 13 · el recuerdo que vuelve (frases 28-29)
    ini, fin = f(28)[0], f(30)[0]
    plano("p13", ini, fin, recuerdo_vuelve(), {"scale": 1.05, "x": 40}, {"scale": 1.35, "x": 260, "y": 330}, ease="power1.in")
    tw(f'tl.fromTo("#camina13",{{x:640,y:1720}},{{x:430,y:1720,duration:{f(29)[1]-ini-0.9:.3f},ease:"none"}},{ini:.3f});')
    tw(f'tl.set("#alcanza13",{{x:430,y:1720}},{ini:.3f});')
    t_esc = palabra(29, "esconde")
    tw(f'tl.to("#camina13",{{opacity:0,duration:.15}},{t_esc-0.6:.3f});')
    tw(f'tl.to("#alcanza13",{{opacity:1,duration:.15}},{t_esc-0.6:.3f});')
    tw(f'tl.fromTo("#r13holoN",{{opacity:.9}},{{opacity:.6,duration:.4,repeat:7,yoyo:true}},{ini:.3f});')

    # 14 · regreso a la sala (frases 30-32 + 1 s de silencio)
    ini, fin = f(30)[0], TOTAL
    pant = recuerdo_vuelve(con_espectador=False).replace('id="', 'id="p14')
    pant = pant.replace('id="p14alcanza13" opacity="0"', 'id="p14alcanza13" opacity="1" transform="translate(430 1720)"')
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
