import datetime
from pathlib import Path
import platform
import uuid
import hashlib
import json
import sqlite3
from utils.encryption import decrypt_ini, update_config_secure
import os

# Chemins des fichiers
CONFIG_PATH = "SECURITY/config_admin.ini.enc"
DB_PATH = Path(__file__).resolve().parent.parent / "data" / "phoenix.db"
LICENSE_PATH = "LICENSE_ADMIN/license.key.enc"
FERNET_KEY_FILE = "fernet.key"
ALERT_LOG_FILE = "LICENSE_ADMIN/alert_sent.log"
PROMO_PATH = "PROMOTIONS/promo_templates.json"
BANDEAU_PATH = "PROMOTIONS/bandeau_default.json"

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

def get_machine_uuid():
    """
    Génère un UUID unique pour la machine basé sur les caractéristiques matérielles.
    """
    system_info = {
        'platform': platform.system(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'node': platform.node()
    }
    unique_string = str(system_info)
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, unique_string))

def get_license_data():
    """Récupère les données de licence admin."""
    try:
        return decrypt_ini(CONFIG_PATH)
    except Exception:
        return {}

def is_admin_license():
    """Vérifie si l'utilisateur a une licence admin valide."""
    data = get_license_data()
    if data.get("type", "").lower() != "admin":
        return False
        
    # Vérification de la date d'expiration
    exp_str = data.get("expiration")
    if not exp_str:
        return False
    try:
        exp_date = datetime.datetime.strptime(exp_str, "%Y-%m-%d")
        return exp_date >= datetime.datetime.today()
    except:
        return False

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
    if is_admin_license():
        return False
    has_license, _ = check_client_license()
    return not has_license

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
    """Détermine si un rappel doit être affiché."""
    days_left = get_days_remaining()
    return days_left in [30, 7, 2]

def should_show_promo():
    """Détermine si une promotion doit être affichée."""
    days_left = get_days_remaining()
    return days_left == 2  # 48h avant expiration

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

def get_license_info():
    """Récupère les informations complètes de la licence."""
    if is_admin_license():
        data = get_license_data()
        return {
            "type": "admin",
            "expiration": data.get("expiration", "illimitée"),
            "status": "active",
            "email": data.get("email", ""),
            "promo_active": should_show_promo(),
            "promo_bandeau": get_promo_bandeau(),
            "jours_restants": get_days_remaining()
        }
        
    has_license, license_info = check_client_license()
    if has_license:
        return {
            "type": license_info['type'],
            "expiration": license_info['expiration'],
            "status": license_info['status'],
            "email": "",
            "promo_active": should_show_promo(),
            "promo_bandeau": get_promo_bandeau(),
            "jours_restants": get_days_remaining()
        }
        
    return {
        "type": "demo",
        "expiration": "non définie",
        "status": "inactive",
        "email": "",
        "promo_active": should_show_promo(),
        "promo_bandeau": get_promo_bandeau(),
        "jours_restants": 0
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

        from utils.encryption import update_config_secure
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
