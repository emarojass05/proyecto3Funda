# ===========================================================
# adapter.py — Adaptador entre GUI y CPU
# ===========================================================
from simulator.parser import load_program
from simulator.cpu import CPU


class SimulatorAdapter:
    def __init__(self, program_path, hazard_unit_enabled=False, branch_prediction_enabled=False):
        self.program = load_program(program_path)
        self.cpu = CPU(self.program, program_name=program_path.split("/")[-1],
                       hazard_unit_enabled=hazard_unit_enabled,
                       branch_prediction_enabled=branch_prediction_enabled)

    def step(self):
        self.cpu.step()
        return {
            "cycle": self.cpu.cycle_count,
            "pc": self.cpu.pc,
            "halted": self.cpu.halted,
        }

    def reset(self, path):
        self.__init__(path)

    def halted(self):
        return self.cpu.halted

    def metrics(self):
        return {
            "cycles": self.cpu.cycle_count,
            "alu_ops": self.cpu.alu_ops,
            "mem_accesses": self.cpu.mem_accesses,
            "branches": self.cpu.branches,
            "stalls": self.cpu.hazard_stalls,
            "branch_hits": self.cpu.branch_hits,
            "branch_misses": self.cpu.branch_misses,
        }
