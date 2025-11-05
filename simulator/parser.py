# ===========================================================
# parser.py — Carga y parsing de programas RISC-V (ASM)
# ===========================================================

class Instruction:
    def __init__(self, text):
        self.text = text.strip()
        self.opcode = None
        self.args = []
        self.rd = None
        self.rs1 = None
        self.rs2 = None
        self.imm = None
        self.parse_line(text)

    def parse_line(self, text):
        # eliminar comentarios
        line = text.split('#')[0].strip()
        if not line:
            return

        # separar opcode y argumentos
        parts = line.replace(',', '').split()
        if len(parts) == 0:
            return

        self.opcode = parts[0].upper()
        self.args = parts[1:]

        # decodificar campos según tipo
        if self.opcode in ["ADD", "SUB", "AND", "OR"]:
            # formato R: op rd, rs1, rs2
            if len(self.args) == 3:
                self.rd, self.rs1, self.rs2 = self.args
        elif self.opcode in ["LW"]:
            # formato I: op rd, offset(base)
            if len(self.args) == 2:
                self.rd = self.args[0]
                offset, base = self.args[1].split('(')
                self.imm = int(offset)
                self.rs1 = base.replace(')', '')
        elif self.opcode in ["SW"]:
            # formato S: op rs2, offset(base)
            if len(self.args) == 2:
                self.rs2 = self.args[0]
                offset, base = self.args[1].split('(')
                self.imm = int(offset)
                self.rs1 = base.replace(')', '')
        elif self.opcode == "HALT":
            pass

    def __repr__(self):
        return f"{self.opcode} {' '.join(self.args)}"


# ===========================================================
# Función para cargar un programa desde archivo .asm
# ===========================================================

def load_program(filename):
    program = []
    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                instr = Instruction(line)
                if instr.opcode:
                    program.append(instr)
    return program
