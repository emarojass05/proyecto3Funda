# Programa F — Test de memoria extendida
# --------------------------------------

ADDI x1, x0, 0          # base = 0
ADDI x2, x0, 10         # valor inicial = 10
ADDI x3, x0, 5          # cantidad = 5

store_loop:
SW   x2, 0(x1)
ADDI x1, x1, 4
ADDI x2, x2, 1
ADDI x3, x3, -1
BNE  x3, x0, store_loop

HALT
