"""Biblioteca de dibujo de la marca: personajes, muebles, sala de cine y filtros.

Todo devuelve texto SVG. Coordenadas en píxeles del lienzo 1080x1920.
Las piezas usan degradados (luz -> base -> sombra) y sombra de contacto,
según ESTILO.md §7.1 (nivel de diseño mínimo).

Uso:
    from svgkit import Defs, persona, sillon, sala_cine
    d = Defs()
    svg = persona(d, x=400, y=1500, alto=620, pose="sentada", mira="der", ...)
    html = f"<svg ...><defs>{d.render()}</defs>{svg}</svg>"
"""
import colorsys
import math


def _hex(c):
    c = c.lstrip("#")
    if len(c) == 3:
        c = "".join(ch * 2 for ch in c)
    return tuple(int(c[i:i + 2], 16) / 255 for i in (0, 2, 4))


def _to_hex(rgb):
    return "#" + "".join(f"{max(0, min(255, round(v * 255))):02x}" for v in rgb)


def tono(c, luz=0.0, sat=0.0):
    """Aclara (luz>0) u oscurece (luz<0) un color en HLS, y ajusta saturación."""
    h, l, s = colorsys.rgb_to_hls(*_hex(c))
    l = min(1, max(0, l + luz))
    s = min(1, max(0, s + sat))
    return _to_hex(colorsys.hls_to_rgb(h, l, s))


def mulberry32(seed):
    a = seed & 0xFFFFFFFF

    def r():
        nonlocal a
        a = (a + 0x6D2B79F5) & 0xFFFFFFFF
        t = a
        t = ((t ^ (t >> 15)) * (1 | t)) & 0xFFFFFFFF
        t = (t + (((t ^ (t >> 7)) * (61 | t)) & 0xFFFFFFFF) ^ t) & 0xFFFFFFFF
        return ((t ^ (t >> 14)) & 0xFFFFFFFF) / 4294967296

    return r


class Defs:
    """Acumula degradados y filtros con ids únicos y estables."""

    def __init__(self, prefijo="k"):
        self.p = prefijo
        self.items = {}

    def _add(self, key, svg):
        if key not in self.items:
            self.items[key] = svg
        return key

    def vol(self, color, dir="h", fuerza=0.16):
        """Degradado de volumen: luz -> base -> sombra."""
        key = f"{self.p}v{dir}{color.lstrip('#')}{int(fuerza * 100)}"
        x2, y2 = ("1", "0") if dir == "h" else ("0", "1")
        return "url(#" + self._add(key, (
            f'<linearGradient id="{key}" x1="0" y1="0" x2="{x2}" y2="{y2}">'
            f'<stop offset="0" stop-color="{tono(color, fuerza)}"/>'
            f'<stop offset=".45" stop-color="{color}"/>'
            f'<stop offset="1" stop-color="{tono(color, -fuerza * 1.4)}"/></linearGradient>')) + ")"

    def lineal(self, key, paradas, vertical=True):
        k = f"{self.p}{key}"
        x2, y2 = ("0", "1") if vertical else ("1", "0")
        stops = "".join(f'<stop offset="{o}" stop-color="{c}" stop-opacity="{a}"/>' for o, c, a in paradas)
        return "url(#" + self._add(k, f'<linearGradient id="{k}" x1="0" y1="0" x2="{x2}" y2="{y2}">{stops}</linearGradient>') + ")"

    def radial(self, key, paradas, cx=".5", cy=".5", r=".5"):
        k = f"{self.p}{key}"
        stops = "".join(f'<stop offset="{o}" stop-color="{c}" stop-opacity="{a}"/>' for o, c, a in paradas)
        return "url(#" + self._add(k, f'<radialGradient id="{k}" cx="{cx}" cy="{cy}" r="{r}">{stops}</radialGradient>') + ")"

    def filtros(self):
        """Filtros comunes: brillo, suave, grano, pintura (acabado de la historia), halo."""
        self._add(f"{self.p}brillo", f'<filter id="{self.p}brillo" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="16"/></filter>')
        self._add(f"{self.p}suave", f'<filter id="{self.p}suave" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="3"/></filter>')
        self._add(f"{self.p}grano", (
            f'<filter id="{self.p}grano" x="0" y="0" width="100%" height="100%">'
            '<feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="7"/>'
            '<feColorMatrix type="saturate" values="0"/>'
            '<feComponentTransfer><feFuncA type="table" tableValues="0 .09"/></feComponentTransfer></filter>'))
        self._add(f"{self.p}pintura", (
            f'<filter id="{self.p}pintura" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB">'
            '<feTurbulence type="fractalNoise" baseFrequency=".012 .04" numOctaves="2" seed="3" result="t"/>'
            '<feDisplacementMap in="SourceGraphic" in2="t" scale="7" xChannelSelector="R" yChannelSelector="G" result="d"/>'
            '<feMorphology in="d" operator="dilate" radius="1.2" result="m"/>'
            '<feGaussianBlur in="m" stdDeviation=".8" result="b"/>'
            '<feTurbulence type="fractalNoise" baseFrequency=".35 .06" numOctaves="2" seed="11" result="tx"/>'
            '<feColorMatrix in="tx" type="matrix" values="0 0 0 0 .5  0 0 0 0 .5  0 0 0 0 .5  0 0 0 0 .22" result="lz"/>'
            '<feComposite in="lz" in2="b" operator="in" result="lzIn"/>'
            '<feBlend in="b" in2="lzIn" mode="overlay" result="pin"/>'
            '<feColorMatrix in="pin" type="saturate" values="1.3"/></filter>'))
        self._add(f"{self.p}halo", (
            f'<filter id="{self.p}halo" x="-30%" y="-10%" width="160%" height="120%">'
            '<feMorphology in="SourceAlpha" operator="dilate" radius="5" result="g"/>'
            '<feGaussianBlur in="g" stdDeviation="9" result="gb"/>'
            '<feFlood flood-color="#7fe8ff" flood-opacity=".95"/><feComposite in2="gb" operator="in" result="glow"/>'
            '<feMerge><feMergeNode in="glow"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'))
        return {k: f"url(#{self.p}{k})" for k in ("brillo", "suave", "grano", "pintura", "halo")}

    def render(self):
        return "".join(self.items.values())


