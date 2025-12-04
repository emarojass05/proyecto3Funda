# ============================================================
# program3.asm — Programa completo de prueba del simulador RISC-V
# ============================================================

# --- Inicialización ---
ADDI x1, x0, 5        # x1 = 5
ADDI x2, x0, 10       # x2 = 10

# --- Operaciones básicas ---
ADD  x3, x1, x2       # x3 = 15
SUB  x4, x2, x1       # x4 = 5
AND  x5, x3, x4       # x5 = 5
OR   x6, x3, x4       # x6 = 15

# --- Memoria ---
SW   x6, 0(x0)        # Mem[0] = 15
LW   x7, 0(x0)        # x7 = 15

# --- Operaciones inmediatas ---
ADDI x8, x7, 3        # x8 = 18
ANDI x9, x8, 7        # x9 = 2
ORI  x10, x9, 4       # x10 = 6

# --- NOP para sincronización ---
NOP

# --- Saltos condicionales y control de flujo ---
BEQ  x1, x4, equal_lbl    # si x1 == x4 → ir a equal_lbl
BNE  x1, x2, noteq_lbl    # si x1 != x2 → ir a noteq_lbl
JAL  x11, end_lbl         # salto incondicional a end_lbl

# ============================================================
# Bloque de etiquetas
# ============================================================

equal_lbl:
    ADDI x12, x0, 111     # x12 = 111
    JALR x13, x12, 2      # salto indirecto

noteq_lbl:
    ADDI x14, x0, 222     # x14 = 222
    BEQ  x0, x0, done     # salto incondicional a done

end_lbl:
    ADDI x15, x0, 333     # x15 = 333
    NOP

done:
    HALT
