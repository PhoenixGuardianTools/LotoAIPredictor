import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from core.encryption import decrypt_ini

def send_email(subject, body, recipient=None):
    """
    Fonction générique pour envoyer un email.
    
    Args:
        subject (str): Sujet de l'email
        body (str): Corps du message
        recipient (str, optional): Destinataire. Si None, utilise l'expéditeur par défaut.
    
    Returns:
        bool: True si l'envoi a réussi, False sinon
    """
    try:
        # Chemin du fichier de configuration
        config_path = Path(__file__).resolve().parent.parent / "SECURITY" / "config_admin.ini.enc"
        
        # Déchiffrement de la configuration
        config = decrypt_ini(config_path)
        
        # Récupération des paramètres SMTP
        smtp_server = config['EMAIL']['smtp_server']
        smtp_port = int(config['EMAIL']['smtp_port'])
        sender_email = config['EMAIL']['sender']
        smtp_password = config['EMAIL']['password']
        
        # Si aucun destinataire n'est spécifié, utiliser l'expéditeur
        if recipient is None:
            recipient = sender_email
        
        # Création du message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient
        msg['Subject'] = subject
        
        # Ajout du corps du message
        if '<html' in body.lower() or '<body' in body.lower():
            msg.attach(MIMEText(body, 'html'))
        else:
            msg.attach(MIMEText(body, 'plain'))
        
        # Connexion et envoi
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, smtp_password)
            server.send_message(msg)
        
        return True
        
    except Exception as e:
        print(f"⚠️ Erreur lors de l'envoi de l'email : {e}")
        return False 