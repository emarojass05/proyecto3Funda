# ===========================================================
# cpu.py — Simulador RISC-V Pipelined con trazas visuales (mejorado)
# ===========================================================
from simulator.memory import Memory
from simulator.registers import RegisterFile
from simulator.hazards import HazardUnit
import os

# Colores para mejor visualización
C_RESET = "\033[0m"
C_YELLOW = "\033[93m"
C_GREEN = "\033[92m"
C_BLUE = "\033[94m"
C_RED = "\033[91m"


class CPU:
    def __init__(self, program, program_name="program.asm"):
        self.regs = RegisterFile()
        self.memory = Memory()
        self.hazard_unit = HazardUnit()
        self.pipeline = {"IF": None, "ID": None, "EX": None, "MEM": None, "WB": None}
        self.pc = 0
        self.clock = 0
        self.halted = False
        self.instructions = program
        self.program_name = program_name

        # Métricas
        self.cycle_count = 0
        self.mem_accesses = 0
        self.alu_ops = 0
        self.branches = 0

    # =======================================================
    # Etapa de ejecución (EX)
    # =======================================================
    def execute_stage(self, instr):
        if instr is None:
            return None

        opcode = instr.opcode
        rd, rs1, rs2, imm, label = instr.rd, instr.rs1, instr.rs2, instr.imm, getattr(instr, "label", None)

        def val(reg):
            if reg is None:
                return 0
            if isinstance(reg, str) and reg.startswith("x"):
                return self.regs.read(int(reg[1:]))
            return 0

        v1, v2 = val(rs1), val(rs2)

        # ===================================================
        # Instrucciones aritméticas / lógicas
        # ===================================================
        if opcode in ["ADD", "SUB", "AND", "OR", "ADDI", "ANDI", "ORI"]:
            self.alu_ops += 1
            result = None
            if opcode == "ADD":
                result = v1 + v2
            elif opcode == "SUB":
                result = v1 - v2
            elif opcode == "AND":
                result = v1 & v2
            elif opcode == "OR":
                result = v1 | v2
            elif opcode == "ADDI":
                result = v1 + (imm or 0)
            elif opcode == "ANDI":
                result = v1 & (imm or 0)
            elif opcode == "ORI":
                result = v1 | (imm or 0)
            print(f"{C_GREEN}-> ALU: {opcode} ejecutada (rd={rd}, resultado={result}){C_RESET}")
            return ("WB", int(rd[1:]), result)

        # ===================================================
        # Carga / almacenamiento
        # ===================================================
        elif opcode == "LW":
            self.mem_accesses += 1
            addr = v1 + (imm or 0)
            val = self.memory.load(addr)
            print(f"{C_BLUE}-> LOAD: x{rd[1:]} = Mem[{addr}] = {val}{C_RESET}")
            return ("WB", int(rd[1:]), val)

        elif opcode == "SW":
            self.mem_accesses += 1
            addr = v1 + (imm or 0)
            self.memory.store(addr, v2)
            print(f"{C_BLUE}-> STORE: Mem[{addr}] = {v2} (desde {rs2}){C_RESET}")
            return None

        # ===================================================
        # Saltos y control de flujo
        # ===================================================
        elif opcode in ["BEQ", "BNE"]:
            self.branches += 1
            condition = (v1 == v2) if opcode == "BEQ" else (v1 != v2)
            if condition:
                target = self.find_label(label)
                print(f"{C_YELLOW}-> SALTO TOMADO ({opcode}) hacia {label} (PC={target}){C_RESET}")
                self.pc = target
                # flush del pipeline tras salto tomado
                self.pipeline["IF"] = None
                self.pipeline["ID"] = None
            else:
                print(f"{C_YELLOW}-> SALTO NO tomado ({opcode}){C_RESET}")

        elif opcode == "JAL":
            self.branches += 1
            self.regs.write(int(rd[1:]), self.pc)
            target = self.find_label(label)
            print(f"{C_YELLOW}-> JAL: salto a {label} (PC={target}), guardado link en {rd}{C_RESET}")
            self.pc = target
            self.pipeline["IF"] = None
            self.pipeline["ID"] = None

        elif opcode == "JALR":
            self.branches += 1
            next_pc = v1 + (imm or 0)
            self.regs.write(int(rd[1:]), self.pc)
            print(f"{C_YELLOW}-> JALR: salto indirecto a {next_pc}, link en {rd}{C_RESET}")
            self.pc = next_pc
            self.pipeline["IF"] = None
            self.pipeline["ID"] = None

        elif opcode == "NOP":
            print(f"{C_BLUE}-> NOP ejecutado (sin efecto){C_RESET}")
            return None

        # ===================================================
        # HALT — Termina el programa
        # ===================================================
        elif opcode == "HALT":
            self.halted = True
            print(f"{C_RED} Instrucción HALT detectada: fin del programa.{C_RESET}")
            return None

        else:
            print(f"[WARN] Instrucción desconocida: {opcode}")
            return None

    # -------------------------------------------------------
    # Buscar una etiqueta (simulada por nombre en lista)
    # -------------------------------------------------------
    def find_label(self, label):
        for i, instr in enumerate(self.instructions):
            if instr.raw.strip().endswith(f"{label}:"):
                return i
        print(f"[WARN] Etiqueta '{label}' no encontrada.")
        return self.pc

    # =======================================================
    # Ejecución de un ciclo del pipeline
    # =======================================================
    def step(self):
        if self.halted:
            return

        self.clock += 1
        self.cycle_count += 1
        print(f"\n{C_BLUE}--- Ciclo {self.clock} ---{C_RESET}")

        # --- Detectar hazard ---
        hazard = self.hazard_unit.detect_data_hazard(
            self.pipeline["ID"], self.pipeline["EX"]
        )

        # ===================================================
        # Manejo de hazard (stall de un ciclo)
        # ===================================================
        if hazard:
            print(f"{C_YELLOW}[STALL] Burbuja insertada en ciclo {self.clock}{C_RESET}")
            self.pipeline["WB"] = self.pipeline["MEM"]
            self.pipeline["MEM"] = None
            self.pipeline["EX"] = None
        else:
            # Avanzar pipeline
            self.pipeline["WB"] = self.pipeline["MEM"]
            self.pipeline["MEM"] = self.pipeline["EX"]
            self.pipeline["EX"] = self.pipeline["ID"]
            self.pipeline["ID"] = self.pipeline["IF"]

            # Fetch
            if self.pc < len(self.instructions):
                instr = self.instructions[self.pc]
                # Ignorar líneas que son etiquetas
                if instr.opcode and not instr.opcode.endswith(":"):
                    self.pipeline["IF"] = instr
                else:
                    self.pipeline["IF"] = None
                self.pc += 1
            else:
                self.pipeline["IF"] = None

        # ===================================================
        # EX stage
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
            print(f"{C_GREEN}-> WB: x{dest} actualizado = {val}{C_RESET}")

        # ===================================================
        # Fin del programa
        # ===================================================
        if self.pc >= len(self.instructions) and all(v is None for v in self.pipeline.values()):
            self.halted = True
            print(f"\n{C_GREEN}=== PROGRAMA FINALIZADO CORRECTAMENTE ==={C_RESET}")
            self.print_metrics()
            self.save_history()
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
                print(f"{stage:<5}: {instr.opcode} {instr.rd or ''} {instr.rs1 or ''} {instr.rs2 or ''} {instr.imm or ''}")

    # =======================================================
    # Mostrar métricas
    # =======================================================
    def print_metrics(self):
        print(f"\n{C_YELLOW}--- METRICAS ---{C_RESET}")
        print(f"Ciclos totales: {self.cycle_count}")
        print(f"Accesos a memoria: {self.mem_accesses}")
        print(f"Operaciones ALU: {self.alu_ops}")
        print(f"Instrucciones de salto: {self.branches}")

    # =======================================================
    # Guardar historial
    # =======================================================
    def save_history(self):
        history_path = "history.txt"
        line = f"{self.program_name} - Ciclos: {self.cycle_count}\n"

        if os.path.exists(history_path):
            with open(history_path, "r") as f:
                lines = f.readlines()[-9:]
        else:
            lines = []

        with open(history_path, "w") as f:
            f.writelines(lines + [line])
        print(f"{C_BLUE}[INFO] Ejecucion guardada en {history_path}{C_RESET}")
