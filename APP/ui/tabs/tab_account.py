from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton, QFileDialog, QMessageBox
)
from LICENSE_ADMIN.license_checker import should_show_promo
from utils.encryption import decrypt_ini, import_license_file
import webbrowser

class AccountTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        self.titre = QLabel("🔐 Choisissez votre licence :")
        self.combo = QComboBox()
        self.combo.addItems(["1 mois", "3 mois", "6 mois", "1 an"])
        self.combo.currentIndexChanged.connect(self.update_prices)

        self.label_prix = QLabel()
        self.promo_active = should_show_promo()

        self.pay_btn = QPushButton("💳 Payer avec PayPal")
        self.pay_btn.clicked.connect(self.lancer_paiement)

        self.import_btn = QPushButton("📥 Importer licence")
        self.import_btn.clicked.connect(self.importer_licence)

        layout.addWidget(self.titre)
        layout.addWidget(self.combo)
        layout.addWidget(self.label_prix)
        layout.addWidget(self.pay_btn)
        layout.addWidget(self.import_btn)

        self.setLayout(layout)
        self.update_prices()

    def update_prices(self):
        base_prices = {
            "1 mois": 15,
            "3 mois": 40,
            "6 mois": 75,
            "1 an": 120
        }
        choix = self.combo.currentText()
        prix = base_prices[choix]

        if self.promo_active:
            prix_red = round(prix * 0.9, 2)
            self.label_prix.setText(
                f"💰 Prix : <s>{prix} €</s> <span style='color:red;'> {prix_red} €</span> (-10%)"
            )
        else:
            self.label_prix.setText(f"💰 Prix : {prix} €")

    def lancer_paiement(self):
        choix = self.combo.currentText()
        prix = {
            "1 mois": 15,
            "3 mois": 40,
            "6 mois": 75,
            "1 an": 120
        }[choix]

        if self.promo_active:
            prix = round(prix * 0.9, 2)

        # Remplace ceci par ton lien réel PayPal
        lien = f"https://paypal.me/phoenixpay?amount={prix}"
        webbrowser.open(lien)

        QMessageBox.information(self, "Paiement lancé",
            "Merci de finaliser le paiement sur PayPal.\n"
            "Une licence vous sera envoyée par mail.")

    def importer_licence(self):
        fichier, _ = QFileDialog.getOpenFileName(self, "Sélectionner votre fichier de licence", "", "Licence (*.key)")
        if fichier:
            try:
                import_license_file(fichier)
                QMessageBox.information(self, "✅ Licence activée", "Votre licence a été importée.")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur d'import : {e}")
