import sys
import os

# Ajouter le répertoire courant au PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(current_dir)
sys.path.append(parent_dir)

from ui.gui import launch_app
from core.database import init_db
from core.scheduler import launch_in_background
from LICENSE_ADMIN.license_checker import get_user_permissions, is_demo_mode, check_expiration_alert

def main():
    print("=== Lancement de LotoAiPredictor ===")
    
    # Initialisation de la base de données
    init_db()
    
    # Vérification des permissions
    permissions = get_user_permissions()
    
    # Affichage du mode
    if permissions['is_admin']:
        print("👑 Mode Administrateur")
    elif permissions['is_client']:
        print("👤 Mode Client")
    else:
        print("🎮 Mode Démo")
    
    # Vérification des alertes de licence
    check_expiration_alert()
    
    # Démarrage des tâches en arrière-plan
    launch_in_background()
    
    # Lancement de l'application avec les permissions
    launch_app(permissions)

if __name__ == "__main__":
    main()
