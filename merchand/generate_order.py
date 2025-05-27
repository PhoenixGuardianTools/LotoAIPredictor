import os
from pathlib import Path
from datetime import datetime
from core.export import export_to_pdf
from core.mailer import Mailer
import qrcode
import json
import sqlite3

class OrderGenerator:
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
        self._init_db()

    def _init_db(self):
        """Initialise la base de données des clients avec les tables pour les commandes et produits."""
        conn = sqlite3.connect('merchand/data/clients.db')
        cursor = conn.cursor()
        
        # Table des produits
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,  -- licence, abonnement, etc.
            name TEXT NOT NULL,
            duration TEXT NOT NULL,  -- 1 semaine, 1 mois, etc.
            base_price REAL NOT NULL,
            description TEXT,
            is_active BOOLEAN DEFAULT 1
        )
        ''')
        
        # Table des commandes
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_number TEXT PRIMARY KEY,
            client_id TEXT NOT NULL,
            date TEXT NOT NULL,
            due_date TEXT NOT NULL,
            items TEXT NOT NULL,  -- JSON string des items
            subtotal REAL NOT NULL,
            vat REAL NOT NULL,
            total REAL NOT NULL,
            payment_method TEXT,
            payment_link TEXT,
            promo_info TEXT,
            status TEXT DEFAULT 'pending',  -- pending, paid, cancelled
            is_editable BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES clients(client_id)
        )
        ''')
        
        # Table des factures
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            invoice_number TEXT PRIMARY KEY,
            order_number TEXT NOT NULL,
            client_id TEXT NOT NULL,
            date TEXT NOT NULL,
            items TEXT NOT NULL,  -- JSON string des items
            subtotal REAL NOT NULL,
            vat REAL NOT NULL,
            total REAL NOT NULL,
            status TEXT DEFAULT 'pending',  -- pending, paid
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (order_number) REFERENCES orders(order_number),
            FOREIGN KEY (client_id) REFERENCES clients(client_id)
        )
        ''')
        
        # Insérer les produits par défaut s'ils n'existent pas
        default_products = [
            ('licence', 'Licence 1 semaine', '1 semaine', 9.99, 'Licence hebdomadaire'),
            ('licence', 'Licence 1 mois', '1 mois', 19.99, 'Licence mensuelle'),
            ('licence', 'Licence 3 mois', '3 mois', 49.99, 'Licence trimestrielle'),
            ('licence', 'Licence 6 mois', '6 mois', 89.99, 'Licence semestrielle'),
            ('licence', 'Licence 1 an', '1 an', 149.99, 'Licence annuelle'),
            ('abonnement', 'Abonnement 1 mois', '1 mois', 29.99, 'Abonnement mensuel'),
            ('abonnement', 'Abonnement 3 mois', '3 mois', 79.99, 'Abonnement trimestriel'),
            ('abonnement', 'Abonnement 6 mois', '6 mois', 149.99, 'Abonnement semestriel'),
            ('abonnement', 'Abonnement 1 an', '1 an', 249.99, 'Abonnement annuel')
        ]
        
        cursor.executemany('''
            INSERT OR IGNORE INTO products (type, name, duration, base_price, description)
            VALUES (?, ?, ?, ?, ?)
        ''', default_products)
        
        conn.commit()
        conn.close()

    def get_products_by_type(self, product_type):
        """Récupère tous les produits d'un type donné."""
        conn = sqlite3.connect('merchand/data/clients.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT product_id, name, duration, base_price, description
            FROM products
            WHERE type = ? AND is_active = 1
            ORDER BY base_price
        ''', (product_type,))
        products = cursor.fetchall()
        conn.close()
        return products

    def get_product_types(self):
        """Récupère tous les types de produits disponibles."""
        conn = sqlite3.connect('merchand/data/clients.db')
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT type FROM products WHERE is_active = 1')
        types = [row[0] for row in cursor.fetchall()]
        conn.close()
        return types

    def calculate_totals(self, items):
        """Calcule les totaux en tenant compte des réductions."""
        subtotal = 0
        for item in items:
            price = item['base_price']
            if 'discount_percent' in item:
                price = price * (1 - item['discount_percent'] / 100)
            subtotal += price * item['quantity']
        vat = subtotal * 0.20  # TVA 20%
        total = subtotal + vat
        return subtotal, vat, total

    def update_order(self, order_number, updated_data):
        """
        Met à jour un bon de commande existant.
        
        Args:
            order_number (str): Numéro de commande
            updated_data (dict): Nouvelles données contenant :
                - items: Liste des articles avec leurs réductions
                - payment_method: Méthode de paiement
                - payment_link: Lien de paiement
                - promo_info: Information promotionnelle
        Returns:
            bool: Succès de la mise à jour
        """
        try:
            conn = sqlite3.connect('merchand/data/clients.db')
            cursor = conn.cursor()
            
            # Vérifier si la commande est éditable
            cursor.execute('SELECT is_editable FROM orders WHERE order_number = ?', (order_number,))
            result = cursor.fetchone()
            
            if not result or not result[0]:
                print("❌ Cette commande n'est plus éditable")
                return False
            
            # Calculer les nouveaux totaux
            subtotal, vat, total = self.calculate_totals(updated_data['items'])
            
            # Mettre à jour les données
            cursor.execute('''
                UPDATE orders SET
                    items = ?,
                    subtotal = ?,
                    vat = ?,
                    total = ?,
                    payment_method = ?,
                    payment_link = ?,
                    promo_info = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE order_number = ?
            ''', (
                json.dumps(updated_data['items']),
                subtotal,
                vat,
                total,
                updated_data['payment_method'],
                updated_data['payment_link'],
                updated_data.get('promo_info'),
                order_number
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Erreur lors de la mise à jour de la commande : {e}")
            return False

    def generate_order(self, order_data):
        """
        Génère un bon de commande au format PDF et le sauvegarde en base.
        
        Args:
            order_data (dict): Données du bon de commande
        Returns:
            str: Chemin du fichier PDF généré
        """
        try:
            # Calculer les totaux
            subtotal, vat, total = self.calculate_totals(order_data['items'])

            # Générer le QR code pour le paiement avec le montant
            payment_data = {
                "amount": total,
                "currency": "EUR",
                "payment_link": order_data['payment_link']
            }
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(json.dumps(payment_data))
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white")
            qr_path = f"merchand/data/qr_{order_data['order_number']}.png"
            qr_img.save(qr_path)

            # Sauvegarder la commande en base
            conn = sqlite3.connect('merchand/data/clients.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO orders (
                    order_number, client_id, date, due_date, items,
                    subtotal, vat, total, payment_method, payment_link,
                    promo_info, status, is_editable
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                order_data['order_number'],
                order_data['client']['id'],
                order_data['date'],
                order_data['due_date'],
                json.dumps(order_data['items']),
                subtotal,
                vat,
                total,
                order_data['payment_method'],
                order_data['payment_link'],
                order_data.get('promo_info'),
                'pending',
                1
            ))
            conn.commit()
            conn.close()

            # Préparer les données pour l'export PDF
            report = {
                "type": "order",
                "objet": "Bon de Commande",
                "order_number": order_data['order_number'],
                "date": order_data['date'],
                "due_date": order_data['due_date'],
                "company": self.company,
                "client": order_data['client'],
                "items": order_data['items'],
                "subtotal": subtotal,
                "vat": vat,
                "total": total,
                "payment_method": order_data['payment_method'],
                "payment_link": order_data['payment_link'],
                "promo_info": order_data.get('promo_info'),
                "background_color": order_data.get('background_color', '#F5F5F5'),
                "logo_path": self.logo_path,
                "qr_code": qr_path
            }

            # Générer le PDF
            output_path = f"merchand/data/orders/order_{order_data['order_number']}.pdf"
            pdf_path = export_to_pdf(report, output_path=output_path)

            # Nettoyer le QR code temporaire
            os.remove(qr_path)

            return pdf_path

        except Exception as e:
            print(f"Erreur lors de la génération du bon de commande : {e}")
            return None

def send_order_email(to_email: str, pdf_path: Path, order_number: str):
    """Envoie le bon de commande par email."""
    try:
        mailer = Mailer()
        subject = f"Votre bon de commande {order_number}"
        body = f"""
        Bonjour,
        
        Veuillez trouver ci-joint votre bon de commande {order_number}.
        
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