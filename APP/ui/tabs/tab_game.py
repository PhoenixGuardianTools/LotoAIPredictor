from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox,
    QListWidget, QComboBox, QSpinBox
)
from core.analytics import suggest_play_strategy
from core.predictor import generate_grille, get_active_model
from core.database import save_grille
from LICENSE_ADMIN.license_checker import (
    is_demo_mode, get_license_info, decrement_grilles_demo
)

import random

class GameTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()

        # Sélection du jeu
        self.jeu_selector = QComboBox()
        self.jeu_selector.addItems(["loto", "euromillion", "eurodream"])
        self.layout.addWidget(QLabel("🎰 Sélectionnez un jeu :"))
        self.layout.addWidget(self.jeu_selector)

        # Nombre de grilles
        self.nb_grilles = QSpinBox()
        self.nb_grilles.setMinimum(1)
        self.nb_grilles.setMaximum(10)
        self.nb_grilles.setValue(3)
        self.layout.addWidget(QLabel("🔢 Nombre de grilles à générer :"))
        self.layout.addWidget(self.nb_grilles)

        # Bouton de génération
        gen_btn = QPushButton("🎯 Générer les grilles")
        gen_btn.clicked.connect(self.gen_grilles)
        self.layout.addWidget(gen_btn)

        # Affichage des grilles générées
        self.list_grilles = QListWidget()
        self.layout.addWidget(self.list_grilles)

        # Encart Conseil du jour
        self.suggestion_label = QLabel()
        self.layout.addWidget(self.suggestion_label)
        self.update_suggestion_display()

        self.setLayout(self.layout)

        self.check_demo_banner()

    def check_demo_banner(self):
        if is_demo_mode():
            if random.random() < 0.5:
                info = get_license_info()
                QMessageBox.information(self, "🔓 Mode Démo",
                    f"Vous êtes en mode démo. Grilles restantes : {info['grilles_restantes']}\n"
                    "Abonnez-vous pour débloquer toutes les fonctions !")

    def gen_grilles(self):
        jeu = self.jeu_selector.currentText()
        n = self.nb_grilles.value()
        self.list_grilles.clear()

        if is_demo_mode():
            info = get_license_info()
            if info["grilles_restantes"] <= 0:
                QMessageBox.critical(self, "🔒 Limite atteinte",
                    "Votre quota de 10 grilles en mode démo est atteint.\nPassez à la version complète.")
                return

            if n > info["grilles_restantes"]:
                QMessageBox.warning(self, "⚠️ Trop de grilles",
                    f"Il vous reste {info['grilles_restantes']} grilles. Ajustez le nombre.")
                return

        for _ in range(n):
            grille = generate_grille(jeu)
            modele = get_active_model()
            save_grille(jeu, grille, modele)
            self.list_grilles.addItem(f"{jeu.upper()} - {grille} (modèle {modele})")

            if is_demo_mode():
                decrement_grilles_demo()

    def update_suggestion_display(self):
        suggestion = suggest_play_strategy()
        self.suggestion_label.setText(f"📈 Conseil du jour : {suggestion}")
