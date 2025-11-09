# ===========================================================
# main.py – Entrada del proyecto (GUI por defecto, CLI opcional)
# ===========================================================

import sys

# ===========================================================
# Importar CPU y parser (soporta 'simulator' o 'simulacion')
# ===========================================================
try:
    from simulator.cpu import CPU
    from simulator.parser import load_program
except Exception:
    from simulacion.cpu import CPU
    from simulacion.parser import load_program

# ===========================================================
# Colores para la consola (modo CLI)
# ===========================================================
RED   = "\033[91m"
GREEN = "\033[92m"
YELLOW= "\033[93m"
BLUE  = "\033[94m"
RESET = "\033[0m"

# ===========================================================
# Modo consola original
# ===========================================================
def main():
    print(f"{YELLOW}=== SIMULADOR RISC-V PIPELINED (CLI) ==={RESET}\n")

    # Cargar programa desde carpeta examples/
    program = load_program("examples/program1.asm")

    # Inicializar CPU con el programa
    cpu = CPU(program)

    ciclo = 1
    MAX_CICLOS = 30  # 🔸 límite para evitar bucles infinitos

    while not getattr(cpu, "halted", False) and ciclo <= MAX_CICLOS:
        print(f"\n{BLUE}--- Ciclo {ciclo} ---{RESET}\n")
        cpu.step()
        ciclo += 1

    # =======================================================
    # Fin de la simulación
    # =======================================================
    print(f"\n{GREEN}=== EJECUCIÓN FINALIZADA ==={RESET}")
    print(f"{YELLOW}Total de ciclos ejecutados:{RESET} {ciclo - 1}")

    print(f"\n{YELLOW}--- REGISTROS FINALES ---{RESET}")
    cpu.regs.dump()

    # Si la memoria tiene método dump, mostrarla
    if hasattr(cpu, "memory") and hasattr(cpu.memory, "dump"):
        print(f"\n{YELLOW}--- MEMORIA FINAL ---{RESET}")
        cpu.memory.dump()
    else:
        print(f"\n{YELLOW}(No hay método dump() en memoria){RESET}")

    print(f"\n{GREEN}Programa finalizado correctamente.{RESET}")

# ===========================================================
# Punto de entrada: GUI por defecto, CLI con --cli
# ===========================================================
if __name__ == "__main__":
    if "--cli" in sys.argv:
        # Forzar modo consola:
        main()
    else:
        # Intentar abrir la GUI
        try:
            from gui.app import run as run_gui
            run_gui()
        except Exception as e:
            # Fallback a CLI si la GUI no está disponible
            print(f"{YELLOW}[Aviso]{RESET} No se pudo iniciar la GUI ({e}).")
            print(f"{YELLOW}[Aviso]{RESET} Ejecutando en modo consola…\n")
            main()
