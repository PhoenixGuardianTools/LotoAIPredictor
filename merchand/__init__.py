"""
Package merchand pour la gestion des commandes et factures.
"""

__version__ = '1.0.0'

# Ce fichier est intentionnellement vide pour éviter les importations automatiques
# Les modules doivent être importés explicitement quand nécessaire

# Importations conditionnelles pour éviter les erreurs si certains modules ne sont pas installés
try:
    from .newsletter_manager import NewsletterManager
except ImportError:
    NewsletterManager = None

try:
    from .promo_manager import PromoManager
except ImportError:
    PromoManager = None

try:
    from .payment_manager import PaymentManager
except ImportError:
    PaymentManager = None

try:
    from .invoice_manager import InvoiceManager
except ImportError:
    InvoiceManager = None

__all__ = [
    'NewsletterManager',
    'PromoManager',
    'PaymentManager',
    'InvoiceManager'
] 