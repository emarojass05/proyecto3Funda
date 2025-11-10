# ===========================================================
# hazards.py — Unidad de detección y manejo de riesgos (Hazard Unit)
# ===========================================================
from simulator.utils import reg_index


class HazardUnit:
    def __init__(self):
        self.stalled = False

    # =======================================================
    # Detección de riesgos de datos tipo RAW (realistas)
    # =======================================================
    def detect_data_hazard(self, id_instr, ex_instr):
        """
        Detecta riesgos de datos entre la instrucción en ID y la que está en EX.
        Solo genera un stall si la instrucción en EX escribe un registro (rd)
        que será leído por la instrucción en ID (rs1 o rs2).
        """
        if not id_instr or not ex_instr:
            return False

        rd_ex = reg_index(ex_instr.rd) if ex_instr.rd else None
        rs1_id = reg_index(id_instr.rs1) if id_instr.rs1 else None
        rs2_id = reg_index(id_instr.rs2) if id_instr.rs2 else None

        # Solo aplicar si la instrucción EX tiene destino y no es HALT o SW
        if rd_ex is None or ex_instr.opcode in ["HALT", "SW"]:
            return False

        # Riesgo real de datos tipo RAW
        if rd_ex != 0 and (rd_ex == rs1_id or rd_ex == rs2_id):
            print(f"[STALL] Riesgo de datos detectado entre {ex_instr.opcode} -> {id_instr.opcode}")
            return True

        return False

    # =======================================================
    # Forwarding (reenvío de datos desde MEM o WB)
    # =======================================================
    def apply_forwarding(self, cpu, instr):
        """Reenvío de resultados desde etapas MEM o WB"""
        if not instr or not instr.opcode:
            return None, None

        rs1_val, rs2_val = None, None
        rs1 = reg_index(instr.rs1) if instr.rs1 else None
        rs2 = reg_index(instr.rs2) if instr.rs2 else None

        # Etapa MEM
        if "MEM" in cpu.pipeline and isinstance(cpu.pipeline["MEM"], tuple):
            dest, val = cpu.pipeline["MEM"][1], cpu.pipeline["MEM"][2]
            if rs1 == dest:
                rs1_val = val
            if rs2 == dest:
                rs2_val = val

        # Etapa WB
        if "WB" in cpu.pipeline and isinstance(cpu.pipeline["WB"], tuple):
            dest, val = cpu.pipeline["WB"][1], cpu.pipeline["WB"][2]
            if rs1 == dest:
                rs1_val = val
            if rs2 == dest:
                rs2_val = val

        # Si no hubo reenvío, leer del banco
        if rs1_val is None and rs1 is not None:
            rs1_val = cpu.regs.read(rs1)
        if rs2_val is None and rs2 is not None:
            rs2_val = cpu.regs.read(rs2)

        return rs1_val, rs2_val
