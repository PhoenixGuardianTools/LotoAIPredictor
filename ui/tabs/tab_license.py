import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
from APP.core.database import get_user_permissions, get_machine_uuid
from APP.core.license_manager import LicenseManager
from pathlib import Path
import platform

class LicenseTab(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        
        # Initialisation du gestionnaire de licences
        db_path = Path(__file__).resolve().parent.parent.parent / "data" / "phoenix.db"
        self.license_manager = LicenseManager(db_path)
        
        # Récupération des permissions
        self.permissions = get_user_permissions()
        
        # Création de l'interface
        self._create_widgets()
        
        # Mise à jour des informations
        self._update_info()
    
    def _create_widgets(self):
        """Crée les widgets de l'interface."""
        # Titre
        title = "🔑 Gestion des Licences" if self.permissions['is_admin'] else "📋 État de la Licence"
        tk.Label(self, text=title, font=("Arial", 14, "bold")).pack(pady=10)
        
        # Frame pour les informations
        info_frame = ttk.LabelFrame(self, text="Informations")
        info_frame.pack(fill="x", padx=10, pady=5)
        
        # UUID de la machine
        tk.Label(info_frame, text="UUID Machine:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.uuid_label = tk.Label(info_frame, text=get_machine_uuid())
        self.uuid_label.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        # Type de licence
        tk.Label(info_frame, text="Type de Licence:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.type_label = tk.Label(info_frame, text="")
        self.type_label.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        
        # Date d'expiration
        tk.Label(info_frame, text="Date d'Expiration:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.expiration_label = tk.Label(info_frame, text="")
        self.expiration_label.grid(row=2, column=1, sticky="w", padx=5, pady=2)
        
        # Statut
        tk.Label(info_frame, text="Statut:").grid(row=3, column=0, sticky="w", padx=5, pady=2)
        self.status_label = tk.Label(info_frame, text="")
        self.status_label.grid(row=3, column=1, sticky="w", padx=5, pady=2)
        
        # Frame pour l'activation (uniquement en mode démo)
        if self.permissions['is_demo']:
            activation_frame = ttk.LabelFrame(self, text="Activation")
            activation_frame.pack(fill="x", padx=10, pady=5)
            
            tk.Label(activation_frame, text="Clé de Licence:").pack(side="left", padx=5)
            self.license_entry = tk.Entry(activation_frame, width=30)
            self.license_entry.pack(side="left", padx=5)
            
            activate_btn = tk.Button(activation_frame, text="Activer", command=self._activate_license)
            activate_btn.pack(side="left", padx=5)
    
    def _update_info(self):
        """Met à jour les informations affichées."""
        if self.permissions['is_admin']:
            self.type_label.config(text="Administrateur (Illimitée)")
            self.expiration_label.config(text="N/A")
            self.status_label.config(text="Active")
        else:
            # Récupération des informations de licence
            license_info = self.license_manager.get_license_info(get_machine_uuid())
            
            if license_info:
                self.type_label.config(text=license_info['type'].capitalize())
                self.expiration_label.config(text=license_info['expiration'])
                self.status_label.config(text=license_info['status'].capitalize())
            else:
                self.type_label.config(text="Démo")
                self.expiration_label.config(text="N/A")
                self.status_label.config(text="Non activée")
    
    def _activate_license(self):
        """Active une licence."""
        license_key = self.license_entry.get().strip()
        
        if not license_key:
            messagebox.showerror("Erreur", "Veuillez entrer une clé de licence")
            return
        
        # Récupération des informations de la machine
        machine_info = {
            'platform': platform.system(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'node': platform.node()
        }
        
        # Activation de la licence
        if self.license_manager.activate_license(license_key, machine_info):
            messagebox.showinfo("Succès", "Licence activée avec succès")
            self._update_info()
        else:
            messagebox.showerror("Erreur", "Impossible d'activer la licence") 