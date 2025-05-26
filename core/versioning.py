import subprocess
import json
import os
from datetime import datetime
from pathlib import Path
import requests
import hashlib
import platform
import uuid
import time
import ntplib
from typing import Dict, Tuple

class VersionManager:
    def __init__(self):
        self.version_file = Path("VERSION")
        self.build_dir = Path("build")
        self.current_version = self._load_version()
        self.ntp_server = "pool.ntp.org"
        
    def _load_version(self) -> Dict:
        """Charge la version actuelle."""
        if self.version_file.exists():
            with open(self.version_file, 'r') as f:
                return json.load(f)
        return {
            "major": 1,
            "minor": 0,
            "patch": 0,
            "build": 0,
            "last_update": datetime.now().isoformat(),
            "changes": []
        }
        
    def _save_version(self):
        """Sauvegarde la version actuelle."""
        with open(self.version_file, 'w') as f:
            json.dump(self.current_version, f, indent=2)
            
    def _get_git_changes(self) -> list:
        """Récupère les changements Git depuis la dernière version."""
        try:
            result = subprocess.run(
                ["git", "log", "--pretty=format:%h - %s (%cr)", f"v{self.get_version_string()}..HEAD"],
                capture_output=True,
                text=True
            )
            return result.stdout.split('\n')
        except:
            return []
            
    def _get_real_time(self) -> datetime:
        """Récupère l'heure réelle depuis un serveur NTP."""
        try:
            client = ntplib.NTPClient()
            response = client.request(self.ntp_server)
            return datetime.fromtimestamp(response.tx_time)
        except:
            return datetime.now()
            
    def _check_time_manipulation(self) -> bool:
        """Vérifie si l'heure système a été manipulée."""
        real_time = self._get_real_time()
        system_time = datetime.now()
        diff = abs((real_time - system_time).total_seconds())
        return diff > 3600  # Plus d'une heure de différence
        
    def get_version_string(self) -> str:
        """Retourne la version sous forme de chaîne."""
        v = self.current_version
        return f"{v['major']}.{v['minor']}.{v['patch']}+{v['build']}"
        
    def increment_version(self, change_type: str, description: str):
        """Incrémente la version selon le type de changement."""
        if change_type == "major":
            self.current_version["major"] += 1
            self.current_version["minor"] = 0
            self.current_version["patch"] = 0
        elif change_type == "minor":
            self.current_version["minor"] += 1
            self.current_version["patch"] = 0
        elif change_type == "patch":
            self.current_version["patch"] += 1
            
        self.current_version["build"] += 1
        self.current_version["last_update"] = datetime.now().isoformat()
        self.current_version["changes"].append({
            "type": change_type,
            "description": description,
            "timestamp": datetime.now().isoformat()
        })
        
        self._save_version()
        
    def check_for_updates(self) -> Tuple[bool, str]:
        """Vérifie les mises à jour disponibles."""
        try:
            response = requests.get("https://api.lotoaipredictor.com/version")
            if response.status_code != 200:
                return False, ""
                
            latest = response.json()
            current = self.get_version_string()
            
            if latest["version"] > current:
                return True, latest["download_url"]
                
            return False, ""
            
        except Exception as e:
            print(f"⚠️ Erreur lors de la vérification des mises à jour : {e}")
            return False, ""
            
    def force_update(self):
        """Force la mise à jour du logiciel."""
        has_update, url = self.check_for_updates()
        if has_update:
            # Téléchargement et installation de la mise à jour
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    installer_path = self.build_dir / "update.msi"
                    with open(installer_path, 'wb') as f:
                        f.write(response.content)
                        
                    # Lancement de l'installateur
                    subprocess.run(["msiexec", "/i", str(installer_path), "/quiet"])
                    return True
            except Exception as e:
                print(f"⚠️ Erreur lors de la mise à jour : {e}")
                
        return False
        
    def verify_installation(self) -> bool:
        """Vérifie l'intégrité de l'installation."""
        if self._check_time_manipulation():
            return False
            
        # Vérification de l'UUID
        machine_id = self._get_machine_id()
        if not self._verify_machine_id(machine_id):
            return False
            
        return True
        
    def _get_machine_id(self) -> str:
        """Génère un ID unique pour la machine."""
        system_info = {
            'platform': platform.system(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'node': platform.node(),
            'uuid': str(uuid.getnode())
        }
        return hashlib.md5(str(system_info).encode()).hexdigest()
        
    def _verify_machine_id(self, machine_id: str) -> bool:
        """Vérifie si l'ID machine est valide."""
        try:
            response = requests.post(
                "https://api.lotoaipredictor.com/verify",
                json={"machine_id": machine_id}
            )
            return response.status_code == 200
        except:
            return False
            
    def create_release(self):
        """Crée une nouvelle release sur GitHub."""
        version = self.get_version_string()
        changes = self._get_git_changes()
        
        # Création du tag
        subprocess.run(["git", "tag", f"v{version}"])
        subprocess.run(["git", "push", "origin", f"v{version}"])
        
        # Création de la release
        release_data = {
            "tag_name": f"v{version}",
            "name": f"Version {version}",
            "body": "\n".join(changes),
            "draft": False,
            "prerelease": False
        }
        
        # TODO: Implémenter la création de release via l'API GitHub
        
    def build_installer(self):
        """Construit l'installateur MSI."""
        # TODO: Implémenter la construction de l'installateur
        pass 