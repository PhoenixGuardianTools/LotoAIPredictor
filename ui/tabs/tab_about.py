import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import webbrowser
import configparser
from view.class_ui.tabs.class_tab import ClassTab
from core.versioning import VersionManager

class AboutTab(ClassTab):
    def create_widgets(self):
        # Charger la configuration
        config = configparser.ConfigParser()
        config.read('config/society_config.ini')
        
        # Obtenir la version
        version_manager = VersionManager()
        version = version_manager.get_version_string()
        
        # Frame pour les informations
        info_frame = ttk.LabelFrame(self, text="À propos")
        info_frame.pack(fill="x", padx=10, pady=5)
        
        # Logo
        try:
            logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                    "WEB", "assets", "Logo_LotoAIPredictor.png")
            if os.path.exists(logo_path):
                logo = Image.open(logo_path)
                logo = logo.resize((100, 100), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(logo)
                logo_label = ttk.Label(info_frame, image=photo)
                logo_label.image = photo  # Garde une référence
                logo_label.pack(pady=10)
        except Exception as e:
            print(f"Erreur lors du chargement du logo : {e}")
        
        # Titre
        title_label = ttk.Label(info_frame, text="LotoAI Predictor", font=("Helvetica", 16, "bold"))
        title_label.pack(pady=5)
        
        # Version
        version_label = ttk.Label(info_frame, text=f"Version {version}")
        version_label.pack()
        
        # Description
        desc_text = """LotoAI Predictor est un outil d'aide à la prédiction 
pour les jeux de loterie, utilisant l'intelligence artificielle 
pour analyser les tendances et générer des prédictions."""
        desc_label = ttk.Label(info_frame, text=desc_text, wraplength=350, justify=tk.CENTER)
        desc_label.pack(pady=10)
        
        # Frame pour le support
        support_frame = ttk.LabelFrame(self, text="Support")
        support_frame.pack(fill="x", padx=10, pady=5)
        
        # Bouton site web
        web_button = ttk.Button(support_frame, text="Visiter notre site web", 
                              command=lambda: webbrowser.open(config['Company']['link_website']))
        web_button.pack(pady=5)
        
        # Bouton GitHub
        git_button = ttk.Button(support_frame, text="Voir le code source", 
                              command=lambda: webbrowser.open(config['Company']['link_git']))
        git_button.pack(pady=5)
        
        # Bouton PayPal
        paypal_button = ttk.Button(support_frame, text="Faire un don via PayPal", 
                                 command=lambda: webbrowser.open(config['Company']['link_paypal']))
        paypal_button.pack(pady=5)
        
        # Copyright et Licence
        copyright_label = ttk.Label(support_frame, text=config['Company']['copyright'])
        copyright_label.pack(pady=5)
        
        license_label = ttk.Label(support_frame, text=config['Company']['LicenseMIT'])
        license_label.pack(pady=5) 