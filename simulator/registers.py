class RegisterFile:
    def __init__(self):
        self.regs = [0] * 32  # 32 registros RISC-V

    def read(self, idx):
        if isinstance(idx, str) and idx.startswith("x"):
            idx = int(idx[1:])
        return self.regs[idx]

    def write(self, idx, value):
        if isinstance(idx, str) and idx.startswith("x"):
            idx = int(idx[1:])
        if idx != 0:  # x0 siempre es 0
            self.regs[idx] = value

    # =======================================================
    # Imprime el estado de los registros
    # =======================================================
    def dump(self):
        print("\nRegistros:")
        for i in range(0, 32, 8):
            fila = " ".join([f"x{i+j:02}={self.regs[i+j]:8}" for j in range(8)])
            print(fila)
