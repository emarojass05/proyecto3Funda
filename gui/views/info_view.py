import tkinter as tk

class InfoView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#001a66", bd=2, relief="ridge")

        tk.Label(self, text="Información general", bg="#001a66", fg="white", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=8, pady=4)
        self.label = tk.Label(self, text="Ciclo actual: 0 | PC1: 0 | PC2: 0", bg="#0a0a0a", fg="#00ffcc", font=("Consolas", 10), relief="sunken", width=40)
        self.label.pack(padx=8, pady=(0, 6))

    def update_info(self, cycle, pc1, pc2):
        self.label.config(text=f"Ciclo actual: {cycle} | PC1: {pc1} | PC2: {pc2}")
