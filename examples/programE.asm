# Programa E — Saltos condicionales múltiples
# ------------------------------------------

ADDI x1, x0, 5
ADDI x2, x0, 2
ADDI x3, x0, 0

loop:
BEQ x1, x0, end         # si contador = 0, salir
ADD x3, x3, x2          # suma += 2
ADDI x1, x1, -1
JAL x0, loop

end:
SW x3, 0(x0)            # guarda suma final (10)
HALT
