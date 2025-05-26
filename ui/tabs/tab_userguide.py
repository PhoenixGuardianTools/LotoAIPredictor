import tkinter as tk

class UserGuideTab(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack(fill="both", expand=True)

        tk.Label(self, text="📘 Guide utilisateur", anchor="w", justify="left", font=("Arial", 12, "bold")).pack(fill="x", padx=5, pady=5)

        guide_text = (
            "Bienvenue dans LotoAiPredictor.\n\n"
            "- 🎰 Onglet Jeux : Générez des grilles automatiquement.\n"
            "- 📅 Résultats : Consultez les tirages passés.\n"
            "- 📤 Export : Sauvegardez vos prédictions et vos gains.\n"
            "- ⚙️ Configuration : Paramétrez vos mails d'envoi et préférences.\n"
            "- 💬 Feedback : Envoyez-nous vos remarques.\n"
            "- ℹ️ À propos : Infos sur votre licence.\n\n"
            "Besoin d'aide ? Contactez-nous via le formulaire de feedback."
        )

        text_widget = tk.Text(self, height=14, wrap="word")
        text_widget.insert("1.0", guide_text)
        text_widget.config(state="disabled")
        text_widget.pack(fill="both", expand=True, padx=5, pady=5)
