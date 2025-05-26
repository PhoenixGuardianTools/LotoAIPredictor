import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from core.mailer import send_email

sujet = "Test d'envoi de mail PhoenixProject"
corps = """
Bonjour,

Ceci est un test d'envoi de mail automatique depuis PhoenixProject.

Merci de confirmer la bonne réception.

Cordialement,
L'équipe PhoenixProject
"""

destinataire = "phoenix38@riseup.net"

resultat = send_email(sujet, corps, destinataire)
if resultat:
    print("✅ Email envoyé avec succès à phoenix38@riseup.net")
else:
    print("❌ Échec de l'envoi de l'email.") 