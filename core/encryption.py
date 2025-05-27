from cryptography.fernet import Fernet
import json
import os
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from pathlib import Path

# Chemin relatif au dossier APP/SECURITY
FERNET_PATH = "SECURITY/fernet.key"

def get_fernet_key():
    """Récupère la clé Fernet depuis le fichier."""
    key_path = Path(__file__).resolve().parent.parent / "SECURITY" / "fernet.key"
    try:
        with open(key_path, 'rb') as key_file:
            return key_file.read()
    except Exception as e:
        print(f"Erreur lors de la lecture de la clé : {e}")
        return None

def decrypt_ini(file_path):
    """Décrypte un fichier .ini.enc."""
    try:
        key = get_fernet_key()
        if not key:
            return {}
            
        f = Fernet(key)
        with open(file_path, 'rb') as file:
            encrypted_data = file.read()
            decrypted_data = f.decrypt(encrypted_data)
            return json.loads(decrypted_data)
    except Exception as e:
        print(f"Erreur lors du décryptage : {e}")
        return {}

def update_config_secure(data):
    """Met à jour le fichier de configuration de manière sécurisée."""
    try:
        key = get_fernet_key()
        if not key:
            return False
            
        f = Fernet(key)
        config_path = Path(__file__).resolve().parent.parent / "SECURITY" / "config_admin.ini.enc"
        
        # Encrypter les données
        encrypted_data = f.encrypt(json.dumps(data).encode())
        
        # Sauvegarder le fichier
        with open(config_path, 'wb') as file:
            file.write(encrypted_data)
            
        return True
    except Exception as e:
        print(f"Erreur lors de la mise à jour de la configuration : {e}")
        return False

def update_config_admin(data: dict):
    update_config_secure(data)

def import_license_file(path):
    import shutil
    shutil.copy(path, "SECURITY/license.key")

def generate_key(password: str, salt: bytes = None) -> tuple[bytes, bytes]:
    """Génère une clé de chiffrement à partir d'un mot de passe."""
    if salt is None:
        salt = os.urandom(16)
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key, salt

def encrypt_config(config_data: dict, password: str) -> dict:
    """Chiffre les données de configuration."""
    # Génération de la clé
    key, salt = generate_key(password)
    f = Fernet(key)
    
    # Conversion des données en JSON puis chiffrement
    json_data = json.dumps(config_data)
    encrypted_data = f.encrypt(json_data.encode())
    
    return {
        'data': encrypted_data.decode(),
        'salt': base64.b64encode(salt).decode()
    }

def decrypt_config(encrypted_config: dict, password: str) -> dict:
    """Déchiffre les données de configuration."""
    # Récupération du sel et génération de la clé
    salt = base64.b64decode(encrypted_config['salt'])
    key, _ = generate_key(password, salt)
    f = Fernet(key)
    
    # Déchiffrement et conversion en dictionnaire
    decrypted_data = f.decrypt(encrypted_config['data'].encode())
    return json.loads(decrypted_data.decode()) 