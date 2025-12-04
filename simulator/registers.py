# ===========================================================
# registers.py — Banco de registros RISC-V
# ===========================================================

from simulator.utils import reg_index

class RegisterFile:
    def __init__(self):
        self.regs = [0] * 32  # 32 registros de propósito general

    def read(self, idx):
        if idx is None:
            return 0
        idx = reg_index(idx)
        if idx == 0 or idx is None:
            return 0
        return self.regs[idx]

    def write(self, idx, value):
        idx = reg_index(idx)
        if idx is None or idx == 0:
            return
        self.regs[idx] = int(value)

    def dump(self):
        print("\nRegistros:")
        for i in range(0, 32, 8):
            fila = " ".join([f"x{i+j:02}={self.regs[i+j]:8}" for j in range(8)])
            print(fila)
