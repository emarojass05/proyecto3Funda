# ===========================================================
# controller.py — Controlador principal de la interfaz dual CPU
# ===========================================================
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from .adapter import SimulatorAdapter
import time


# ===========================================================
# Clase auxiliar para cada CPU individual (Procesador A / B)
# ===========================================================
class CPUController:
    def __init__(self, parent_frame, title):
        self.parent = parent_frame
        self.title = title
        self.sim = None
        self.program_path = None
        self.hazard_enabled = False
        self.prediction_enabled = False
        self.running = False
        self.thread = None
        self.period_ms = 300  # Delay entre ciclos en modo Run
        self._build_ui()

    # =======================================================
    # Construcción visual
    # =======================================================
    def _build_ui(self):
        frame = tk.LabelFrame(self.parent, text=f"Procesador {self.title}",
                              padx=10, pady=10, bg="#1e1e1e", fg="#ffffff",
                              font=("Segoe UI", 10, "bold"))
        frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5, pady=5)

        # === Selección de modo ===
        mode_frame = tk.LabelFrame(frame, text="Modo de ejecución",
                                   padx=5, pady=5, bg="#2a2a2a", fg="#f0f0f0")
        mode_frame.pack(fill=tk.X, pady=4)
        self.mode_var = tk.StringVar(value="a")

        modes = [
            ("a) Sin unidad de riesgos", "a"),
            ("b) Con unidad de riesgos", "b"),
            ("c) Con predicción de saltos", "c"),
            ("d) Con unidad de riesgos + predicción", "d"),
        ]
        for text, val in modes:
            tk.Radiobutton(mode_frame, text=text, variable=self.mode_var,
                           value=val, bg="#2a2a2a", fg="#ffffff",
                           selectcolor="#333333",
                           command=self._update_mode).pack(anchor=tk.W)

        # === Botones principales ===
        btn_frame = tk.Frame(frame, bg="#1e1e1e")
        btn_frame.pack(fill=tk.X, pady=6)
        tk.Button(btn_frame, text="Cargar .asm", command=self.load_program).pack(side=tk.LEFT, padx=4)
        tk.Button(btn_frame, text="Step", command=self.step).pack(side=tk.LEFT, padx=4)
        tk.Button(btn_frame, text="Run", command=self.run).pack(side=tk.LEFT, padx=4)
        tk.Button(btn_frame, text="Pause", command=self.pause).pack(side=tk.LEFT, padx=4)
        tk.Button(btn_frame, text="Reset", command=self.reset).pack(side=tk.LEFT, padx=4)

        # === Estado ===
        self.status_lbl = tk.Label(frame, text="Ciclo: — | PC: — | Halted: —",
                                   anchor="w", bg="#1e1e1e", fg="#00ffcc", font=("Consolas", 10))
        self.status_lbl.pack(fill=tk.X, pady=2)

        # === Métricas ===
        self.metrics_txt = tk.Text(frame, height=7, width=60,
                                   bg="#0f0f0f", fg="#00ffcc", font=("Consolas", 10))
        self.metrics_txt.pack(fill=tk.BOTH, expand=True, pady=4)
        self.frame = frame

    # =======================================================
    # Actualización del modo seleccionado
    # =======================================================
    def _update_mode(self):
        """Actualiza los flags internos según el modo seleccionado"""
        mode = self.mode_var.get()
        self.hazard_enabled = mode in ("b", "d")
        self.prediction_enabled = mode in ("c", "d")

        info = []
        if self.hazard_enabled:
            info.append("Unidad de riesgos")
        if self.prediction_enabled:
            info.append("Predicción de saltos")

        if not info:
            self.update_status("Modo: Sin unidad de riesgos")
        else:
            self.update_status(f"Modo: {' + '.join(info)}")

    # =======================================================
    # Cargar programa .asm
    # =======================================================
    def load_program(self):
        path = filedialog.askopenfilename(
            title="Seleccionar archivo ASM",
            filetypes=[("Assembly files", "*.asm"), ("Todos los archivos", "*.*")]
        )
        if not path:
            return

        self.program_path = path
        self._update_mode()  # asegurarse de usar modo actual

        try:
            self.sim = SimulatorAdapter(
                program_path=path,
                hazard_unit_enabled=self.hazard_enabled,
                branch_prediction_enabled=self.prediction_enabled,
            )
            self.update_status(f"Programa cargado ({path.split('/')[-1]})")
        except Exception as e:
            messagebox.showerror(f"Error CPU {self.title}", str(e))

    # =======================================================
    # Ejecución paso a paso / continua
    # =======================================================
    def step(self):
        if not self.sim:
            messagebox.showwarning(f"CPU {self.title}", "Primero carga un programa .asm")
            return

        snap = self.sim.step()
        self.display_snapshot(snap)

    def run(self):
        if not self.sim:
            messagebox.showwarning(f"CPU {self.title}", "Primero carga un programa .asm")
            return
        self.running = True
        self.thread = threading.Thread(target=self._auto_run)
        self.thread.start()

    def _auto_run(self):
        while self.running and not self.sim.halted():
            snap = self.sim.step()
            self.display_snapshot(snap)
            time.sleep(self.period_ms / 1000.0)
        self.running = False

    def pause(self):
        self.running = False
        self.update_status("Ejecución pausada")

    def reset(self):
        if self.sim:
            self.sim.reset(self.program_path)
            self.update_status("Reiniciado")
            self.metrics_txt.delete("1.0", tk.END)

    # =======================================================
    # Visualización de resultados
    # =======================================================
    def display_snapshot(self, snap):
        try:
            cycle = snap["cycle"]
            pc = snap["pc"]
            halted = snap["halted"]
            self.status_lbl.config(text=f"Ciclo: {cycle} | PC: {pc} | Halted: {halted}")

            metrics = self.sim.metrics()
            text = [
                f"Ciclos totales: {metrics['cycles']}",
                f"Operaciones ALU: {metrics['alu_ops']}",
                f"Accesos a memoria: {metrics['mem_accesses']}",
                f"Saltos ejecutados: {metrics['branches']}",
                f"Stalls (riesgos): {metrics['stalls']}",
                f"Predicciones correctas: {metrics['branch_hits']}",
                f"Predicciones fallidas: {metrics['branch_misses']}",
            ]

            total_pred = metrics["branch_hits"] + metrics["branch_misses"]
            if total_pred > 0:
                acc = (metrics["branch_hits"] / total_pred) * 100
                text.append(f"Precisión predictor: {acc:.2f}%")
            else:
                text.append(f"Precisión predictor: —")

            self.metrics_txt.delete("1.0", tk.END)
            self.metrics_txt.insert(tk.END, "\n".join(text))

        except Exception as e:
            self.metrics_txt.insert(tk.END, f"\n[Error] {e}")

    def update_status(self, msg):
        self.status_lbl.config(text=f"{msg}")


