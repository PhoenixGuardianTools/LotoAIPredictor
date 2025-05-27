"""
Module de gestion des connexions SMTP pour l'envoi d'emails.
"""

import smtplib
from typing import NoReturn

def test_smtp_connection(host: str, port: int) -> NoReturn:
    """
    Teste la connexion à un serveur SMTP.
    
    Args:
        host (str): L'adresse du serveur SMTP
        port (int): Le port du serveur SMTP
        
    Raises:
        ConnectionError: Si la connexion échoue
    """
    try:
        server = smtplib.SMTP_SSL(host, port, timeout=5)
        server.quit()
    except Exception as e:
        raise ConnectionError(f"Connexion échouée : {e}")
