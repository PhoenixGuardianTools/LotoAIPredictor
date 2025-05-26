import sys
import os
from pathlib import Path

# Ajouter le dossier racine du projet au PYTHONPATH
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from APP.core.database import send_update_notification
from APP.core.encryption import decrypt_ini
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def test_email():
    print("📧 Test d'envoi d'email...")
    try:
        # Chemin du fichier de configuration
        config_path = Path(__file__).resolve().parent.parent / "SECURITY" / "config_admin.ini.enc"
        print(f"📂 Lecture du fichier de configuration : {config_path}")
        
        # Déchiffrement de la configuration
        config = decrypt_ini(config_path)
        print("✅ Configuration déchiffrée avec succès")
        
        # Récupération des paramètres SMTP
        smtp_server = config['EMAIL']['smtp_server']
        smtp_port = int(config['EMAIL']['smtp_port'])
        sender_email = config['EMAIL']['sender']
        smtp_password = config['EMAIL']['password']
        
        print(f"\n🔌 Connexion au serveur SMTP :")
        print(f"   Serveur : {smtp_server}")
        print(f"   Port : {smtp_port}")
        print(f"   Expéditeur : {sender_email}")
        
        # Création du message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = sender_email
        msg['Subject'] = "Test d'envoi d'email - LotoAIPredictor"
        
        body = f"""
        Test d'envoi d'email depuis LotoAIPredictor
        Date : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        Ce message est un test de la fonctionnalité d'envoi d'email.
        """
        msg.attach(MIMEText(body, 'plain'))
        
        # Connexion au serveur SMTP
        print("\n🔄 Connexion au serveur SMTP...")
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            print("✅ Connexion établie")
            server.starttls()
            print("✅ TLS activé")
            server.login(sender_email, smtp_password)
            print("✅ Authentification réussie")
            server.send_message(msg)
            print("✅ Message envoyé")
        
        print("\n✨ Test d'email réussi !")
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur lors du test d'email : {str(e)}")
        return False

if __name__ == "__main__":
    test_email() 