# ===========================================================
# cpu.py — Simulador RISC-V Pipelined con hazard + branch predictor
# ===========================================================
from simulator.memory import Memory
from simulator.registers import RegisterFile
from simulator.hazards import HazardUnit
from simulator.branch_predictor import BranchPredictor
import os

# Colores para depuración (solo CLI)
C_RESET = "\033[0m"
C_YELLOW = "\033[93m"
C_GREEN = "\033[92m"
C_BLUE = "\033[94m"
C_RED = "\033[91m"


class CPU:
    def __init__(self, program, program_name="program.asm",
                 hazard_unit_enabled=True, branch_prediction_enabled=False):
        self.regs = RegisterFile()
        self.memory = Memory()
        self.hazard_unit = HazardUnit() if hazard_unit_enabled else None
        self.branch_predictor = BranchPredictor() if branch_prediction_enabled else None
        # pipeline: en cada etapa guardamos la instrucción (o resultado de WB)
        self.pipeline = {"IF": None, "ID": None, "EX": None, "MEM": None, "WB": None}

        self.pc = 0           # índice dentro de self.instructions
        self.clock = 0
        self.halted = False
        self.instructions = program
        self.program_name = program_name

        # Métricas
        self.cycle_count = 0
        self.mem_accesses = 0
        self.alu_ops = 0
        self.branches = 0
        self.hazard_stalls = 0
        self.branch_hits = 0
        self.branch_misses = 0

        # ===================================================
        # Tabla de etiquetas: label -> índice de instrucción
        #   Se llena a partir de instrucciones que TIENEN
        #   label pero NO son BEQ / BNE / JAL (es decir,
        #   instrucciones que están precedidas por "foo:" )
        # ===================================================
        self.labels = {}
        for idx, instr in enumerate(self.instructions):
            lbl = getattr(instr, "label", None)
            if lbl and instr.opcode not in ["BEQ", "BNE", "JAL"]:
                self.labels[lbl] = idx

    # =======================================================
    # Obtener valor de registro
    # =======================================================
    def val(self, reg):
        if reg is None:
            return 0
        if isinstance(reg, str) and reg.startswith("x"):
            return self.regs.read(int(reg[1:]))
        return self.regs.read(reg)

    # =======================================================
    # Etapa de ejecución (EX)
    # =======================================================
    def execute_stage(self, instr):
        if instr is None:
            return None

        opcode = instr.opcode.upper()
        rd, rs1, rs2, imm, label = instr.rd, instr.rs1, instr.rs2, instr.imm, getattr(instr, "label", None)
        v1, v2 = self.val(rs1), self.val(rs2)

        # ===================================================
        # Aritmética / Lógica
        # ===================================================
        if opcode in ["ADD", "SUB", "AND", "OR", "ADDI", "ANDI", "ORI"]:
            self.alu_ops += 1
            result = {
                "ADD": v1 + v2,
                "SUB": v1 - v2,
                "AND": v1 & v2,
                "OR":  v1 | v2,
                "ADDI": v1 + (imm or 0),
                "ANDI": v1 & (imm or 0),
                "ORI":  v1 | (imm or 0),
            }[opcode]
            return ("WB", int(rd[1:]), result)

        # ===================================================
        # Carga / Almacenamiento
        # ===================================================
        elif opcode == "LW":
            self.mem_accesses += 1
            addr = v1 + (imm or 0)
            val = self.memory.load(addr)
            return ("WB", int(rd[1:]), val)

        elif opcode == "SW":
            self.mem_accesses += 1
            addr = v1 + (imm or 0)
            self.memory.store(addr, v2)
            return None

        # ===================================================
        # Saltos condicionales con predicción
        # ===================================================
        elif opcode in ["BEQ", "BNE"]:
            self.branches += 1
            taken_real = (v1 == v2) if opcode == "BEQ" else (v1 != v2)

            # PC del branch (la instrucción en EX es la que se
            # fetchéo en un ciclo anterior; aquí usamos pc-1 como
            # aproximación para la tabla del predictor).
            branch_pc = max(self.pc - 1, 0)

            predicted_taken = False
            if self.branch_predictor:
                predicted_taken = self.branch_predictor.predict(branch_pc)

            # Si el predictor predice salto tomado
            if predicted_taken:
                target = self.find_label(label)
                self.pc = target

            # Comparar predicción vs realidad
            if self.branch_predictor:
                if predicted_taken == taken_real:
                    self.branch_hits += 1
                else:
                    self.branch_misses += 1
                    # Corrige la predicción errónea (flush)
                    self.pipeline["IF"] = None
                    self.pipeline["ID"] = None
                    if taken_real:
                        target = self.find_label(label)
                        self.pc = target
                self.branch_predictor.update(branch_pc, taken_real)
            else:
                # Sin predictor: salto clásico
                if taken_real:
                    target = self.find_label(label)
                    self.pc = target

            return None

        # ===================================================
        # Saltos incondicionales
        # ===================================================
        elif opcode == "JAL":
            self.branches += 1
            self.regs.write(int(rd[1:]), self.pc)
            target = self.find_label(label)
            self.pc = target
            return None

        elif opcode == "JALR":
            self.branches += 1
            self.regs.write(int(rd[1:]), self.pc)
            self.pc = v1 + (imm or 0)
            return None

        elif opcode == "NOP":
            return None

        elif opcode == "HALT":
            self.halted = True
            return None

        else:
            print(f"[WARN] Instrucción desconocida: {opcode}")
            return None

    # -------------------------------------------------------
    # Buscar etiqueta (PC destino)
    # -------------------------------------------------------
    def find_label(self, label):
        if label is None:
            return self.pc
        return self.labels.get(label, self.pc)

    # =======================================================
    # Ciclo del pipeline
    # =======================================================
    def step(self):
        if self.halted:
            return

        try:
            self.clock += 1
            self.cycle_count += 1

            hazard = False
            if self.hazard_unit:
                hazard = self.hazard_unit.detect_data_hazard(
                    self.pipeline["ID"], self.pipeline["EX"]
                )

            # Stalling por riesgo
            if hazard:
                self.hazard_stalls += 1
                self.pipeline["WB"] = self.pipeline["MEM"]
                self.pipeline["MEM"] = None
                self.pipeline["EX"] = None
            else:
                # Avance normal del pipeline
                self.pipeline["WB"] = self.pipeline["MEM"]
                self.pipeline["MEM"] = self.pipeline["EX"]
                self.pipeline["EX"] = self.pipeline["ID"]
                self.pipeline["ID"] = self.pipeline["IF"]

                # Fetch siguiente instrucción
                if self.pc < len(self.instructions):
                    instr = self.instructions[self.pc]
                    # Si es una instrucción real (no etiqueta)
                    if instr.opcode and not instr.opcode.endswith(":"):
                        self.pipeline["IF"] = instr
                    else:
                        self.pipeline["IF"] = None
                    self.pc += 1
                else:
                    self.pipeline["IF"] = None

            # Etapa EX
            if self.pipeline["EX"]:
                result = self.execute_stage(self.pipeline["EX"])
                self.pipeline["MEM"] = result

            # Write Back
            wb_stage = self.pipeline["WB"]
            if isinstance(wb_stage, tuple) and wb_stage[0] == "WB":
                dest, val = wb_stage[1], wb_stage[2]
                self.regs.write(dest, val)

            # Fin del programa
            if self.pc >= len(self.instructions) and all(v is None for v in self.pipeline.values()):
                self.halted = True
                self.save_history()
                return

        except Exception as e:
            print(f"[ERROR ciclo {self.clock}] {e}")
            self.halted = True

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

    # =======================================================
    # Obtener métricas para GUI
    # =======================================================
    def get_metrics(self):
        return {
            "cycles": self.cycle_count,
            "alu_ops": self.alu_ops,
            "mem_accesses": self.mem_accesses,
            "branches": self.branches,
            "stalls": self.hazard_stalls,
            "branch_hits": self.branch_hits,
            "branch_misses": self.branch_misses,
        }

    # =======================================================
    # Snapshot para la GUI (registros, memoria, pipeline)
    # =======================================================
    def _pipeline_instr_str(self, obj):
        """Convierte lo que haya en una etapa del pipeline a texto amigable."""
        if obj is None:
            return None
        # Resultado de WB: ('WB', rd, val)
        if isinstance(obj, tuple):
            tag = obj[0]
            if tag == "WB":
                dest = obj[1]
                return f"WB x{dest}"
            return str(obj)

        # Instrucción normal: usar su línea raw sin comentarios
        raw = getattr(obj, "raw", None)
        if isinstance(raw, str):
            return raw.split("#")[0].strip()
        return str(obj)

    def get_snapshot(self):
        """
        Devuelve toda la info que la GUI necesita para mostrar:
        - ciclo, pc, halted
        - registros x0..x31
        - memoria completa
        - instrucción en cada etapa del pipeline
        """
        regs_dict = {f"x{i}": self.regs.read(i) for i in range(32)}
        mem_list = list(self.memory.mem)  # lista de enteros

        pipeline_view = {
            stage: self._pipeline_instr_str(obj)
            for stage, obj in self.pipeline.items()
        }

        return {
            "cycle": self.cycle_count,
            "pc": self.pc,
            "halted": self.halted,
            "registers": regs_dict,
            "memory": mem_list,
            "pipeline": pipeline_view,
            "sim_time": None,  # si luego agregas tiempo simulado lo pones aquí
        }
