# Programa 2 — Evitar stall de load-use con NOP/reordenamiento
ADD x1, x0, x0          # x1 = 0
ADD x2, x1, x1          # Cadena ALU (forwarding EX->ID)
ADD x3, x2, x1
SW  x3, 12(x0)          # Mem[12] = x3
LW  x4, 12(x0)          # x4 = Mem[12]
ADD x0, x0, x0          # NOP (burbuja intencional para romper el load-use)
ADD x5, x4, x3          # Consumidor de LW después del NOP → sin stall
AND x6, x5, x4
OR  x7, x6, x5
HALT
