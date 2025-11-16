# ===========================================================
# memory_view.py — Visor de memoria con offset dinámico (Bloque 3)
# ===========================================================
import tkinter as tk
from tkinter import ttk


class MemoryView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.offset = tk.IntVar(value=0)
        self.controller_ref = None  # 🆕 se asigna desde app.py

        # ---- Barra superior
        top = ttk.Frame(self)
        top.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(top, text="Offset:").pack(side=tk.LEFT)
        self.spin = ttk.Spinbox(
            top,
            from_=0,
            to=65535,
            textvariable=self.offset,
            width=8,
            command=self._on_offset
        )
        self.spin.pack(side=tk.LEFT, padx=6)

        # ---- Tabla de memoria
        cols = ("Addr", "Valor")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=20)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=100 if c == "Addr" else 300, anchor="center")
        self.tree.pack(fill="both", expand=True)

        # Pre-cargar 16 filas vacías
        for _ in range(16):
            self.tree.insert("", "end", values=("", ""))

    # -------------------------------------------------------
    # Cuando el usuario cambia el offset desde el Spinbox
    # -------------------------------------------------------
    def _on_offset(self):
        try:
            offset = int(self.offset.get())
        except Exception:
            offset = 0

        # Llamar al controlador si existe
        if self.controller_ref:
            self.controller_ref.refresh_offset(offset)
        else:
            print(f"[INFO] Offset cambiado a {offset}, pero sin controller_ref asignado.")

    # -------------------------------------------------------
    # Actualizar las celdas de la memoria
    # -------------------------------------------------------
    def update_memory(self, mem_list):
        # mem_list: [(addr, value), ...]
        for i in self.tree.get_children(""):
            self.tree.delete(i)
        for addr, val in mem_list:
            self.tree.insert("", "end", values=(addr, val))
