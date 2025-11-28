
# -----------------------------------------------
# Sección 1 — Prueba básica ALU (sin riesgos)
# -----------------------------------------------
ADDI x1, x0, 5       # x1 = 5
ADDI x2, x0, 10      # x2 = 10
ADD  x3, x1, x2      # x3 = 15
SUB  x4, x2, x1      # x4 = 5
AND  x5, x3, x4      # x5 = 5
OR   x6, x3, x4      # x6 = 15

# -----------------------------------------------
# Sección 2 — Prueba de riesgos de datos (RAW)
# Estas instrucciones dependen inmediatamente de las previas
# -----------------------------------------------
ADDI x7, x6, 2       # x7 = x6 + 2   → depende de OR
ADD  x8, x7, x1      # x8 = x7 + x1  → depende de x7
SUB  x9, x8, x2      # x9 = x8 - x2  → depende de x8
AND  x10, x9, x3     # x10 = x9 & x3 → depende de x9
OR   x11, x10, x4    # x11 = x10 | x4 → depende de x10

# -----------------------------------------------
# Sección 3 — Prueba de acceso a memoria
# -----------------------------------------------
SW   x11, 0(x0)      # Guarda x11 en Mem[0]
LW   x12, 0(x0)      # Carga x12 = Mem[0]

# -----------------------------------------------
# Sección 4 — Prueba de saltos condicionales
# Debe activar predicción si está habilitada
# -----------------------------------------------
ADDI x13, x0, 5
ADDI x14, x0, 5
BEQ  x13, x14, etiqueta_igual     # Debe cumplirse (salto tomado)
ADDI x15, x0, 99                  # Debe saltarse si predicción correcta
JAL  x0, etiqueta_fin

etiqueta_igual:
ADDI x15, x0, 42