# ---------------------------------------------------------------- personas

PELOS = {"moño_blanco", "ondulado", "corto_flequillo", "rapado", "moño_castaño", "corto_oscuro"}


def _cabeza(d, u, piel, pelo, pelo_color, barba=None, anteojos=False, ojos="abiertos"):
    """Cabeza de perfil mirando a la derecha. Centro en (0,0)."""
    s = []
    pv = d.vol(piel, "h", 0.12)
    # pelo detrás (moños y melenas)
    if pelo in ("moño_blanco", "moño_castaño"):
        s.append(f'<ellipse cx="{-0.42*u:.1f}" cy="{0.12*u:.1f}" rx="{0.2*u:.1f}" ry="{0.17*u:.1f}" fill="{d.vol(pelo_color, "v", .12)}"/>')
    if pelo == "ondulado":
        s.append(f'<path d="M{-0.46*u:.1f} {-0.1*u:.1f} Q{-0.62*u:.1f} {0.35*u:.1f} {-0.3*u:.1f} {0.5*u:.1f} L{-0.1*u:.1f} {0.3*u:.1f} Z" fill="{tono(pelo_color, -.08)}"/>')
    # cuello y cabeza
    s.append(f'<path d="M{-0.16*u:.1f} {0.35*u:.1f} L{0.12*u:.1f} {0.35*u:.1f} L{0.14*u:.1f} {0.75*u:.1f} L{-0.2*u:.1f} {0.75*u:.1f} Z" fill="{tono(piel, -.08)}"/>')
    s.append(f'<ellipse cx="0" cy="0" rx="{0.42*u:.1f}" ry="{0.52*u:.1f}" fill="{pv}"/>')
    # mandíbula y nariz
    s.append(f'<path d="M{0.3*u:.1f} {-0.05*u:.1f} Q{0.5*u:.1f} {0.02*u:.1f} {0.42*u:.1f} {0.1*u:.1f} Q{0.4*u:.1f} {0.2*u:.1f} {0.36*u:.1f} {0.28*u:.1f} Q{0.2*u:.1f} {0.5*u:.1f} {0.0:.1f} {0.48*u:.1f}" fill="{piel}" stroke="{tono(piel,-.18)}" stroke-width="{0.025*u:.1f}"/>')
    # oreja
    s.append(f'<ellipse cx="{-0.08*u:.1f}" cy="{0.02*u:.1f}" rx="{0.08*u:.1f}" ry="{0.13*u:.1f}" fill="{tono(piel,-.06)}"/>')
    # ojo, ceja, boca
    if ojos == "cerrados":
        s.append(f'<path d="M{0.2*u:.1f} {-0.07*u:.1f} q{0.07*u:.1f} {0.05*u:.1f} {0.14*u:.1f} 0" stroke="#2a1a14" stroke-width="{0.03*u:.1f}" fill="none" stroke-linecap="round"/>')
    else:
        s.append(f'<ellipse cx="{0.27*u:.1f}" cy="{-0.08*u:.1f}" rx="{0.045*u:.1f}" ry="{0.055*u:.1f}" fill="#2a1a14"/>')
        s.append(f'<circle cx="{0.285*u:.1f}" cy="{-0.1*u:.1f}" r="{0.014*u:.1f}" fill="#fff" opacity=".8"/>')
    ceja = tono(pelo_color, -.25) if pelo_color else "#3a2a22"
    s.append(f'<path d="M{0.18*u:.1f} {-0.2*u:.1f} q{0.1*u:.1f} {-0.05*u:.1f} {0.2*u:.1f} {0.0:.1f}" stroke="{ceja}" stroke-width="{0.035*u:.1f}" fill="none" stroke-linecap="round"/>')
    s.append(f'<path d="M{0.26*u:.1f} {0.24*u:.1f} q{0.06*u:.1f} {0.02*u:.1f} {0.1*u:.1f} {-0.01*u:.1f}" stroke="{tono(piel,-.3)}" stroke-width="{0.025*u:.1f}" fill="none" stroke-linecap="round"/>')
    s.append(f'<ellipse cx="{0.22*u:.1f}" cy="{0.1*u:.1f}" rx="{0.07*u:.1f}" ry="{0.045*u:.1f}" fill="#e06a5a" opacity=".22"/>')
    # pelo delante
    pc = d.vol(pelo_color, "v", .14) if pelo_color else None
    if pelo in ("moño_blanco", "moño_castaño"):
        s.append(f'<path d="M{-0.42*u:.1f} {0.12*u:.1f} C{-0.48*u:.1f} {-0.45*u:.1f} {0.1*u:.1f} {-0.66*u:.1f} {0.4*u:.1f} {-0.25*u:.1f} C{0.2*u:.1f} {-0.38*u:.1f} {0.0:.1f} {-0.3*u:.1f} {-0.12*u:.1f} {-0.1*u:.1f} C{-0.2*u:.1f} {0.05*u:.1f} {-0.3*u:.1f} {0.12*u:.1f} {-0.42*u:.1f} {0.12*u:.1f}Z" fill="{pc}"/>')
        s.append(f'<path d="M{-0.3*u:.1f} {-0.35*u:.1f} C{-0.1*u:.1f} {-0.5*u:.1f} {0.15*u:.1f} {-0.45*u:.1f} {0.3*u:.1f} {-0.3*u:.1f}" stroke="{tono(pelo_color,.12)}" stroke-width="{0.025*u:.1f}" fill="none" opacity=".8"/>')
    elif pelo == "ondulado":
        s.append(f'<path d="M{-0.45*u:.1f} {0.15*u:.1f} C{-0.6*u:.1f} {-0.5*u:.1f} {0.05*u:.1f} {-0.78*u:.1f} {0.45*u:.1f} {-0.3*u:.1f} C{0.35*u:.1f} {-0.32*u:.1f} {0.28*u:.1f} {-0.22*u:.1f} {0.18*u:.1f} {-0.28*u:.1f} C{0.05*u:.1f} {-0.2*u:.1f} {-0.05*u:.1f} {-0.05*u:.1f} {-0.15*u:.1f} {0.05*u:.1f} C{-0.25*u:.1f} {0.2*u:.1f} {-0.35*u:.1f} {0.25*u:.1f} {-0.45*u:.1f} {0.15*u:.1f}Z" fill="{pc}"/>')
        for k in range(3):
            s.append(f'<path d="M{(-0.35+k*0.18)*u:.1f} {(-0.45+k*0.05)*u:.1f} q{0.08*u:.1f} {0.1*u:.1f} {0.02*u:.1f} {0.22*u:.1f}" stroke="{tono(pelo_color,.15)}" stroke-width="{0.03*u:.1f}" fill="none"/>')
    elif pelo == "corto_flequillo":
        s.append(f'<path d="M{-0.45*u:.1f} {0.2*u:.1f} C{-0.58*u:.1f} {-0.5*u:.1f} {0.1*u:.1f} {-0.75*u:.1f} {0.44*u:.1f} {-0.32*u:.1f} L{0.42*u:.1f} {-0.16*u:.1f} C{0.25*u:.1f} {-0.2*u:.1f} {0.05*u:.1f} {-0.2*u:.1f} {-0.1*u:.1f} {-0.05*u:.1f} L{-0.2*u:.1f} {0.25*u:.1f}Z" fill="{pc}"/>')
    elif pelo == "rapado":
        s.append(f'<path d="M{-0.4*u:.1f} {0.05*u:.1f} C{-0.45*u:.1f} {-0.45*u:.1f} {0.15*u:.1f} {-0.62*u:.1f} {0.38*u:.1f} {-0.28*u:.1f} C{0.1*u:.1f} {-0.42*u:.1f} {-0.2*u:.1f} {-0.3*u:.1f} {-0.4*u:.1f} {0.05*u:.1f}Z" fill="{tono(piel,-.12)}" opacity=".55"/>')
        s.append(f'<ellipse cx="{0.05*u:.1f}" cy="{-0.35*u:.1f}" rx="{0.18*u:.1f}" ry="{0.07*u:.1f}" fill="#fff" opacity=".25"/>')
    elif pelo == "corto_oscuro":
        s.append(f'<path d="M{-0.44*u:.1f} {0.1*u:.1f} C{-0.55*u:.1f} {-0.5*u:.1f} {0.1*u:.1f} {-0.72*u:.1f} {0.42*u:.1f} {-0.3*u:.1f} C{0.2*u:.1f} {-0.35*u:.1f} {-0.05*u:.1f} {-0.28*u:.1f} {-0.18*u:.1f} {0.02*u:.1f}Z" fill="{pc}"/>')
    if barba:
        s.append(f'<path d="M{-0.05*u:.1f} {0.2*u:.1f} Q{0.05*u:.1f} {0.55*u:.1f} {0.3*u:.1f} {0.42*u:.1f} Q{0.42*u:.1f} {0.3*u:.1f} {0.38*u:.1f} {0.2*u:.1f} Q{0.28*u:.1f} {0.32*u:.1f} {0.1*u:.1f} {0.22*u:.1f}Z" fill="{d.vol(barba, "v", .1)}"/>')
    if anteojos:
        s.append(f'<rect x="{0.18*u:.1f}" y="{-0.16*u:.1f}" width="{0.2*u:.1f}" height="{0.14*u:.1f}" rx="{0.03*u:.1f}" fill="#bfe3ff" fill-opacity=".25" stroke="#111" stroke-width="{0.035*u:.1f}"/>')
        s.append(f'<path d="M{0.18*u:.1f} {-0.1*u:.1f} L{-0.05*u:.1f} {-0.05*u:.1f}" stroke="#111" stroke-width="{0.03*u:.1f}"/>')
    return "".join(s)


