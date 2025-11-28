# ===========================================================
# branch_predictor.py — Predictor de saltos simple (1-bit)
# ===========================================================

class BranchPredictor:
    def __init__(self):
        # Mapa de direcciones a predicciones: {pc: bool}
        self.history = {}

    # -------------------------------------------------------
    # Predecir si se tomará el salto
    # -------------------------------------------------------
    def predict(self, pc):
        # Si no está en la tabla, por defecto: no tomado
        return self.history.get(pc, False)

    # -------------------------------------------------------
    # Actualizar predicción según resultado real
    # -------------------------------------------------------
    def update(self, pc, taken):
        self.history[pc] = taken
