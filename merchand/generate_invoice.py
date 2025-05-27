import os
from pathlib import Path
from datetime import datetime
from core.export import export_to_pdf
from core.mailer import Mailer
import qrcode
import json
import sqlite3

class InvoiceGenerator:
    def __init__(self):
        self.logo_path = "merchand/data/logo.png"
        self.company = {
            "name": "PhoenixProject",
            "address": "123 Rue de l'Innovation",
            "city": "69000 Lyon",
            "country": "France",
            "email": "contact@phoenixproject.fr",
            "phone": "+33 4 56 78 90 12",
            "siret": "123 456 789 00012",
            "tva": "FR 12 123456789"
        }
        self._init_invoice_db()

    def _init_invoice_db(self):
        """Initialise la base de données des factures."""
        conn = sqlite3.connect('merchand/data/invoices.db')
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            invoice_number TEXT PRIMARY KEY,
            order_number TEXT,
            date TEXT,
            client_id TEXT,
            total REAL,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        conn.commit()
        conn.close()

    def _get_next_invoice_number(self):
        """Génère un numéro de facture unique au format invYYYYMMDDnumber."""
        today = datetime.now().strftime('%Y%m%d')
        conn = sqlite3.connect('merchand/data/clients.db')
        cursor = conn.cursor()
        
        # Trouver le dernier numéro pour aujourd'hui
        cursor.execute('''
            SELECT invoice_number FROM invoices 
            WHERE invoice_number LIKE ? 
            ORDER BY invoice_number DESC LIMIT 1
        ''', (f"inv{today}%",))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            last_number = int(result[0][-3:])  # Prend les 3 derniers chiffres
            new_number = last_number + 1
        else:
            new_number = 1
        
        return f"inv{today}{new_number:03d}"

    def generate_invoice_from_order(self, order_number):
        """
        Génère une facture à partir d'une commande payée.
        
        Args:
            order_number (str): Numéro de commande
        Returns:
            str: Chemin du fichier PDF généré
        """
        try:
            conn = sqlite3.connect('merchand/data/clients.db')
            cursor = conn.cursor()
            
            # Récupérer les données de la commande
            cursor.execute('''
                SELECT o.*, c.name, c.email, c.address, c.city, c.country
                FROM orders o
                JOIN clients c ON o.client_id = c.client_id
                WHERE o.order_number = ? AND o.status = 'paid'
            ''', (order_number,))
            
            order_data = cursor.fetchone()
            if not order_data:
                print("❌ Commande non trouvée ou non payée")
                return None
            
            # Vérifier si une facture existe déjà
            cursor.execute('SELECT invoice_number FROM invoices WHERE order_number = ?', (order_number,))
            if cursor.fetchone():
                print("❌ Une facture existe déjà pour cette commande")
                return None
            
            # Générer le numéro de facture
            invoice_number = self._get_next_invoice_number()
            
            # Générer le QR code pour le dépôt Git
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data("https://github.com/PhoenixProject/LotoAIPredictor")
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white")
            qr_path = f"merchand/data/qr_{invoice_number}.png"
            qr_img.save(qr_path)

            # Préparer les données pour l'export PDF
            items = json.loads(order_data[4])  # items est stocké en JSON
            report = {
                "type": "invoice",
                "objet": "Facture",
                "invoice_number": invoice_number,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "company": self.company,
                "client": {
                    "id": order_data[1],  # client_id
                    "name": order_data[13],  # name
                    "email": order_data[14],  # email
                    "address": order_data[15],  # address
                    "city": order_data[16],  # city
                    "country": order_data[17],  # country
                    "billing_address": order_data[15],  # même adresse
                    "billing_city": order_data[16],
                    "billing_country": order_data[17]
                },
                "items": items,
                "subtotal": order_data[5],  # subtotal
                "vat": order_data[6],  # vat
                "total": order_data[7],  # total
                "background_color": "#F5F5F5",
                "logo_path": self.logo_path,
                "qr_code": qr_path
            }

            # Générer le PDF
            output_path = f"merchand/data/invoices/invoice_{invoice_number}.pdf"
            pdf_path = export_to_pdf(report, output_path=output_path)

            # Sauvegarder la facture dans la base de données
            cursor.execute('''
                INSERT INTO invoices (
                    invoice_number, order_number, client_id, date,
                    items, subtotal, vat, total, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                invoice_number,
                order_number,
                order_data[1],  # client_id
                datetime.now().strftime("%Y-%m-%d"),
                json.dumps(items),
                order_data[5],  # subtotal
                order_data[6],  # vat
                order_data[7],  # total
                'paid'
            ))
            
            # Marquer la commande comme non éditable
            cursor.execute('''
                UPDATE orders SET
                    is_editable = 0,
                    status = 'completed'
                WHERE order_number = ?
            ''', (order_number,))
            
            conn.commit()
            conn.close()

            # Nettoyer le QR code temporaire
            os.remove(qr_path)

            return pdf_path

        except Exception as e:
            print(f"Erreur lors de la génération de la facture : {e}")
            return None

def send_invoice_email(to_email: str, pdf_path: Path, invoice_number: str):
    """Envoie la facture par email."""
    try:
        mailer = Mailer()
        subject = f"Votre facture {invoice_number}"
        body = f"""
        Bonjour,
        
        Veuillez trouver ci-joint votre facture {invoice_number}.
        
        Cordialement,
        L'équipe PhoenixProject
        """
        
        success = mailer.send_email(
            to_email=to_email,
            subject=subject,
            body=body,
            attachments=[str(pdf_path)]
        )
        
        if success:
            print(f"✅ Email envoyé avec succès à {to_email}")
        else:
            print(f"❌ Erreur lors de l'envoi de l'email à {to_email}")
            
    except Exception as e:
        print(f"⚠️ Erreur lors de l'envoi de l'email : {e}") 