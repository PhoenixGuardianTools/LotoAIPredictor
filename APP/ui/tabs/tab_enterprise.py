from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QLabel, QPushButton, QFileDialog, QComboBox, QMessageBox
from utils.encryption import update_config_admin, decrypt_ini

class EnterpriseTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        self.nom = QLineEdit()
        self.siret = QLineEdit()
        self.tva = QComboBox()
        self.tva.addItems(["Non applicable", "10%", "20%"])
        self.site = QLineEdit()
        self.mail = QLineEdit()
        self.tel = QLineEdit()
        self.logo_path = QLineEdit()

        logo_btn = QPushButton("📁 Sélectionner un logo")
        logo_btn.clicked.connect(self.select_logo)

        save_btn = QPushButton("💾 Enregistrer")
        save_btn.clicked.connect(self.save)

        layout.addWidget(QLabel("Nom entreprise :")); layout.addWidget(self.nom)
        layout.addWidget(QLabel("SIRET :")); layout.addWidget(self.siret)
        layout.addWidget(QLabel("TVA :")); layout.addWidget(self.tva)
        layout.addWidget(QLabel("Site web :")); layout.addWidget(self.site)
        layout.addWidget(QLabel("Email contact :")); layout.addWidget(self.mail)
        layout.addWidget(QLabel("Téléphone :")); layout.addWidget(self.tel)
        layout.addWidget(QLabel("Logo :")); layout.addWidget(self.logo_path)
        layout.addWidget(logo_btn)
        layout.addWidget(save_btn)

        self.setLayout(layout)

    def select_logo(self):
        file, _ = QFileDialog.getOpenFileName(self, "Sélectionner un logo", "", "Images (*.png *.jpg *.jpeg)")
        if file:
            self.logo_path.setText(file)

    def save(self):
        data = {
            "entreprise": self.nom.text(),
            "siret": self.siret.text(),
            "tva": self.tva.currentText(),
            "site": self.site.text(),
            "email_contact": self.mail.text(),
            "tel": self.tel.text(),
            "logo": self.logo_path.text()
        }
        update_config_admin(data)
        QMessageBox.information(self, "Enregistré", "Configuration entreprise sauvegardée.")
