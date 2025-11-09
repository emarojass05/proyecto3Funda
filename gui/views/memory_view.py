# memory_view.py — visor de memoria con offset (16 entradas)
import tkinter as tk
from tkinter import ttk

class MemoryView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.offset = tk.IntVar(value=0)

        top = ttk.Frame(self)
        top.pack(side=tk.TOP, fill=tk.X)
        ttk.Label(top, text="Offset:").pack(side=tk.LEFT)
        self.spin = ttk.Spinbox(top, from_=0, to=65535, textvariable=self.offset, width=8, command=self._on_offset)
        self.spin.pack(side=tk.LEFT, padx=6)

        cols = ("Addr", "Valor")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=20)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=100 if c=="Addr" else 300, anchor="center")
        self.tree.pack(fill="both", expand=True)

        for _ in range(16):
            self.tree.insert("", "end", values=("", ""))

    def _on_offset(self):
        # En esta versión base, el Controller refresca el snapshot.
        # Si quieres paginar aquí, puedes disparar un evento o callback.
        pass

    def update_memory(self, mem_list):
        # mem_list: [(addr, value), ...]
        for i in self.tree.get_children(""):
            self.tree.delete(i)
        for addr, val in mem_list:
            self.tree.insert("", "end", values=(addr, val))
