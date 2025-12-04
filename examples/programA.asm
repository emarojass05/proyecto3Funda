# Programa A — Aritmética y Forwarding
# ------------------------------------

ADDI x1, x0, 5          # x1 = 5
ADDI x2, x0, 10         # x2 = 10
ADD  x3, x1, x2         # x3 = 15
SUB  x4, x3, x1         # x4 = 10  (usa resultado previo de x3)
AND  x5, x3, x4         # x5 = 15 AND 10 = 10
OR   x6, x5, x1         # x6 = 10 OR 5 = 15
ADDI x7, x6, -5         # x7 = 10
HALT
