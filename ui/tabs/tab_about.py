import tkinter as tk
from tkinter import ttk
from LICENSE_ADMIN.license_checker import get_license_info
from PIL import Image, ImageTk
import os
import webbrowser

class AboutTab(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        
        # Informations de licence
        info = get_license_info()
        
        # Frame pour les informations
        info_frame = ttk.LabelFrame(self, text="Informations de licence")
        info_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(info_frame, text="🧠 Logiciel : LotoAiPredictor", anchor="w").pack(fill="x", padx=5, pady=2)
        ttk.Label(info_frame, text=f"🔐 Type de licence : {info['type']}", anchor="w").pack(fill="x", padx=5, pady=2)
        ttk.Label(info_frame, text=f"📅 Expiration : {info['expiration']}", anchor="w").pack(fill="x", padx=5, pady=2)
        ttk.Label(info_frame, text=f"⏳ Jours restants : {info['jours_restants']}", anchor="w").pack(fill="x", padx=5, pady=2)
        
        if info['type'] == "demo":
            ttk.Label(info_frame, text=f"🎟️ Grilles restantes : {info['grilles_restantes']}", anchor="w").pack(fill="x", padx=5, pady=2)
        
        # Frame pour le support
        support_frame = ttk.LabelFrame(self, text="Support du projet")
        support_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(support_frame, text="💝 Soutenez le développement", anchor="w").pack(fill="x", padx=5, pady=2)
        ttk.Label(support_frame, text="Votre soutien nous aide à améliorer le logiciel", anchor="w").pack(fill="x", padx=5, pady=2)
        
        # Bouton de don PayPal
        paypal_button = ttk.Button(support_frame, text="Faire un don via PayPal", 
                                 command=self.open_paypal)
        paypal_button.pack(pady=5)
        
        # Frame pour les boutons de simulation
        sim_frame = ttk.LabelFrame(self, text="Simulation des modes")
        sim_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(sim_frame, text="Mode Admin", command=lambda: self.simulate_mode("admin")).pack(fill="x", padx=5, pady=2)
        ttk.Button(sim_frame, text="Mode Client", command=lambda: self.simulate_mode("client")).pack(fill="x", padx=5, pady=2)
        ttk.Button(sim_frame, text="Mode Démo", command=lambda: self.simulate_mode("demo")).pack(fill="x", padx=5, pady=2)
        
        # Bouton Quitter
        ttk.Button(self, text="Quitter", command=self.quit_application).pack(pady=10)
    
    def open_paypal(self):
        """Ouvre la page PayPal pour faire un don."""
        webbrowser.open("https://www.paypal.com/paypalme/PhoenixGuardianSales?country.x=FR&locale.x=fr_FR")
    
    def simulate_mode(self, mode):
        """Simule un mode d'utilisation spécifique."""
        from ui.gui import launch_app
        
        # Définition des permissions selon le mode
        permissions = {
            "admin": {"is_admin": True, "is_client": False},
            "client": {"is_admin": False, "is_client": True},
            "demo": {"is_admin": False, "is_client": False}
        }
        
        # Redémarrage de l'application avec les nouvelles permissions
        self.master.destroy()
        launch_app(permissions[mode])
    
    def quit_application(self):
        """Ferme proprement l'application."""
        self.master.destroy()

def show_about_dialog(parent):
    """Affiche la boîte de dialogue À propos."""
    dialog = tk.Toplevel(parent)
    dialog.title("À propos")
    dialog.geometry("400x300")
    dialog.resizable(False, False)
    
    # Empêcher l'interaction avec la fenêtre principale
    dialog.transient(parent)
    dialog.grab_set()
    
    # Frame principal
    main_frame = ttk.Frame(dialog, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Logo
    try:
        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                "WEB", "assets", "Logo_LotoAIPredictor.png")
        if os.path.exists(logo_path):
            logo = Image.open(logo_path)
            logo = logo.resize((100, 100), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(logo)
            logo_label = ttk.Label(main_frame, image=photo)
            logo_label.image = photo  # Garde une référence
            logo_label.pack(pady=10)
    except Exception as e:
        print(f"Erreur lors du chargement du logo : {e}")
    
    # Titre
    title_label = ttk.Label(main_frame, text="LotoAI Predictor", font=("Helvetica", 16, "bold"))
    title_label.pack(pady=5)
    
    # Version
    version_label = ttk.Label(main_frame, text="Version 1.0.0")
    version_label.pack()
    
    # Description
    desc_text = """LotoAI Predictor est un outil d'aide à la prédiction 
pour les jeux de loterie, utilisant l'intelligence artificielle 
pour analyser les tendances et générer des prédictions."""
    desc_label = ttk.Label(main_frame, text=desc_text, wraplength=350, justify=tk.CENTER)
    desc_label.pack(pady=10)
    
    # Support
    support_text = "💝 Soutenez le développement du projet"
    support_label = ttk.Label(main_frame, text=support_text, wraplength=350, justify=tk.CENTER)
    support_label.pack(pady=5)
    
    # Bouton PayPal
    paypal_button = ttk.Button(main_frame, text="Faire un don via PayPal", 
                             command=lambda: webbrowser.open("https://www.paypal.com/paypalme/PhoenixGuardianSales?country.x=FR&locale.x=fr_FR"))
    paypal_button.pack(pady=5)
    
    # Copyright
    copyright_label = ttk.Label(main_frame, text="© 2024 PhoenixGuardianTools")
    copyright_label.pack(pady=5)
    
    # Bouton Fermer
    ttk.Button(main_frame, text="Fermer", command=dialog.destroy).pack(pady=10)
    
    # Centrer la fenêtre
    dialog.update_idletasks()
    width = dialog.winfo_width()
    height = dialog.winfo_height()
    x = (dialog.winfo_screenwidth() // 2) - (width // 2)
    y = (dialog.winfo_screenheight() // 2) - (height // 2)
    dialog.geometry(f'{width}x{height}+{x}+{y}')
    
    # Attendre que la fenêtre soit fermée
    parent.wait_window(dialog)
