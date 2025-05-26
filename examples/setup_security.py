import sys
import os
from pathlib import Path
import time
import getpass

# Ajouter le dossier racine du projet au PYTHONPATH
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from cryptography.fernet import Fernet
import json

def get_input(prompt):
    """Fonction pour obtenir une entrée utilisateur avec une pause"""
    print("\n" + "="*50)
    print(prompt)
    print("="*50)
    return input("> ")

def setup_security():
    print("\n🔐 Configuration de la sécurité...")
    time.sleep(1)
    
    # Création du dossier SECURITY s'il n'existe pas
    security_dir = Path(__file__).resolve().parent.parent / "SECURITY"
    security_dir.mkdir(parents=True, exist_ok=True)
    
    # Génération de la clé Fernet
    key_path = security_dir / "fernet.key"
    if not key_path.exists():
        print("\n🔑 Génération d'une nouvelle clé Fernet...")
        key = Fernet.generate_key()
        with open(key_path, "wb") as f:
            f.write(key)
        print("✅ Clé Fernet générée avec succès")
    else:
        print("\nℹ️ La clé Fernet existe déjà")
    
    # Configuration SMTP avec les valeurs prédéfinies
    print("\n📧 Configuration des paramètres SMTP...")
    
    # Demande sécurisée du mot de passe
    print("\nEntrez le mot de passe SMTP (il ne sera pas affiché) :")
    password = getpass.getpass("> ")
    
    smtp_config = {
        "EMAIL": {
            "smtp_server": "smtp.riseup.net",
            "smtp_port": "587",
            "sender": "phoenix38@riseup.net",
            "password": password
        }
    }
    
    # Chiffrement de la configuration
    print("\n🔒 Chiffrement de la configuration...")
    time.sleep(1)
    
    with open(key_path, "rb") as f:
        key = f.read()
    fernet = Fernet(key)
    encrypted = fernet.encrypt(json.dumps(smtp_config).encode())
    
    config_path = security_dir / "config_admin.ini.enc"
    with open(config_path, "wb") as f:
        f.write(encrypted)
    
    print("\n✅ Configuration chiffrée et sauvegardée avec succès")
    print(f"Fichier de configuration : {config_path}")

if __name__ == "__main__":
    setup_security() 