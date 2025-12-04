# ===========================================================
# utils.py — Funciones auxiliares del simulador RISC-V
# ===========================================================

def reg_index(reg_name):
    """
    Convierte un nombre de registro (por ejemplo 'x5') a su índice entero (5).
    Si el argumento no es válido, devuelve None.
    """
    if reg_name is None:
        return None
    try:
        if isinstance(reg_name, str) and reg_name.startswith("x"):
            return int(reg_name[1:])
        elif isinstance(reg_name, int):
            return reg_name
        else:
            return None
    except ValueError:
        return None
