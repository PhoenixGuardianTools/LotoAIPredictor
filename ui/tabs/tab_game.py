import tkinter as tk
from tkinter import ttk, messagebox
from core.predictor import generate_grille, get_active_model
from core.database import save_grille
from LICENSE_ADMIN.license_checker import (
    is_demo_mode, get_license_info, decrement_grilles_demo
)
from core.predictions import generate_predictions, suggest_play_strategy
import pandas as pd
import random
import datetime

class GameTab(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        
        # Sélection du jeu
        tk.Label(self, text="🎰 Sélectionnez un jeu :").pack(anchor="w")
        self.jeu_selector = ttk.Combobox(self, values=["loto", "euromillion", "eurodream"])
        self.jeu_selector.current(0)
        self.jeu_selector.pack(fill="x", padx=5, pady=2)

        # Nombre de grilles
        tk.Label(self, text="🔢 Nombre de grilles à générer :").pack(anchor="w")
        self.nb_grilles = tk.Spinbox(self, from_=1, to=10)
        self.nb_grilles.pack(fill="x", padx=5, pady=2)

        # Bouton de génération
        gen_btn = tk.Button(self, text="🎯 Générer les grilles", command=self.gen_grilles)
        gen_btn.pack(fill="x", padx=5, pady=5)

        # Affichage des grilles générées
        self.list_grilles = tk.Listbox(self)
        self.list_grilles.pack(fill="both", expand=True, padx=5, pady=5)

        # Encart Conseil du jour
        self.suggestion_label = tk.Label(self, anchor="w", justify="left")
        self.suggestion_label.pack(fill="x", padx=5, pady=2)
        self.update_suggestion_display()

        # Encart Prédictions du jour
        self.prediction_label = tk.Label(self, anchor="w", justify="left")
        self.prediction_label.pack(fill="x", padx=5, pady=2)
        self.update_prediction_display()

        # Bouton pour rafraîchir les prédictions (optionnel)
        refresh_btn = tk.Button(self, text="🔄 Rafraîchir les prédictions du jour", command=self.update_prediction_display)
        refresh_btn.pack(fill="x", padx=5, pady=5)

        self.check_demo_banner()

    def check_demo_banner(self):
        if is_demo_mode():
            if random.random() < 0.5:
                info = get_license_info()
                messagebox.showinfo(
                    "🔓 Mode Démo",
                    f"Vous êtes en mode démo. Grilles restantes : {info['grilles_restantes']}\n"
                    "Abonnez-vous pour débloquer toutes les fonctions !"
                )

    def gen_grilles(self):
        jeu = self.jeu_selector.get()
        n = int(self.nb_grilles.get())
        self.list_grilles.delete(0, tk.END)

        if is_demo_mode():
            info = get_license_info()
            if info["grilles_restantes"] <= 0:
                messagebox.showerror(
                    "🔒 Limite atteinte",
                    "Votre quota de 10 grilles en mode démo est atteint.\nPassez à la version complète."
                )
                return

            if n > info["grilles_restantes"]:
                messagebox.showwarning(
                    "⚠️ Trop de grilles",
                    f"Il vous reste {info['grilles_restantes']} grilles. Ajustez le nombre."
                )
                return

        for _ in range(n):
            grille = generate_grille(jeu)
            modele = get_active_model()
            save_grille(jeu, grille, modele)
            self.list_grilles.insert(tk.END, f"{jeu.upper()} - {grille} (modèle {modele})")

            if is_demo_mode():
                decrement_grilles_demo()

    def update_suggestion_display(self):
        suggestion = suggest_play_strategy()
        self.suggestion_label.config(text=f"📈 Conseil du jour : {suggestion}")

    def update_prediction_display(self):
        """Met à jour l'encart avec les prédictions du jour."""
        try:
            history_df = pd.read_csv("data/history.csv")  # Chemin à adapter
        except Exception:
            self.prediction_label.config(text="❌ Impossible de charger l'historique pour les prédictions.")
            return

        predictions = generate_predictions(history_df)
        today = datetime.date.today().strftime("%d/%m/%Y")
        txt = f"🎯 Prédictions du {today} :\n"
        for jeu, nums in predictions.items():
            txt += f"{jeu} : {', '.join(map(str, nums))}\n"
        self.prediction_label.config(text=txt)
