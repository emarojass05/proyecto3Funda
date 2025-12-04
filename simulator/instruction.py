# instruction.py
class Instruction:
    def __init__(self, text):
        self.raw = text.strip()
        self.op, *args = self.raw.replace(",", "").split()
        self.args = args

    def __repr__(self):
        return f"{self.op} {' '.join(self.args)}"

    def rd(self):
        if len(self.args) > 0 and self.args[0].startswith("x"):
            return int(self.args[0][1:])
        return None

    def rs1(self):
        if len(self.args) > 1 and self.args[1].startswith("x"):
            return int(self.args[1][1:])
        return None

    def rs2(self):
        if len(self.args) > 2 and self.args[2].startswith("x"):
            return int(self.args[2][1:])
        return None
