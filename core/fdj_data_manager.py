import os
import zipfile
import requests
import pandas as pd
from datetime import datetime
from configparser import ConfigParser
from regles import GAMES
from bs4 import BeautifulSoup

class FDJDataManager:
    def __init__(self):
        self.config = ConfigParser()
        self.config.read('config/config.ini')
        self.data_dir = 'data/fdj'
        os.makedirs(self.data_dir, exist_ok=True)

    def download_historical_data(self, game_name):
        """Télécharge les données historiques pour un jeu spécifique"""
        if game_name not in GAMES:
            raise ValueError(f"Jeu {game_name} non reconnu")

        game_rules = GAMES[game_name]
        url = self.config['FDJ'][f'{game_name}_URL']
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            # Sauvegarde du fichier ZIP
            zip_path = os.path.join(self.data_dir, f'{game_name.lower()}_historical.zip')
            with open(zip_path, 'wb') as f:
                f.write(response.content)
            
            # Extraction du ZIP
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(os.path.join(self.data_dir, game_name.lower()))
            
            return True
        except Exception as e:
            print(f"Erreur lors du téléchargement des données pour {game_name}: {str(e)}")
            return False

    def process_historical_data(self, game_name):
        """Traite les données historiques pour un jeu spécifique"""
        game_dir = os.path.join(self.data_dir, game_name.lower())
        if not os.path.exists(game_dir):
            return None

        # Lecture et traitement des fichiers CSV/Excel
        data_files = [f for f in os.listdir(game_dir) if f.endswith(('.csv', '.xlsx'))]
        all_data = []

        for file in data_files:
            file_path = os.path.join(game_dir, file)
            if file.endswith('.csv'):
                df = pd.read_csv(file_path, sep=',')
            else:
                df = pd.read_excel(file_path)
            all_data.append(df)

        if all_data:
            combined_data = pd.concat(all_data, ignore_index=True)
            return combined_data
        return None

    def update_all_games(self):
        """Met à jour les données pour tous les jeux"""
        results = {}
        for game_name in GAMES.keys():
            if self.download_historical_data(game_name):
                data = self.process_historical_data(game_name)
                results[game_name] = data is not None
        return results

    def get_latest_results(self, game_name):
        """Récupère les derniers résultats pour un jeu spécifique"""
        if game_name not in GAMES:
            raise ValueError(f"Jeu {game_name} non reconnu")

        url = self.config['FDJ']['FDJ_URL']
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Recherche de la section du jeu spécifique
            game_section = soup.find('div', {'class': f'game-{game_name.lower()}'})
            if not game_section:
                print(f"Section non trouvée pour {game_name}")
                return None

            # Extraction des numéros
            numbers = []
            number_elements = game_section.find_all('div', {'class': 'number'})
            for num in number_elements:
                numbers.append(int(num.text.strip()))

            # Extraction des numéros spéciaux (chance, étoiles, etc.)
            special_numbers = []
            special_elements = game_section.find_all('div', {'class': 'special-number'})
            for num in special_elements:
                special_numbers.append(int(num.text.strip()))

            # Extraction de la date du tirage
            date_element = game_section.find('div', {'class': 'draw-date'})
            draw_date = date_element.text.strip() if date_element else None

            # Extraction du jackpot
            jackpot_element = game_section.find('div', {'class': 'jackpot'})
            jackpot = jackpot_element.text.strip() if jackpot_element else None

            return {
                'game': game_name,
                'date': draw_date,
                'numbers': numbers,
                'special_numbers': special_numbers,
                'jackpot': jackpot
            }

        except Exception as e:
            print(f"Erreur lors de la récupération des derniers résultats pour {game_name}: {str(e)}")
            return None 