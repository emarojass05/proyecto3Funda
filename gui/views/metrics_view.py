import tkinter as tk

class MetricsView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#001a66", bd=2, relief="ridge")

        tk.Label(self, text="Historial de métricas", bg="#001a66", fg="white", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=8, pady=4)
        self.text = tk.Text(self, height=6, bg="#0a0a0a", fg="#00ffcc", font=("Consolas", 9))
        self.text.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

    def update_metrics(self, text):
        self.text.delete("1.0", tk.END)
        self.text.insert(tk.END, text)
