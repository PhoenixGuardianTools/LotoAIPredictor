import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Installation automatique des dépendances
import subprocess
import importlib

def install_requirements():
    print("🔍 Installation des dépendances...")
    requirements_file = Path(__file__).parent.parent / 'requirements.txt'
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)])
        print("✅ Installation terminée !")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Erreur lors de l'installation : {e}")
        sys.exit(1)

def check_dependencies():
    required_modules = ['stripe', 'wmi', 'qrcode', 'jinja2', 'pdfkit']
    missing_modules = []
    
    for module in required_modules:
        try:
            importlib.import_module(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print(f"⚠️ Modules manquants : {', '.join(missing_modules)}")
        install_requirements()
        # Vérifier à nouveau après l'installation
        for module in missing_modules:
            try:
                importlib.import_module(module)
            except ImportError:
                print(f"❌ Impossible d'installer le module {module}")
                sys.exit(1)

check_dependencies()

from merchand.newsletter_manager import NewsletterManager
from merchand.promo_manager import PromoManager
from datetime import datetime

def test_mothers_day():
    # Initialisation des gestionnaires
    newsletter_manager = NewsletterManager()
    promo_manager = PromoManager()
    
    # Génération du code promo
    promo_code = promo_manager.generate_promo_code(
        event="Fête des Mères",
        discount=20,
        duration_days=30
    )
    print(f"🎁 Code promo généré : {promo_code}")
    
    # Création de l'événement
    event = {
        "name": "Fête des Mères 2024",
        "date": "26 Mai 2024",
        "message": f"""
        <h2>🎀 Offre Spéciale Fête des Mères !</h2>
        <p>Chère cliente,</p>
        <p>À l'occasion de la Fête des Mères, nous vous offrons une réduction exceptionnelle de 20% sur tous nos produits !</p>
        <p>Utilisez le code promo : <strong>{promo_code}</strong></p>
        <p>Cette offre est valable jusqu'au 26 Mai 2024.</p>
        <p style="text-align: center;">
            <a href="#" style="background-color: #ff69b4; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">
                Profiter de l'offre
            </a>
        </p>
        """
    }
    
    # Envoi de la newsletter
    success = newsletter_manager.send_event_newsletter(event)
    if success:
        print("✅ Newsletter envoyée avec succès !")
    else:
        print("❌ Erreur lors de l'envoi de la newsletter")

if __name__ == "__main__":
    test_mothers_day() 