import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from pathlib import Path

class ConfigWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Configuration initiale")
        self.geometry("800x600")
        
        # Empêcher la fermeture de la fenêtre
        self.protocol("WM_DELETE_WINDOW", lambda: None)
        
        # Création des widgets
        self.create_widgets()
        
        # Centrer la fenêtre
        self.center_window()
    
    def create_widgets(self):
        """Crée les widgets de l'interface."""
        # Frame principal
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titre
        title_label = ttk.Label(main_frame, text="Configuration initiale", font=("Helvetica", 16, "bold"))
        title_label.pack(pady=10)
        
        # Frame pour les informations
        info_frame = ttk.LabelFrame(main_frame, text="Informations personnelles", padding="10")
        info_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Civilité
        ttk.Label(info_frame, text="Civilité:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.civilite = ttk.Combobox(info_frame, values=["Monsieur", "Madame", "Mademoiselle"])
        self.civilite.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        # Nom
        ttk.Label(info_frame, text="Nom:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.nom = ttk.Entry(info_frame)
        self.nom.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        # Prénom
        ttk.Label(info_frame, text="Prénom:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.prenom = ttk.Entry(info_frame)
        self.prenom.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        # Email
        ttk.Label(info_frame, text="Email:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.email = ttk.Entry(info_frame)
        self.email.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        
        # Téléphone
        ttk.Label(info_frame, text="Téléphone:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.telephone = ttk.Entry(info_frame)
        self.telephone.grid(row=4, column=1, padx=5, pady=5, sticky="w")
        
        # Frame pour les boutons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        # Bouton Valider
        ttk.Button(btn_frame, text="Valider", command=self.validate).pack(side=tk.RIGHT, padx=5)
    
    def center_window(self):
        """Centre la fenêtre sur l'écran."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def validate(self):
        """Valide les informations saisies."""
        # Vérification des champs obligatoires
        if not all([self.nom.get(), self.prenom.get(), self.email.get()]):
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs obligatoires")
            return
        
        # Création du dossier config s'il n'existe pas
        config_dir = Path("config")
        config_dir.mkdir(exist_ok=True)
        
        # Création de la configuration
        config = {
            "user": {
                "civilite": self.civilite.get(),
                "nom": self.nom.get(),
                "prenom": self.prenom.get(),
                "email": self.email.get(),
                "telephone": self.telephone.get()
            }
        }
        
        # Sauvegarde de la configuration
        config_file = config_dir / "user_config.json"
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        
        # Fermeture de la fenêtre
        self.destroy()
        
        # Ouverture de la fenêtre d'accueil
        from ui.frm.frm_accueil import AccueilWindow
        AccueilWindow(self.master)

def show_config_window(parent):
    """Affiche la fenêtre de configuration."""
    window = ConfigWindow(parent)
    parent.wait_window(window) 