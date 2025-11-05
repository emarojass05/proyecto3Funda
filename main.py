# ===========================================================
# main.py – Simulador RISC-V Pipeline Mejorado
# ===========================================================

from simulator.cpu import CPU
from simulator.parser import load_program

# ===========================================================
# Colores para la consola
# ===========================================================
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

# ===========================================================
# Función principal
# ===========================================================
def main():
    print(f"{YELLOW}=== SIMULADOR RISC-V PIPELINED ==={RESET}\n")

    # Cargar programa desde carpeta examples/
    program = load_program("examples/program1.asm")

    # Inicializar CPU con el programa
    cpu = CPU(program)

    ciclo = 1
    MAX_CICLOS = 30  # 🔸 límite para evitar bucles infinitos

    while not cpu.halted and ciclo <= MAX_CICLOS:
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
    if hasattr(cpu.memory, "dump"):
        print(f"\n{YELLOW}--- MEMORIA FINAL ---{RESET}")
        cpu.memory.dump()
    else:
        print(f"\n{YELLOW}(No hay método dump() en memoria){RESET}")

    print(f"\n{GREEN}Programa finalizado correctamente.{RESET}")


# ===========================================================
# Punto de entrada
# ===========================================================
if __name__ == "__main__":
    main()
