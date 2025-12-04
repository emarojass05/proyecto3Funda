# Programa 1 — Forwarding y hazard load-use
ADD x1, x0, x0          # x1 = 0   (semilla para la cadena)
ADD x2, x1, x1          # RAW: x2 depende de x1 (forwarding EX->ID)
ADD x3, x2, x1          # RAW doble: usa x2 recién escrito
OR  x4, x3, x2          # RAW: x4 depende de x3 y x2
AND x5, x4, x3          # RAW: x5 depende de x4 y x3
SW  x5, 10(x0)          # Mem[10] = x5
LW  x6, 10(x0)          # x6 = Mem[10]
ADD x7, x6, x5          # Hazard load-use inmediato (LW -> ADD)
HALT                    # detener simulación
