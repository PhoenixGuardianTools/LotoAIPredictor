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
import configparser
from core.encryption import encrypt_config, decrypt_config
from core.export import export_to_pdf

class InvoiceGenerator:
    def __init__(self):
        self.templates_dir = Path("merchand/templates")
        self.output_dir = Path("merchand/output")
        self.config_file = Path("config/society_config.ini")
        self.encrypted_config_file = Path("config/society_config.enc")
        
        # Créer les dossiers s'ils n'existent pas
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Charger la configuration
        self.company_info = self._load_company_config()
        
    def _load_company_config(self) -> Dict:
        """Charge la configuration de la société."""
        try:
            if self.encrypted_config_file.exists():
                # Charger et déchiffrer la configuration
                with open(self.encrypted_config_file, 'r') as f:
                    encrypted_data = json.load(f)
                config_data = decrypt_config(encrypted_data, "society_key")
                
                # Convertir en dictionnaire
                config = configparser.ConfigParser()
                config.read_string(config_data)
                return dict(config['Company'])
            else:
                # Charger la configuration en clair
                config = configparser.ConfigParser()
                config.read(self.config_file)
                return dict(config['Company'])
        except Exception as e:
            print(f"⚠️ Erreur lors du chargement de la configuration : {e}")
            return {
                "name": "PhoenixProject",
                "address": "17 F RUE GUSTAVE NADAUD",
                "city": "69007 LYON",
                "country": "France",
                "email": "contact@phonxproject.onmicrosoft.com",
                "phone": "+33 6 77 37 61 96",
                "siret": "",
                "tva": "Non applicable",
                "logo_path": "WEB/assets/Logo_LotoAIPredictor.png"
            }
    
    def generate_invoice(self, invoice_data: Dict) -> str:
        """Génère une facture au format PDF."""
        try:
            # Calculer les totaux
            subtotal = sum(item['quantity'] * item['unit_price'] for item in invoice_data['items'])
            vat = 0  # TVA non applicable par défaut
            total = subtotal
            
            # Générer le QR code pour le paiement
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(f"Paiement facture {invoice_data['invoice_number']}: {total}€")
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white")
            qr_path = self.output_dir / f"qr_{invoice_data['invoice_number']}.png"
            qr_img.save(qr_path)
            
            # Construire le rapport pour export_to_pdf
            report = {
                "type": "invoice",
                "objet": "Facture",
                "invoice_number": invoice_data['invoice_number'],
                "date": invoice_data['date'],
                "due_date": invoice_data['due_date'],
                "client": invoice_data['client'],
                "items": invoice_data['items'],
                "subtotal": subtotal,
                "vat": vat,
                "total": total,
                "company": self.company_info,
                "qr_code": str(qr_path),
                "logo_path": self.company_info['logo_path'],
                "payment_method": invoice_data.get('payment_method', ''),
                "payment_link": invoice_data.get('payment_link', ''),
                "date_objet": "date_achat"
            }
            
            pdf_path = self.output_dir / f"invoice_{invoice_data['invoice_number']}.pdf"
            export_to_pdf(report, report_type="invoice", output_path=str(pdf_path))
            
            # Envoyer la facture par email
            self._send_invoice_email(invoice_data['client']['email'], pdf_path)
            
            return str(pdf_path)
            
        except Exception as e:
            import traceback
            print(f"⚠️ Erreur lors de la génération de la facture : {e}")
            traceback.print_exc()
            return None
            
    def _send_invoice_email(self, to_email: str, pdf_path: Path):
        """Envoie la facture par email."""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.company_info['email']
            msg['To'] = to_email
            msg['Subject'] = f"Votre facture {self.company_info['name']}"
            
            body = f"""
            Bonjour,
            
            Veuillez trouver ci-joint votre facture.
            
            Cordialement,
            L'équipe {self.company_info['name']}
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