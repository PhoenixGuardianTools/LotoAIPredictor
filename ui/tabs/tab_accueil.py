import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from pathlib import Path
from datetime import datetime

class AccueilTab(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        
        # Chargement du logo
        logo_path = Path(__file__).resolve().parent.parent.parent / "WEB" / "assets" / "Logo_LotoAIPredictor.png"
        if logo_path.exists():
            logo_img = Image.open(logo_path)
            logo_img = logo_img.resize((200, 200), Image.Resampling.LANCZOS)
            self.logo = ImageTk.PhotoImage(logo_img)
            logo_label = tk.Label(self, image=self.logo)
            logo_label.pack(pady=20)
        
        # Titre du logiciel
        title_label = tk.Label(self, text="LotoAI Predictor", font=("Helvetica", 24, "bold"))
        title_label.pack(pady=20)
        
        # Boutons de sélection du jeu
        games_frame = ttk.Frame(self)
        games_frame.pack(pady=20)
        
        ttk.Button(games_frame, text="Loto", command=lambda: self.open_game_window("Loto")).pack(side="left", padx=10)
        ttk.Button(games_frame, text="EuroDreams", command=lambda: self.open_game_window("EuroDreams")).pack(side="left", padx=10)
        ttk.Button(games_frame, text="Euromillions", command=lambda: self.open_game_window("Euromillions")).pack(side="left", padx=10)
        
        # Version et copyright
        version_label = tk.Label(self, text="Version 1.0", font=("Helvetica", 8))
        version_label.pack(side="right", padx=10, pady=5)
        
        copyright_label = tk.Label(self, text=f"© PhoenixProject {datetime.now().year}", font=("Helvetica", 8))
        copyright_label.pack(side="bottom", pady=5)
    
    def open_game_window(self, game_type):
        """Ouvre la fenêtre de jeu correspondante."""
        from ui.frm.frm_game_window import GameWindow
        GameWindow(self, game_type) 