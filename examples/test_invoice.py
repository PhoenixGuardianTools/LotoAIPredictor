import sys
import os
from pathlib import Path
import sqlite3
from datetime import datetime, timedelta

# Ajouter le répertoire parent au PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from merchand.invoice_generator import InvoiceGenerator
from core.mailer import Mailer

# Mapping des durées de licence
LICENSE_DURATIONS = {
    "1week": "1 semaine",
    "1month": "1 mois",
    "3months": "3 mois",
    "6months": "6 mois",
    "1year": "1 an"
}

def calculate_discount(duration: str) -> tuple:
    """Calcule la réduction dégressive en fonction de la durée."""
    prices = {
        "1week": 9.99,    # Prix de base pour 1 semaine
        "1month": 19.99,  # Prix pour 1 mois
        "3months": 49.99, # Prix pour 3 mois
        "6months": 89.99, # Prix pour 6 mois
        "1year": 149.99   # Prix pour 1 an
    }
    
    base_price = prices["1week"]
    final_price = prices[duration]
    
    # Calcul du pourcentage de réduction
    if duration == "1week":
        discount_percent = 0
    else:
        # Calcul de la réduction en pourcentage
        # Exemple pour 1 mois : (19.99 - 9.99) / 19.99 * 100 = 50%
        discount_percent = round(((final_price - base_price) / final_price) * 100)
    
    return discount_percent, final_price

def init_db():
    conn = sqlite3.connect('merchand/data/products.db')
    cursor = conn.cursor()
    
    # Table des produits
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        display_name TEXT NOT NULL,
        price REAL NOT NULL,
        duration TEXT NOT NULL
    )
    ''')
    
    # Table des clients
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS clients (
        client_id TEXT PRIMARY KEY,
        last_name TEXT NOT NULL,
        first_name TEXT NOT NULL,
        email TEXT NOT NULL,
        address TEXT NOT NULL,
        city TEXT NOT NULL,
        country TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(client_id)
    )
    ''')
    
    # Insérer les produits s'ils n'existent pas déjà
    products = [
        ('License1week', 'Licence 1 semaine', 9.99, '1week'),
        ('License1month', 'Licence 1 mois', 19.99, '1month'),
        ('License3months', 'Licence 3 mois', 49.99, '3months'),
        ('License6months', 'Licence 6 mois', 89.99, '6months'),
        ('License1year', 'Licence 1 an', 149.99, '1year')
    ]
    for product in products:
        cursor.execute('INSERT OR IGNORE INTO products (name, display_name, price, duration) VALUES (?, ?, ?, ?)', product)
    conn.commit()
    conn.close()

def generate_client_id(last_name: str) -> str:
    """Génère un ID client unique basé sur le nom de famille et la date."""
    conn = sqlite3.connect('merchand/data/products.db')
    cursor = conn.cursor()
    
    today = datetime.now().strftime('%Y%m%d')
    base_id = f"{last_name.upper()}{today}"
    
    # Trouver le dernier rang pour ce nom et cette date
    cursor.execute('''
        SELECT client_id FROM clients 
        WHERE client_id LIKE ? 
        ORDER BY client_id DESC LIMIT 1
    ''', (f"{base_id}%",))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        last_id = result[0]
        last_rank = int(last_id[-1])
        new_rank = last_rank + 1
    else:
        new_rank = 1
    
    return f"{base_id}{new_rank}"

def save_client(client_data: dict) -> str:
    """Sauvegarde un nouveau client et retourne son ID."""
    conn = sqlite3.connect('merchand/data/products.db')
    cursor = conn.cursor()
    
    client_id = generate_client_id(client_data['name'].split()[0])  # Prend le nom de famille
    
    cursor.execute('''
        INSERT INTO clients (client_id, last_name, first_name, email, address, city, country)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        client_id,
        client_data['name'].split()[0],  # Nom de famille
        ' '.join(client_data['name'].split()[1:]),  # Prénom(s)
        client_data['email'],
        client_data['address'],
        client_data['city'],
        client_data['country']
    ))
    
    conn.commit()
    conn.close()
    return client_id

def get_product_info(product_name):
    conn = sqlite3.connect('merchand/data/products.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name, display_name, price, duration FROM products WHERE name = ?', (product_name,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return {
            'name': result[0],
            'display_name': result[1],
            'price': result[2],
            'duration': result[3],
            'discount_percent': '0%'  # Valeur par défaut si non présente
        }
    return None

def send_invoice_email(to_email: str, pdf_path: Path, invoice_number: str):
    """Envoie la facture par email en utilisant le mailer."""
    try:
        mailer = Mailer()
        subject = f"Votre facture {invoice_number}"
        body = f"""
        Bonjour,
        
        Veuillez trouver ci-joint votre facture {invoice_number}.
        
        Cordialement,
        L'équipe PhoenixProject
        """
        
        # Envoyer l'email avec la pièce jointe
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

def generate_license_invoice():
    """Génère une facture pour une licence."""
    try:
        # Initialiser la base de données
        init_db()
        
        # Récupérer les informations du produit
        product_info = get_product_info("License1month")
        if not product_info:
            print("❌ Produit non trouvé")
            return
        
        # Créer le dossier des factures s'il n'existe pas
        invoices_dir = Path("merchand/data/invoices")
        invoices_dir.mkdir(parents=True, exist_ok=True)
        
        # Créer les données du client
        client_data = {
            "name": "Client Test",
            "email": "phoenix38@riseup.net",
            "address": "123 Rue Test",
            "city": "69000 Lyon",
            "country": "France"
        }
        
        # Sauvegarder le client et obtenir son ID
        client_id = save_client(client_data)
        
        # Créer les données de la facture
        invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-001"
        invoice_data = {
            "invoice_number": invoice_number,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "due_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
            "client": {
                "id": client_id,
                "name": client_data["name"],
                "email": client_data["email"],
                "address": client_data["address"],
                "city": client_data["city"],
                "country": client_data["country"],
                "billing_address": client_data["address"],  # Adresse de facturation identique
                "billing_city": client_data["city"],
                "billing_country": client_data["country"]
            },
            "items": [
                {
                    "name": product_info["name"],
                    "description": product_info["display_name"],
                    "quantity": 1,
                    "unit_price": product_info["price"],
                    "discount": f"{product_info['discount_percent']}%"
                }
            ],
            "payment_method": "PayPal",
            "payment_link": "https://www.paypal.com/paypalme/PhoenixGuardianSales?country.x=FR&locale.x=fr_FR",
            "promo_info": "Paiement sous 48h pour bénéficier de la promotion",
            "background_color": "#F5F5F5"  # Gris clair pour le fond
        }
        
        # Générer la facture
        generator = InvoiceGenerator()
        pdf_path = generator.generate_invoice(invoice_data)
        
        if pdf_path:
            # Renommer le fichier selon le format demandé
            new_name = f"invoice_{client_id}_{product_info['duration']}_{datetime.now().strftime('%Y%m%d')}.pdf"
            new_path = invoices_dir / new_name
            os.rename(pdf_path, new_path)
            print(f"✅ Facture générée avec succès : {new_path}")
            
            # Envoyer la facture par email
            send_invoice_email(
                to_email=invoice_data["client"]["email"],
                pdf_path=new_path,
                invoice_number=invoice_number
            )
        else:
            print("❌ Erreur lors de la génération de la facture")
            
    except Exception as e:
        import traceback
        print(f"⚠️ Erreur : {e}")
        traceback.print_exc()

if __name__ == "__main__":
    generate_license_invoice() 