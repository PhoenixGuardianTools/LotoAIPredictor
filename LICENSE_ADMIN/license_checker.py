import datetime
from pathlib import Path
import platform
import uuid
import hashlib
import json
import sqlite3
import os
import sys

# Ajouter le répertoire parent au PYTHONPATH
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.append(str(parent_dir))

from core.encryption import decrypt_ini, update_config_secure

# Chemins des fichiers
BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "SECURITY" / "config_admin.ini.enc"
DB_PATH = BASE_DIR / "data" / "phoenix.db"
LICENSE_PATH = BASE_DIR / "SECURITY" / "license_PhoenixProject.key.enc"
PROMO_PATH = BASE_DIR / "PROMOTIONS" / "promo_templates.json"
BANDEAU_PATH = BASE_DIR / "PROMOTIONS" / "bandeau_default.json"
ALERT_LOG_FILE = BASE_DIR / "LICENSE_ADMIN" / "alert_sent.log"

#Licence
FERNET_KEY_FILE = BASE_DIR / "SECURITY" / "fernet.key"

# Configuration email
RECIPIENT = "phoenix38@riseup.net"
SENDER = "phoenix38@riseup.net"
SMTP_SERVER = "mail.riseup.net"
PORT = 465

def load_alert_log():
    """Charge le journal des alertes envoyées."""
    if os.path.exists(ALERT_LOG_FILE):
        with open(ALERT_LOG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_alert_log(log):
    """Sauvegarde le journal des alertes."""
    with open(ALERT_LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)

def send_alert(days_left, exp_date):
    """Envoie une alerte d'expiration de licence."""
    subject = f"⚠️ Alerte : Licence expirera dans {days_left} jours"
    body = f"Votre licence expire le {exp_date}.\nRenouvelez-la avant expiration pour conserver l'accès complet."
    send_email(subject, body, RECIPIENT, SMTP_SERVER, PORT, SENDER)
    print(f"[✓] Alerte J-{days_left} envoyée.")

def check_expiration_alert():
    """Vérifie et envoie les alertes d'expiration de licence."""
    try:
        # Vérification de la licence admin
        if is_admin_license():
            data = get_license_data()
            if data.get("expiration") == "illimité":
                return

            exp = datetime.datetime.strptime(data["expiration"], "%Y-%m-%d")
            now = datetime.datetime.utcnow()
            days_left = (exp - now).days

            log = load_alert_log()

            if days_left <= 30 and "30d" not in log:
                send_alert(30, exp.date())
                log["30d"] = True
            if days_left <= 7 and "7d" not in log:
                send_alert(7, exp.date())
                log["7d"] = True
            if days_left <= 2 and "48h" not in log:
                send_alert(2, exp.date())
                log["48h"] = True

            save_alert_log(log)
            return

        # Vérification de la licence client
        has_license, license_info = check_client_license()
        if has_license:
            exp = datetime.datetime.strptime(license_info['expiration'], "%Y-%m-%d")
            now = datetime.datetime.utcnow()
            days_left = (exp - now).days

            log = load_alert_log()
            client_key = f"client_{get_machine_uuid()}"

            if days_left <= 30 and f"{client_key}_30d" not in log:
                send_alert(30, exp.date())
                log[f"{client_key}_30d"] = True
            if days_left <= 7 and f"{client_key}_7d" not in log:
                send_alert(7, exp.date())
                log[f"{client_key}_7d"] = True
            if days_left <= 2 and f"{client_key}_48h" not in log:
                send_alert(2, exp.date())
                log[f"{client_key}_48h"] = True

            save_alert_log(log)

    except Exception as e:
        print(f"[✗] Erreur dans le contrôle de licence : {e}")

def get_config():
    """Récupère la configuration depuis le fichier encrypté."""
    try:
        return decrypt_ini(CONFIG_PATH)
    except Exception as e:
        print(f"⚠️ Erreur lors de la lecture de la configuration : {e}")
        return {}

def get_license_info():
    """Retourne les informations de la licence."""
    try:
        config = get_config()
        return {
            'type': config.get('LICENSE', {}).get('type', 'demo'),
            'expiration': config.get('LICENSE', {}).get('expiration', 'N/A'),
            'jours_restants': 999999,  # Valeur fixe pour la licence illimitée
            'grilles_restantes': int(config.get('LICENSE', {}).get('grilles_restantes', 0))
        }
    except Exception as e:
        print(f"⚠️ Erreur lors de la récupération des infos de licence : {e}")
        return {
            'type': 'demo',
            'expiration': 'N/A',
            'jours_restants': 0,
            'grilles_restantes': 0
        }

def is_admin_license():
    """Vérifie si l'utilisateur a une licence admin valide."""
    try:
        config = get_config()
        return config.get('LICENSE', {}).get('type') == 'unlimited' and config.get('LICENSE', {}).get('status') == 'active'
    except Exception as e:
        print(f"⚠️ Erreur lors de la vérification de la licence admin : {e}")
        return False

def get_machine_uuid():
    """
    Génère un UUID unique pour la machine basé sur les caractéristiques matérielles.
    Pour la licence admin, retourne l'UUID stocké dans la configuration.
    """
    try:
        config = get_config()
        return config.get('LICENSE', {}).get('uuid', 'default-uuid')
    except Exception as e:
        print(f"⚠️ Erreur lors de la récupération de l'UUID : {e}")
        return 'default-uuid'

def get_email_config():
    """Récupère la configuration email depuis le fichier encrypté."""
    try:
        config = get_config()
        return {
            'recipient': config.get('EMAIL', {}).get('recipient'),
            'sender': config.get('EMAIL', {}).get('sender'),
            'smtp_server': config.get('EMAIL', {}).get('smtp_server'),
            'port': config.get('EMAIL', {}).get('port'),
            'password': config.get('EMAIL', {}).get('password')
        }
    except Exception as e:
        print(f"⚠️ Erreur lors de la récupération de la config email : {e}")
        return {}

def get_license_data():
    """Récupère les données de licence admin."""
    try:
        return decrypt_ini(CONFIG_PATH)
    except Exception:
        return {}

def get_license_path():
    """Retourne le chemin de la licence admin."""
    return Path(__file__).resolve().parent.parent / "SECURITY" / "license_PhoenixProject.key.enc"

def check_client_license():
    """
    Vérifie si l'utilisateur a une licence client valide.
    Retourne un tuple (bool, dict) : (validité de la licence, infos de la licence)
    """
    try:
        machine_uuid = get_machine_uuid()
        
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT licence_type, date_expiration, status
                FROM licence_client
                WHERE uuid = ?
            """, (machine_uuid,))
            
            result = cursor.fetchone()
            if not result:
                return False, None
                
            licence_type, expiration_date, status = result
            
            # Vérification de la date d'expiration
            if datetime.datetime.strptime(expiration_date, '%Y-%m-%d') < datetime.datetime.today():
                return False, None
                
            # Vérification du statut
            if status != 'active':
                return False, None
                
            return True, {
                'type': licence_type,
                'expiration': expiration_date,
                'status': status
            }
            
    except Exception as e:
        print(f"⚠️ Erreur lors de la vérification de la licence client : {e}")
        return False, None

def is_demo_mode():
    """Vérifie si l'application est en mode démo."""
    return not is_admin_license()

def get_days_remaining():
    """Calcule le nombre de jours restants avant expiration."""
    if is_admin_license():
        return 999999  # Illimité pour les admins
        
    has_license, license_info = check_client_license()
    if not has_license:
        return 0
        
    try:
        exp = datetime.datetime.strptime(license_info['expiration'], "%Y-%m-%d")
        delta = (exp - datetime.datetime.today()).days
        return max(0, delta)
    except:
        return 0

def should_show_reminder():
    """Vérifie si un rappel de licence doit être affiché."""
    info = get_license_info()
    if info['type'] == 'demo':
        return True
    return info['jours_restants'] <= 7

def should_show_promo():
    """Vérifie si une promotion doit être affichée."""
    return is_demo_mode()

def get_promo_bandeau():
    """Récupère le bandeau de promotion."""
    if not should_show_promo():
        return None
        
    promo = get_active_promo()
    if not promo:
        return load_bandeau()
        
    return {
        "bandeau": {
            "text": f"🔥 Promo exceptionnelle : {promo['percentage']}% de réduction avec le code {promo['code']} ! 🔥",
            "color": "#FF4500",
            "background": "#FFF5E5"
        }
    }

def get_user_permissions():
    """
    Retourne les permissions de l'utilisateur.
    """
    permissions = {
        'is_admin': False,
        'is_client': False,
        'is_demo': True,
        'can_access_crm': False,
        'can_access_billing': False,
        'can_play': True,
        'can_feedback': True,
        'can_settings': True,
        'can_check_license': True
    }
    
    # Vérification des droits admin
    if is_admin_license():
        permissions.update({
            'is_admin': True,
            'is_demo': False,
            'can_access_crm': True,
            'can_access_billing': True
        })
        return permissions
        
    # Vérification des droits client
    has_license, _ = check_client_license()
    if has_license:
        permissions.update({
            'is_client': True,
            'is_demo': False
        })
        
    return permissions

def decrement_grilles_demo():
    data = get_license_data()
    if is_demo_mode() and data.get("grilles", "").isdigit():
        remaining = int(data["grilles"]) - 1
        if remaining < 0:
            remaining = 0
        data["grilles"] = str(remaining)

        from core.encryption import update_config_secure
        update_config_secure(data)

def load_promo_data():
    """Charge les données de promotion."""
    try:
        with open(PROMO_PATH, 'r') as f:
            return json.load(f)
    except:
        return {"active_promotions": []}

def load_bandeau():
    """Charge le bandeau de promotion."""
    try:
        with open(BANDEAU_PATH, 'r') as f:
            return json.load(f)
    except:
        return {"bandeau": {"text": "", "color": "#000000", "background": "#FFFFFF"}}

def get_active_promo():
    """Récupère la promotion active."""
    promo_data = load_promo_data()
    now = datetime.datetime.now()
    
    for promo in promo_data.get("active_promotions", []):
        valid_from = datetime.datetime.strptime(promo["valid_from"], "%Y-%m-%d")
        valid_to = datetime.datetime.strptime(promo["valid_to"], "%Y-%m-%d")
        
        if valid_from <= now <= valid_to:
            return promo
    return None
