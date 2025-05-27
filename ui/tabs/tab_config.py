import tkinter as tk
from tkinter import messagebox
from core.encryption import update_config_secure

class ConfigTab(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack(fill="both", expand=True)

        tk.Label(self, text="⚙️ Paramètres SMTP :").pack(anchor="w", padx=5, pady=2)

        tk.Label(self, text="Hôte SMTP").pack(anchor="w", padx=5, pady=2)
        self.smtp_host = tk.Entry(self)
        self.smtp_host.pack(fill="x", padx=5, pady=2)

        tk.Label(self, text="Port SMTP").pack(anchor="w", padx=5, pady=2)
        self.smtp_port = tk.Entry(self)
        self.smtp_port.pack(fill="x", padx=5, pady=2)

        save_btn = tk.Button(self, text="Enregistrer", command=self.save_config)
        save_btn.pack(padx=5, pady=10)

    def save_config(self):
        data = {
            "host": self.smtp_host.get(),
            "port": self.smtp_port.get()
        }
        update_config_secure(data)
        messagebox.showinfo("Enregistré", "Configuration SMTP sauvegardée.")
