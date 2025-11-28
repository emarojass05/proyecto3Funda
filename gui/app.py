import tkinter as tk
from .controller import Controller


def run():
    root = tk.Tk()
    root.title("RISC-V Pipeline Simulator — Comparador Dual")
    root.geometry("1300x700")
    root.configure(bg="#1e1e1e")

    # Construye toda la GUI (incluye barras superior, CPUs, controles inferiores)
    Controller(root)

    root.mainloop()


if __name__ == "__main__":
    run()