def persona(d, x, y, alto, pose="pie", mira="der", piel="#d9a47e", pelo="corto_oscuro", pelo_color="#3a2a22",
            torso="#2d4a7a", piernas="#555b66", falda=None, chal=None, barba=None, anteojos=False, bastón=False,
            encorvada=0, ojos="abiertos", brazo="abajo", holograma=False, sombra=True, extra=""):
    """Persona con volumen vista de perfil. (x,y) = pies (de pie) o base del asiento (sentada)."""
    u = alto / 8.0
    s = []
    zap = "#2a1f1a"
    if sombra and not holograma:
        s.append(f'<ellipse cx="{0.1*u:.1f}" cy="0" rx="{(1.6 if pose=="sentada" else 0.9)*u:.1f}" ry="{0.16*u:.1f}" fill="#000" opacity=".35"/>')
    pv = d.vol(piernas, "h", .14)
    tv = d.vol(torso, "h", .16)
    W = 0.56 * u  # grosor de pierna

    def pierna(pts, color, pie_dx=0.28):
        (hx, hy), (kx, ky), (ax, ay) = pts
        out = (f'<path d="M{hx:.1f} {hy:.1f} L{kx:.1f} {ky:.1f} L{ax:.1f} {ay:.1f}" stroke="{color}" stroke-width="{W:.1f}" '
               f'fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
               f'<path d="M{hx+0.1*u:.1f} {hy:.1f} L{kx+0.1*u:.1f} {ky:.1f}" stroke="{tono(piernas,.12)}" stroke-width="{0.07*u:.1f}" '
               f'fill="none" stroke-linecap="round" opacity=".6"/>'
               f'<path d="M{ax-0.18*u:.1f} {ay-0.02*u:.1f} Q{ax-0.15*u:.1f} {ay-0.22*u:.1f} {ax+0.08*u:.1f} {ay-0.2*u:.1f} '
               f'Q{ax+pie_dx*u+0.2*u:.1f} {ay-0.14*u:.1f} {ax+pie_dx*u+0.22*u:.1f} {ay:.1f} Z" fill="{zap}"/>')
        return out

    if pose == "pie":
        cadera = -4.0 * u
        s.append(pierna(((-0.12*u, cadera), (-0.16*u, -2.05*u), (-0.22*u, -0.12*u)), tono(piernas, -.12)))
        s.append(pierna(((0.05*u, cadera), (0.12*u, -2.0*u), (0.06*u, -0.1*u)), pv))
        base_torso = cadera
    elif pose == "arrodillado":
        cadera = -2.35 * u
        # pierna de atrás: rodilla en el suelo, pie hacia atrás
        s.append(pierna(((-0.1*u, cadera), (0.05*u, -0.25*u), (-1.55*u, -0.2*u)), tono(piernas, -.12), pie_dx=-0.5))
        # pierna de adelante: rodilla arriba, pie apoyado
        s.append(pierna(((0.05*u, cadera), (1.25*u, -2.1*u), (1.2*u, -0.12*u)), pv))
        base_torso = cadera
    else:  # sentada
        cadera = -2.15 * u
        s.append(pierna(((-0.1*u, cadera), (1.35*u, cadera+0.05*u), (1.3*u, -0.12*u)), tono(piernas, -.12)))
        s.append(pierna(((0.0, cadera-0.05*u), (1.5*u, cadera), (1.48*u, -0.1*u)), pv))
        base_torso = cadera - 0.1 * u
    # tronco (rotación para encorvar)
    t = []
    top = base_torso - 2.85 * u
    if falda and pose == "pie":
        s.append(f'<path d="M{-0.54*u:.1f} {base_torso-0.2*u:.1f} L{0.5*u:.1f} {base_torso-0.2*u:.1f} L{0.72*u:.1f} {-1.2*u:.1f} Q{0.0:.1f} {-1.05*u:.1f} {-0.72*u:.1f} {-1.2*u:.1f} Z" fill="{d.vol(falda, "h", .14)}"/>')
    elif falda and pose == "sentada":
        s.append(f'<path d="M{-0.45*u:.1f} {base_torso-0.4*u:.1f} L{1.35*u:.1f} {base_torso-0.35*u:.1f} L{1.5*u:.1f} {base_torso+0.7*u:.1f} L{1.0*u:.1f} {base_torso+0.75*u:.1f} L{-0.4*u:.1f} {base_torso+0.3*u:.1f} Z" fill="{d.vol(falda, "h", .14)}"/>')
    t.append(f'<path d="M{-0.56*u:.1f} {top+0.1*u:.1f} Q{-0.1*u:.1f} {top-0.14*u:.1f} {0.42*u:.1f} {top+0.05*u:.1f} Q{0.7*u:.1f} {top+0.6*u:.1f} {0.58*u:.1f} {top+1.3*u:.1f} L{0.5*u:.1f} {base_torso+0.1*u:.1f} L{-0.56*u:.1f} {base_torso+0.1*u:.1f} Q{-0.72*u:.1f} {top+1.2*u:.1f} {-0.46*u:.1f} {top+0.1*u:.1f} Z" fill="{tv}"/>')
    t.append(f'<path d="M{-0.05*u:.1f} {top+0.3*u:.1f} L{-0.02*u:.1f} {base_torso-0.1*u:.1f}" stroke="{tono(torso,-.2)}" stroke-width="{0.03*u:.1f}" opacity=".5"/>')
    if chal:
        t.append(f'<path d="M{-0.66*u:.1f} {top+0.05*u:.1f} Q{0.0:.1f} {top-0.27*u:.1f} {0.55*u:.1f} {top+0.1*u:.1f} L{0.62*u:.1f} {top+1.1*u:.1f} Q{0.0:.1f} {top+1.55*u:.1f} {-0.72*u:.1f} {top+1.2*u:.1f} Z" fill="{d.vol(chal, "h", .14)}"/>')
        for k in range(4):
            t.append(f'<path d="M{(-0.45+k*0.25)*u:.1f} {top+1.2*u:.1f} l0 {0.18*u:.1f}" stroke="{tono(chal,-.1)}" stroke-width="{0.03*u:.1f}"/>')
    # brazo
    hx, hy = 0.0, top + 0.35 * u
    if brazo == "abajo":
        ex, ey, mx, my = 0.08 * u, top + 1.5 * u, 0.3 * u, top + 2.5 * u
    elif brazo == "regazo":
        ex, ey, mx, my = 0.15 * u, top + 1.6 * u, 0.85 * u, top + 2.1 * u
    elif brazo == "adelante":
        ex, ey, mx, my = 0.5 * u, top + 1.2 * u, 1.1 * u, top + 1.0 * u
    elif brazo == "arriba":
        ex, ey, mx, my = 0.45 * u, top - 0.2 * u, 0.75 * u, top - 1.1 * u
    else:  # bastón
        ex, ey, mx, my = 0.25 * u, top + 1.4 * u, 0.6 * u, top + 2.2 * u
    manga = tono(chal or torso, -.06)
    t.append(f'<path d="M{hx:.1f} {hy:.1f} L{ex:.1f} {ey:.1f} L{mx:.1f} {my:.1f}" stroke="{manga}" stroke-width="{0.38*u:.1f}" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
    t.append(f'<path d="M{hx-0.05*u:.1f} {hy:.1f} L{ex-0.05*u:.1f} {ey:.1f}" stroke="{tono(manga,.12)}" stroke-width="{0.06*u:.1f}" fill="none" stroke-linecap="round" opacity=".7"/>')
    t.append(f'<circle cx="{mx:.1f}" cy="{my:.1f}" r="{0.16*u:.1f}" fill="{d.vol(piel, "h", .1)}"/>')
    if bastón:
        t.append(f'<path d="M{mx+0.05*u:.1f} {my:.1f} L{mx+0.35*u:.1f} {-0.05*u:.1f}" stroke="#d7b27a" stroke-width="{0.09*u:.1f}" stroke-linecap="round"/>')
        t.append(f'<path d="M{mx-0.08*u:.1f} {my-0.06*u:.1f} q{0.1*u:.1f} {-0.12*u:.1f} {0.16*u:.1f} {0.05*u:.1f}" stroke="#c49a5e" stroke-width="{0.09*u:.1f}" fill="none" stroke-linecap="round"/>')
    if extra:
        t.append(extra.format(u=u, top=top, mx=mx, my=my))
    t.append(f'<g transform="translate({0.04*u:.1f} {top-0.6*u:.1f})">{_cabeza(d, u, piel, pelo, pelo_color, barba, anteojos, ojos)}</g>')
    giro = f' transform="rotate({encorvada} 0 {base_torso:.1f})"' if encorvada else ""
    s.append(f"<g{giro}>{''.join(t)}</g>")
    flip = " scale(-1 1)" if mira == "izq" else ""
    cuerpo = "".join(s)
    if holograma:
        return (f'<g transform="translate({x:.1f} {y:.1f}){flip}" filter="{holograma}" opacity=".78">'
                f'<g style="mix-blend-mode:screen">{cuerpo}</g></g>')
    return f'<g transform="translate({x:.1f} {y:.1f}){flip}">{cuerpo}</g>'


# ---------------------------------------------------------------- muebles

def sillon(d, x, y, ancho, color="#8a3b2a", mira="der"):
    """Sillón de perfil: (x,y) = base. Respaldo detrás del personaje (dibujar antes)."""
    a = ancho
    flip = " scale(-1 1)" if mira == "izq" else ""
    cv = d.vol(color, "v", .14)
    return (f'<g transform="translate({x:.1f} {y:.1f}){flip}">'
            f'<ellipse cx="{0.15*a:.1f}" cy="0" rx="{0.7*a:.1f}" ry="{0.06*a:.1f}" fill="#000" opacity=".35"/>'
            f'<path d="M{-0.45*a:.1f} {-1.25*a:.1f} Q{-0.5*a:.1f} {-1.4*a:.1f} {-0.3*a:.1f} {-1.38*a:.1f} L{-0.18*a:.1f} {-0.55*a:.1f} L{-0.35*a:.1f} {-0.5*a:.1f} Z" fill="{cv}"/>'
            f'<rect x="{-0.4*a:.1f}" y="{-0.62*a:.1f}" width="{1.1*a:.1f}" height="{0.32*a:.1f}" rx="{0.08*a:.1f}" fill="{cv}"/>'
            f'<rect x="{0.5*a:.1f}" y="{-0.78*a:.1f}" width="{0.22*a:.1f}" height="{0.5*a:.1f}" rx="{0.08*a:.1f}" fill="{d.vol(tono(color,-.05), "h", .12)}"/>'
            f'<path d="M{-0.32*a:.1f} {-0.3*a:.1f} L{-0.36*a:.1f} 0 M{0.62*a:.1f} {-0.3*a:.1f} L{0.66*a:.1f} 0" stroke="#3a2416" stroke-width="{0.05*a:.1f}" stroke-linecap="round"/>'
            f'</g>')


def lampara_pie(d, x, y, alto, encendida=True, gid=""):
    luz = (f'<g id="{gid}"><ellipse cx="0" cy="{-alto+0.1*alto:.1f}" rx="{0.9*alto:.1f}" ry="{0.75*alto:.1f}" '
           f'fill="{d.radial("lampa", [(0, "#ffcf7a", .55), (.5, "#ff9a3d", .18), (1, "#000", 0)])}"/></g>') if encendida else ""
    return (f'<g transform="translate({x:.1f} {y:.1f})">{luz}'
            f'<ellipse cx="0" cy="0" rx="{0.12*alto:.1f}" ry="{0.03*alto:.1f}" fill="#000" opacity=".4"/>'
            f'<path d="M0 0 L0 {-0.85*alto:.1f}" stroke="#2b2520" stroke-width="{0.025*alto:.1f}"/>'
            f'<path d="M{-0.13*alto:.1f} {-0.82*alto:.1f} L{0.13*alto:.1f} {-0.82*alto:.1f} L{0.08*alto:.1f} {-alto:.1f} L{-0.08*alto:.1f} {-alto:.1f} Z" fill="{"#ffd98a" if encendida else "#8a7a60"}"/>'
            f'</g>')


def planta(d, x, y, alto, seed=1):
    r = mulberry32(seed)
    hojas = []
    for i in range(9):
        ang = -90 + (r() - 0.5) * 110
        l = alto * (0.5 + r() * 0.45)
        ex, ey = l * math.cos(math.radians(ang)), l * math.sin(math.radians(ang))
        c = ["#2f8a4a", "#3aa05a", "#246b3a"][i % 3]
        hojas.append(f'<path d="M0 {-0.3*alto:.1f} Q{ex*0.3-12:.1f} {ey*0.6-0.3*alto:.1f} {ex:.1f} {ey-0.25*alto:.1f} Q{ex*0.5+12:.1f} {ey*0.4-0.3*alto:.1f} 0 {-0.3*alto:.1f}Z" fill="{c}"/>')
    return (f'<g transform="translate({x:.1f} {y:.1f})"><ellipse cx="0" cy="0" rx="{0.25*alto:.1f}" ry="{0.05*alto:.1f}" fill="#000" opacity=".35"/>'
            f'{"".join(hojas)}<path d="M{-0.18*alto:.1f} {-0.32*alto:.1f} L{0.18*alto:.1f} {-0.32*alto:.1f} L{0.13*alto:.1f} 0 L{-0.13*alto:.1f} 0Z" fill="{d.vol("#c4643a","h",.15)}"/></g>')


# ---------------------------------------------------------------- sala de cine (marca)

def espectador_espalda(d, x, y, escala=0.56):
    """El Espectador de espaldas, sentado: (x,y) aprox. a la altura del respaldo de su butaca."""
    sud = d.lineal("sud", [(0, "#ffc844", 1), (.35, "#e0a526", 1), (1, "#8a5a0c", 1)])
    sudl = d.lineal("sudl", [(0, "#3a2000", .55), (.35, "#000", 0), (.7, "#000", 0), (1, "#3a2000", .6)], vertical=False)
    pelo = d.radial("pelo", [(0, "#3a2a22", 1), (.6, "#1a110d", 1), (1, "#0b0706", 1)], cy=".3", r=".7")
    piel = d.lineal("pielE", [(0, "#5a3626", 1), (.5, "#b07a5c", 1), (1, "#6a4030", 1)], vertical=False)
    return (f'<g transform="translate({x} {y}) scale({escala})">'
            f'<path d="M-150 220 C-150 120 -120 70 -60 55 L60 55 C120 70 150 120 150 220 Z" fill="{sud}"/>'
            f'<path d="M-150 220 C-150 120 -120 70 -60 55 L60 55 C120 70 150 120 150 220 Z" fill="{sudl}"/>'
            f'<path d="M-78 58 C-86 20 -50 -2 0 -2 C50 -2 86 20 78 58 C60 96 -60 96 -78 58Z" fill="#c98e1c"/>'
            f'<path d="M-62 60 C-50 82 50 82 62 60" stroke="#7a4f08" stroke-width="7" fill="none"/>'
            f'<path d="M-78 58 C-86 20 -50 -2 0 -2" stroke="#ffd877" stroke-width="5" fill="none" opacity=".8"/>'
            f'<path d="M0 82 V220" stroke="#8a5a0c" stroke-width="4" opacity=".6"/>'
            f'<path d="M-30 10 L30 10 L34 -40 L-34 -40Z" fill="{piel}"/>'
            f'<ellipse cx="-58" cy="-78" rx="12" ry="22" fill="#9a664a"/><ellipse cx="58" cy="-78" rx="12" ry="22" fill="#7a4c36"/>'
            f'<ellipse cx="0" cy="-78" rx="58" ry="72" fill="#8a5a44"/><ellipse cx="0" cy="-78" rx="58" ry="72" fill="#2a1a14" opacity=".7"/>'
            f'<path d="M-57 -70 C-62 -165 62 -165 57 -70 C50 -30 30 -12 0 -10 C-30 -12 -50 -30 -57 -70Z" fill="{pelo}"/>'
            f'<path d="M-40 -40 C-20 -22 20 -22 40 -40" stroke="#4a3024" stroke-width="6" fill="none" opacity=".8"/>'
            f'<path d="M-54 -112 C-40 -150 40 -150 54 -112" stroke="#ffb070" stroke-width="4" fill="none" opacity=".7"/>'
            f'<path d="M-120 90 C-80 62 80 62 120 90" stroke="#ffcf7a" stroke-width="5" fill="none" opacity=".55"/>'
            f'</g>')


def butaca(d, x, y, w, h):
    bt = d.lineal("but", [(0, "#e0384f", 1), (.18, "#b3172f", 1), (.7, "#6e0a1c", 1), (1, "#2a0309", 1)])
    bl = d.lineal("butl", [(0, "#000", .45), (.25, "#000", 0), (.75, "#000", 0), (1, "#000", .5)], vertical=False)
    return (f'<g><ellipse cx="{x+w/2:.1f}" cy="{y+h:.1f}" rx="{w*0.6:.1f}" ry="{h*0.08:.1f}" fill="#000" opacity=".5"/>'
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w}" height="{h}" rx="{w*0.22:.1f}" fill="{bt}"/>'
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w}" height="{h}" rx="{w*0.22:.1f}" fill="{bl}"/>'
            f'<path d="M{x+w*0.18:.1f} {y+h*0.06:.1f} Q{x+w/2:.1f} {y-h*0.02:.1f} {x+w*0.82:.1f} {y+h*0.06:.1f}" stroke="#ff8a7a" stroke-width="{max(2, w*0.025):.1f}" fill="none" opacity=".55"/>'
            f'<path d="M{x+w*0.33:.1f} {y+h*0.2:.1f} V{y+h*0.85:.1f} M{x+w*0.67:.1f} {y+h*0.2:.1f} V{y+h*0.85:.1f}" stroke="#3a0410" stroke-width="{max(2, w*0.02):.1f}" opacity=".5"/></g>')


