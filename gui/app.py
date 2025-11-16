# ===========================================================
# app.py — GUI principal (Tkinter) con historial y exportación
# ===========================================================
import tkinter as tk
from tkinter import ttk
from .controller import Controller
from .views.pipeline_view import PipelineView
from .views.registers_view import RegistersView
from .views.memory_view import MemoryView


def run():
    root = tk.Tk()
    root.title("RISC-V Pipeline Simulator — GUI")
    root.geometry("1100x700")

    # ---- Status variables
    status_text = tk.StringVar(value="Listo")
    info_text = tk.StringVar(value="Ciclo: —   PC: —   Halted: —")

    # ---- Top controls
    top = ttk.Frame(root, padding=8)
    top.pack(side=tk.TOP, fill=tk.X)

    btn_load = ttk.Button(top, text="Cargar .asm")
    btn_step = ttk.Button(top, text="Step")
    btn_run = ttk.Button(top, text="Run")
    btn_pause = ttk.Button(top, text="Pause")
    btn_reset = ttk.Button(top, text="Reset")
    btn_metrics = ttk.Button(top, text="Métricas")
    btn_history = ttk.Button(top, text="Historial")      
    btn_export = ttk.Button(top, text="Guardar resultados")  

    for w in (btn_load, btn_step, btn_run, btn_pause, btn_reset,
              btn_metrics, btn_history, btn_export):
        w.pack(side=tk.LEFT, padx=4)

    # ---- Control de velocidad
    ttk.Label(top, text="Velocidad (ms):").pack(side=tk.LEFT, padx=(16, 4))
    speed = ttk.Scale(top, from_=50, to=1000, orient="horizontal")
    speed.set(300)
    speed.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)

    # ---- Paneles principales
    paned = ttk.Panedwindow(root, orient=tk.HORIZONTAL)
    paned.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

    left = ttk.Frame(paned, padding=8)
    paned.add(left, weight=3)
    pipeline = PipelineView(left)
    pipeline.pack(fill=tk.BOTH, expand=True)

    right = ttk.Notebook(paned)
    paned.add(right, weight=2)

    tab_regs = ttk.Frame(right, padding=8)
    tab_mem = ttk.Frame(right, padding=8)
    right.add(tab_regs, text="Registros")
    right.add(tab_mem, text="Memoria")

    regs = RegistersView(tab_regs)
    regs.pack(fill=tk.BOTH, expand=True)
    mem = MemoryView(tab_mem)
    mem.pack(fill=tk.BOTH, expand=True)

    # ---- Info & Status bars
    info = ttk.Label(root, textvariable=info_text, anchor="w")
    info.pack(side=tk.TOP, fill=tk.X, padx=8)
    status = ttk.Label(root, textvariable=status_text,
                       relief=tk.SUNKEN, anchor="w")
    status.pack(side=tk.BOTTOM, fill=tk.X)

    # ---- Controller wire-up
    views = {
        "pipeline": pipeline,
        "registers": regs,
        "memory": mem,
        "status": status_text,
        "info": info_text,
    }
    ctl = Controller(root, views)
    mem.controller_ref = ctl

    btn_load.config(command=ctl.load_program)
    btn_step.config(command=ctl.step)
    btn_run.config(command=ctl.run)
    btn_pause.config(command=ctl.pause)
    btn_reset.config(command=ctl.reset)
    btn_metrics.config(command=ctl.show_metrics)
    btn_history.config(command=ctl.show_history)     
    btn_export.config(command=ctl.export_results)    
    speed.config(command=lambda v: ctl.set_speed(float(v)))

    root.mainloop()


if __name__ == "__main__":
    run()
