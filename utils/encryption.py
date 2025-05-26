from cryptography.fernet import Fernet
import json
import os

FERNET_PATH = "SECURITY/fernet.key"

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
    with open("SECURITY/config_admin.ini.enc", "wb") as f:
        f.write(encrypted)

def update_config_admin(data: dict):
    update_config_secure(data)

def import_license_file(path):
    import shutil
    shutil.copy(path, "SECURITY/license.key")