def sala_cine(d, contenido_pantalla, polvo_id="polvo", seed=42, vb="0 980 1080 733"):
    """Sala de cine de la marca (acabado híbrido aprobado). contenido_pantalla: SVG en 908x616."""
    r = mulberry32(seed)
    f = d.filtros()
    muro = d.lineal("muro", [(0, "#1c0d14", 1), (.55, "#2a0f1a", 1), (1, "#0a0508", 1)])
    derr = d.radial("derr", [(0, "#ff7a3d", .5), (.5, "#ff3d6e", .16), (1, "#000", 0)], cy=".3", r=".6")
    haz = d.lineal("haz", [(0, "#fff1d0", .55), (1, "#ffd59a", 0)])
    vin = d.radial("vin", [(.55, "#000", 0), (1, "#000", .75)], cy=".45", r=".75")
    polvo = "".join(
        f'<circle cx="{128 + t * 872 + (128 - t * 48 - 128 - t * 872) * v:.1f}" cy="{82 + t * 170:.1f}" r="{0.8 + r() * 2.2:.1f}" opacity="{0.25 + r() * 0.6:.2f}"/>'
        for t, v in ((r(), r()) for _ in range(90)))
    filas = []
    for k, (fy, w, h, n) in enumerate([(1170, 150, 170, 7), (1350, 210, 240, 5), (1600, 300, 340, 4)]):
        total = n * w + (n - 1) * w * 0.12
        x0 = 540 - total / 2 + (40 if k == 1 else 0)
        for i in range(n):
            filas.append(butaca(d, x0 + i * w * 1.12, fy, w, h))
        if k == 1:
            filas.append(espectador_espalda(d, 815, 1287))
            filas.append(butaca(d, x0 + 3 * w * 1.12, fy, w, h))
    return (f'<rect width="1080" height="1920" fill="{muro}"/>'
            '<g opacity=".9"><path d="M0 0 H70 Q40 600 70 1200 H0 Z" fill="#5a0a1a"/><path d="M1010 0 H1080 V1200 H1010 Q1040 600 1010 0Z" fill="#5a0a1a"/>'
            '<path d="M18 0 Q4 600 22 1200" stroke="#2a0510" stroke-width="10" fill="none"/><path d="M1062 0 Q1076 600 1058 1200" stroke="#2a0510" stroke-width="10" fill="none"/></g>'
            f'<ellipse cx="540" cy="620" rx="760" ry="620" fill="{derr}"/>'
            f'<path d="M128 82 L1000 252 L1000 880 L80 880 L80 252 Z" fill="{haz}" opacity=".4"/>'
            f'<circle cx="128" cy="82" r="26" fill="#fff6dc" filter="{f["brillo"]}"/><circle cx="128" cy="82" r="9" fill="#fff"/>'
            f'<g id="{polvo_id}" fill="#fff3d6">{polvo}</g>'
            '<rect x="74" y="250" width="932" height="640" rx="6" fill="#050304"/>'
            f'<g filter="{f["pintura"]}"><svg x="86" y="262" width="908" height="616" viewBox="{vb}" preserveAspectRatio="xMidYMid slice">{contenido_pantalla}</svg></g>'
            '<rect x="74" y="250" width="932" height="640" rx="6" fill="none" stroke="#000" stroke-opacity=".6" stroke-width="12"/>'
            '<path d="M0 1150 H1080 V1920 H0Z" fill="#0d0609"/>'
            f'<ellipse cx="540" cy="1150" rx="620" ry="70" fill="#ff7a3d" opacity=".10" filter="{f["brillo"]}"/>'
            f'{"".join(filas)}<rect width="1080" height="1920" fill="{vin}"/>')


