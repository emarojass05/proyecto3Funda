# ===========================================================
# app.py — Interfaz principal con el controlador dual integrado
# ===========================================================
import tkinter as tk
from tkinter import ttk
from .controller import Controller


def run():
    root = tk.Tk()
    root.title("RISC-V Pipeline Simulator — Comparador Dual")
    root.geometry("1300x700")
    root.configure(bg="#1e1e1e")

    # =======================================================
    # Barra superior
    # =======================================================
    top = ttk.Frame(root, padding=8)
    top.pack(side=tk.TOP, fill=tk.X)

    ttk.Label(top, text="Configuración del procesador",
              font=("Segoe UI", 11, "bold")).pack(side=tk.LEFT, padx=10)

    # =======================================================
    # Crear controlador dual (Procesador A y B)
    # =======================================================
    ctl = Controller(root)

    # =======================================================
    # Barra inferior (estado)
    # =======================================================
    status_bar = ttk.Label(root, text="Listo", relief=tk.SUNKEN, anchor="w")
    status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    root.mainloop()


if __name__ == "__main__":
    run()
