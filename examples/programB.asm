# Programa B — Memoria y load-use
# -------------------------------

ADDI x1, x0, 4          # x1 = 4 (base de memoria)
ADDI x2, x0, 100        # x2 = 100
SW   x2, 0(x1)          # Mem[4] = 100
LW   x3, 0(x1)          # x3 = Mem[4] = 100
ADD  x4, x3, x2         # x4 = 200 (load-use hazard)
SW   x4, 4(x1)          # Mem[8] = 200
HALT
