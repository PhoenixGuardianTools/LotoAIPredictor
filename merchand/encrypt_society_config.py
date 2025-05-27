import json
import configparser
from pathlib import Path
from core.encryption import encrypt_config

def encrypt_society_config():
    """Chiffre la configuration de la société."""
    try:
        # Lire la configuration en clair
        config = configparser.ConfigParser()
        config.read("config/society_config.ini")
        
        # Convertir en chaîne
        config_str = ""
        for section in config.sections():
            config_str += f"[{section}]\n"
            for key, value in config[section].items():
                config_str += f"{key} = {value}\n"
            config_str += "\n"
        
        # Chiffrer la configuration
        encrypted_data = encrypt_config({"config": config_str}, "society_key")
        
        # Sauvegarder la configuration chiffrée
        with open("config/society_config.enc", 'w') as f:
            json.dump(encrypted_data, f, indent=4)
            
        print("✅ Configuration chiffrée avec succès")
        
    except Exception as e:
        print(f"⚠️ Erreur lors du chiffrement : {e}")

if __name__ == "__main__":
    encrypt_society_config() 