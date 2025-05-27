"""
Module de gestion des alertes temporelles pour les licences.
"""

import datetime
from typing import Optional
from LICENSE_ADMIN.license_checker import get_days_remaining

def check_alert_state() -> Optional[str]:
    """
    Vérifie l'état des alertes de licence et retourne un message approprié.
    
    Returns:
        Optional[str]: Un message d'alerte si nécessaire, None sinon.
        
    Note:
        Les alertes sont déclenchées à :
        - 30 jours avant expiration
        - 7 jours avant expiration
        - 2 jours avant expiration (avec offre promotionnelle)
    """
    days = get_days_remaining()
    if days in [30, 7]:
        return f"💡 Votre licence expire dans {days} jours. Pensez à la renouveler."
    elif days == 2:
        return "🔥 Promo -10% valable 48h avant expiration !"
    return None
