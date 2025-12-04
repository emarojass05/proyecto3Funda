# Programa C — Bucle de conteo (branch prediction)
# ------------------------------------------------

ADDI x1, x0, 5          # contador = 5
ADDI x2, x0, 0          # suma = 0

loop:
ADD  x2, x2, x1         # suma += contador
ADDI x1, x1, -1         # contador--
BNE  x1, x0, loop       # mientras x1 != 0, repetir

SW   x2, 0(x0)          # guarda resultado (15)
HALT
