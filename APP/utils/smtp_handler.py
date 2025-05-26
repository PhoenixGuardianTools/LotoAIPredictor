import smtplib

def test_smtp_connection(host: str, port: int):
    try:
        server = smtplib.SMTP_SSL(host, port, timeout=5)
        server.quit()
    except Exception as e:
        raise ConnectionError(f"Connexion échouée : {e}")
