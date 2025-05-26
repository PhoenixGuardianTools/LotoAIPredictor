import sys
import os

# Ajouter le répertoire courant au PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(current_dir)
sys.path.append(parent_dir)

from LICENSE_ADMIN.license_checker import get_license_info, get_promo_bandeau

def print_bandeau():
    """Affiche le bandeau de promotion en ASCII."""
    promo = get_promo_bandeau()
    if not promo:
        return
        
    bandeau = promo["bandeau"]
    text = bandeau["text"]
    width = len(text) + 4
    
    print("\n" + "=" * width)
    print("| " + text + " |")
    print("=" * width + "\n")

def print_user_page():
    """Affiche la page utilisateur en ASCII."""
    info = get_license_info()
    
    # En-tête
    print("\n" + "=" * 50)
    print(" " * 15 + "LOTO AI PREDICTOR")
    print("=" * 50)
    
    # Informations de licence
    print("\n📋 INFORMATIONS DE LICENCE")
    print("-" * 50)
    print(f"Type de licence : {info['type'].upper()}")
    print(f"Statut : {info['status']}")
    print(f"Expiration : {info['expiration']}")
    
    # Jours restants
    days = info['jours_restants']
    if days > 0:
        print(f"\n⏳ Jours restants : {days}")
        if days <= 2:
            print("⚠️  Votre licence expire bientôt !")
    else:
        print("\n❌ Licence expirée")
    
    # Promotion
    if info['promo_active']:
        print("\n🎁 PROMOTION ACTIVE")
        print("-" * 50)
        if info['promo_bandeau']:
            print(info['promo_bandeau']['bandeau']['text'])
    
    # Pied de page
    print("\n" + "=" * 50)
    print(" " * 10 + "© 2024 LOTO AI PREDICTOR")
    print("=" * 50 + "\n")

if __name__ == "__main__":
    print_bandeau()
    print_user_page() 