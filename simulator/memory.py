# memory.py
class Memory:
    def __init__(self, size=1024):
        self.size = size
        self.mem = [0] * size

    def load(self, addr):
        if 0 <= addr < self.size:
            return self.mem[addr]
        else:
            raise IndexError(f"Memory load out of bounds: {addr}")

    def store(self, addr, value):
        if isinstance(value, (int, float)):
            self.mem[addr] = value
        else:
            self.mem[addr] = value


    def dump(self, start=0, end=16):
        print("Memory[{}..{}]:".format(start, min(end, self.size - 1)))
        for a in range(start, min(end, self.size)):
            print(f"{a:04}: {self.mem[a]}")

# ======================================================
# Banco de registros
# ======================================================
class RegisterFile:
    def __init__(self):
        self.regs = [0] * 32

    def read(self, idx):
        if idx is None:
            return 0
        if idx == 0:
            return 0
        return self.regs[idx]

    def write(self, idx, value):
        if idx is None or idx == 0:
            return
        self.regs[idx] = int(value)

    def dump(self, cols=8):
        for r in range(0, 32, cols):
            line = []
            for i in range(r, min(r + cols, 32)):
                line.append(f"x{i:02}={self.regs[i]:>8}")
            print("  ".join(line))
