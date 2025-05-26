from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from LICENSE_ADMIN.license_checker import get_license_info

class AboutTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        info = get_license_info()

        layout.addWidget(QLabel("🧠 Logiciel : LotoAiPredictor"))
        layout.addWidget(QLabel(f"🔐 Type de licence : {info['type']}"))
        layout.addWidget(QLabel(f"📅 Expiration : {info['expiration']}"))
        layout.addWidget(QLabel(f"⏳ Jours restants : {info['jours_restants']}"))

        if info['type'] == "demo":
            layout.addWidget(QLabel(f"🎟️ Grilles restantes : {info['grilles_restantes']}"))

        self.setLayout(layout)
