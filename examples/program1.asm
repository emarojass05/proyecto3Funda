# Programa ejemplo RISC-V pipeline
ADD x1, x0, x0      # x1 = 0
ADD x2, x1, x1      # x2 = 0 + 0
SUB x3, x2, x1      # x3 = x2 - x1
AND x4, x3, x1      # x4 = x3 & x1
OR  x5, x3, x2      # x5 = x3 | x2
SW  x5, 10(x0)      # Mem[10] = x5
LW  x6, 10(x0)      # x6 = Mem[10]
HALT                # detener simulación
