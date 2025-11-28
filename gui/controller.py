import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from .adapter import SimulatorAdapter
import time
import os


class CPUController:
    """
    Controlador de una sola CPU dentro de la interfaz dual.
    Maneja:
      - selección de modo
      - carga de programa
      - step / run (ritmo) / run completo / reset
      - visualización de estado, pipeline, métricas, registros, memoria
    """

    def __init__(self, parent_frame, title: str, column: int):
        self.parent = parent_frame
        self.title = title
        self.column = column

        # backend
        self.sim: SimulatorAdapter | None = None
        self.program_path: str | None = None
        self.hazard_enabled = False
        self.prediction_enabled = False

        # control de ejecución
        self.running = False
        self.thread: threading.Thread | None = None
        self.period_ms = 300          # delay en modo Run (ritmo)
        self.start_wall_time: float | None = None

        self._build_ui()

    # =======================================================
    # Construcción visual
    # =======================================================
    def _build_ui(self):
        frame = tk.LabelFrame(
            self.parent,
            text=f"Procesador {self.title}",
            padx=8,
            pady=8,
            bg="#1e1e1e",
            fg="#ffffff",
            font=("Segoe UI", 10, "bold"),
        )
        frame.grid(row=0, column=self.column, sticky="nsew", padx=5, pady=5)
        self.parent.columnconfigure(self.column, weight=1)
        self.parent.rowconfigure(0, weight=1)
        self.frame = frame

        # === Selección de modo ===
        mode_frame = tk.LabelFrame(
            frame,
            text="Modo de ejecución",
            padx=5,
            pady=5,
            bg="#252525",
            fg="#f0f0f0",
        )
        mode_frame.pack(fill=tk.X, pady=4)

        self.mode_var = tk.StringVar(value="a")
        modes = [
            ("a) Sin unidad de riesgos", "a"),
            ("b) Con unidad de riesgos", "b"),
            ("c) Con predicción de saltos", "c"),
            ("d) Con unidad de riesgos + predicción", "d"),
        ]
        for text, value in modes:
            tk.Radiobutton(
                mode_frame,
                text=text,
                variable=self.mode_var,
                value=value,
                bg="#252525",
                fg="#ffffff",
                selectcolor="#333333",
                command=self._update_mode,
                anchor="w",
            ).pack(fill=tk.X, anchor="w")

        # === Botones locales (por CPU) ===
        btn_frame = tk.Frame(frame, bg="#1e1e1e")
        btn_frame.pack(fill=tk.X, pady=4)
        self.btn_load = tk.Button(
            btn_frame, text="Cargar .asm", command=self.load_program
        )
        self.btn_load.pack(side=tk.LEFT, padx=4)
        self.btn_step = tk.Button(btn_frame, text="Step", command=self.step)
        self.btn_step.pack(side=tk.LEFT, padx=4)

        # === Estado general ===
        self.status_lbl = tk.Label(
            frame,
            text="Ciclo: — | Tiempo: — | PC: — | Halted: —",
            anchor="w",
            bg="#1e1e1e",
            fg="#00ffcc",
            font=("Consolas", 10),
        )
        self.status_lbl.pack(fill=tk.X, pady=(2, 4))

        # === Pipeline ===
        pipe_frame = tk.LabelFrame(
            frame,
            text="Pipeline (IF → ID → EX → MEM → WB)",
            padx=4,
            pady=4,
            bg="#1e1e1e",
            fg="#f0f0f0",
        )
        pipe_frame.pack(fill=tk.X, pady=(0, 4))

        self.if_var = tk.StringVar(value="–")
        self.id_var = tk.StringVar(value="–")
        self.ex_var = tk.StringVar(value="–")
        self.mem_var = tk.StringVar(value="–")
        self.wb_var = tk.StringVar(value="–")

        def make_stage(col: int, label_text: str, var: tk.StringVar):
            tk.Label(
                pipe_frame,
                text=f"{label_text}:",
                bg="#1e1e1e",
                fg="#ffffff",
                font=("Consolas", 9, "bold"),
            ).grid(row=0, column=col * 2, sticky="w", padx=(4, 0))
            tk.Label(
                pipe_frame,
                textvariable=var,
                bg="#0f0f0f",
                fg="#00ffcc",
                relief=tk.SUNKEN,
                anchor="w",
                font=("Consolas", 9),
            ).grid(row=0, column=col * 2 + 1, sticky="ew", padx=(0, 4))
            pipe_frame.columnconfigure(col * 2 + 1, weight=1)

        make_stage(0, "IF", self.if_var)
        make_stage(1, "ID", self.id_var)
        make_stage(2, "EX", self.ex_var)
        make_stage(3, "MEM", self.mem_var)
        make_stage(4, "WB", self.wb_var)

        # === Métricas ===
        metrics_frame = tk.LabelFrame(
            frame,
            text="Métricas",
            padx=4,
            pady=4,
            bg="#1e1e1e",
            fg="#f0f0f0",
        )
        metrics_frame.pack(fill=tk.X, pady=(0, 4))
        self.metrics_txt = tk.Text(
            metrics_frame,
            height=6,
            width=60,
            bg="#0f0f0f",
            fg="#00ffcc",
            font=("Consolas", 10),
        )
        self.metrics_txt.pack(fill=tk.BOTH, expand=True)

        # === Registros + Memoria ===
        rm_frame = tk.Frame(frame, bg="#1e1e1e")
        rm_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 4))

        # Registros
        regs_frame = tk.LabelFrame(
            rm_frame,
            text="Registros (x0–x31)",
            padx=4,
            pady=4,
            bg="#1e1e1e",
            fg="#f0f0f0",
        )
        regs_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 2))
        self.reg_txt = tk.Text(
            regs_frame,
            height=10,
            bg="#000000",
            fg="#ffffff",
            font=("Consolas", 9),
        )
        self.reg_txt.pack(fill=tk.BOTH, expand=True)

        # Memoria
        mem_frame = tk.LabelFrame(
            rm_frame,
            text="Memoria (0 … última celda)",
            padx=4,
            pady=4,
            bg="#1e1e1e",
            fg="#f0f0f0",
        )
        mem_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(2, 0))
        self.mem_txt = tk.Text(
            mem_frame,
            height=10,
            bg="#000000",
            fg="#ffffff",
            font=("Consolas", 9),
        )
        self.mem_txt.pack(fill=tk.BOTH, expand=True)

    # =======================================================
    # Actualización del modo seleccionado
    # =======================================================
    def _update_mode(self):
        mode = self.mode_var.get()
        self.hazard_enabled = mode in ("b", "d")
        self.prediction_enabled = mode in ("c", "d")

        info = []
        if self.hazard_enabled:
            info.append("Unidad de riesgos")
        if self.prediction_enabled:
            info.append("Predicción de saltos")

        if not info:
            self.update_status_bar(extra="Modo: Sin unidad de riesgos")
        else:
            self.update_status_bar(extra=f"Modo: {' + '.join(info)}")

    # =======================================================
    # Cargar programa .asm (solo esta CPU)
    # =======================================================
    def load_program(self):
        path = filedialog.askopenfilename(
            title="Seleccionar archivo ASM",
            filetypes=[("Assembly files", "*.asm"), ("Todos los archivos", "*.*")],
        )
        if not path:
            return
        self.load_program_from_path(path)

    # usado desde el botón general "Cargar .asm en ambos"
    def load_program_from_path(self, path: str):
        self.program_path = path
        self._update_mode()  # usar modo actual
        try:
            self.sim = SimulatorAdapter(
                program_path=path,
                hazard_unit_enabled=self.hazard_enabled,
                branch_prediction_enabled=self.prediction_enabled,
            )
            self.start_wall_time = None
            self.metrics_txt.delete("1.0", tk.END)
            self.reg_txt.delete("1.0", tk.END)
            self.mem_txt.delete("1.0", tk.END)
            self.if_var.set("–")
            self.id_var.set("–")
            self.ex_var.set("–")
            self.mem_var.set("–")
            self.wb_var.set("–")
            self.update_status_bar(extra=f"Programa cargado ({os.path.basename(path)})")
        except Exception as e:
            messagebox.showerror(f"Error CPU {self.title}", str(e))

    # =======================================================
    # Ejecución
    # =======================================================
    def step(self):
        if not self.sim:
            messagebox.showwarning(
                f"CPU {self.title}", "Primero carga un programa .asm"
            )
            return
        if self.start_wall_time is None:
            self.start_wall_time = time.time()
        snap = self.sim.step()
        self.display_snapshot(snap)

    def _auto_run(self, delay_s: float):
        last_snap = None
        if self.start_wall_time is None:
            self.start_wall_time = time.time()
        while self.running and self.sim and not self.sim.halted():
            last_snap = self.sim.step()
            self.display_snapshot(last_snap)
            if delay_s > 0:
                time.sleep(delay_s)
        self.running = False
        if last_snap is not None:
            self.display_snapshot(last_snap)

    def run_ritmo(self):
        """Run con delay entre ciclos (modo 'Run (ritmo)')."""
        if not self.sim:
            messagebox.showwarning(
                f"CPU {self.title}", "Primero carga un programa .asm"
            )
            return
        if self.running:
            return
        self.running = True
        t = threading.Thread(
            target=self._auto_run, args=(self.period_ms / 1000.0,), daemon=True
        )
        self.thread = t
        t.start()

    def run_completo(self):
        """Run rápido hasta HALT (sin delay)."""
        if not self.sim:
            messagebox.showwarning(
                f"CPU {self.title}", "Primero carga un programa .asm"
            )
            return
        if self.running:
            return
        self.running = True
        t = threading.Thread(target=self._auto_run, args=(0.0,), daemon=True)
        self.thread = t
        t.start()

    def pause(self):
        self.running = False
        self.update_status_bar(extra="Ejecución pausada")

    def reset(self):
        if self.sim and self.program_path:
            try:
                self.sim = SimulatorAdapter(
                    program_path=self.program_path,
                    hazard_unit_enabled=self.hazard_enabled,
                    branch_prediction_enabled=self.prediction_enabled,
                )
                self.running = False
                self.start_wall_time = None
                self.metrics_txt.delete("1.0", tk.END)
                self.reg_txt.delete("1.0", tk.END)
                self.mem_txt.delete("1.0", tk.END)
                self.if_var.set("–")
                self.id_var.set("–")
                self.ex_var.set("–")
                self.mem_var.set("–")
                self.wb_var.set("–")
                self.update_status_bar(extra="Reiniciado")
            except Exception as e:
                messagebox.showerror(f"Error CPU {self.title}", str(e))

    # =======================================================
    # Visualización
    # =======================================================
    def update_status_bar(self, extra: str | None = None, cycle=None, pc=None, halted=None):
        # tiempo desde el primer step/run
        if self.start_wall_time is not None:
            elapsed = time.time() - self.start_wall_time
            t_str = f"{elapsed:0.3f}s"
        else:
            t_str = "—"

        if cycle is None or pc is None or halted is None:
            base = f"Ciclo: — | Tiempo: {t_str} | PC: — | Halted: —"
        else:
            base = f"Ciclo: {cycle} | Tiempo: {t_str} | PC: {pc} | Halted: {halted}"

        if extra:
            self.status_lbl.config(text=f"{base}  |  {extra}")
        else:
            self.status_lbl.config(text=base)

    def display_snapshot(self, snap: dict):
        if not snap:
            return

        cycle = snap.get("cycle", "—")
        pc = snap.get("pc", "—")
        halted = snap.get("halted", False)
        self.update_status_bar(cycle=cycle, pc=pc, halted=halted)

        # métricas
        if self.sim:
            metrics = self.sim.metrics()
            lines = [
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
                lines.append(f"Precisión predictor: {acc:.2f}%")
            else:
                lines.append("Precisión predictor: —")
            self.metrics_txt.delete("1.0", tk.END)
            self.metrics_txt.insert(tk.END, "\n".join(lines))

        # pipeline
        pipe = snap.get("pipeline") or {}
        self.if_var.set(pipe.get("IF", "–") or "–")
        self.id_var.set(pipe.get("ID", "–") or "–")
        self.ex_var.set(pipe.get("EX", "–") or "–")
        self.mem_var.set(pipe.get("MEM", "–") or "–")
        self.wb_var.set(pipe.get("WB", "–") or "–")

        # registros
        regs = snap.get("registers")
        if isinstance(regs, dict):
            reg_lines = []
            for i in range(32):
                val = regs.get(f"x{i}", 0)
                reg_lines.append(f"x{i:02}: {val}")
            self.reg_txt.delete("1.0", tk.END)
            self.reg_txt.insert(tk.END, "\n".join(reg_lines))

        # memoria (primeras celdas)
        mem = snap.get("memory")
        if isinstance(mem, (list, tuple)):
            max_cells = min(len(mem), 32)
            mem_lines = [f"{addr:08}: {mem[addr]}" for addr in range(max_cells)]
            self.mem_txt.delete("1.0", tk.END)
            self.mem_txt.insert(tk.END, "\n".join(mem_lines))


# ===========================================================
# Ventana principal — Comparador Dual
# ===========================================================
class Controller:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.configure(bg="#1e1e1e")

        # === Barra superior con título y botón general de carga ===
        top_bar = tk.Frame(root, bg="#1e1e1e")
        top_bar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        title_lbl = tk.Label(
            top_bar,
            text="Configuración del procesador (dual) — CE1107 Proyecto 2",
            bg="#1e1e1e",
            fg="#ffffff",
            font=("Segoe UI", 11, "bold"),
        )
        title_lbl.pack(side=tk.LEFT, padx=5)

        self.btn_load_both = tk.Button(
            top_bar, text="Cargar .asm en ambos", command=self.load_program_both
        )
        self.btn_load_both.pack(side=tk.RIGHT, padx=5)

        # === Área central con los dos procesadores ===
        main_frame = tk.Frame(root, bg="#1e1e1e")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)

        self.cpu_a = CPUController(main_frame, "A", column=0)
        self.cpu_b = CPUController(main_frame, "B", column=1)

        # === Controles inferiores (ambos procesadores) ===
        bottom_controls = tk.Frame(root, bg="#1e1e1e")
        bottom_controls.pack(fill=tk.X, padx=5, pady=(0, 4))

        tk.Button(
            bottom_controls, text="Run (ritmo) ambos", command=self.run_ritmo_ambos
        ).pack(side=tk.LEFT, padx=4)
        tk.Button(
            bottom_controls, text="Run completo ambos", command=self.run_completo_ambos
        ).pack(side=tk.LEFT, padx=4)
        tk.Button(
            bottom_controls, text="Pause ambos", command=self.pause_ambos
        ).pack(side=tk.LEFT, padx=4)
        tk.Button(
            bottom_controls, text="Reset ambos", command=self.reset_ambos
        ).pack(side=tk.LEFT, padx=4)

        # === Botón de comparación de métricas ===
        compare_frame = tk.Frame(root, bg="#1e1e1e")
        compare_frame.pack(fill=tk.X, padx=5, pady=(0, 4))
        tk.Button(
            compare_frame,
            text="Comparar métricas finales",
            command=self.compare_metrics,
            bg="#004c40",
            fg="#ffffff",
            font=("Segoe UI", 10, "bold"),
        ).pack(pady=2)

        # === Historial de ejecuciones (últimas 10) ===
        history_frame = tk.LabelFrame(
            root,
            text="Historial últimas 10 ejecuciones",
            padx=4,
            pady=4,
            bg="#1e1e1e",
            fg="#f0f0f0",
        )
        history_frame.pack(fill=tk.BOTH, padx=5, pady=(0, 5))
        self.history_txt = tk.Text(
            history_frame,
            height=4,
            bg="#000000",
            fg="#00ffcc",
            font=("Consolas", 9),
        )
        self.history_txt.pack(fill=tk.BOTH, expand=True)
        self.refresh_history()

    # -------------------------------------------------------
    # Botones globales
    # -------------------------------------------------------
    def load_program_both(self):
        path = filedialog.askopenfilename(
            title="Seleccionar archivo ASM",
            filetypes=[("Assembly files", "*.asm"), ("Todos los archivos", "*.*")],
        )
        if not path:
            return
        self.cpu_a.load_program_from_path(path)
        self.cpu_b.load_program_from_path(path)

    def run_ritmo_ambos(self):
        self.cpu_a.run_ritmo()
        self.cpu_b.run_ritmo()

    def run_completo_ambos(self):
        self.cpu_a.run_completo()
        self.cpu_b.run_completo()

    def pause_ambos(self):
        self.cpu_a.pause()
        self.cpu_b.pause()

    def reset_ambos(self):
        self.cpu_a.reset()
        self.cpu_b.reset()
        self.refresh_history()

    # -------------------------------------------------------
    # Comparación entre CPU A y B
    # -------------------------------------------------------
    def compare_metrics(self):
        if not (self.cpu_a.sim and self.cpu_b.sim):
            messagebox.showwarning("Comparación", "Carga programas en ambas CPUs.")
            return

        mA = self.cpu_a.sim.metrics()
        mB = self.cpu_b.sim.metrics()

        def fmt(m):
            total_pred = m["branch_hits"] + m["branch_misses"]
            acc = (m["branch_hits"] / total_pred) * 100 if total_pred else 0.0
            return (
                f"Ciclos: {m['cycles']}\n"
                f"ALU ops: {m['alu_ops']}\n"
                f"Mem accesos: {m['mem_accesses']}\n"
                f"Saltos: {m['branches']}\n"
                f"Stalls: {m['stalls']}\n"
                f"Precisión pred.: {acc:.2f}%"
            )

        msg = f"=== CPU A ===\n{fmt(mA)}\n\n=== CPU B ===\n{fmt(mB)}"
        messagebox.showinfo("Comparación final", msg)
        self.refresh_history()

    # -------------------------------------------------------
    # Historial (history.txt)
    # -------------------------------------------------------
    def refresh_history(self):
        try:
            with open("history.txt", "r") as f:
                content = f.read()
        except FileNotFoundError:
            content = ""
        self.history_txt.delete("1.0", tk.END)
        if content.strip():
            self.history_txt.insert(tk.END, content)
        else:
            self.history_txt.insert(tk.END, "(Sin ejecuciones registradas aún)")
