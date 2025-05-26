import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from merchand import NewsletterManager
from datetime import datetime
import uuid

def test_newsletter_system():
    # Initialisation
    newsletter_manager = NewsletterManager()
    
    # Test inscription
    test_email = "test@example.com"
    test_uuid = str(uuid.uuid4())
    
    success, message = newsletter_manager.subscribe(test_email, test_uuid)
    print(f"✅ Test inscription : {'Succès' if success else 'Échec'}")
    print(f"Message : {message}")
    
    # Test génération newsletter événement
    test_event = {
        "name": "Fête des Mères",
        "date": "26/05/2024",
        "message": "🎁 Offrez à votre maman une chance de gagner !"
    }
    
    content = newsletter_manager.generate_event_newsletter(test_event)
    print(f"\n📧 Test génération newsletter : {'Succès' if content else 'Échec'}")
    if content:
        print("Aperçu du contenu :")
        print(content[:200] + "...")
    
    # Test envoi newsletter
    newsletter_manager.send_event_newsletter(test_event)
    print("\n📨 Test envoi newsletter : Succès")
    
    # Test désinscription
    unsubscribe_success = newsletter_manager.unsubscribe(test_email)
    print(f"\n❌ Test désinscription : {'Succès' if unsubscribe_success else 'Échec'}")
    
    # Vérification des informations
    subscriber_info = newsletter_manager.get_subscriber_info(test_email)
    print("\n📋 Informations abonné :")
    print(f"Email : {subscriber_info['email']}")
    print(f"Statut : {'Actif' if subscriber_info['is_active'] else 'Inactif'}")
    print(f"Date d'inscription : {subscriber_info['created_at']}")
    print(f"Dernière mise à jour : {subscriber_info['last_updated']}")

def test_newsletter():
    # Initialisation
    newsletter_manager = NewsletterManager()
    
    # Création d'un événement de test
    event = {
        "name": "Fête des Mères",
        "date": "26/05/2024",
        "message": """
        <h2>🎁 Offrez à votre maman une chance de gagner !</h2>
        
        <p>Pour la Fête des Mères, offrez-lui le plus beau des cadeaux : la chance de gagner !</p>
        
        <p>Utilisez le code promo exclusif : <strong>MAMAN2024</strong><br>
        pour bénéficier de -15% sur votre abonnement.</p>
        
        <p>Cette offre est valable pendant 48h seulement !</p>
        
        <p>Ne manquez pas cette occasion unique de faire plaisir à votre maman
        tout en lui offrant la possibilité de réaliser ses rêves.</p>
        
        <p style="text-align: center; margin-top: 30px;">
            <a href="https://lotoaipredictor.com/offre-maman" 
               style="background-color: #4CAF50; color: white; padding: 15px 30px; 
                      text-decoration: none; border-radius: 5px;">
                Profiter de l'offre maintenant
            </a>
        </p>
        """
    }
    
    # Génération de la newsletter
    newsletter_content = newsletter_manager.generate_event_newsletter(event)
    
    # Affichage dans le terminal
    print("\n📧 Contenu de la newsletter :")
    print("=" * 80)
    print(newsletter_content)
    print("=" * 80)
    
    # Sauvegarde dans un fichier HTML pour visualisation
    output_path = Path("examples/newsletter_preview.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(newsletter_content)
    print(f"\n✅ Newsletter sauvegardée dans : {output_path}")
    print("Ouvrez ce fichier dans votre navigateur pour voir le rendu final.")

if __name__ == "__main__":
    test_newsletter_system()
    test_newsletter() 