# ===========================================================
# Ventana principal — Comparador Dual
# ===========================================================
class Controller:
    def __init__(self, root):
        self.root = root
        self.root.configure(bg="#1e1e1e")

        # Marco principal
        main_frame = tk.Frame(root, bg="#1e1e1e")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Crear CPUs
        self.cpu_a = CPUController(main_frame, "A")
        self.cpu_b = CPUController(main_frame, "B")

        # Botón de comparación
        compare_btn = tk.Button(root, text="Comparar métricas finales",
                                command=self.compare_metrics,
                                bg="#2e2e2e", fg="#00ffcc",
                                font=("Segoe UI", 10, "bold"), relief=tk.RAISED)
        compare_btn.pack(pady=6)

    # =======================================================
    # Comparación entre CPU A y B
    # =======================================================
    def compare_metrics(self):
        if not (self.cpu_a.sim and self.cpu_b.sim):
            messagebox.showwarning("Comparación", "Carga programas en ambas CPUs.")
            return

        mA = self.cpu_a.sim.metrics()
        mB = self.cpu_b.sim.metrics()

        def fmt(m):
            acc = 0
            total_pred = m["branch_hits"] + m["branch_misses"]
            if total_pred:
                acc = (m["branch_hits"] / total_pred) * 100
            return (
                f"Ciclos: {m['cycles']}\n"
                f"ALU ops: {m['alu_ops']}\n"
                f"Mem accesos: {m['mem_accesses']}\n"
                f"Saltos: {m['branches']}\n"
                f"Stalls: {m['stalls']}\n"
                f"Precisión pred.: {acc:.2f}%"
            )

        msg = (
            f"=== CPU A ===\n{fmt(mA)}\n\n"
            f"=== CPU B ===\n{fmt(mB)}"
        )
        messagebox.showinfo("Comparación final", msg)
