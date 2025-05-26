import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import qrcode
from jinja2 import Environment, FileSystemLoader
import pdfkit
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

class InvoiceGenerator:
    def __init__(self):
        self.templates_dir = Path("merchand/templates")
        self.output_dir = Path("merchand/output")
        self.company_info = {
            "name": "PhoenixProject",
            "address": "123 Rue de la Chance",
            "city": "75000 Paris",
            "country": "France",
            "email": "contact@phonxproject.onmicrosoft.com",
            "phone": "+33 1 23 45 67 89",
            "siret": "123 456 789 00000",
            "tva": "FR12345678900"
        }
        
        # Créer les dossiers s'ils n'existent pas
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_invoice(self, invoice_data: Dict) -> str:
        """Génère une facture au format PDF."""
        try:
            # Calculer les totaux
            subtotal = sum(item['quantity'] * item['unit_price'] for item in invoice_data['items'])
            vat = subtotal * 0.20  # TVA 20%
            total = subtotal + vat
            
            # Générer le QR code pour le paiement
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(f"Paiement facture {invoice_data['invoice_number']}: {total}€")
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white")
            qr_path = self.output_dir / f"qr_{invoice_data['invoice_number']}.png"
            qr_img.save(qr_path)
            
            # Préparer les données pour le template
            template_data = {
                "invoice": {
                    "number": invoice_data['invoice_number'],
                    "date": invoice_data['date'],
                    "due_date": invoice_data['due_date']
                },
                "client": invoice_data['client'],
                "items": invoice_data['items'],
                "subtotal": subtotal,
                "vat": vat,
                "total": total,
                "company": self.company_info,
                "qr_code": str(qr_path)
            }
            
            # Rendre le template HTML
            env = Environment(loader=FileSystemLoader(self.templates_dir))
            template = env.get_template('invoice.html')
            html_content = template.render(**template_data)
            
            # Générer le PDF
            pdf_path = self.output_dir / f"invoice_{invoice_data['invoice_number']}.pdf"
            pdfkit.from_string(html_content, str(pdf_path))
            
            # Envoyer la facture par email
            self._send_invoice_email(invoice_data['client']['email'], pdf_path)
            
            return str(pdf_path)
            
        except Exception as e:
            print(f"⚠️ Erreur lors de la génération de la facture : {e}")
            return None
            
    def _send_invoice_email(self, to_email: str, pdf_path: Path):
        """Envoie la facture par email."""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.company_info['email']
            msg['To'] = to_email
            msg['Subject'] = "Votre facture PhoenixProject"
            
            body = """
            Bonjour,
            
            Veuillez trouver ci-joint votre facture.
            
            Cordialement,
            L'équipe PhoenixProject
            """
            msg.attach(MIMEText(body, 'plain'))
            
            # Attacher le PDF
            with open(pdf_path, 'rb') as f:
                pdf = MIMEApplication(f.read(), _subtype='pdf')
                pdf.add_header('Content-Disposition', 'attachment', filename=pdf_path.name)
                msg.attach(pdf)
            
            # Envoyer l'email
            with smtplib.SMTP('smtp.office365.com', 587) as server:
                server.starttls()
                server.login(self.company_info['email'], "password")  # À configurer
                server.send_message(msg)
                
        except Exception as e:
            print(f"⚠️ Erreur lors de l'envoi de l'email : {e}")
            
    def get_invoice_info(self, invoice_number: str) -> Dict:
        """Récupère les informations d'une facture."""
        try:
            pdf_path = self.output_dir / f"invoice_{invoice_number}.pdf"
            if not pdf_path.exists():
                return None
                
            # TODO: Extraire les informations du PDF
            return {
                "number": invoice_number,
                "path": str(pdf_path),
                "created_at": datetime.fromtimestamp(pdf_path.stat().st_mtime).isoformat()
            }
            
        except Exception as e:
            print(f"⚠️ Erreur lors de la récupération des infos : {e}")
            return None 