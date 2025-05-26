from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit

class UserGuideTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("📘 Guide utilisateur"))

        guide_text = QTextEdit()
        guide_text.setReadOnly(True)
        guide_text.setPlainText(
            "Bienvenue dans LotoAiPredictor.\n\n"
            "- 🎰 Onglet Jeux : Générez des grilles automatiquement.\n"
            "- 📅 Résultats : Consultez les tirages passés.\n"
            "- 📤 Export : Sauvegardez vos prédictions et vos gains.\n"
            "- ⚙️ Configuration : Paramétrez vos mails d'envoi et préférences.\n"
            "- 💬 Feedback : Envoyez-nous vos remarques.\n"
            "- ℹ️ À propos : Infos sur votre licence.\n\n"
            "Besoin d'aide ? Contactez-nous via le formulaire de feedback."
        )
        layout.addWidget(guide_text)

        self.setLayout(layout)
