# ===========================================================
# controller.py — lógica de ejecución (step / run / pause / reset + métricas)
# ===========================================================
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

    # -------------------------------------------------------
    # Cargar programa ASM
    # -------------------------------------------------------
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

    # -------------------------------------------------------
    # Un solo paso del pipeline
    # -------------------------------------------------------
    def step(self):
        if not self.adapter:
            messagebox.showinfo("Info", "Primero carga un programa .asm")
            return
        self.adapter.step()
        self.refresh()

    # -------------------------------------------------------
    # Ejecución automática
    # -------------------------------------------------------
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
            # Muestra métricas automáticamente al terminar
            self.show_metrics()
            return
        self.adapter.step()
        self.refresh()
        self.root.after(self.period_ms, self._tick)

    # -------------------------------------------------------
    # Controles varios
    # -------------------------------------------------------
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

    # -------------------------------------------------------
    # Actualizar vistas (pipeline, registros, memoria, estado)
    # -------------------------------------------------------
    def refresh(self):
        if not self.adapter:
            return
        snap = self.adapter.snapshot()
        # Actualizar vistas
        self.views["pipeline"].update_pipeline(snap["pipeline"], snap["cycle"])
        self.views["registers"].update_registers(snap["registers"])
        self.views["memory"].update_memory(snap["memory"])
        self.views["info"].set(
            f"Ciclo: {snap['cycle']}   PC: {snap['pc']}   Halted: {snap['halted']}"
        )


    def show_metrics(self):
        if not self.adapter:
            messagebox.showinfo("Info", "Primero ejecuta un programa.")
            return
        try:
            cpu = self.adapter.cpu
            metrics = [
                f"Ciclos totales: {getattr(cpu, 'cycle_count', '?')}",
                f"Accesos a memoria: {getattr(cpu, 'mem_accesses', '?')}",
                f"Operaciones ALU: {getattr(cpu, 'alu_ops', '?')}",
                f"Instrucciones de salto: {getattr(cpu, 'branches', '?')}"
            ]
            messagebox.showinfo("Métricas del programa", "\n".join(metrics))
        except Exception as e:
            messagebox.showerror("Error métricas", str(e))

  
    def refresh_offset(self, offset):
        if not self.adapter:
            return
        snap = self.adapter.snapshot(mem_start=offset, mem_len=16)
        self.views["memory"].update_memory(snap["memory"])

     # =======================================================
    # Mostrar historial de ejecuciones
    # =======================================================
    def show_history(self):
        import os
        history_path = "history.txt"
        if not os.path.exists(history_path):
            messagebox.showinfo("Historial", "No hay ejecuciones previas registradas.")
            return
        with open(history_path, "r", encoding="utf-8") as f:
            data = f.read().strip() or "Sin datos."

        win = tk.Toplevel(self.root)
        win.title("Historial de ejecuciones")
        win.geometry("520x350")
        win.configure(bg="#1e1e1e")

        frame = tk.Frame(win, bg="#1e1e1e")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")

        text = tk.Text(
            frame,
            wrap="word",
            bg="#1e1e1e",
            fg="#dcdcdc",
            insertbackground="#dcdcdc",
            selectbackground="#444",
            font=("Consolas", 11),
            yscrollcommand=scrollbar.set,
            relief="flat",
            padx=8,
            pady=6,
        )
        text.pack(fill="both", expand=True)
        scrollbar.config(command=text.yview)

        text.tag_configure("header", foreground="#6fa8dc", font=("Consolas", 11, "bold"))
        text.tag_configure("line", foreground="#dcdcdc")

        for line in data.splitlines():
            if line.startswith("=") or line.startswith("Programa"):
                text.insert("end", line + "\n", "header")
            else:
                text.insert("end", line + "\n", "line")

        text.configure(state="disabled")

    # =======================================================
    # Exportar resultados (registros + métricas)
    # =======================================================
    def export_results(self):
        if not self.adapter:
            messagebox.showinfo("Info", "Primero carga y ejecuta un programa.")
            return

        file_path = filedialog.asksaveasfilename(
            title="Guardar resultados",
            defaultextension=".txt",
            filetypes=[("Archivos de texto", "*.txt")]
        )
        if not file_path:
            return

        snap = self.adapter.snapshot()
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("=== Resultados del simulador RISC-V ===\n\n")
                f.write(f"Ciclo final: {snap['cycle']}\n")
                f.write(f"PC final: {snap['pc']}\n")
                f.write(f"Halted: {snap['halted']}\n\n")

                f.write("[Registros]\n")
                for i, v in enumerate(snap["registers"]):
                    f.write(f"x{i:02} = {v}\n")

                f.write("\n[Memoria inicial]\n")
                for addr, val in snap["memory"]:
                    f.write(f"{addr:04} : {val}\n")

                f.write("\n[Pipeline final]\n")
                for stage, val in snap["pipeline"].items():
                    f.write(f"{stage}: {val}\n")

            messagebox.showinfo("Exportar resultados", f"Resultados guardados en:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error al guardar", str(e))
