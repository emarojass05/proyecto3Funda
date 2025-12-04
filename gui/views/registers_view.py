# registers_view.py — Treeview con x0..x31
from tkinter import ttk

class RegistersView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        cols = ("Reg", "Valor")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=16)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=80, anchor="center")
        self.tree.pack(fill="both", expand=True)

        # preload rows
        for i in range(32):
            self.tree.insert("", "end", iid=f"r{i}", values=(f"x{i:02}", 0))

    def update_registers(self, regs_list):
        if not regs_list:
            return
        for i, v in enumerate(regs_list):
            try:
                self.tree.item(f"r{i}", values=(f"x{i:02}", v))
            except Exception:
                pass
