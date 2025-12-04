# ===========================================================
# pipeline_view.py — Canvas con las 5 etapas (Bloque 3 mejorado)
# ===========================================================
import tkinter as tk
from tkinter import ttk


class PipelineView(ttk.Frame):
    STAGES = ["IF", "ID", "EX", "MEM", "WB"]

    # 🎨 Colores personalizados por etapa
    STAGE_COLORS = {
        "IF":  "#4ec9b0",   # verde agua
        "ID":  "#569cd6",   # azul
        "EX":  "#ce9178",   # naranja
        "MEM": "#c586c0",   # violeta
        "WB":  "#dcdcaa",   # amarillo
    }

    def __init__(self, parent):
        super().__init__(parent)
        self.canvas = tk.Canvas(self, background="#111", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.bind("<Configure>", self._redraw)
        self._data = {s: "—" for s in self.STAGES}
        self._cycle = 0

    # -------------------------------------------------------
    # Actualiza la información mostrada en cada etapa
    # -------------------------------------------------------
    def update_pipeline(self, data, cycle):
        if data:
            for st in self.STAGES:
                if st in data:
                    self._data[st] = data[st]
        self._cycle = cycle
        self._redraw()

    # -------------------------------------------------------
    # Dibuja las cajas y el contenido del pipeline
    # -------------------------------------------------------
    def _redraw(self, event=None):
        w = self.winfo_width()
        h = self.winfo_height()
        self.canvas.delete("all")

        pad = 20
        box_w = max(120, (w - pad * (len(self.STAGES) + 1)) // len(self.STAGES))
        box_h = int(h * 0.6)
        y0 = (h - box_h) // 2

        # Título
        self.canvas.create_text(
            10, 10, anchor="nw", fill="#ddd",
            text=f"Pipeline — Ciclo {self._cycle}"
        )

        # Dibujar cada etapa con su color
        for i, st in enumerate(self.STAGES):
            x0 = pad + i * (box_w + pad)
            x1 = x0 + box_w
            y1 = y0 + box_h

            # Color por etapa
            color = self.STAGE_COLORS.get(st, "#6cf")

            # Fondo y borde
            self.canvas.create_rectangle(
                x0, y0, x1, y1,
                fill="#222", outline=color, width=3
            )

            # Nombre de la etapa
            self.canvas.create_text(
                (x0 + x1) // 2, y0 + 18,
                fill=color,
                text=st,
                font=("TkDefaultFont", 12, "bold")
            )

            # Contenido de la etapa (instrucción)
            instr = self._data.get(st, "—")
            wrapped = self._wrap(instr, max_chars=28)
            self.canvas.create_text(
                (x0 + x1) // 2, (y0 + y1) // 2,
                fill="#ddd",
                text=wrapped,
                justify="center"
            )

    # -------------------------------------------------------
    # Formatea texto para que no se desborde de la caja
    # -------------------------------------------------------
    def _wrap(self, s, max_chars=28):
        if not isinstance(s, str):
            s = str(s)
        lines = []
        while len(s) > max_chars:
            cut = s.rfind(" ", 0, max_chars)
            if cut <= 0:
                cut = max_chars
            lines.append(s[:cut])
            s = s[cut:].lstrip()
        lines.append(s)
        return "\n".join(lines)
