"""Escala y proporciones del video.

Regla: todo objeto se dibuja con medidas reales en metros, proyectadas con la misma
perspectiva de la camara. Nunca se elige un tamano en pixeles "a ojo".

Referencia de camara (lienzo 720x1280):
  - La linea de horizonte esta en HZ_Y.
  - Una persona adulta de 1,75 m con los pies en Y_REF mide PPM_REF * 1,75 pixeles.
  - Para cualquier otro objeto apoyado en el suelo, px/m = PPM_REF * (y - HZ_Y) / (Y_REF - HZ_Y).
"""

# ---- dimensiones reales (metros) ----
PERSONA_ALTO = 1.75
PERSONA_HOMBROS = 0.45        # ancho de hombros de un adulto
AUTO_ALTO = 1.45              # auto pequeno de reparto
AUTO_ANCHO = 1.75             # visto de atras
AUTO_LARGO = 4.3
PATRULLA_ALTO = 1.5
PATRULLA_ANCHO = 1.8
CAMIONETA_ALTO = 1.9          # camioneta negra
CAMIONETA_ANCHO = 1.95
BUTACA_ANCHO = 0.55
BUTACA_ALTO_RESPALDO = 0.95
CAJA_ANCHO = 0.50             # caja termica
CAJA_ALTO = 0.30
MOSTRADOR_ALTO = 1.00
BUZON_ALTO = 1.10
PANTALLA_ANCHO = 12.0         # pantalla de cine
MUJER_ALTO = 1.65
CASA_ANCHO = 8.0
CASA_ALTO_PARED = 3.0

# ---- camara ----
HZ_Y = 600                    # horizonte
Y_REF = 1180                  # pies de la persona de referencia
PPM_REF = 620 / PERSONA_ALTO  # 354 px/m en Y_REF
PANTALLA_PX = 640             # ancho de la pantalla de cine dentro del cuadro (ocupa casi todo el ancho)


def ppm(y):
    """Pixeles por metro para un objeto con los pies en la linea y."""
    return PPM_REF * (y - HZ_Y) / (Y_REF - HZ_Y)


def altura(y, metros=PERSONA_ALTO):
    """Altura en pixeles de algo de `metros` de alto apoyado en y."""
    return metros * ppm(y)


def ancho(y, metros):
    return metros * ppm(y)


def comparar(nombre, px_a, px_b, esperado, tol=0.25):
    """Compara la proporcion px_a / px_b con la proporcion real `esperado` (± tol relativa).
    Imprime el resultado y devuelve True si cae dentro de la tolerancia."""
    r = px_a / px_b
    ok = abs(r - esperado) <= tol * esperado
    print(f"{'OK ' if ok else 'MAL'} {nombre}: {r:.2f} (esperado {esperado:.2f})")
    return ok


def chequeo():
    """Verifica las proporciones clave del guion. Ejecutar: python3 escala.py"""
    r = []
    # auto de reparto de atras vs persona, a la misma profundidad
    r.append(comparar("auto alto / persona alta (mismo plano)", AUTO_ALTO, PERSONA_ALTO, AUTO_ALTO / PERSONA_ALTO))
    # butaca vs hombros de quien esta sentado
    r.append(comparar("hombros / butaca (misma fila)", PERSONA_HOMBROS, BUTACA_ANCHO, PERSONA_HOMBROS / BUTACA_ANCHO))
    # pantalla vs butaca: 12 m de pantalla = ~22 butacas a igual distancia; la pantalla esta
    # a unas 5 veces la distancia de la fila del espectador, asi que se ve ~4,5 butacas de ancho.
    FACTOR_DISTANCIA = 5.0
    r.append(comparar("pantalla / butaca en la imagen (fila 1000)", PANTALLA_PX,
                      ancho(1000, BUTACA_ANCHO), PANTALLA_ANCHO / BUTACA_ANCHO / FACTOR_DISTANCIA, tol=0.1))
    return all(r)


if __name__ == "__main__":
    print("chequeo de escala:", "OK" if chequeo() else "REVISAR")
