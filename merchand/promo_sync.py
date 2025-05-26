import json
import requests
import hashlib
import os
from datetime import datetime
from pathlib import Path

class PromoSync:
    def __init__(self):
        self.promo_path = Path("PROMOTIONS/promo_templates.json")
        self.bandeau_path = Path("PROMOTIONS/bandeau_default.json")
        self.last_sync_path = Path("PROMOTIONS/last_sync.json")
        self.server_url = "https://api.lotoaipredictor.com/promos"  # URL à configurer
        
    def _get_local_hash(self):
        """Calcule le hash des fichiers de promotion locaux."""
        hashes = {}
        if self.promo_path.exists():
            with open(self.promo_path, 'rb') as f:
                hashes['promo'] = hashlib.md5(f.read()).hexdigest()
        if self.bandeau_path.exists():
            with open(self.bandeau_path, 'rb') as f:
                hashes['bandeau'] = hashlib.md5(f.read()).hexdigest()
        return hashes
        
    def _save_last_sync(self, server_hash):
        """Sauvegarde le hash du dernier sync."""
        data = {
            'timestamp': datetime.now().isoformat(),
            'server_hash': server_hash
        }
        with open(self.last_sync_path, 'w') as f:
            json.dump(data, f)
            
    def _load_last_sync(self):
        """Charge le hash du dernier sync."""
        if self.last_sync_path.exists():
            with open(self.last_sync_path, 'r') as f:
                return json.load(f)
        return None
        
    def check_for_updates(self):
        """Vérifie si des mises à jour sont disponibles."""
        try:
            # Récupération du hash serveur
            response = requests.get(f"{self.server_url}/hash")
            if response.status_code != 200:
                return False
                
            server_hash = response.json()
            local_hash = self._get_local_hash()
            last_sync = self._load_last_sync()
            
            # Vérification des changements
            if not last_sync or server_hash != last_sync['server_hash']:
                return True
                
            return False
            
        except Exception as e:
            print(f"⚠️ Erreur lors de la vérification des mises à jour : {e}")
            return False
            
    def sync_promos(self):
        """Synchronise les promotions avec le serveur."""
        try:
            # Récupération des données
            response = requests.get(f"{self.server_url}/data")
            if response.status_code != 200:
                return False
                
            data = response.json()
            
            # Sauvegarde des fichiers
            with open(self.promo_path, 'w') as f:
                json.dump(data['promo'], f, indent=2)
                
            with open(self.bandeau_path, 'w') as f:
                json.dump(data['bandeau'], f, indent=2)
                
            # Mise à jour du hash
            self._save_last_sync(data['hash'])
            
            print("✅ Promotions synchronisées avec succès")
            return True
            
        except Exception as e:
            print(f"⚠️ Erreur lors de la synchronisation : {e}")
            return False
            
    def start_sync_service(self):
        """Démarre le service de synchronisation."""
        if self.check_for_updates():
            self.sync_promos()
            
def sync_promos():
    """Fonction de synchronisation à appeler périodiquement."""
    sync = PromoSync()
    sync.start_sync_service() 