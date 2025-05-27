import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from core.encryption import update_config_admin, decrypt_ini

class EnterpriseTab(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack(fill="both", expand=True)

        tk.Label(self, text="Nom entreprise :").pack(anchor="w", padx=5, pady=2)
        self.nom = tk.Entry(self)
        self.nom.pack(fill="x", padx=5, pady=2)

        tk.Label(self, text="SIRET :").pack(anchor="w", padx=5, pady=2)
        self.siret = tk.Entry(self)
        self.siret.pack(fill="x", padx=5, pady=2)

        tk.Label(self, text="TVA :").pack(anchor="w", padx=5, pady=2)
        self.tva = ttk.Combobox(self, values=["Non applicable", "10%", "20%"], state="readonly")
        self.tva.current(0)
        self.tva.pack(fill="x", padx=5, pady=2)

        tk.Label(self, text="Site web :").pack(anchor="w", padx=5, pady=2)
        self.site = tk.Entry(self)
        self.site.pack(fill="x", padx=5, pady=2)

        tk.Label(self, text="Email contact :").pack(anchor="w", padx=5, pady=2)
        self.mail = tk.Entry(self)
        self.mail.pack(fill="x", padx=5, pady=2)

        tk.Label(self, text="Téléphone :").pack(anchor="w", padx=5, pady=2)
        self.tel = tk.Entry(self)
        self.tel.pack(fill="x", padx=5, pady=2)

        tk.Label(self, text="Logo :").pack(anchor="w", padx=5, pady=2)
        self.logo_path = tk.Entry(self)
        self.logo_path.pack(fill="x", padx=5, pady=2)

        logo_btn = tk.Button(self, text="📁 Sélectionner un logo", command=self.select_logo)
        logo_btn.pack(fill="x", padx=5, pady=2)

        save_btn = tk.Button(self, text="💾 Enregistrer", command=self.save)
        save_btn.pack(fill="x", padx=5, pady=10)

    def select_logo(self):
        file = filedialog.askopenfilename(
            title="Sélectionner un logo",
            filetypes=[("Images", "*.png *.jpg *.jpeg")]
        )
        if file:
            self.logo_path.delete(0, tk.END)
            self.logo_path.insert(0, file)

    def save(self):
        data = {
            "entreprise": self.nom.get(),
            "siret": self.siret.get(),
            "tva": self.tva.get(),
            "site": self.site.get(),
            "email_contact": self.mail.get(),
            "tel": self.tel.get(),
            "logo": self.logo_path.get()
        }
        update_config_admin(data)
        messagebox.showinfo("Enregistré", "Configuration entreprise sauvegardée.")
