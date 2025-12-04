# ===========================================================
# parser.py — Carga y parsing de programas RISC-V (ASM) con soporte de etiquetas
# ===========================================================

class Instruction:
    def __init__(self, text):
        self.raw = text.strip()
        self.opcode = None
        self.rd = None
        self.rs1 = None
        self.rs2 = None
        self.imm = None
        self.label = None
        self.parse_line(text)

    # -----------------------------------------------------------
    # Función principal de parsing
    # -----------------------------------------------------------
    def parse_line(self, text):
        # Quitar comentarios
        line = text.split("#")[0].strip()
        if not line:
            return

        # Si es una etiqueta (termina con :)
        if line.endswith(":"):
            self.opcode = line  # se guarda tal cual para que el CPU la reconozca
            return

        # Reemplazar comas por espacios y limpiar
        line = line.replace(",", " ")
        parts = [p for p in line.split() if p.strip()]
        if len(parts) == 0:
            return

        self.opcode = parts[0].upper()
        args = parts[1:]

        # =======================================================
        # Formatos R (ADD, SUB, AND, OR)
        # =======================================================
        if self.opcode in ["ADD", "SUB", "AND", "OR"]:
            if len(args) == 3:
                self.rd, self.rs1, self.rs2 = args

        # =======================================================
        # Formato I (ADDI, ANDI, ORI)
        # =======================================================
        elif self.opcode in ["ADDI", "ANDI", "ORI"]:
            if len(args) == 3:
                self.rd, self.rs1, imm = args
                try:
                    self.imm = int(imm, 0)
                except ValueError:
                    print(f"[WARN] Inmediato inválido en {self.opcode}: '{imm}' -> 0")
                    self.imm = 0

        # =======================================================
        # LW rd, offset(base)
        # =======================================================
        elif self.opcode == "LW":
            if len(args) == 2 and "(" in args[1]:
                self.rd = args[0]
                offset, base = args[1].split("(")
                self.imm = int(offset)
                self.rs1 = base.replace(")", "")

        # =======================================================
        # SW rs2, offset(base)
        # =======================================================
        elif self.opcode == "SW":
            if len(args) == 2 and "(" in args[1]:
                self.rs2 = args[0]
                offset, base = args[1].split("(")
                self.imm = int(offset)
                self.rs1 = base.replace(")", "")

        # =======================================================
        # Instrucciones de salto / control de flujo
        # =======================================================
        elif self.opcode in ["BEQ", "BNE"]:
            # BEQ rs1, rs2, label
            if len(args) == 3:
                self.rs1, self.rs2, self.label = args
        elif self.opcode == "JAL":
            # JAL rd, label
            if len(args) == 2:
                self.rd, self.label = args
        elif self.opcode == "JALR":
            # JALR rd, rs1, imm
            if len(args) == 3:
                self.rd, self.rs1, imm = args
                try:
                    self.imm = int(imm, 0)
                except ValueError:
                    self.imm = 0

        # =======================================================
        # NOP / HALT
        # =======================================================
        elif self.opcode in ["NOP", "HALT"]:
            pass

        else:
            print(f"[WARN] Instrucción desconocida: {line}")

        # Depuración opcional
        print(f"[DEBUG] Parsed: {self.opcode} -> rd={self.rd}, rs1={self.rs1}, rs2={self.rs2}, imm={self.imm}, label={self.label}")

    # -----------------------------------------------------------
    # Representación legible
    # -----------------------------------------------------------
    def __repr__(self):
        parts = [p for p in [self.rd, self.rs1, self.rs2, self.imm, self.label] if p]
        return f"{self.opcode} {' '.join(map(str, parts))}"


# ===========================================================
# Función de carga de programa desde archivo
# ===========================================================
def load_program(filename):
    program = []
    pending_label = None  # etiqueta detectada pendiente de asignar

    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # Si la línea es una etiqueta
            if line.endswith(":"):
                pending_label = line[:-1]  # guardar sin los dos puntos
                continue

            # Parsear instrucción normal
            instr = Instruction(line)
            if pending_label:
                instr.label = pending_label  # asignar etiqueta previa
                pending_label = None
            if instr.opcode:
                program.append(instr)

    print(f"[INFO] {len(program)} instrucciones cargadas desde {filename}.")
    return program
