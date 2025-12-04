import tkinter as tk

class ConfigView(tk.Frame):
    def __init__(self, parent, modes_callback):
        super().__init__(parent, bg="#001a66", bd=2, relief="ridge")

        tk.Label(
            self,
            text="Configuración de procesadores",
            bg="#001a66",
            fg="white",
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", padx=8, pady=(4, 4))

        frame = tk.Frame(self, bg="#001a66")
        frame.pack(fill=tk.BOTH, expand=True)

        # Variables para cada CPU
        self.mode_vars = [tk.StringVar(value="a"), tk.StringVar(value="a")]

        # Opciones de modos
        options = [
            ("Sin Unidad de Riesgos", "a"),
            ("Con Unidad de Riesgos", "b"),
            ("Predicción de Saltos", "c"),
            ("Riesgos + Predicción", "d"),
        ]

        for i, lbl in enumerate(["Procesador 1", "Procesador 2"]):
            cpu_id = f"P{i+1}"
            block = tk.LabelFrame(frame, text=lbl, bg="#001a66", fg="white")
            block.grid(row=0, column=i, padx=8, pady=4, sticky="nsew")

            for text, val in options:
                tk.Radiobutton(
                    block,
                    text=text,
                    variable=self.mode_vars[i],
                    value=val,
                    bg="#001a66",
                    fg="white",
                    selectcolor="#003399",
                    command=lambda cpu=cpu_id, v=val: modes_callback(cpu, v),
                ).pack(anchor="w", padx=5)

        frame.columnconfigure((0, 1), weight=1)