def sello_svg(gid, x, y, texto, ancho, color="#ff4a4a", tam=70):
    """Sello rotado -8° dentro del SVG (se mueve con la cámara de la escena)."""
    return (f'<g id="{gid}" opacity="0" transform="translate({x} {y}) rotate(-8)">'
            f'<rect x="{-ancho/2}" y="{-tam*0.75}" width="{ancho}" height="{tam*1.25}" fill="#140000" fill-opacity=".3" stroke="{color}" stroke-width="8"/>'
            f'<text x="0" y="{tam*0.32}" text-anchor="middle" font-family="Archivo Black" font-size="{tam}" fill="{color}">{texto}</text></g>')


def espectador_pie(d, x, y, alto):
    """El Espectador de pie, de espaldas (pies en x,y). Mismos colores que en la sala."""
    u = alto / 8.0
    sud = d.lineal("sud", [(0, "#ffc844", 1), (.35, "#e0a526", 1), (1, "#8a5a0c", 1)])
    jean = d.vol("#2a3550", "h", .12)
    pelo = d.radial("pelo", [(0, "#3a2a22", 1), (.6, "#1a110d", 1), (1, "#0b0706", 1)], cy=".3", r=".7")
    return (f'<g transform="translate({x:.1f} {y:.1f})">'
            f'<ellipse cx="0" cy="0" rx="{1.0*u:.1f}" ry="{0.15*u:.1f}" fill="#000" opacity=".35"/>'
            f'<path d="M{-0.55*u:.1f} {-3.9*u:.1f} L{-0.05*u:.1f} {-3.9*u:.1f} L{-0.12*u:.1f} {-0.15*u:.1f} L{-0.5*u:.1f} {-0.15*u:.1f} Z" fill="{jean}"/>'
            f'<path d="M{0.05*u:.1f} {-3.9*u:.1f} L{0.55*u:.1f} {-3.9*u:.1f} L{0.5*u:.1f} {-0.15*u:.1f} L{0.12*u:.1f} {-0.15*u:.1f} Z" fill="{jean}"/>'
            f'<ellipse cx="{-0.32*u:.1f}" cy="{-0.1*u:.1f}" rx="{0.26*u:.1f}" ry="{0.12*u:.1f}" fill="#1a1410"/><ellipse cx="{0.32*u:.1f}" cy="{-0.1*u:.1f}" rx="{0.26*u:.1f}" ry="{0.12*u:.1f}" fill="#1a1410"/>'
            f'<path d="M{-0.95*u:.1f} {-6.4*u:.1f} Q{0.0:.1f} {-6.9*u:.1f} {0.95*u:.1f} {-6.4*u:.1f} L{0.85*u:.1f} {-3.7*u:.1f} L{-0.85*u:.1f} {-3.7*u:.1f} Z" fill="{sud}"/>'
            f'<path d="M{-0.95*u:.1f} {-6.4*u:.1f} L{-1.1*u:.1f} {-4.2*u:.1f} M{0.95*u:.1f} {-6.4*u:.1f} L{1.1*u:.1f} {-4.2*u:.1f}" stroke="#c48a14" stroke-width="{0.34*u:.1f}" stroke-linecap="round"/>'
            f'<path d="M{-0.5*u:.1f} {-6.65*u:.1f} C{-0.55*u:.1f} {-7.1*u:.1f} {0.55*u:.1f} {-7.1*u:.1f} {0.5*u:.1f} {-6.65*u:.1f} C{0.35*u:.1f} {-6.35*u:.1f} {-0.35*u:.1f} {-6.35*u:.1f} {-0.5*u:.1f} {-6.65*u:.1f}Z" fill="#c98e1c"/>'
            f'<path d="M0 {-6.3*u:.1f} V{-3.8*u:.1f}" stroke="#8a5a0c" stroke-width="{0.04*u:.1f}" opacity=".6"/>'
            f'<rect x="{-0.18*u:.1f}" y="{-7.1*u:.1f}" width="{0.36*u:.1f}" height="{0.4*u:.1f}" fill="#7a4c36"/>'
            f'<ellipse cx="0" cy="{-7.55*u:.1f}" rx="{0.42*u:.1f}" ry="{0.52*u:.1f}" fill="#6a4232"/>'
            f'<path d="M{-0.42*u:.1f} {-7.5*u:.1f} C{-0.46*u:.1f} {-8.2*u:.1f} {0.46*u:.1f} {-8.2*u:.1f} {0.42*u:.1f} {-7.5*u:.1f} C{0.36*u:.1f} {-7.2*u:.1f} {-0.36*u:.1f} {-7.2*u:.1f} {-0.42*u:.1f} {-7.5*u:.1f}Z" fill="{pelo}"/>'
            f'<ellipse cx="{-0.43*u:.1f}" cy="{-7.55*u:.1f}" rx="{0.07*u:.1f}" ry="{0.13*u:.1f}" fill="#8a5a44"/><ellipse cx="{0.43*u:.1f}" cy="{-7.55*u:.1f}" rx="{0.07*u:.1f}" ry="{0.13*u:.1f}" fill="#6a4030"/>'
            f'</g>')


