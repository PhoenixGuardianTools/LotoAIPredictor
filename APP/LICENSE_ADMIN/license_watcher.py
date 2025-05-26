from cryptography.fernet import Fernet
from datetime import datetime, timedelta
import os
import json
from core.mailer import send_email

LICENSE_PATH = "LICENSE_ADMIN/license.key.enc"
FERNET_KEY_FILE = "fernet.key"
ALERT_LOG_FILE = "LICENSE_ADMIN/alert_sent.log"

RECIPIENT = "phoenix38@riseup.net"
SENDER = "phoenix38@riseup.net"
SMTP_SERVER = "mail.riseup.net"
PORT = 465

def load_license():
    with open(FERNET_KEY_FILE, "rb") as f:
        key = f.read()
    with open(LICENSE_PATH, "rb") as f:
        data = Fernet(key).decrypt(f.read())
    return json.loads(data)

def load_alert_log():
    if os.path.exists(ALERT_LOG_FILE):
        with open(ALERT_LOG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_alert_log(log):
    with open(ALERT_LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)

def check_expiration_alert():
    try:
        license = load_license()
        if license.get("expiration") == "illimité":
            return

        exp = datetime.strptime(license["expiration"], "%Y-%m-%d")
        now = datetime.utcnow()
        days_left = (exp - now).days

        log = load_alert_log()

        if days_left <= 30 and "30d" not in log:
            send_alert(30, exp.date())
            log["30d"] = True
        if days_left <= 7 and "7d" not in log:
            send_alert(7, exp.date())
            log["7d"] = True

        save_alert_log(log)

    except Exception as e:
        print(f"[✗] Erreur dans le contrôle de licence : {e}")

def send_alert(d, exp_date):
    subject = f"⚠️ Alerte : Licence expirera dans {d} jours"
    body = f"Votre licence expire le {exp_date}.\nRenouvelez-la avant expiration pour conserver l'accès complet."
    send_email(subject, body, RECIPIENT, SMTP_SERVER, PORT, SENDER)
    print(f"[✓] Alerte J-{d} envoyée.")
