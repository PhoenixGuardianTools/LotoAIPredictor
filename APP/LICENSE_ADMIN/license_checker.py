import datetime
from utils.encryption import decrypt_ini

CONFIG_PATH = "SECURITY/config_admin.ini.enc"

def get_license_data():
    try:
        return decrypt_ini(CONFIG_PATH)
    except Exception:
        return {}

def is_admin_license():
    data = get_license_data()
    return data.get("type", "").lower() == "admin"

def is_demo_mode():
    data = get_license_data()
    return data.get("type", "").lower() == "demo"

def is_license_expired():
    data = get_license_data()
    exp_str = data.get("expiration")
    if not exp_str:
        return True
    try:
        exp_date = datetime.datetime.strptime(exp_str, "%Y-%m-%d")
        return exp_date < datetime.datetime.today()
    except:
        return True

def get_days_remaining():
    data = get_license_data()
    try:
        exp = datetime.datetime.strptime(data["expiration"], "%Y-%m-%d")
        delta = (exp - datetime.datetime.today()).days
        return max(0, delta)
    except:
        return 0

def should_show_reminder():
    days_left = get_days_remaining()
    return days_left in [30, 7, 2]

def should_show_promo():
    return get_days_remaining() == 2

def get_license_info():
    data = get_license_data()
    return {
        "type": data.get("type", "inconnu"),
        "expiration": data.get("expiration", "non définie"),
        "grilles_restantes": int(data.get("grilles", 0)),
        "email": data.get("email", ""),
        "promo_active": should_show_promo(),
        "jours_restants": get_days_remaining()
    }

def decrement_grilles_demo():
    data = get_license_data()
    if is_demo_mode() and data.get("grilles", "").isdigit():
        remaining = int(data["grilles"]) - 1
        if remaining < 0:
            remaining = 0
        data["grilles"] = str(remaining)

        from utils.encryption import update_config_secure
        update_config_secure(data)
