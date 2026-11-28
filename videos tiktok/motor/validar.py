#!/usr/bin/env python3
"""Valida un video o una carpeta de fotogramas contra ESTILO.md (look, quietud, duración).

Uso:
  python3 -I "videos tiktok/motor/validar.py" video.mp4
  python3 -I "videos tiktok/motor/validar.py" carpeta_con_png/

Revisa:
  - Look por fotograma (1 por segundo): saturación media, luminosidad y contraste dentro de rango.
  - Quietud: ningún tramo de más de 3 s sin cambio visible (solo video).
  - Duración: 61 s mínimo, objetivo 70 a 90 s (solo video).
Sale con código 1 si algo falla. La revisión visual de §7.1 (forma humana, escala,
textos que tapan sujetos) la hace Claude mirando la hoja de contacto: este script no la reemplaza.
"""
import colorsys
import pathlib
import subprocess
import sys
import tempfile

from PIL import Image, ImageChops, ImageStat

# Rangos de ESTILO.md §7.1 (actualizar aquí si cambia el estilo)
SAT_MIN, SAT_MAX = 0.40, 0.75
CONTRASTE_MIN = 40.0
LUMA_MIN, LUMA_MAX = 45.0, 170.0
QUIETO_MAX_S = 3.0
UMBRAL_CAMBIO = 2.0  # diferencia media de píxeles (0-255) por cuadro a 6 fps; bajo esto la imagen se percibe quieta (ref01: 0,5-1,6 en el cierre)
DUR_MIN, DUR_OBJ = 61.0, (70.0, 90.0)


def look(im):
    im = im.convert("RGB").resize((180, 320))
    px = im.get_flattened_data() if hasattr(im, "get_flattened_data") else im.getdata()
    px = list(px)
    sat = sum(colorsys.rgb_to_hsv(*(c / 255 for c in p))[1] for p in px) / len(px)
    st = ImageStat.Stat(im.convert("L"))
    return sat, st.mean[0], st.stddev[0]


def fotogramas_de_video(video, fps, carpeta):
    subprocess.run(["ffmpeg", "-v", "error", "-i", str(video), "-vf", f"fps={fps},scale=180:320",
                    str(carpeta / "f%05d.png")], check=True)
    return sorted(carpeta.glob("f*.png"))


def duracion(video):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                          str(video)], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    ruta = pathlib.Path(sys.argv[1])
    fallas = []
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        if ruta.is_dir():
            cuadros, es_video = sorted(ruta.glob("*.png")), False
        else:
            es_video = True
            d = duracion(ruta)
            print(f"Duración: {d:.1f} s")
            if d < DUR_MIN:
                fallas.append(f"dura {d:.1f} s, menos de {DUR_MIN:.0f} s")
            elif not DUR_OBJ[0] <= d <= DUR_OBJ[1]:
                print(f"  aviso: fuera del objetivo {DUR_OBJ[0]:.0f}-{DUR_OBJ[1]:.0f} s")
            cuadros = fotogramas_de_video(ruta, 1, tmp / "1fps" if (tmp / "1fps").mkdir() is None else tmp)
        for i, c in enumerate(cuadros):
            sat, luma, con = look(Image.open(c))
            malo = []
            if not SAT_MIN <= sat <= SAT_MAX:
                malo.append(f"saturación {sat:.2f}")
            if con < CONTRASTE_MIN:
                malo.append(f"contraste {con:.0f}")
            if not LUMA_MIN <= luma <= LUMA_MAX:
                malo.append(f"luminosidad {luma:.0f}")
            etiqueta = f"{i}s" if es_video else c.name
            if malo:
                fallas.append(f"{etiqueta}: " + ", ".join(malo))
        if es_video:
            fps = 6
            cuadros = fotogramas_de_video(ruta, fps, tmp / "q" if (tmp / "q").mkdir() is None else tmp)
            quieto, prev = 0, None
            for i, c in enumerate(cuadros):
                im = Image.open(c).convert("L")
                if prev is not None:
                    dif = ImageStat.Stat(ImageChops.difference(im, prev)).mean[0]
                    quieto = quieto + 1 if dif < UMBRAL_CAMBIO else 0
                    if quieto / fps > QUIETO_MAX_S and quieto % fps == 0:
                        fallas.append(f"{i / fps:.1f}s: imagen quieta más de {QUIETO_MAX_S:.0f} s")
                prev = im
    if fallas:
        print("FALLAS:")
        for f in fallas:
            print("  -", f)
        sys.exit(1)
    print("OK: look, quietud y duración dentro del estilo.")


if __name__ == "__main__":
    main()
