import tkinter as tk
from tkinter import ttk, messagebox
import os

class FactureTab(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack(fill="both", expand=True)

        tk.Label(self, text="📄 Liste des factures générées").pack(anchor="w", padx=5, pady=5)

        self.liste = tk.Listbox(self)
        self.liste.pack(fill="both", expand=True, padx=5, pady=5)

        refresh_btn = tk.Button(self, text="🔄 Rafraîchir", command=self.charger_factures)
        refresh_btn.pack(padx=5, pady=5)

        self.charger_factures()

    def charger_factures(self):
        self.liste.delete(0, tk.END)
        factures_dir = "FACTURES"
        if not os.path.exists(factures_dir):
            self.liste.insert(tk.END, "Aucune facture trouvée.")
            return
        fichiers = [f for f in os.listdir(factures_dir) if f.endswith(".pdf") or f.endswith(".docx")]
        if not fichiers:
            self.liste.insert(tk.END, "Aucune facture trouvée.")
        else:
            for f in fichiers:
                self.liste.insert(tk.END, f)