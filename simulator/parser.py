# ===========================================================
# parser.py — Carga y parsing de programas RISC-V (ASM)
# ===========================================================

class Instruction:
    def __init__(self, text):
        self.raw = text.strip()
        self.opcode = None
        self.rd = None
        self.rs1 = None
        self.rs2 = None
        self.imm = None
        self.parse_line(text)

    def parse_line(self, text):
        # Eliminar comentarios y espacios extra
        line = text.split("#")[0].strip()
        if not line:
            return

        # Reemplazar comas y limpiar
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
        # Formatos I (ADDI, ANDI, ORI)
        # =======================================================
        elif self.opcode in ["ADDI", "ANDI", "ORI"]:
            if len(args) == 3:
                self.rd, self.rs1, imm = args
                try:
                    self.imm = int(imm, 0)
                except ValueError:
                    print(f"[WARN] Inmediato inválido en {self.opcode}: '{imm}' → 0")
                    self.imm = 0
            else:
                print(f"[DEBUG] {self.opcode} tiene argumentos inesperados: {args}")

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

        elif self.opcode == "HALT":
            pass
        else:
            print(f"[WARN] Instrucción desconocida: {line}")

        # Mostrar depuración
        print(f"[DEBUG] Parsed: {self.opcode} → rd={self.rd}, rs1={self.rs1}, rs2={self.rs2}, imm={self.imm}")

    def __repr__(self):
        return f"{self.opcode} {self.rd or ''} {self.rs1 or ''} {self.rs2 or ''} {self.imm or ''}"


def load_program(filename):
    program = []
    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                instr = Instruction(line)
                if instr.opcode:
                    program.append(instr)
    print(f"[INFO] {len(program)} instrucciones cargadas.")
    return program
