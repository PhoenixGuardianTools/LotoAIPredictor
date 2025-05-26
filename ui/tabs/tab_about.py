import tkinter as tk
from LICENSE_ADMIN.license_checker import get_license_info

class AboutTab(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack(fill="both", expand=True)

        info = get_license_info()

        tk.Label(self, text="🧠 Logiciel : LotoAiPredictor", anchor="w", justify="left").pack(fill="x", padx=5, pady=2)
        tk.Label(self, text=f"🔐 Type de licence : {info['type']}", anchor="w", justify="left").pack(fill="x", padx=5, pady=2)
        tk.Label(self, text=f"📅 Expiration : {info['expiration']}", anchor="w", justify="left").pack(fill="x", padx=5, pady=2)
        tk.Label(self, text=f"⏳ Jours restants : {info['jours_restants']}", anchor="w", justify="left").pack(fill="x", padx=5, pady=2)

        if info['type'] == "demo":
            tk.Label(self, text=f"🎟️ Grilles restantes : {info['grilles_restantes']}", anchor="w", justify="left").pack(fill="x", padx=5, pady=2)
