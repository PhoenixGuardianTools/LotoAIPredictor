from PyQt6.QtWidgets import QWidget, QVBoxLayout, QComboBox, QTextEdit, QPushButton, QLabel, QLineEdit, QMessageBox
from utils.encryption import decrypt_ini
from email.mime.text import MIMEText
import smtplib

class SupportTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        self.subject_selector = QComboBox()
        self.subject_selector.addItems(["Message", "Remerciement", "Bug", "Demande d'évolution"])

        self.email_field = QLineEdit()
        self.email_field.setPlaceholderText("Votre adresse email")

        self.msg_box = QTextEdit()
        self.msg_box.setPlaceholderText("Votre message (500 caractères max)")
        self.msg_box.setMaximumHeight(100)

        send_btn = QPushButton("📤 Envoyer au support")
        send_btn.clicked.connect(self.send)

        layout.addWidget(QLabel("Sujet :"))
        layout.addWidget(self.subject_selector)
        layout.addWidget(QLabel("Email :"))
        layout.addWidget(self.email_field)
        layout.addWidget(QLabel("Message :"))
        layout.addWidget(self.msg_box)
        layout.addWidget(send_btn)

        self.setLayout(layout)

    def send(self):
        sujet = self.subject_selector.currentText()
        message = self.msg_box.toPlainText().strip()[:500]
        user_email = self.email_field.text().strip()

        if not user_email or not message:
            QMessageBox.warning(self, "Erreur", "Veuillez remplir tous les champs.")
            return

        try:
            conf = decrypt_ini("SECURITY/config_admin.ini.enc")
            msg = MIMEText(message)
            msg["Subject"] = f"[{sujet}] - Demande utilisateur"
            msg["From"] = conf["email"]
            msg["To"] = conf["support"]
            msg["Cc"] = user_email

            with smtplib.SMTP_SSL(conf["smtp_host"], int(conf["smtp_port"])) as server:
                server.login(conf["email"], conf["token"])
                server.send_message(msg)

            QMessageBox.information(self, "Envoyé", "Votre message a bien été transmis.")
            self.msg_box.clear()
        except Exception as e:
            QMessageBox.critical(self, "Erreur SMTP", str(e))
