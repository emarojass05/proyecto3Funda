# ===========================================================
# adapter.py — Adaptador entre GUI y CPU
# ===========================================================
from simulator.parser import load_program
from simulator.cpu import CPU


class SimulatorAdapter:
    def __init__(self, program_path, hazard_unit_enabled=False, branch_prediction_enabled=False):
        self.program = load_program(program_path)
        self.cpu = CPU(
            self.program,
            program_name=program_path.split("/")[-1],
            hazard_unit_enabled=hazard_unit_enabled,
            branch_prediction_enabled=branch_prediction_enabled,
        )

    def step(self):
        """Ejecuta un ciclo del procesador y retorna un snapshot para la GUI."""
        self.cpu.step()

        # Si CPU expone get_snapshot(), usarlo:
        if hasattr(self.cpu, "get_snapshot"):
            return self.cpu.get_snapshot()

        # Fallback mínimo (por si acaso)
        return {
            "cycle": getattr(self.cpu, "cycle_count", None),
            "pc": getattr(self.cpu, "pc", None),
            "halted": getattr(self.cpu, "halted", False),
            "registers": None,
            "memory": None,
            "pipeline": getattr(self.cpu, "pipeline", None),
            "sim_time": None,
        }

    def reset(self, path):
        hazard_enabled = getattr(self.cpu, "hazard_unit", None) is not None
        branch_pred_enabled = getattr(self.cpu, "branch_predictor", None) is not None
        self.__init__(
            path,
            hazard_unit_enabled=hazard_enabled,
            branch_prediction_enabled=branch_pred_enabled,
        )

    def halted(self):
        return self.cpu.halted

    def metrics(self):
        # La GUI usa estas métricas
        return {
            "cycles": self.cpu.cycle_count,
            "alu_ops": self.cpu.alu_ops,
            "mem_accesses": self.cpu.mem_accesses,
            "branches": self.cpu.branches,
            "stalls": self.cpu.hazard_stalls,
            "branch_hits": self.cpu.branch_hits,
            "branch_misses": self.cpu.branch_misses,
        }
