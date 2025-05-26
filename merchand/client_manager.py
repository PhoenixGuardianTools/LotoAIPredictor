import json
import hashlib
import uuid
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Tuple

# Import optionnel de stripe
try:
    import stripe
    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False

# Import optionnel de paypal
try:
    import paypalrestsdk
    PAYPAL_AVAILABLE = True
except ImportError:
    PAYPAL_AVAILABLE = False

from core.mailer import send_email

class ClientManager:
    def __init__(self):
        self.db_path = Path("data/clients.db")
        self.stripe_key = "sk_test_..."  # À configurer
        self.paypal_client_id = "..."    # À configurer
        self.paypal_secret = "..."       # À configurer
        
        # Configuration des APIs de paiement si disponibles
        if STRIPE_AVAILABLE:
            stripe.api_key = self.stripe_key
        if PAYPAL_AVAILABLE:
            paypalrestsdk.configure({
                "mode": "sandbox",
                "client_id": self.paypal_client_id,
                "client_secret": self.paypal_secret
            })
        
    def _init_db(self):
        """Initialise la base de données clients."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS clients (
                    id INTEGER PRIMARY KEY,
                    email TEXT UNIQUE,
                    uuid TEXT UNIQUE,
                    referral_code TEXT UNIQUE,
                    referred_by TEXT,
                    birth_date TEXT,
                    license_expiry TEXT,
                    is_active BOOLEAN,
                    created_at TEXT,
                    last_login TEXT
                )
            """)
            conn.commit()
            
    def create_client(self, email: str, birth_date: str, machine_uuid: str) -> Tuple[bool, str]:
        """Crée un nouveau client."""
        try:
            referral_code = self._generate_referral_code(email)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO clients (
                        email, uuid, referral_code, birth_date,
                        license_expiry, is_active, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    email,
                    machine_uuid,
                    referral_code,
                    birth_date,
                    (datetime.now() + timedelta(days=30)).isoformat(),
                    True,
                    datetime.now().isoformat()
                ))
                conn.commit()
                
            return True, referral_code
            
        except Exception as e:
            return False, str(e)
            
    def _generate_referral_code(self, email: str) -> str:
        """Génère un code de parrainage unique."""
        base = f"{email}{datetime.now().isoformat()}"
        return hashlib.md5(base.encode()).hexdigest()[:8].upper()
        
    def apply_referral(self, client_email: str, referral_code: str) -> bool:
        """Applique un code de parrainage."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Vérifier si le client a déjà été parrainé
                cursor.execute("""
                    SELECT referred_by FROM clients WHERE email = ?
                """, (client_email,))
                result = cursor.fetchone()
                if result and result[0]:
                    return False
                    
                # Vérifier si le code de parrainage existe
                cursor.execute("""
                    SELECT email FROM clients WHERE referral_code = ?
                """, (referral_code,))
                referrer = cursor.fetchone()
                if not referrer:
                    return False
                    
                # Appliquer le parrainage
                cursor.execute("""
                    UPDATE clients 
                    SET referred_by = ?,
                        license_expiry = datetime(license_expiry, '+30 days')
                    WHERE email = ?
                """, (referrer[0], client_email))
                
                # Prolonger la licence du parrain
                cursor.execute("""
                    UPDATE clients 
                    SET license_expiry = datetime(license_expiry, '+30 days')
                    WHERE email = ?
                """, (referrer[0],))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"⚠️ Erreur lors de l'application du parrainage : {e}")
            return False
            
    def process_payment(self, client_email: str, payment_method: str, amount: float) -> Tuple[bool, str]:
        """Traite un paiement."""
        try:
            if payment_method == "card":
                # Traitement Stripe
                payment = stripe.PaymentIntent.create(
                    amount=int(amount * 100),
                    currency="eur",
                    payment_method_types=["card"],
                    receipt_email=client_email
                )
                
            elif payment_method == "paypal":
                # Traitement PayPal
                payment = paypalrestsdk.Payment({
                    "intent": "sale",
                    "payer": {
                        "payment_method": "paypal"
                    },
                    "transactions": [{
                        "amount": {
                            "total": str(amount),
                            "currency": "EUR"
                        }
                    }]
                })
                
            if payment.create():
                # Générer et envoyer la nouvelle licence
                new_license = self._generate_license(client_email)
                self._send_license_email(client_email, new_license)
                return True, "Paiement traité avec succès"
                
            return False, "Erreur lors du traitement du paiement"
            
        except Exception as e:
            return False, str(e)
            
    def _generate_license(self, client_email: str) -> str:
        """Génère une nouvelle licence."""
        # TODO: Implémenter la génération de licence
        return "LICENSE_KEY"
        
    def _send_license_email(self, client_email: str, license_key: str):
        """Envoie la licence par email."""
        subject = "Votre nouvelle licence LotoAiPredictor"
        body = f"""
        Bonjour,
        
        Votre nouvelle licence est : {license_key}
        
        Pour l'activer :
        1. Ouvrez LotoAiPredictor
        2. Allez dans Paramètres > Licence
        3. Entrez votre clé
        
        Merci de votre confiance !
        """
        send_email(subject, body, client_email)
        
    def check_client_status(self, client_email: str) -> bool:
        """Vérifie le statut du client."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT is_active, license_expiry 
                    FROM clients 
                    WHERE email = ?
                """, (client_email,))
                result = cursor.fetchone()
                
                if not result:
                    return False
                    
                is_active, expiry = result
                if not is_active:
                    return False
                    
                expiry_date = datetime.fromisoformat(expiry)
                return expiry_date > datetime.now()
                
        except Exception as e:
            print(f"⚠️ Erreur lors de la vérification du statut : {e}")
            return False
            
    def get_client_info(self, client_email: str) -> Optional[Dict]:
        """Récupère les informations du client."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM clients WHERE email = ?
                """, (client_email,))
                result = cursor.fetchone()
                
                if not result:
                    return None
                    
                return {
                    "email": result[1],
                    "referral_code": result[3],
                    "referred_by": result[4],
                    "birth_date": result[5],
                    "license_expiry": result[6],
                    "is_active": result[7]
                }
                
        except Exception as e:
            print(f"⚠️ Erreur lors de la récupération des infos : {e}")
            return None 