from cryptography.fernet import Fernet
import json
import os
from pathlib import Path

# Chemin relatif au dossier APP/SECURITY
FERNET_PATH = Path(__file__).resolve().parent.parent / "SECURITY" / "fernet.key"

def load_key():
    with open(FERNET_PATH, "rb") as f:
        return Fernet(f.read())

def decrypt_ini(enc_file):
    fernet = load_key()
    with open(enc_file, "rb") as f:
        data = fernet.decrypt(f.read())
    return json.loads(data)

def update_config_secure(data: dict):
    fernet = load_key()
    encrypted = fernet.encrypt(json.dumps(data).encode())
    config_path = Path(__file__).resolve().parent.parent / "SECURITY" / "config_admin.ini.enc"
    with open(config_path, "wb") as f:
        f.write(encrypted)

def update_config_admin(data: dict):
    update_config_secure(data)

def import_license_file(path):
    import shutil
    license_path = Path(__file__).resolve().parent.parent / "SECURITY" / "license.key"
    shutil.copy(path, license_path) 