import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from pathlib import Path
from core.encryption import decrypt_ini

class Mailer:
    def __init__(self):
        """Initialise le mailer avec la configuration par défaut."""
        self.config_path = Path(__file__).resolve().parent.parent / "SECURITY" / "config_admin.ini.enc"
        self.config = decrypt_ini(self.config_path)
        self.smtp_server = self.config['EMAIL']['smtp_server']
        self.smtp_port = int(self.config['EMAIL']['smtp_port'])
        self.sender_email = self.config['EMAIL']['sender']
        self.smtp_password = self.config['EMAIL']['password']

    def send_email(self, to_email: str, subject: str, body: str, attachments: list = None) -> bool:
        """
        Envoie un email avec pièces jointes optionnelles.
        
        Args:
            to_email (str): Adresse email du destinataire
            subject (str): Sujet de l'email
            body (str): Corps du message
            attachments (list, optional): Liste des chemins des fichiers à joindre
        
        Returns:
            bool: True si l'envoi a réussi, False sinon
        """
        try:
            # Création du message
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Ajout du corps du message
            if '<html' in body.lower() or '<body' in body.lower():
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            # Ajout des pièces jointes
            if attachments:
                for file_path in attachments:
                    with open(file_path, 'rb') as f:
                        part = MIMEApplication(f.read(), Name=Path(file_path).name)
                        part['Content-Disposition'] = f'attachment; filename="{Path(file_path).name}"'
                        msg.attach(part)
            
            # Connexion et envoi
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.smtp_password)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"⚠️ Erreur lors de l'envoi de l'email : {e}")
            return False

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
    mailer = Mailer()
    return mailer.send_email(
        to_email=recipient or mailer.sender_email,
        subject=subject,
        body=body
    ) 