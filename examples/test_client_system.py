from APP.merchand.client_manager import ClientManager
from core.newsletter_manager import NewsletterManager
from datetime import datetime
import uuid

def test_client_system():
    # Initialisation
    client_manager = ClientManager()
    newsletter_manager = NewsletterManager()
    
    # Test création client
    test_email = "test@example.com"
    test_uuid = str(uuid.uuid4())
    success, referral_code = client_manager.create_client(
        test_email,
        "1990-01-01",
        test_uuid
    )
    
    print(f"✅ Création client : {'Succès' if success else 'Échec'}")
    print(f"📝 Code de parrainage : {referral_code}")
    
    # Test parrainage
    new_client_email = "new@example.com"
    new_client_uuid = str(uuid.uuid4())
    success, _ = client_manager.create_client(
        new_client_email,
        "1995-01-01",
        new_client_uuid
    )
    
    if success:
        referral_success = client_manager.apply_referral(new_client_email, referral_code)
        print(f"✅ Application parrainage : {'Succès' if referral_success else 'Échec'}")
        
        # Vérification des licences
        referrer_info = client_manager.get_client_info(test_email)
        referred_info = client_manager.get_client_info(new_client_email)
        
        print("\n📊 Informations parrain :")
        print(f"Email : {referrer_info['email']}")
        print(f"Date d'expiration : {referrer_info['license_expiry']}")
        
        print("\n📊 Informations filleul :")
        print(f"Email : {referred_info['email']}")
        print(f"Parrainé par : {referred_info['referred_by']}")
        print(f"Date d'expiration : {referred_info['license_expiry']}")
    
    # Test paiement
    payment_success, message = client_manager.process_payment(
        test_email,
        "card",
        29.99
    )
    print(f"\n💳 Test paiement : {'Succès' if payment_success else 'Échec'}")
    print(f"Message : {message}")
    
    # Test newsletter
    context = {
        "version": "2.0.0",
        "features": [
            "Nouvelle interface",
            "Prédictions améliorées",
            "Mode hors ligne"
        ],
        "promo": "SPECIAL20"
    }
    
    try:
        content = newsletter_manager.generate_newsletter("Mise à jour", context)
        print("\n📧 Test newsletter :")
        print(content)
        
        # Test envoi
        newsletter_manager.send_newsletter(
            "Nouvelle version disponible !",
            content,
            [test_email],
            is_test=True
        )
        print("✅ Newsletter envoyée avec succès")
        
    except Exception as e:
        print(f"❌ Erreur newsletter : {e}")
    
    # Statistiques
    stats = newsletter_manager.get_newsletter_stats()
    print("\n📊 Statistiques newsletters :")
    print(f"Total envoyées : {stats['total_newsletters']}")
    print(f"Dernier envoi : {stats['last_sent']}")

if __name__ == "__main__":
    test_client_system() 