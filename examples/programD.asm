# Programa D — Integración completa
# ---------------------------------

ADDI x1, x0, 3          # N = 3
ADDI x2, x0, 0          # base = 0
ADDI x3, x0, 1          # val1 = 1
ADDI x4, x0, 2          # val2 = 2
ADDI x5, x0, 3          # val3 = 3

SW   x3, 0(x2)          # Mem[0] = 1
SW   x4, 4(x2)          # Mem[4] = 2
SW   x5, 8(x2)          # Mem[8] = 3

ADDI x6, x0, 0          # suma = 0
ADDI x7, x0, 0          # índice = 0

loop:
LW   x8, 0(x7)          # carga Mem[x7]
ADD  x6, x6, x8         # acumula suma += valor
ADDI x7, x7, 4          # avanza puntero
ADDI x1, x1, -1         # decrementa N
BNE  x1, x0, loop       # repite mientras N != 0

SW   x6, 12(x2)         # guarda suma (6)
HALT
