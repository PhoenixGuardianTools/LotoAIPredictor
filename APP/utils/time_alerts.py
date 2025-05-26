import datetime
from LICENSE_ADMIN.license_checker import get_days_remaining

def check_alert_state():
    days = get_days_remaining()
    if days in [30, 7]:
        return f"💡 Votre licence expire dans {days} jours. Pensez à la renouveler."
    elif days == 2:
        return "🔥 Promo -10% valable 48h avant expiration !"
    return None
