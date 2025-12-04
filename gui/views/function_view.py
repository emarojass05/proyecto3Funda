import tkinter as tk

class FunctionView(tk.Frame):
    def __init__(self, parent, callbacks: dict):
        super().__init__(parent, bg="#001a66", bd=2, relief="ridge")

        tk.Label(self, text="Funcionalidades", bg="#001a66", fg="white", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=8, pady=(4, 2))
        btn_cfg = dict(width=12, height=1, font=("Segoe UI", 9, "bold"), bg="#262626", fg="#ffffff", activebackground="#0073e6")

        tk.Button(self, text="Run", command=callbacks.get("run"), **btn_cfg).pack(padx=6, pady=3)
        tk.Button(self, text="Paso a Paso", command=callbacks.get("step"), **btn_cfg).pack(padx=6, pady=3)
        tk.Button(self, text="Auto", command=callbacks.get("auto"), **btn_cfg).pack(padx=6, pady=3)
        tk.Button(self, text="Completa", command=callbacks.get("full"), **btn_cfg).pack(padx=6, pady=3)
