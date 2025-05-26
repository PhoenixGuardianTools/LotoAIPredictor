import tkinter as tk
from tkinter import messagebox
from core.exporter import export_to_excel

class ExportTab(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack(fill="both", expand=True)

        tk.Label(self, text="📤 Export des données").pack(anchor="w", padx=5, pady=5)
        export_btn = tk.Button(self, text="Exporter vers Excel", command=self.export)
        export_btn.pack(padx=5, pady=10)

    def export(self):
        try:
            export_to_excel()
            messagebox.showinfo("Export", "Export Excel terminé avec succès.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'export : {e}")
