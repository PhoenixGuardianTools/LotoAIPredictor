import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple
import stripe
import paypalrestsdk
from .invoice_manager import InvoiceManager

class PaymentManager:
    def __init__(self):
        self.config_path = Path("merchand/config/payment.json")
        self.invoice_manager = InvoiceManager()
        self._load_config()
        
    def _load_config(self):
        """Charge la configuration des paiements."""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                config = json.load(f)
        else:
            config = {
                "stripe": {
                    "key": "sk_test_...",
                    "webhook_secret": "whsec_..."
                },
                "paypal": {
                    "client_id": "...",
                    "secret": "...",
                    "mode": "sandbox"
                }
            }
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
                
        # Configuration des APIs
        stripe.api_key = config["stripe"]["key"]
        paypalrestsdk.configure({
            "mode": config["paypal"]["mode"],
            "client_id": config["paypal"]["client_id"],
            "client_secret": config["paypal"]["secret"]
        })
        
    def process_payment(self, 
                       client_info: Dict,
                       items: list,
                       payment_method: str,
                       invoice_number: str) -> Tuple[bool, str]:
        """Traite un paiement."""
        try:
            # Calcul du total
            total = sum(item["price"] * item["quantity"] for item in items)
            
            if payment_method == "card":
                # Création de l'intention de paiement Stripe
                payment = stripe.PaymentIntent.create(
                    amount=int(total * 100),  # Stripe utilise les centimes
                    currency="eur",
                    payment_method_types=["card"],
                    receipt_email=client_info["email"],
                    metadata={
                        "invoice_number": invoice_number,
                        "client_email": client_info["email"]
                    }
                )
                
                # Génération de la facture
                self.invoice_manager.generate_invoice(
                    client_info,
                    items,
                    invoice_number,
                    "Carte bancaire"
                )
                
                return True, payment.client_secret
                
            elif payment_method == "paypal":
                # Création du paiement PayPal
                payment = paypalrestsdk.Payment({
                    "intent": "sale",
                    "payer": {
                        "payment_method": "paypal"
                    },
                    "transactions": [{
                        "amount": {
                            "total": f"{total:.2f}",
                            "currency": "EUR"
                        },
                        "description": f"Facture {invoice_number}",
                        "custom": client_info["email"]
                    }],
                    "redirect_urls": {
                        "return_url": "https://lotoaipredictor.com/payment/success",
                        "cancel_url": "https://lotoaipredictor.com/payment/cancel"
                    }
                })
                
                if payment.create():
                    # Génération de la facture
                    self.invoice_manager.generate_invoice(
                        client_info,
                        items,
                        invoice_number,
                        "PayPal"
                    )
                    
                    return True, payment.links[1].href  # URL d'approbation
                    
            return False, "Méthode de paiement non supportée"
            
        except Exception as e:
            return False, str(e)
            
    def verify_payment(self, payment_id: str, payment_method: str) -> bool:
        """Vérifie le statut d'un paiement."""
        try:
            if payment_method == "card":
                payment = stripe.PaymentIntent.retrieve(payment_id)
                return payment.status == "succeeded"
                
            elif payment_method == "paypal":
                payment = paypalrestsdk.Payment.find(payment_id)
                return payment.state == "approved"
                
            return False
            
        except Exception as e:
            print(f"⚠️ Erreur lors de la vérification du paiement : {e}")
            return False
            
    def refund_payment(self, payment_id: str, payment_method: str, amount: float = None) -> Tuple[bool, str]:
        """Effectue un remboursement."""
        try:
            if payment_method == "card":
                refund = stripe.Refund.create(
                    payment_intent=payment_id,
                    amount=int(amount * 100) if amount else None
                )
                return True, refund.id
                
            elif payment_method == "paypal":
                payment = paypalrestsdk.Payment.find(payment_id)
                refund = payment.refund({
                    "amount": {
                        "total": f"{amount:.2f}" if amount else payment.transactions[0].amount.total,
                        "currency": "EUR"
                    }
                })
                return True, refund.id
                
            return False, "Méthode de paiement non supportée"
            
        except Exception as e:
            return False, str(e) 