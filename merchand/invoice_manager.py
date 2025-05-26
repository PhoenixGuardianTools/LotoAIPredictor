import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional
import pdfkit
from jinja2 import Environment, FileSystemLoader
import qrcode
from core.mailer import send_email

class InvoiceManager:
    def __init__(self):
        self.templates_dir = Path("merchand/templates")
        self.output_dir = Path("data/invoices")
        self.company_info = {
            "name": "LotoAiPredictor",
            "address": "123 Rue de la Chance",
            "city": "75000 Paris",
            "country": "France",
            "vat": "FR12345678900",
            "email": "contact@lotoaipredictor.com",
            "phone": "+33 1 23 45 67 89"
        }
        
        # Initialisation de l'environnement Jinja2
        self.env = Environment(
            loader=FileSystemLoader(self.templates_dir),
            autoescape=True
        )
        
        # Création des répertoires nécessaires
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_invoice(self, 
                        client_info: Dict,
                        items: list,
                        invoice_number: str,
                        payment_method: str) -> str:
        """Génère une facture au format PDF."""
        try:
            # Calcul du total
            subtotal = sum(item["price"] * item["quantity"] for item in items)
            vat_rate = 0.20  # 20% TVA
            vat_amount = subtotal * vat_rate
            total = subtotal + vat_amount
            
            # Génération du QR code pour le paiement
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(f"INVOICE:{invoice_number}\nTOTAL:{total:.2f}EUR")
            qr.make(fit=True)
            qr_path = self.output_dir / f"qr_{invoice_number}.png"
            qr.make_image().save(qr_path)
            
            # Préparation des données pour le template
            template_data = {
                "invoice_number": invoice_number,
                "date": datetime.now().strftime("%d/%m/%Y"),
                "due_date": (datetime.now() + timedelta(days=30)).strftime("%d/%m/%Y"),
                "company": self.company_info,
                "client": client_info,
                "items": items,
                "subtotal": f"{subtotal:.2f}",
                "vat_rate": f"{vat_rate * 100}%",
                "vat_amount": f"{vat_amount:.2f}",
                "total": f"{total:.2f}",
                "payment_method": payment_method,
                "qr_code": str(qr_path)
            }
            
            # Rendu du template
            template = self.env.get_template("invoice.html")
            html_content = template.render(**template_data)
            
            # Génération du PDF
            pdf_path = self.output_dir / f"invoice_{invoice_number}.pdf"
            pdfkit.from_string(html_content, str(pdf_path))
            
            # Envoi par email
            self._send_invoice_email(client_info["email"], pdf_path, invoice_number)
            
            return str(pdf_path)
            
        except Exception as e:
            print(f"⚠️ Erreur lors de la génération de la facture : {e}")
            return None
            
    def _send_invoice_email(self, client_email: str, pdf_path: Path, invoice_number: str):
        """Envoie la facture par email."""
        subject = f"Facture LotoAiPredictor - {invoice_number}"
        body = f"""
        Bonjour,
        
        Veuillez trouver ci-joint votre facture n°{invoice_number}.
        
        Merci de votre confiance !
        
        Cordialement,
        L'équipe LotoAiPredictor
        """
        
        send_email(subject, body, client_email, attachments=[str(pdf_path)])
        
    def get_invoice_info(self, invoice_number: str) -> Optional[Dict]:
        """Récupère les informations d'une facture."""
        try:
            invoice_path = self.output_dir / f"invoice_{invoice_number}.pdf"
            if not invoice_path.exists():
                return None
                
            # TODO: Extraire les informations du PDF
            return {
                "number": invoice_number,
                "path": str(invoice_path),
                "created_at": datetime.fromtimestamp(invoice_path.stat().st_mtime).isoformat()
            }
            
        except Exception as e:
            print(f"⚠️ Erreur lors de la récupération des infos : {e}")
            return None 