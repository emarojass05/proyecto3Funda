# adapter.py — adapta la CPU existente a una interfaz estable para la GUI
import sys
import importlib
from types import ModuleType

def _wire_user_modules():
    """
    Enlaza el paquete del simulador del usuario de forma flexible:
    - Prioriza 'simulator'
    - Si existe 'simulacion', lo alias a 'simulator'
    - Si no hay paquete, se intenta importación plana (cpu.py, parser.py en PYTHONPATH)
    """
    found_pkg = None
    for name in ("simulator", "simulacion"):
        try:
            mod = importlib.import_module(name)
            found_pkg = name
            # Alias cruzado para que valgan ambos nombres
            if name == "simulator" and "simulacion" not in sys.modules:
                sys.modules["simulacion"] = mod
            if name == "simulacion" and "simulator" not in sys.modules:
                sys.modules["simulator"] = mod
            break
        except Exception:
            continue
    return found_pkg

_wire_user_modules()

# Imports tolerantes: primero paquete, luego módulos planos
try:
    from simulator.cpu import CPU              # type: ignore
    from simulator.parser import load_program  # type: ignore
except Exception:
    try:
        from simulacion.cpu import CPU         # type: ignore
        from simulacion.parser import load_program  # type: ignore
    except Exception:
        from cpu import CPU                    # type: ignore
        from parser import load_program        # type: ignore

class SimulatorAdapter:
    """Envoltura mínima para exponer un snapshot estable a la GUI."""
    def __init__(self, program_path=None, program_lines=None):
        if program_lines is not None:
            # Guardar a un archivo temporal si nos pasan líneas
            from tempfile import NamedTemporaryFile
            tmp = NamedTemporaryFile(delete=False, suffix=".asm", mode="w", encoding="utf-8")
            tmp.write("\n".join(program_lines))
            tmp.close()
            program_path = tmp.name

        if program_path is None:
            raise ValueError("Debes proporcionar program_path o program_lines")

        program = load_program(program_path)
        self.cpu = CPU(program)
        self._last_snapshot = None
        self._cycle = 0  # contador local en caso de que la CPU no tenga 'clock'

    # Control
    def reset(self, program_path=None):
        if program_path is not None:
            program = load_program(program_path)
            self.cpu = CPU(program)
        else:
            # recrear CPU con el mismo contenido de memoria (mejorable según tu API)
            mem = getattr(self.cpu, "memory", None)
            program = []
            if mem is not None and hasattr(mem, "mem"):
                for i in range(len(mem.mem)):
                    try:
                        v = mem.load(i)
                        if v:
                            program.append(v)
                    except Exception:
                        pass
            self.cpu = CPU(program)
        self._last_snapshot = None
        self._cycle = 0

    def step(self):
        if getattr(self.cpu, "halted", False):
            return self.snapshot()
        self.cpu.step()
        # Intentar leer 'clock' de la CPU, si no existe usamos contador local
        clk = getattr(self.cpu, "clock", None)
        if isinstance(clk, int):
            self._cycle = clk
        else:
            self._cycle += 1
        return self.snapshot()

    def halted(self):
        return bool(getattr(self.cpu, "halted", False))

    # Observación
    def snapshot(self, mem_start=0, mem_len=16):
        # Pipeline
        pipeline_dict = {}
        pipe = getattr(self.cpu, "pipeline", None)
        if isinstance(pipe, dict):
            pipeline_dict = dict(pipe)
        elif pipe is not None:
            # Soporta objeto con atributos IF/ID/EX/MEM/WB
            for st in ("IF", "ID", "EX", "MEM", "WB"):
                pipeline_dict[st] = getattr(pipe, st, None)

        def _fmt_instr(i):
            if i is None:
                return "—"
            if isinstance(i, str):
                return i
            if hasattr(i, "raw"):
                return getattr(i, "raw")
            if hasattr(i, "opcode"):
                try:
                    args = getattr(i, "args", [])
                    if isinstance(args, (list, tuple)):
                        args = " ".join(map(str, args))
                    return f"{i.opcode} {args}".strip()
                except Exception:
                    pass
            return repr(i)

        pipeline = {stage: _fmt_instr(instr) for stage, instr in pipeline_dict.items()}

        # Registros
        regs = []
        rf = getattr(self.cpu, "regs", None)
        if rf is not None:
            if hasattr(rf, "regs"):
                raw_regs = rf.regs
            elif hasattr(rf, "as_list"):
                raw_regs = rf.as_list()
            else:
                raw_regs = [rf.read(i) for i in range(32)]
            regs = [int(x) if isinstance(x, (int, float)) else 0 for x in raw_regs]

        # Memoria
        mem = []
        mem_mod = getattr(self.cpu, "memory", None)
        if mem_mod is not None:
            for a in range(mem_start, mem_start + mem_len):
                val = None
                try:
                    if hasattr(mem_mod, "load"):
                        val = mem_mod.load(a)
                    elif hasattr(mem_mod, "__getitem__"):
                        val = mem_mod[a]
                except Exception:
                    val = None
                if hasattr(val, "opcode"):
                    vv = f"{getattr(val, 'opcode', '?')} {' '.join(getattr(val, 'args', []))}"
                else:
                    vv = val
                mem.append((a, vv))

        # Ciclo y PC
        clk = getattr(self.cpu, "clock", None)
        if isinstance(clk, int):
            cycle = clk
        else:
            cycle = self._cycle

        snap = {
            "cycle": int(cycle),
            "pc": int(getattr(self.cpu, "pc", 0)),
            "halted": self.halted(),
            "pipeline": pipeline,
            "registers": regs,
            "memory": mem,
        }
        self._last_snapshot = snap
        return snap
