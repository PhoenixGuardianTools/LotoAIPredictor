from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget
from ui.tabs.tab_game import GameTab
from ui.tabs.tab_results import ResultsTab
from ui.tabs.tab_export import ExportTab
from ui.tabs.tab_about import AboutTab
from ui.tabs.tab_admin import AdminTab
from ui.tabs.tab_userguide import UserGuideTab
from ui.tabs.tab_support import SupportTab
from ui.tabs.tab_enterprise import EnterpriseTab

from LICENSE_ADMIN.license_checker import (
    is_admin_license,
    is_demo_mode,
    get_license_info,
    should_show_reminder,
    should_show_promo
)
from PyQt6.QtWidgets import QMessageBox

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LotoAiPredictor")

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Onglets communs
        self.tabs.addTab(GameTab(), "🎰 Jeux")
        self.tabs.addTab(ResultsTab(), "📅 Résultats")
        self.tabs.addTab(ExportTab(), "📤 Export")
        self.tabs.addTab(SupportTab(), "📬 Support")
        self.tabs.addTab(UserGuideTab(), "📘 Guide")
        self.tabs.addTab(AboutTab(), "ℹ️ À propos")

        # Onglets admin uniquement si licence admin
        if is_admin_license():
            self.tabs.addTab(AdminTab(), "🛠️ Admin")
            self.tabs.addTab(EnterpriseTab(), "🏢 Entreprise")

        self.check_license_state()

    def check_license_state(self):
        info = get_license_info()

        # Message expiration ou promo
        if should_show_reminder():
            QMessageBox.information(self, "⏰ Rappel licence",
                f"Votre licence expire dans {info['jours_restants']} jours.\n"
                f"Pensez à la renouveler pour éviter toute interruption.")

        if should_show_promo():
            QMessageBox.information(self, "🔥 Promo exclusive",
                "10% de réduction sur le renouvellement\nValable pendant 48h avant expiration.")

        if is_demo_mode():
            QMessageBox.warning(self, "🔓 Mode démo actif",
                f"Il vous reste {info['grilles_restantes']} grilles à générer.\n"
                "Passez à la version complète pour débloquer toutes les fonctions.")

def launch_app():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
