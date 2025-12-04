# Programa 4 — Prueba de predicción de saltos

ADD x1, x0, x0      # x1 = 0
ADD x2, x0, 5       # x2 = 5
ADD x3, x0, 0       # x3 = 0

LOOP:               # etiqueta para salto
ADD x3, x3, 1       # x3++
BNE x3, x2, LOOP    # si x3 != x2, salta a LOOP
HALT
