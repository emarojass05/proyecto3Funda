# ===========================================================
# hazards.py — Unidad de detección de riesgos
# ===========================================================

class HazardUnit:
    def __init__(self):
        pass

    # -------------------------------------------------------
    # Detecta riesgo de datos RAW (Read After Write)
    # entre la instrucción en ID y la instrucción en EX
    # -------------------------------------------------------
    def detect_data_hazard(self, id_instr, ex_instr):
        if id_instr is None or ex_instr is None:
            return False

        # Si cualquiera no tiene destino o fuente, no hay riesgo
        if not hasattr(ex_instr, "rd") or ex_instr.rd is None:
            return False

        # Registros fuente en ID
        srcs = []
        if hasattr(id_instr, "rs1") and id_instr.rs1:
            srcs.append(id_instr.rs1)
        if hasattr(id_instr, "rs2") and id_instr.rs2:
            srcs.append(id_instr.rs2)

        # Si el destino de EX coincide con algún src de ID → stall
        if ex_instr.rd in srcs:
            print(f"[STALL] Riesgo de datos detectado entre {ex_instr.opcode} -> {id_instr.opcode}")
            return True
        return False
