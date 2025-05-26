import sys
import os
from pathlib import Path

# Ajouter le dossier racine du projet au PYTHONPATH
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from APP.core.database import send_email
from datetime import datetime

def test_feedback():
    print("📧 Test d'envoi de feedback...")
    
    # Données de test
    subject = "Test de feedback"
    message = """
    Ceci est un message de test pour vérifier le système de feedback.
    
    Fonctionnalités testées :
    - Envoi d'email
    - Formatage du message
    - Gestion des erreurs
    
    Date du test : {}
    """.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    # Formatage du corps du message
    body = f"""
    Nouveau feedback reçu :
    
    Sujet : {subject}
    Date : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    
    Message :
    {message}
    """
    
    # Envoi du feedback
    print("\n🔄 Envoi du feedback...")
    if send_email(subject, body):
        print("✅ Feedback envoyé avec succès")
        return True
    else:
        print("❌ Échec de l'envoi du feedback")
        return False

if __name__ == "__main__":
    test_feedback() 