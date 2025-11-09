# controller.py — lógica de ejecución (step / run / pause / reset)
import tkinter as tk
from tkinter import filedialog, messagebox
from .adapter import SimulatorAdapter

class Controller:
    def __init__(self, root, views):
        self.root = root
        self.views = views
        self.adapter = None
        self.running = False
        self.period_ms = 300  # velocidad por defecto

    def load_program(self):
        path = filedialog.askopenfilename(
            title="Seleccionar programa .asm",
            filetypes=[("ASM", "*.asm"), ("Todos", "*.*")]
        )
        if not path:
            return
        try:
            self.adapter = SimulatorAdapter(program_path=path)
            self.refresh()
            self.views["status"].set(f"Programa cargado: {path}")
        except Exception as e:
            messagebox.showerror("Error al cargar", str(e))

    def step(self):
        if not self.adapter:
            messagebox.showinfo("Info", "Primero carga un programa .asm")
            return
        self.adapter.step()
        self.refresh()

    def run(self):
        if not self.adapter:
            messagebox.showinfo("Info", "Primero carga un programa .asm")
            return
        if self.running:
            return
        self.running = True
        self._tick()

    def _tick(self):
        if not self.running:
            return
        if self.adapter.halted():
            self.running = False
            self.refresh()
            return
        self.adapter.step()
        self.refresh()
        self.root.after(self.period_ms, self._tick)

    def pause(self):
        self.running = False

    def reset(self):
        if not self.adapter:
            return
        try:
            self.adapter.reset()
            self.refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def set_speed(self, ms):
        self.period_ms = int(ms)

    def refresh(self):
        if not self.adapter:
            return
        snap = self.adapter.snapshot()
        # Actualizar vistas
        self.views["pipeline"].update_pipeline(snap["pipeline"], snap["cycle"])
        self.views["registers"].update_registers(snap["registers"])
        self.views["memory"].update_memory(snap["memory"])
        self.views["info"].set(f"Ciclo: {snap['cycle']}   PC: {snap['pc']}   Halted: {snap['halted']}")
