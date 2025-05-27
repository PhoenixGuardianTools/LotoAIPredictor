import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import webbrowser
from PIL import Image, ImageTk

# Ajouter le répertoire courant au PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(current_dir)
sys.path.append(parent_dir)

from ui.gui import launch_app
from core.database import init_db
from core.scheduler import launch_in_background
from LICENSE_ADMIN.license_checker import get_user_permissions, is_demo_mode, check_expiration_alert
from ui.first_run import FirstRunDialog
from core.config_manager import ConfigManager
from ui.frm.frm_config import show_config_window
from LICENSE_ADMIN.license_text import MIT_LICENSE

class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Configuration de la fenêtre principale
        self.title("LotoAI Predictor")
        self.withdraw()  # Cache la fenêtre principale
        
        # Chargement de l'icône
        self.load_icon()
        
        # Création du menu contextuel
        self.create_context_menu()
        
        # Liaison du clic droit
        self.bind("<Button-3>", self.show_context_menu)
        
        # Vérification de la première exécution
        if check_first_run():
            # Affichage de la configuration initiale
            show_config_window(self)
    
    def load_icon(self):
        """Charge l'icône de l'application."""
        try:
            icon_path = os.path.join(current_dir, "WEB", "assets", "Logo_LotoAIPredictor.png")
            if os.path.exists(icon_path):
                icon = Image.open(icon_path)
                photo = ImageTk.PhotoImage(icon)
                self.iconphoto(True, photo)
        except Exception as e:
            print(f"Erreur lors du chargement de l'icône : {e}")
    
    def create_context_menu(self):
        """Crée le menu contextuel."""
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Mettre à jour", command=self.update_app)
        self.context_menu.add_command(label="À propos", command=self.show_about)
        self.context_menu.add_command(label="Licence MIT", command=self.show_license)
        self.context_menu.add_command(label="GitHub", command=self.open_github)
    
    def show_context_menu(self, event):
        """Affiche le menu contextuel."""
        self.context_menu.post(event.x_root, event.y_root)
    
    def update_app(self):
        """Met à jour l'application."""
        # TODO: Implémenter la mise à jour
        messagebox.showinfo("Mise à jour", "Recherche de mises à jour...")
    
    def show_about(self):
        """Affiche la boîte de dialogue À propos."""
        try:
            from ui.tabs.tab_about import show_about_dialog
            show_about_dialog(self)
        except ImportError:
            messagebox.showinfo("À propos", "LotoAI Predictor\nVersion 1.0.0")
    
    def show_license(self):
        """Affiche la licence MIT."""
        dialog = tk.Toplevel(self)
        dialog.title("Licence MIT")
        dialog.geometry("600x400")
        
        # Empêcher l'interaction avec la fenêtre principale
        dialog.transient(self)
        dialog.grab_set()
        
        # Frame principal avec scrollbar
        main_frame = ttk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Création du widget Text avec scrollbar
        text_widget = tk.Text(main_frame, wrap=tk.WORD, padx=10, pady=10)
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        # Placement des widgets
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Insertion du texte de la licence
        text_widget.insert(tk.END, MIT_LICENSE)
        text_widget.configure(state='disabled')  # Rendre le texte en lecture seule
        
        # Bouton Fermer
        ttk.Button(dialog, text="Fermer", command=dialog.destroy).pack(pady=10)
        
        # Centrer la fenêtre
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
    
    def open_github(self):
        """Ouvre la page GitHub du projet."""
        webbrowser.open("https://github.com/PhoenixGuardianTools/LotoAIPredictor/")

def check_first_run():
    """Vérifie si c'est la première exécution."""
    config_file = Path("config/user_config.json")
    return not config_file.exists()

def main():
    """Point d'entrée principal de l'application."""
    from ui.frm.frm_accueil import show_accueil_window
    show_accueil_window()

if __name__ == "__main__":
    main()
