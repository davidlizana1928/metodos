#!/usr/bin/env python3
"""Genera fondos en pintura digital (SD-Turbo, local, sin GPU) y, si se pide, capas recortadas.

Uso:
  /root/sd/bin/python -I "videos tiktok/motor/fondos.py" fondos.json carpeta_salida [--solo id1,id2]

fondos.json: [{"id": "living_dia", "prompt": "...", "seed": 7, "recorte": false}, ...]
  - Se genera en cuadrado (768x768 por defecto, "lado") porque SD-Turbo duplica la arquitectura en formatos altos;
    luego se recorta la franja vertical 9:16 ("centro_x" 0..1 elige dónde) y se escala a 1080x1920.
    El fondo queda algo suave: funciona como desenfoque de profundidad detrás de los personajes nítidos.
  - "recorte": true agrega <id>_frente.png con el sujeto principal recortado (rembg, isnet-general-use),
    para moverlo como capa delantera (parallax).
  - "variantes": n genera n semillas (id_s0, id_s1…) para elegir la mejor.
Requisitos: entorno /root/sd (torch, diffusers, rembg). Descargas de Hugging Face con HF_HUB_DISABLE_XET=1.
Licencia: SD-Turbo exige aceptar la Stability AI Community License para uso comercial (gratis bajo 1 M USD/año).
"""
import json
import os
import pathlib
import sys
import time

os.environ.setdefault("HF_HUB_DISABLE_XET", "1")

ESTILO = ("cinematic digital painting, realistic light, vivid colors, detailed, depth of field, "
          "eye-level, empty floor in lower third")
# CLIP solo lee 77 tokens: «sin personas» va al principio del prompt, no al final.
PREFIJO = "empty scene, no people, no text"


def main():
    args = sys.argv[1:]
    if len(args) < 2:
        sys.exit(__doc__)
    lista = json.load(open(args[0], encoding="utf-8"))
    salida = pathlib.Path(args[1])
    salida.mkdir(parents=True, exist_ok=True)
    solo = set(args[args.index("--solo") + 1].split(",")) if "--solo" in args else None

    import torch
    from diffusers import AutoPipelineForText2Image
    from PIL import Image, ImageFilter
    torch.set_num_threads(os.cpu_count() or 4)
    pipe = AutoPipelineForText2Image.from_pretrained("stabilityai/sd-turbo", torch_dtype=torch.float32)
    pipe.set_progress_bar_config(disable=True)
    sesion = None

    for f in lista:
        if solo and f["id"] not in solo:
            continue
        for v in range(f.get("variantes", 1)):
            nombre = f["id"] if f.get("variantes", 1) == 1 else f"{f['id']}_s{v}"
            t = time.time()
            g = torch.Generator().manual_seed(f.get("seed", 7) + v)
            lado = f.get("lado", 768)
            im = pipe(prompt=f"{PREFIJO}, {f['prompt']}, {ESTILO}", num_inference_steps=f.get("pasos", 2), guidance_scale=0.0,
                      width=lado, height=lado, generator=g).images[0]
            im.save(salida / f"{nombre}_cuadrado.png")
            # recorte vertical 9:16 centrado (o desplazado con "centro_x" 0..1) y escalado a 1080x1920
            ancho = round(lado * 9 / 16)
            cx = f.get("centro_x", 0.5)
            x0 = min(max(0, round(cx * lado - ancho / 2)), lado - ancho)
            im = im.crop((x0, 0, x0 + ancho, lado)).resize((1080, 1920), Image.LANCZOS)
            im = im.filter(ImageFilter.UnsharpMask(radius=3, percent=70, threshold=2))
            im.save(salida / f"{nombre}.png")
            if f.get("recorte"):
                from rembg import new_session, remove
                sesion = sesion or new_session("isnet-general-use")
                remove(im, session=sesion).save(salida / f"{nombre}_frente.png")
            print(f"{nombre}: {time.time() - t:.0f} s")


if __name__ == "__main__":
    main()
