from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, QMessageBox
from utils.facture import generer_facture
from utils.encryption import decrypt_ini
import datetime

class FacturationTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        self.duree_box = QComboBox()
        self.duree_box.addItems(["1 mois", "3 mois", "6 mois", "1 an"])
        layout.addWidget(QLabel("Durée de l'abonnement :"))
        layout.addWidget(self.duree_box)

        btn_facture = QPushButton("📄 Générer une facture + licence")
        btn_facture.clicked.connect(self.generer)

        layout.addWidget(btn_facture)
        self.setLayout(layout)

    def generer(self):
        duree = self.duree_box.currentText()
        info = decrypt_ini("SECURITY/config_admin.ini.enc")
        email = info.get("email", "client@example.com")
        today = datetime.datetime.today().strftime("%Y-%m-%d")

        success = generer_facture(nom_client=email, duree=duree, date=today)

        if success:
            QMessageBox.information(self, "Succès", "Facture et licence générées et envoyées.")
        else:
            QMessageBox.critical(self, "Erreur", "Impossible de générer la facture.")
