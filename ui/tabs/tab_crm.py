import tkinter as tk

class CRMTab(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack(fill="both", expand=True)

        tk.Label(self, text="👥 Liste des clients actifs").pack(anchor="w", padx=5, pady=5)

        self.liste = tk.Listbox(self)
        self.liste.pack(fill="both", expand=True, padx=5, pady=5)

        refresh_btn = tk.Button(self, text="🔄 Rafraîchir", command=self.charger_clients)
        refresh_btn.pack(padx=5, pady=5)

        self.charger_clients()

    def charger_clients(self):
        self.liste.delete(0, tk.END)
        try:
            with open("DATABASE/clients.csv", encoding="utf-8") as f:
                for ligne in f:
                    self.liste.insert(tk.END, ligne.strip())
        except Exception:
            self.liste.insert(tk.END, "Aucun client enregistré.")
