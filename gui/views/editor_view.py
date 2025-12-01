import tkinter as tk
from tkinter import filedialog, messagebox

class EditorView(tk.Frame):
    def __init__(self, parent, on_load_callback=None):
        super().__init__(parent, bg="#001a66", bd=2, relief="ridge")

        self.on_load_callback = on_load_callback  # función externa para cargar ASM

        # === Título ===
        tk.Label(
            self,
            text="Editor de instrucciones",
            bg="#001a66",
            fg="white",
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", padx=8, pady=(4, 2))

        # === Área de texto ===
        self.textbox = tk.Text(
            self,
            height=10,
            bg="#000000",
            fg="#00ffcc",
            insertbackground="white",
            font=("Consolas", 11),
        )
        self.textbox.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)

        # === Botones del editor ===
        btn_frame = tk.Frame(self, bg="#001a66")
        btn_frame.pack(fill=tk.X, padx=6, pady=(0, 4))

        tk.Button(
            btn_frame,
            text="Cargar .asm",
            bg="#004c99",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            command=self.load_asm_file,
        ).pack(side=tk.LEFT, padx=3)

        tk.Button(
            btn_frame,
            text="Ejecutar desde editor",
            bg="#007a3d",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            command=self.run_from_editor,
        ).pack(side=tk.LEFT, padx=3)

    # ============================================================
    # Función: Cargar archivo .asm desde el disco
    # ============================================================
    def load_asm_file(self):
        path = filedialog.askopenfilename(
            title="Seleccionar archivo ASM",
            filetypes=[("Archivos ASM", "*.asm"), ("Todos los archivos", "*.*")],
        )
        if not path:
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                code = f.read()
            self.textbox.delete("1.0", tk.END)
            self.textbox.insert("1.0", code)

            # Notificar al controlador (si hay callback)
            if self.on_load_callback:
                self.on_load_callback(path)
        except Exception as e:
            messagebox.showerror("Error al cargar archivo", str(e))

    # ============================================================
    # Función: Ejecutar directamente el texto del editor
    # ============================================================
    def run_from_editor(self):
        if not self.on_load_callback:
            messagebox.showwarning("Sin controlador", "No hay conexión con el simulador.")
            return

        code = self.textbox.get("1.0", tk.END).strip()
        if not code:
            messagebox.showwarning("Editor vacío", "Escribe o carga un programa antes de ejecutar.")
            return

        temp_path = "temp_editor.asm"
        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                f.write(code)
            # Notificar al controlador que ejecute este archivo
            self.on_load_callback(temp_path)
        except Exception as e:
            messagebox.showerror("Error al guardar temporal", str(e))
