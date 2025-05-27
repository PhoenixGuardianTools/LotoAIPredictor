import os
from pathlib import Path
from datetime import datetime, timedelta
import sqlite3
import sys

# Ajouter le répertoire parent au PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent.parent))

from merchand.ui.order_editor import OrderEditor
from merchand.generate_order import OrderGenerator

def create_example_order():
    """Crée un exemple de bon de commande avec 2 produits."""
    order_generator = OrderGenerator()
    
    # Données du client
    client = {
        'id': 'CLI001',
        'name': 'Jean Dupont',
        'email': 'jean.dupont@example.com',
        'address': '123 Rue de Paris',
        'city': 'Paris',
        'country': 'France',
        'billing_address': '123 Rue de Paris, 75001 Paris, France'
    }
    
    # Articles de la commande
    items = [
        {
            'product_id': 1,
            'name': 'Licence 1 mois',
            'duration': '1 mois',
            'base_price': 19.99,
            'quantity': 2,
            'discount_percent': 10
        },
        {
            'product_id': 6,
            'name': 'Abonnement 3 mois',
            'duration': '3 mois',
            'base_price': 79.99,
            'quantity': 1,
            'discount_percent': 20
        }
    ]
    
    # Données de la commande
    order_data = {
        'order_number': f"CMD{datetime.now().strftime('%Y%m%d%H%M%S')}",
        'date': datetime.now().strftime("%Y-%m-%d"),
        'due_date': (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
        'client': client,
        'items': items,
        'payment_method': "Virement bancaire",
        'payment_link': "https://phoenixproject.fr/payment",
        'promo_info': "Offre spéciale -20% sur les abonnements"
    }
    
    try:
        # Générer le PDF
        pdf_path = order_generator.generate_order(order_data)
        print(f"Bon de commande généré : {pdf_path}")
        
        # Envoyer par email
        from merchand.generate_order import send_order_email
        send_order_email(
            to_email=client['email'],
            pdf_path=Path(pdf_path),
            order_number=order_data['order_number']
        )
        print(f"Email envoyé à {client['email']}")
    except Exception as e:
        print(f"Erreur lors de la génération du bon de commande : {e}")
        return None

def init_test_data():
    """Initialise les données de test dans la base de données."""
    # Créer la base de données
    db_path = Path("merchand/data/clients.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Table des clients
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS clients (
        client_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        address TEXT,
        city TEXT,
        country TEXT,
        billing_address TEXT,
        billing_city TEXT,
        billing_country TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Table des produits
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT NOT NULL,
        name TEXT NOT NULL,
        duration TEXT NOT NULL,
        base_price REAL NOT NULL,
        description TEXT,
        is_active BOOLEAN DEFAULT 1
    )
    ''')
    
    # Insérer des clients de test
    test_clients = [
        ('CLI001', 'Jean Dupont', 'jean.dupont@example.com', '123 Rue de Paris', 'Paris', 'France', '123 Rue de Paris, 75001 Paris, France', 'Paris', 'France'),
        ('CLI002', 'Marie Martin', 'marie.martin@example.com', '456 Avenue des Champs', 'Lyon', 'France', '456 Avenue des Champs, 69000 Lyon, France', 'Lyon', 'France'),
        ('CLI003', 'Pierre Durand', 'pierre.durand@example.com', '789 Boulevard Central', 'Marseille', 'France', '789 Boulevard Central, 13000 Marseille, France', 'Marseille', 'France'),
        # Client fictif avec code formalisé
        ('CLI-20240610-0001', 'Test Client', 'test.client@example.com', '1 Rue du Test', 'Testville', 'France', '1 Rue du Test, 00000 Testville, France', 'Testville', 'France'),
        # Deux clients avec noms proches mais données différentes
        ('CLI-20240610-0002', 'Jean Testeur', 'jean.testeur@exemple.com', '10 Rue Alpha', 'Grenoble', 'France', '10 Rue Alpha, 38000 Grenoble, France', 'Grenoble', 'France'),
        ('CLI-20240610-0003', 'Jean Teston', 'jean.teston@exemple.com', '99 Avenue Omega', 'Nice', 'France', '99 Avenue Omega, 06000 Nice, France', 'Nice', 'France')
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO clients (client_id, name, email, address, city, country, billing_address, billing_city, billing_country)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', test_clients)
    
    # Insérer des produits de test
    test_products = [
        # Licences
        ('licence', 'Licence 1 semaine', '1 semaine', 9.99, 'Licence hebdomadaire'),
        ('licence', 'Licence 1 mois', '1 mois', 19.99, 'Licence mensuelle'),
        ('licence', 'Licence 3 mois', '3 mois', 49.99, 'Licence trimestrielle'),
        ('licence', 'Licence 6 mois', '6 mois', 89.99, 'Licence semestrielle'),
        ('licence', 'Licence 1 an', '1 an', 149.99, 'Licence annuelle'),
        
        # Abonnements
        ('abonnement', 'Abonnement 1 mois', '1 mois', 29.99, 'Abonnement mensuel'),
        ('abonnement', 'Abonnement 3 mois', '3 mois', 79.99, 'Abonnement trimestriel'),
        ('abonnement', 'Abonnement 6 mois', '6 mois', 149.99, 'Abonnement semestriel'),
        ('abonnement', 'Abonnement 1 an', '1 an', 249.99, 'Abonnement annuel'),
        
        # Formations
        ('formation', 'Formation débutant', '2 jours', 299.99, 'Formation complète'),
        ('formation', 'Formation avancée', '3 jours', 499.99, 'Formation expert'),
        ('formation', 'Formation complète', '5 jours', 799.99, 'Formation complète')
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO products (type, name, duration, base_price, description)
        VALUES (?, ?, ?, ?, ?)
    ''', test_products)
    
    conn.commit()
    conn.close()

def main():
    # Créer les répertoires nécessaires
    data_dir = Path("merchand/data")
    orders_dir = data_dir / "orders"
    icons_dir = data_dir / "icons"
    
    for directory in [data_dir, orders_dir, icons_dir]:
        directory.mkdir(parents=True, exist_ok=True)
        
    # Créer un logo par défaut si nécessaire
    logo_path = data_dir / "logo.png"
    if not logo_path.exists():
        from PIL import Image, ImageDraw
        img = Image.new('RGBA', (200, 200), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        draw.ellipse([(50, 50), (150, 150)], fill='blue')
        draw.text((75, 75), "PP", fill='white', font=None, font_size=40)
        img.save(logo_path)
        
    # Initialiser les données de test
    init_test_data()
    
    # Créer un exemple de bon de commande
    create_example_order()
    
    # Lancer l'éditeur
    app = OrderEditor()
    app.mainloop()
    
if __name__ == "__main__":
    main() 