import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from LICENSE_ADMIN.license_checker import should_show_promo
from core.encryption import decrypt_ini, import_license_file
import webbrowser

class AccountTab(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack(fill="both", expand=True)

        self.titre = tk.Label(self, text="🔐 Choisissez votre licence :")
        self.titre.pack(fill="x", padx=5, pady=2)

        self.combo = ttk.Combobox(self, values=["1 mois", "3 mois", "6 mois", "1 an"], state="readonly")
        self.combo.current(0)
        self.combo.pack(fill="x", padx=5, pady=2)
        self.combo.bind("<<ComboboxSelected>>", lambda e: self.update_prices())

        self.label_prix = tk.Label(self)
        self.label_prix.pack(fill="x", padx=5, pady=2)

        self.promo_active = should_show_promo()

        self.pay_btn = tk.Button(self, text="💳 Payer avec PayPal", command=self.lancer_paiement)
        self.pay_btn.pack(fill="x", padx=5, pady=2)

        self.import_btn = tk.Button(self, text="📥 Importer licence", command=self.importer_licence)
        self.import_btn.pack(fill="x", padx=5, pady=2)

        self.update_prices()

    def update_prices(self):
        base_prices = {
            "1 mois": 15,
            "3 mois": 40,
            "6 mois": 75,
            "1 an": 120
        }
        choix = self.combo.get()
        prix = base_prices.get(choix, 15)

        if self.promo_active:
            prix_red = round(prix * 0.9, 2)
            self.label_prix.config(
                text=f"💰 Prix : {prix} €  →  {prix_red} € (-10%)", fg="red"
            )
        else:
            self.label_prix.config(text=f"💰 Prix : {prix} €", fg="black")

    def lancer_paiement(self):
        choix = self.combo.get()
        prix = {
            "1 mois": 15,
            "3 mois": 40,
            "6 mois": 75,
            "1 an": 120
        }.get(choix, 15)

        if self.promo_active:
            prix = round(prix * 0.9, 2)

        lien = f"https://paypal.me/phoenixpay?amount={prix}"
        webbrowser.open(lien)

        messagebox.showinfo("Paiement lancé",
            "Merci de finaliser le paiement sur PayPal.\n"
            "Une licence vous sera envoyée par mail.")

    def importer_licence(self):
        fichier = filedialog.askopenfilename(
            title="Sélectionner votre fichier de licence",
            filetypes=[("Licence", "*.key")]
        )
        if fichier:
            try:
                import_license_file(fichier)
                messagebox.showinfo("✅ Licence activée", "Votre licence a été importée.")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur d'import : {e}")