def sofa(d, x, y, ancho, color="#3a5a8a"):
    """Sofá de frente (x,y = centro de la base)."""
    a = ancho
    cv = d.vol(color, "v", .14)
    return (f'<g transform="translate({x:.1f} {y:.1f})"><ellipse cx="0" cy="0" rx="{0.55*a:.1f}" ry="{0.04*a:.1f}" fill="#000" opacity=".35"/>'
            f'<rect x="{-0.5*a:.1f}" y="{-0.42*a:.1f}" width="{a:.1f}" height="{0.24*a:.1f}" rx="{0.05*a:.1f}" fill="{d.vol(tono(color,-.08),"v",.1)}"/>'
            f'<rect x="{-0.47*a:.1f}" y="{-0.22*a:.1f}" width="{0.94*a:.1f}" height="{0.12*a:.1f}" rx="{0.03*a:.1f}" fill="{cv}"/>'
            f'<rect x="{-0.56*a:.1f}" y="{-0.3*a:.1f}" width="{0.1*a:.1f}" height="{0.24*a:.1f}" rx="{0.04*a:.1f}" fill="{cv}"/>'
            f'<rect x="{0.46*a:.1f}" y="{-0.3*a:.1f}" width="{0.1*a:.1f}" height="{0.24*a:.1f}" rx="{0.04*a:.1f}" fill="{cv}"/>'
            f'<path d="M{-0.45*a:.1f} {-0.06*a:.1f} V0 M{0.45*a:.1f} {-0.06*a:.1f} V0" stroke="#2a1a10" stroke-width="{0.02*a:.1f}"/></g>')


