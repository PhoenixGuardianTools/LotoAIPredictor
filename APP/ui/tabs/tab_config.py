from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QLabel, QPushButton, QMessageBox
from utils.encryption import update_config_secure

class ConfigTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("⚙️ Paramètres SMTP :"))
        self.smtp_host = QLineEdit()
        self.smtp_port = QLineEdit()
        layout.addWidget(QLabel("Hôte SMTP"))
        layout.addWidget(self.smtp_host)
        layout.addWidget(QLabel("Port SMTP"))
        layout.addWidget(self.smtp_port)

        save_btn = QPushButton("Enregistrer")
        save_btn.clicked.connect(self.save_config)
        layout.addWidget(save_btn)

        self.setLayout(layout)

    def save_config(self):
        data = {
            "host": self.smtp_host.text(),
            "port": self.smtp_port.text()
        }
        update_config_secure(data)
        QMessageBox.information(self, "Enregistré", "Configuration SMTP sauvegardée.")
