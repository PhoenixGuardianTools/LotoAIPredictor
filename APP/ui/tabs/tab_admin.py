from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QGroupBox, QMessageBox, QTextEdit
)
from core.predictor import set_active_model
from utils.smtp_handler import test_smtp_connection
from utils.encryption import update_config_admin, decrypt_ini
import smtplib
from email.mime.text import MIMEText
from subprocess import run

class AdminTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        # Modèle de prédiction
        self.model_selector = QComboBox()
        self.model_selector.addItems(["Modèle A (standard)", "Modèle B (optimisé)"])
        self.model_selector.currentIndexChanged.connect(self.set_model)
        layout.addWidget(QLabel("🎯 Modèle actif :"))
        layout.addWidget(self.model_selector)

        # SMTP
        smtp_group = QGroupBox("📡 Configuration SMTP")
        smtp_layout = QVBoxLayout()
        self.smtp_host = QLineEdit()
        self.smtp_port = QLineEdit()
        smtp_layout.addWidget(QLabel("Serveur SMTP :"))
        smtp_layout.addWidget(self.smtp_host)
        smtp_layout.addWidget(QLabel("Port :"))
        smtp_layout.addWidget(self.smtp_port)

        smtp_test = QPushButton("Tester la connexion")
        smtp_test.clicked.connect(self.test_smtp)
        smtp_layout.addWidget(smtp_test)
        smtp_group.setLayout(smtp_layout)
        layout.addWidget(smtp_group)

        # Entreprise
        entreprise_group = QGroupBox("🏢 Informations entreprise")
        ent_layout = QVBoxLayout()
        self.nom_entreprise = QLineEdit()
        self.siret = QLineEdit()
        self.site_web = QLineEdit()

        ent_layout.addWidget(QLabel("Nom entreprise :"))
        ent_layout.addWidget(self.nom_entreprise)
        ent_layout.addWidget(QLabel("SIRET (optionnel) :"))
        ent_layout.addWidget(self.siret)
        ent_layout.addWidget(QLabel("Site web :"))
        ent_layout.addWidget(self.site_web)

        save_btn = QPushButton("💾 Sauvegarder")
        save_btn.clicked.connect(self.save_config)
        ent_layout.addWidget(save_btn)
        entreprise_group.setLayout(ent_layout)
        layout.addWidget(entreprise_group)

        # Feedback
        feedback_group = QGroupBox("📬 Contact support")
        fb_layout = QVBoxLayout()
        self.fb_subject = QLineEdit()
        self.fb_subject.setPlaceholderText("Sujet")
        self.fb_message = QTextEdit()
        self.fb_message.setPlaceholderText("Votre message...")

        fb_btn = QPushButton("Envoyer")
        fb_btn.clicked.connect(self.send_feedback)

        fb_layout.addWidget(self.fb_subject)
        fb_layout.addWidget(self.fb_message)
        fb_layout.addWidget(fb_btn)
        feedback_group.setLayout(fb_layout)
        layout.addWidget(feedback_group)

        # Statistiques web
        web_btn = QPushButton("🌐 Publier les statistiques web")
        web_btn.clicked.connect(self.publish_web)
        layout.addWidget(web_btn)

        self.setLayout(layout)

    def set_model(self):
        model = "A" if self.model_selector.currentIndex() == 0 else "B"
        set_active_model(model)
        QMessageBox.information(self, "Succès", f"Modèle {model} activé.")

    def test_smtp(self):
        try:
            test_smtp_connection(self.smtp_host.text(), int(self.smtp_port.text()))
            QMessageBox.information(self, "Succès", "Connexion SMTP valide.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur SMTP", str(e))

    def save_config(self):
        data = {
            "smtp_host": self.smtp_host.text(),
            "smtp_port": self.smtp_port.text(),
            "entreprise": self.nom_entreprise.text(),
            "siret": self.siret.text(),
            "site": self.site_web.text()
        }
        update_config_admin(data)
        QMessageBox.information(self, "Sauvegardé", "Configuration enregistrée.")

    def send_feedback(self):
        subject = self.fb_subject.text().strip()
        message = self.fb_message.toPlainText().strip()
        if not message:
            QMessageBox.warning(self, "Erreur", "Message vide.")
            return

        try:
            config = decrypt_ini("SECURITY/config_admin.ini.enc")
            msg = MIMEText(message)
            msg["Subject"] = subject or "Feedback Admin"
            msg["From"] = config["email"]
            msg["To"] = "contact@phoenixproject.onmicrosoft.com"

            with smtplib.SMTP_SSL(config["smtp_host"], int(config["smtp_port"])) as server:
                server.login(config["email"], config["token"])
                server.send_message(msg)

            QMessageBox.information(self, "Envoyé", "Message transmis avec succès.")
            self.fb_subject.clear()
            self.fb_message.clear()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Envoi échoué : {e}")

    def publish_web(self):
        try:
            run(["python", "TOOLS/export_web_data.py"], check=True)
            run(["cmd", "/c", "start", "ADMIN_TOOLS/web_push.bat"])
            QMessageBox.information(self, "Publication", "Statistiques web publiées avec succès.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Publication échouée : {e}")
