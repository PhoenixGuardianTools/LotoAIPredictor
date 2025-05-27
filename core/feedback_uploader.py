import smtplib
from email.mime.text import MIMEText
from core.encryption import decrypt_ini

def send_feedback(message, subject="Feedback utilisateur"):
    """
    Envoie un message de feedback à l'équipe support.
    Le fichier SECURITY/config_admin.ini.enc doit contenir les infos SMTP.
    """
    try:
        config = decrypt_ini("SECURITY/config_admin.ini.enc")
        msg = MIMEText(message)
        msg["Subject"] = subject or "Feedback utilisateur"
        msg["From"] = config["email"]
        msg["To"] = config["support"]

        with smtplib.SMTP_SSL(config["smtp_host"], int(config["smtp_port"])) as server:
            server.login(config["email"], config["token"])
            server.send_message(msg)
    except Exception as e:
        raise RuntimeError(f"Erreur lors de l'envoi du feedback : {e}")