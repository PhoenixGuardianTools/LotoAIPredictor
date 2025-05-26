from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton

class CRMTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("👥 Liste des clients actifs"))
        self.liste = QListWidget()
        layout.addWidget(self.liste)

        refresh_btn = QPushButton("🔄 Rafraîchir")
        refresh_btn.clicked.connect(self.charger_clients)

        layout.addWidget(refresh_btn)
        self.setLayout(layout)
        self.charger_clients()

    def charger_clients(self):
        self.liste.clear()
        try:
            with open("DATABASE/clients.csv", encoding="utf-8") as f:
                for ligne in f.readlines():
                    self.liste.addItem(ligne.strip())
        except:
            self.liste.addItem("Aucun client enregistré.")