def mesa(d, x, y, ancho, alto, color="#7a4424"):
    return (f'<g transform="translate({x:.1f} {y:.1f})"><ellipse cx="0" cy="0" rx="{0.55*ancho:.1f}" ry="{0.05*ancho:.1f}" fill="#000" opacity=".3"/>'
            f'<rect x="{-0.5*ancho:.1f}" y="{-alto:.1f}" width="{ancho:.1f}" height="{0.07*alto+6:.1f}" rx="4" fill="{d.vol(color,"v",.15)}"/>'
            f'<path d="M{-0.42*ancho:.1f} {-alto:.1f} V0 M{0.42*ancho:.1f} {-alto:.1f} V0" stroke="{tono(color,-.15)}" stroke-width="{0.03*ancho:.1f}"/></g>')


def lluvia(gid, seed=3, n=120, x0=0, y0=0, w=1080, h=1920, color="#cfe6ff"):
    r = mulberry32(seed)
    return f'<g id="{gid}" stroke="{color}" stroke-width="3" opacity=".7">' + "".join(
        f'<path d="M{x0 + r() * w:.0f} {y0 + r() * h:.0f} l-10 46"/>' for _ in range(n)) + '</g>'


def silla(d, x, y, ancho, color="#6a3a1e", mira="der"):
    """Silla de perfil (x,y = base bajo el asiento). Dibujar antes de la persona sentada."""
    a = ancho
    flip = " scale(-1 1)" if mira == "izq" else ""
    cv = d.vol(color, "v", .15)
    return (f'<g transform="translate({x:.1f} {y:.1f}){flip}"><ellipse cx="{0.25*a:.1f}" cy="0" rx="{0.6*a:.1f}" ry="{0.05*a:.1f}" fill="#000" opacity=".3"/>'
            f'<rect x="{-0.3*a:.1f}" y="{-1.5*a:.1f}" width="{0.1*a:.1f}" height="{1.5*a:.1f}" fill="{cv}"/>'
            f'<rect x="{-0.32*a:.1f}" y="{-0.66*a:.1f}" width="{0.95*a:.1f}" height="{0.1*a:.1f}" rx="{0.03*a:.1f}" fill="{cv}"/>'
            f'<rect x="{0.53*a:.1f}" y="{-0.6*a:.1f}" width="{0.08*a:.1f}" height="{0.6*a:.1f}" fill="{tono(color,-.1)}"/>'
            f'<rect x="{-0.3*a:.1f}" y="{-1.45*a:.1f}" width="{0.1*a:.1f}" height="{0.5*a:.1f}" fill="{tono(color,.1)}"/></g>')
