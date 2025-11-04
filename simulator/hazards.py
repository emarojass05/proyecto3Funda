# ===========================================================
# hazards.py — Unidad de detección y manejo de riesgos (Hazard Unit)
# ===========================================================

from simulator.utils import reg_index

class HazardUnit:
    def __init__(self):
        self.stalled = False

    # =======================================================
    # Detección de riesgos de datos tipo RAW
    # =======================================================
    def detect_data_hazard(self, id_instr, ex_instr):
        """Detecta riesgos de datos entre la instrucción ID y la EX"""
        if not id_instr or not ex_instr:
            return False

        # Extraer registros fuente y destino
        rs1 = reg_index(id_instr.rs1) if id_instr.rs1 else None
        rs2 = reg_index(id_instr.rs2) if id_instr.rs2 else None
        rd_ex = reg_index(ex_instr.rd) if ex_instr.rd else None

        # Detección RAW: EX produce un valor que ID necesita
        if rd_ex is not None and rd_ex != 0:
            if rs1 == rd_ex or rs2 == rd_ex:
                print(f"[STALL] Riesgo de datos detectado entre {ex_instr.opcode} -> {id_instr.opcode}")
                return True

        return False

    # =======================================================
    # Inserción de burbuja (stall)
    # =======================================================
    def insert_stall(self, cpu):
        """Inserta una burbuja en el pipeline"""
        print("[STALL] Burbuja insertada en ciclo actual")
        self.stalled = True
        # Mantener IF y ID, insertar burbuja en EX
        cpu.pipeline["EX"] = None

    # =======================================================
    # Forwarding (reenvío de datos desde MEM o WB)
    # =======================================================
    def apply_forwarding(self, cpu, instr):
        """Reenvío de resultados desde etapas MEM o WB"""
        if not instr or not instr.opcode:
            return None, None

        rs1_val = None
        rs2_val = None

        rs1 = reg_index(instr.rs1) if instr.rs1 else None
        rs2 = reg_index(instr.rs2) if instr.rs2 else None

        # --- Verificar etapa MEM ---
        if "MEM" in cpu.pipeline and isinstance(cpu.pipeline["MEM"], tuple) and cpu.pipeline["MEM"][0] == "WB":
            dest, val = cpu.pipeline["MEM"][1], cpu.pipeline["MEM"][2]
            if rs1 == dest:
                rs1_val = val
            if rs2 == dest:
                rs2_val = val

        # --- Verificar etapa WB ---
        if "WB" in cpu.pipeline and isinstance(cpu.pipeline["WB"], tuple) and cpu.pipeline["WB"][0] == "WB":
            dest, val = cpu.pipeline["WB"][1], cpu.pipeline["WB"][2]
            if rs1 == dest:
                rs1_val = val
            if rs2 == dest:
                rs2_val = val

        # --- Leer de los registros si no hubo reenvío ---
        if rs1_val is None and rs1 is not None:
            rs1_val = cpu.regs.read(rs1)
        if rs2_val is None and rs2 is not None:
            rs2_val = cpu.regs.read(rs2)

        return rs1_val, rs2_val
