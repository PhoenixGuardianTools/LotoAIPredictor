import tkinter as tk
from tkinter import ttk, messagebox
from utils.facture import generer_facture
from utils.encryption import decrypt_ini
import datetime

class FacturationTab(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack(fill="both", expand=True)

        tk.Label(self, text="Durée de l'abonnement :").pack(anchor="w", padx=5, pady=2)
        self.duree_box = ttk.Combobox(self, values=["1 mois", "3 mois", "6 mois", "1 an"], state="readonly")
        self.duree_box.current(0)
        self.duree_box.pack(fill="x", padx=5, pady=2)

        btn_facture = tk.Button(self, text="📄 Générer une facture + licence", command=self.generer)
        btn_facture.pack(padx=5, pady=10)

    def generer(self):
        duree = self.duree_box.get()
        info = decrypt_ini("SECURITY/config_admin.ini.enc")
        email = info.get("email", "client@example.com")
        today = datetime.datetime.today().strftime("%Y-%m-%d")

        success = generer_facture(nom_client=email, duree=duree, date=today)

        if success:
            messagebox.showinfo("Succès", "Facture et licence générées et envoyées.")
        else:
            messagebox.showerror("Erreur", "Impossible de générer la facture.")
