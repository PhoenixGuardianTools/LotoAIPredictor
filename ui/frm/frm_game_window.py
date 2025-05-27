import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from pathlib import Path
import json
from datetime import datetime, timedelta
from merchand.ui.base_window import BaseWindow 
# from merchand.license_manager import check_license
from core.encryption import decrypt_ini
import sqlite3
import requests
from bs4 import BeautifulSoup
import traceback
import configparser

def get_fdj_results():
    """Récupère les résultats depuis le site de la FDJ."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        results = {}
        
        # Loto
        loto_url = "https://www.fdj.fr/jeux-de-tirage/loto/resultats"
        print(f"Récupération des résultats du Loto depuis {loto_url}")
        loto_response = requests.get(loto_url, headers=headers)
        loto_response.raise_for_status()
        loto_soup = BeautifulSoup(loto_response.text, 'html.parser')
        
        # Extraction des numéros du Loto
        loto_nums = loto_soup.find_all('div', class_='numero')
        if loto_nums:
            results['loto'] = {
                'numeros': [n.text.strip() for n in loto_nums[:5]],
                'chance': loto_nums[5].text.strip() if len(loto_nums) > 5 else '',
                'date': datetime.now().strftime("%A %d/%m/%Y %H:%M")
            }
        
        # Euromillions
        euro_url = "https://www.fdj.fr/jeux-de-tirage/euromillions/resultats"
        print(f"Récupération des résultats de l'Euromillions depuis {euro_url}")
        euro_response = requests.get(euro_url, headers=headers)
        euro_response.raise_for_status()
        euro_soup = BeautifulSoup(euro_response.text, 'html.parser')
        
        # Extraction des numéros de l'Euromillions
        euro_nums = euro_soup.find_all('div', class_='numero')
        if euro_nums:
            results['euromillions'] = {
                'numeros': [n.text.strip() for n in euro_nums[:5]],
                'etoiles': [n.text.strip() for n in euro_nums[5:7]] if len(euro_nums) > 6 else [],
                'date': datetime.now().strftime("%A %d/%m/%Y %H:%M")
            }
        
        # Eurodreams
        dream_url = "https://www.fdj.fr/jeux-de-tirage/eurodreams/resultats"
        print(f"Récupération des résultats de l'Eurodreams depuis {dream_url}")
        dream_response = requests.get(dream_url, headers=headers)
        dream_response.raise_for_status()
        dream_soup = BeautifulSoup(dream_response.text, 'html.parser')
        
        # Extraction des numéros de l'Eurodreams
        dream_nums = dream_soup.find_all('div', class_='numero')
        if dream_nums:
            results['eurodreams'] = {
                'numeros': [n.text.strip() for n in dream_nums[:5]],
                'reve': dream_nums[5].text.strip() if len(dream_nums) > 5 else '',
                'date': datetime.now().strftime("%A %d/%m/%Y %H:%M")
            }
        
        return results
    except requests.exceptions.RequestException as e:
        print(f"Erreur de connexion : {e}")
        print("Veuillez vérifier votre connexion internet.")
        return None
    except Exception as e:
        print(f"Erreur inattendue : {e}")
        print(traceback.format_exc())
        return None

def get_local_results():
    """Récupère les résultats des 24 dernières heures depuis la base locale."""
    db_path = Path("data/loto.db")
    if not db_path.exists():
        return {}
    conn = sqlite3.connect(db_path)
    results = {}
    try:
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        for jeu, table in [
            ("loto", "tirages_loto"),
            ("euromillions", "tirages_euromillions"),
            ("eurodreams", "tirages_eurodreams")
        ]:
            try:
                cursor = conn.execute(f"SELECT date, numeros, chance, gagnant_rang1, montant_rang1, prochaine_cagnotte FROM {table} WHERE date >= ? ORDER BY date DESC LIMIT 1", (yesterday.strftime('%Y-%m-%d'),))
                row = cursor.fetchone()
                if row:
                    results[jeu] = {
                        "date": row[0],
                        "numeros": row[1],
                        "chance": row[2],
                        "gagnant_rang1": row[3],
                        "montant_rang1": row[4],
                        "prochaine_cagnotte": row[5],
                    }
            except Exception as e:
                pass
    finally:
        conn.close()
    return results

def print_games_current_results():
    """Affiche les résultats des jeux dans la console (base locale <24h ou web)."""
    try:
        print("\nRecherche des résultats dans la base locale...")
        local_results = get_local_results()
        any_local = any(local_results.values())
        if any_local:
            print("[SUCCÈS] Résultats trouvés dans la base locale (moins de 24h) :\n")
            print("="*50)
            for jeu in ["loto", "euromillions", "eurodreams"]:
                res = local_results.get(jeu)
                if res:
                    print(f"\nRésultat {jeu.capitalize()} - {res['date']}")
                    print(f"Numéros : {res['numeros']}")
                    if res['chance']:
                        print(f"Chance/Étoile/Rêve : {res['chance']}")
                    if res['gagnant_rang1']:
                        print(f"Gagnant(s) Rang 1 : {res['gagnant_rang1']}")
                    if res['montant_rang1']:
                        print(f"Montant Rang 1 : {res['montant_rang1']}")
                    if res['prochaine_cagnotte']:
                        print(f"Prochaine cagnotte : {res['prochaine_cagnotte']}")
                    print()
            print("\n" + "="*50 + "\n")
            return
        else:
            print("[INFO] Aucun résultat récent en base, tentative de récupération web...")
        
        # Récupération web
        fdj_results = get_fdj_results()
        if not fdj_results:
            print("[ÉCHEC] Impossible de récupérer les résultats. Veuillez réessayer plus tard.")
            return
            
        print("[SUCCÈS] Résultats récupérés sur le site FDJ :\n")
        print("="*50)
        
        # Affichage des résultats du Loto
        if 'loto' in fdj_results:
            loto = fdj_results['loto']
            print(f"\nRésultat Loto - {loto['date']}")
            print("Numéros : " + " - ".join(loto['numeros']))
            if loto['chance']:
                print(f"Numéro chance : {loto['chance']}")
            print()
            
        # Affichage des résultats de l'Euromillions
        if 'euromillions' in fdj_results:
            euro = fdj_results['euromillions']
            print(f"\nRésultat Euromillions - {euro['date']}")
            print("Numéros : " + " - ".join(euro['numeros']))
            if euro['etoiles']:
                print(f"Étoiles : " + " - ".join(euro['etoiles']))
            print()
            
        # Affichage des résultats de l'Eurodreams
        if 'eurodreams' in fdj_results:
            dream = fdj_results['eurodreams']
            print(f"\nRésultat Eurodreams - {dream['date']}")
            print("Numéros : " + " - ".join(dream['numeros']))
            if dream['reve']:
                print(f"Rêve : {dream['reve']}")
            print()
            
        print("\n" + "="*50 + "\n")
        
    except Exception as e:
        print(f"[ÉCHEC] Erreur lors de l'affichage des résultats : {e}")
        print(traceback.format_exc())
        print("Impossible de récupérer les résultats en direct. Veuillez vérifier votre connexion internet.")

class GameWindow(BaseWindow):
    def __init__(self, parent):
        super().__init__(title="Phoenix Project - Jeu", width=1200, height=800)
        self.parent = parent
        self._user_config = self._load_config()
        self._create_menu()
        self.create_widgets()
        # Afficher les résultats au démarrage
        print_games_current_results()
        
    def _load_config(self):
        """Charge la configuration utilisateur."""
        try:
            return decrypt_ini("config/user_config.ini")
        except Exception as e:
            print(f"Erreur lors du chargement de la configuration : {e}")
            return {"user": {}}
        
    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.center_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Titre
        title_text = f"Bienvenue {self._user_config['user'].get('prenom', '')} {self._user_config['user'].get('nom', '')}"
        title_label = ttk.Label(main_frame, text=title_text, font=("Helvetica", 16, "bold"))
        title_label.pack(pady=10)
        
        # Frame pour le contenu
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame pour les résultats
        results_frame = ttk.LabelFrame(content_frame, text="Résultats des jeux", padding=20)
        results_frame.pack(fill=tk.X, pady=10)
        
        # Bouton pour afficher les résultats
        show_results_btn = ttk.Button(results_frame, 
                                    text="Afficher les résultats des tirages", 
                                    command=lambda: print_games_current_results())
        show_results_btn.pack(pady=10)
        
        # Label pour afficher les résultats
        self.results_label = ttk.Label(results_frame, 
                                     text="Cliquez sur le bouton pour voir les résultats dans la console",
                                     font=("Helvetica", 12))
        self.results_label.pack(pady=10)
        
    def _create_menu(self):
        """Crée la barre de menu."""
        menubar = tk.Menu(self)
        
        # Menu Fichier
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Nouvelle partie", command=self.new_game)
        file_menu.add_command(label="Charger partie", command=self.load_game)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.quit)
        menubar.add_cascade(label="Fichier", menu=file_menu)
        
        # Menu Aide
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="À propos", command=self.show_about)
        menubar.add_cascade(label="Aide", menu=help_menu)
        
        # Configuration du menu
        self.configure(menu=menubar)
        
    def new_game(self):
        """Démarre une nouvelle partie."""
        from merchand.license_manager import check_license
        if check_license():
            messagebox.showinfo("Nouvelle partie", "Démarrage d'une nouvelle partie...")
        else:
            messagebox.showerror("Erreur", "Licence invalide ou expirée")
            
    def load_game(self):
        """Charge une partie existante."""
        from merchand.license_manager import check_license
        if check_license():
            messagebox.showinfo("Charger partie", "Chargement d'une partie...")
        else:
            messagebox.showerror("Erreur", "Licence invalide ou expirée")
            
    def show_about(self):
        """Affiche la boîte de dialogue À propos."""
        messagebox.showinfo("À propos", 
                          "Phoenix Project\nVersion 1.0\n\n"
                          "Votre assistant intelligent pour le Loto")
        
    def quit(self):
        """Quitte l'application."""
        if messagebox.askyesno("Quitter", "Voulez-vous vraiment quitter ?"):
            self.destroy()
            if self.parent:
                self.parent.deiconify()

def show_game_window(parent=None):
    """Affiche la fenêtre de jeu."""
    window = GameWindow(parent)
    window.mainloop() 