import sys
import os
from pathlib import Path
import webbrowser
from PIL import Image, ImageTk

# Ajouter le repertoire courant au PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(current_dir)
sys.path.append(parent_dir)

from core.database import init_db
from core.scheduler import launch_in_background
from LICENSE_ADMIN.license_checker import get_user_permissions, is_demo_mode, check_expiration_alert
from view.first_run import FirstRunDialog, show_first_run_dialog
from core.config_manager import ConfigManager
from view.config import ConfigWindow, show_config_window
from LICENSE_ADMIN.license_text import MIT_LICENSE
from view.windows.accueil import show_accueil_window

def check_first_run():
    """Verifie si c'est la premiere execution."""
    config_file = Path("config/user_config.json")
    if not config_file.exists():
        dialog = FirstRunDialog(None)
        dialog.mainloop()
        return True
    return False

def main():
    """Point d'entree principal de l'application."""
    # Verification de la premiere execution
    if check_first_run():
        # Affichage de la configuration initiale
        show_config_window(None)
    
    # Lancement de la fenetre d'accueil
    show_accueil_window()

if __name__ == "__main__":
    main() 