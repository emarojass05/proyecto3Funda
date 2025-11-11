# ===========================================================
# cpu.py — Simulador RISC-V Pipelined (versión final estable)
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
        self.instructions = program

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
        imm = instr.imm

        def val(reg):
            if reg is None:
                return 0
            if isinstance(reg, str) and reg.startswith("x"):
                return self.regs.read(int(reg[1:]))
            return 0

        v1, v2 = val(rs1), val(rs2)

        if opcode == "ADD":
            return ("WB", int(rd[1:]), v1 + v2)
        elif opcode == "SUB":
            return ("WB", int(rd[1:]), v1 - v2)
        elif opcode == "AND":
            return ("WB", int(rd[1:]), v1 & v2)
        elif opcode == "OR":
            return ("WB", int(rd[1:]), v1 | v2)
        elif opcode == "ADDI":
            return ("WB", int(rd[1:]), v1 + (imm or 0))
        elif opcode == "LW":
            addr = v1 + (imm or 0)
            val = self.memory.load(addr)
            return ("WB", int(rd[1:]), val)
        elif opcode == "SW":
            addr = v1 + (imm or 0)
            self.memory.store(addr, v2)
            return None
        elif opcode == "HALT":
            self.halted = True
            print(" Instrucción HALT detectada: fin del programa.")
            return None
        else:
            print(f"[WARN] Instrucción desconocida: {opcode}")
            return None

    # =======================================================
    # Ejecución de un ciclo del pipeline
    # =======================================================
    def step(self):
        if self.halted:
            return

        self.clock += 1
        print(f"\n--- Ciclo {self.clock} ---")

        # --- Detectar hazard ---
        hazard = self.hazard_unit.detect_data_hazard(
            self.pipeline["ID"], self.pipeline["EX"]
        )

        # ===================================================
        # Manejo de hazard (stall de un ciclo)
        # ===================================================
        if hazard:
            print(f"[STALL] Burbuja insertada en ciclo {self.clock}")
            # Inserta una burbuja (solo un ciclo) limpiando EX
            self.pipeline["WB"] = self.pipeline["MEM"]
            self.pipeline["MEM"] = None
            self.pipeline["EX"] = None
            # No avanzamos ID/IF este ciclo
        else:
            # --- Avanzar pipeline normal ---
            self.pipeline["WB"] = self.pipeline["MEM"]
            self.pipeline["MEM"] = self.pipeline["EX"]
            self.pipeline["EX"] = self.pipeline["ID"]
            self.pipeline["ID"] = self.pipeline["IF"]

            # --- Fetch nueva instrucción ---
            if self.pc < len(self.instructions):
                instr = self.instructions[self.pc]
                self.pipeline["IF"] = instr
                self.pc += 1
            else:
                self.pipeline["IF"] = None

        # ===================================================
        # Etapa EX
        # ===================================================
        if self.pipeline["EX"]:
            result = self.execute_stage(self.pipeline["EX"])
            self.pipeline["MEM"] = result

        # ===================================================
        # Write Back
        # ===================================================
        wb_stage = self.pipeline["WB"]
        if isinstance(wb_stage, tuple) and wb_stage[0] == "WB":
            dest, val = wb_stage[1], wb_stage[2]
            self.regs.write(dest, val)

        # ===================================================
        # Detección de fin del programa
        # ===================================================
        if self.pc >= len(self.instructions) and all(
            v is None for v in self.pipeline.values()
        ):
            self.halted = True
            print("\n--- Programa finalizado correctamente ---")
            self.regs.dump()
            return

        # ===================================================
        # Estado del ciclo
        # ===================================================
        self.print_pipeline()
        self.regs.dump()

    # =======================================================
    # Mostrar estado del pipeline
    # =======================================================
    def print_pipeline(self):
        for stage, instr in self.pipeline.items():
            if instr is None:
                print(f"{stage:<5}: None")
            elif isinstance(instr, tuple):
                print(f"{stage:<5}: {instr}")
            else:
                print(
                    f"{stage:<5}: {instr.opcode} "
                    f"{getattr(instr, 'rd', '')} "
                    f"{getattr(instr, 'rs1', '')} "
                    f"{getattr(instr, 'rs2', '')} "
                    f"{getattr(instr, 'imm', '')}"
                )
