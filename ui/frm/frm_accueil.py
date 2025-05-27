import tkinter as tk
from tkinter import ttk
import json
from pathlib import Path
from ui.frm.frm_game_window import show_game_window
from ui.base_window import BaseWindow
from ui.gui import launch_app
from LICENSE_ADMIN.license_checker import get_license_info

class AccueilWindow(BaseWindow):
    def __init__(self):
        super().__init__(title="Phoenix Project - Accueil", width=1000, height=700)
        self.create_widgets()
        
    def create_widgets(self):
        # Frame central pour le contenu
        content_frame = ttk.Frame(self.center_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)
        
        # Titre avec logo
        title_frame = ttk.Frame(content_frame)
        title_frame.pack(fill=tk.X, pady=(0, 30))
        
        title_label = ttk.Label(title_frame, 
                              text="Phoenix Project", 
                              font=("Helvetica", 36, "bold"),
                              foreground="#2C3E50")
        title_label.pack()
        
        subtitle_label = ttk.Label(title_frame,
                                 text="Votre assistant intelligent pour le Loto",
                                 font=("Helvetica", 16),
                                 foreground="#7F8C8D")
        subtitle_label.pack(pady=(5, 0))
        
        # Frame pour les fonctionnalités
        features_frame = ttk.LabelFrame(content_frame, text="Fonctionnalités", padding=20)
        features_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        # Liste des fonctionnalités
        features = [
            "🎯 Prédictions intelligentes basées sur l'IA",
            "📊 Analyses statistiques avancées",
            "📈 Visualisations graphiques détaillées",
            "🔍 Historique complet des tirages",
            "📱 Interface intuitive et moderne"
        ]
        
        for feature in features:
            feature_label = ttk.Label(features_frame, 
                                    text=feature,
                                    font=("Helvetica", 12),
                                    padding=(10, 5))
            feature_label.pack(anchor=tk.W, pady=2)
        
        # Frame pour les informations de licence
        license_info = get_license_info()
        license_frame = ttk.LabelFrame(content_frame, text="Informations de licence", padding=20)
        license_frame.pack(fill=tk.X, pady=20)
        
        license_text = f"Type de licence : {license_info['type'].upper()}"
        if license_info['type'] != 'demo':
            license_text += f"\nExpiration : {license_info['expiration']}"
            if license_info['grilles_restantes'] > 0:
                license_text += f"\nGrilles restantes : {license_info['grilles_restantes']}"
        
        license_label = ttk.Label(license_frame,
                                text=license_text,
                                font=("Helvetica", 11),
                                justify=tk.LEFT)
        license_label.pack(anchor=tk.W)
        
        # Frame pour les boutons
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Style pour le bouton principal
        style = ttk.Style()
        style.configure("Accent.TButton", 
                       font=("Helvetica", 12, "bold"),
                       padding=10)
        
        # Bouton Commencer
        start_btn = ttk.Button(button_frame,
                             text="Commencer",
                             command=self.start_app,
                             style="Accent.TButton",
                             width=20)
        start_btn.pack(pady=10)
        
    def start_app(self):
        """Lance l'application principale et ferme la fenêtre d'accueil."""
        self.destroy()  # Ferme la fenêtre d'accueil
        launch_app()  # Lance la fenêtre principale

def show_accueil_window(parent=None):
    """Affiche la fenêtre d'accueil."""
    window = AccueilWindow()
    window.mainloop() 