# ===========================================================
# cpu.py — Simulador RISC-V Pipelined (con manejo de HALT)
# ===========================================================
from simulator.memory import Memory
from simulator.registers import RegisterFile
from simulator.hazards import HazardUnit

class CPU:
    def __init__(self, program):
        self.regs = RegisterFile()
        self.memory = Memory()
        self.hazard_unit = HazardUnit()
        self.pipeline = {"IF": None, "ID": None, "EX": None, "MEM": None, "WB": None}
        self.pc = 0
        self.clock = 0
        self.halted = False  

        # Cargar programa en memoria
        for i, instr in enumerate(program):
            self.memory.store(i, instr)

    # =======================================================
    # Etapa de ejecución (EX)
    # =======================================================
    def execute_stage(self, instr):
        if instr is None:
            return None

        opcode = instr.opcode
        rd = instr.rd
        rs1 = instr.rs1
        rs2 = instr.rs2

        # Aplicar forwarding si es necesario
        rs1_val, rs2_val = self.hazard_unit.apply_forwarding(self, instr)

        # Operaciones básicas
        if opcode == "ADD":
            return ("WB", rd, rs1_val + rs2_val)
        elif opcode == "SUB":
            return ("WB", rd, rs1_val - rs2_val)
        elif opcode == "AND":
            return ("WB", rd, rs1_val & rs2_val)
        elif opcode == "OR":
            return ("WB", rd, rs1_val | rs2_val)
        elif opcode == "LW":
            addr = rs1_val + instr.imm
            return ("MEM", rd, addr)
        elif opcode == "SW":
            addr = rs1_val + instr.imm
            data = self.regs.read(rs2)
            self.memory.store(addr, data)
            return None
        elif opcode == "HALT":
            self.halted = True
            print(" Instrucción HALT detectada: fin del programa.")
            return None
        else:
            return None

    # =======================================================
    # Ejecución de un ciclo del pipeline
    # =======================================================
    def step(self):
        if self.halted:
            return

        self.clock += 1
        print(f"\n--- Ciclo {self.clock} ---")

        if self.pc >= len(self.memory.mem):
            print("Fin del programa (PC fuera de rango).")
            self.halted = True
            return

        # =======================
        # Avance del pipeline
        # =======================
        self.pipeline["WB"] = self.pipeline["MEM"]
        self.pipeline["MEM"] = self.pipeline["EX"]
        self.pipeline["EX"] = self.pipeline["ID"]
        self.pipeline["ID"] = self.pipeline["IF"]

        # =======================
        # Fetch
        # =======================
        instr = self.memory.load(self.pc)
        self.pipeline["IF"] = instr
        self.pc += 1

        # =======================
        # Detectar hazards
        # =======================
        if self.hazard_unit.detect_data_hazard(self.pipeline["ID"], self.pipeline["EX"]):
            print(f"[STALL] Burbuja insertada en ciclo {self.clock}")
            self.pipeline["EX"] = None
            return

        # =======================
        # Ejecutar etapa EX
        # =======================
        if self.pipeline["EX"]:
            result = self.execute_stage(self.pipeline["EX"])
            self.pipeline["MEM"] = result

        # =======================
        # Write Back
        # =======================
        wb_stage = self.pipeline["WB"]

        # Solo procesar si la etapa WB contiene una tupla tipo ('WB', destino, valor)
        if isinstance(wb_stage, tuple) and len(wb_stage) == 3 and wb_stage[0] == "WB":
            dest, val = wb_stage[1], wb_stage[2]
            if isinstance(dest, str) and dest.startswith("x"):
                dest = int(dest[1:])
            self.regs.write(dest, val)

        # =======================
        # Mostrar estado del pipeline
        # =======================
        self.print_pipeline()
        self.regs.dump()

    # =======================================================
    # Impresión del estado del pipeline
    # =======================================================
    def print_pipeline(self):
        for stage, instr in self.pipeline.items():
            if instr is None:
                print(f"{stage:<5}: None")
            elif isinstance(instr, tuple):
                print(f"{stage:<5}: {instr}")
            else:
                try:
                    print(f"{stage:<5}: {instr.opcode} {getattr(instr, 'rd', '')} {getattr(instr, 'rs1', '')} {getattr(instr, 'rs2', '')}")
                except Exception:
                    print(f"{stage:<5}: {instr}")
