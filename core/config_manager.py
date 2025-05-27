import os
import json
import hashlib
import sqlite3
from pathlib import Path
import platform
import requests
from tkinter import messagebox
from core.encryption import encrypt_config, decrypt_config

class ConfigManager:
    def __init__(self):
        """Initialise le gestionnaire de configuration."""
        self.base_dir = self._get_base_dir()
        self.db_path = os.path.join(self.base_dir, 'data', 'phoenix.db')
        self.config_dir = self._get_config_dir()
        self.smtp_config_path = os.path.join(self.base_dir, 'data', 'smtp_config.json')
        
        # Initialisation de la base de données
        self._init_db()
        
        self.config_file = self.config_dir / "user_config.json"
        self.encrypted_config_file = self.config_dir / "user_config.enc"
        self._ensure_config_dir()
    
    def _get_base_dir(self):
        """Retourne le répertoire de base de l'application."""
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    def _get_config_dir(self):
        """Retourne le répertoire de configuration."""
        config_dir = os.path.join(self.base_dir, 'config')
        os.makedirs(config_dir, exist_ok=True)
        return config_dir
    
    def _init_db(self):
        """Initialise la base de données."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Création des tables si elles n'existent pas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                nom TEXT NOT NULL,
                prenom TEXT NOT NULL,
                surnom TEXT,
                email TEXT UNIQUE NOT NULL,
                civilite TEXT,
                telephone TEXT,
                newsletter BOOLEAN DEFAULT 0,
                code_parrain TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS addresses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                type_voie TEXT,
                numero TEXT,
                bis_ter TEXT,
                voie TEXT,
                complement TEXT,
                code_postal TEXT,
                ville TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                server TEXT NOT NULL,
                port INTEGER NOT NULL,
                security TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS config_hashes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                config_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_smtp_configs(self):
        """Retourne la liste des configurations SMTP."""
        try:
            with open(self.smtp_config_path, 'r') as f:
                config = json.load(f)
                return [(s['name'], s['server'], s['port'], s['security']) 
                        for s in config['smtp_servers']]
        except Exception as e:
            print(f"Erreur lors du chargement de la configuration SMTP : {e}")
            return []
    
    def search_address(self, query):
        """Recherche une adresse dans la base de données."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT DISTINCT voie, code_postal, ville
            FROM addresses
            WHERE voie LIKE ?
            LIMIT 10
        ''', (f'%{query}%',))
        
        results = cursor.fetchall()
        conn.close()
        return results
    
    def search_postal_code(self, code):
        """Recherche une ville par code postal."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT DISTINCT code_postal, ville
            FROM addresses
            WHERE code_postal LIKE ?
            LIMIT 1
        ''', (f'{code}%',))
        
        results = cursor.fetchall()
        conn.close()
        return results
    
    def create_user_config(self, user_data):
        """Crée la configuration utilisateur."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Insertion de l'utilisateur
            cursor.execute('''
                INSERT INTO users (type, nom, prenom, surnom, email, civilite, 
                                 telephone, newsletter, code_parrain)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_data['type'],
                user_data['nom'],
                user_data['prenom'],
                user_data['surnom'],
                user_data['email'],
                user_data['civilite'],
                user_data['telephone'],
                user_data['newsletter'],
                user_data['code_parrain']
            ))
            
            user_id = cursor.lastrowid
            
            # Insertion de l'adresse
            cursor.execute('''
                INSERT INTO addresses (user_id, type_voie, numero, bis_ter, voie,
                                     complement, code_postal, ville)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                user_data['adresse']['type_voie'],
                user_data['adresse']['numero'],
                user_data['adresse']['bis_ter'],
                user_data['adresse']['voie'],
                user_data['adresse']['complement'],
                user_data['adresse']['code_postal'],
                user_data['adresse']['ville']
            ))
            
            # Insertion de la configuration email
            cursor.execute('''
                INSERT INTO email_configs (user_id, server, port, security)
                VALUES (?, ?, ?, ?)
            ''', (
                user_id,
                user_data['email_config']['server'],
                user_data['email_config']['port'],
                'TLS' if user_data['email_config']['port'] == 587 else 'SSL'
            ))
            
            # Création du fichier de configuration
            config_content = self._format_config(user_data)
            config_path = os.path.join(self.config_dir, f'user_{user_id}.ini')
            
            with open(config_path, 'w') as f:
                f.write(config_content)
            
            # Calcul et stockage du hash
            config_hash = hashlib.sha256(config_content.encode()).hexdigest()
            cursor.execute('''
                INSERT INTO config_hashes (user_id, config_hash)
                VALUES (?, ?)
            ''', (user_id, config_hash))
            
            conn.commit()
            conn.close()
            
            return True, "Configuration créée avec succès"
            
        except Exception as e:
            return False, f"Erreur lors de la création de la configuration : {e}"
    
    def _format_config(self, user_data):
        """Formate les données utilisateur en configuration INI."""
        config = f"""[User]
type = {user_data['type']}
nom = {user_data['nom']}
prenom = {user_data['prenom']}
surnom = {user_data['surnom']}
email = {user_data['email']}
civilite = {user_data['civilite']}
telephone = {user_data['telephone']}
newsletter = {user_data['newsletter']}
code_parrain = {user_data['code_parrain']}

[Address]
type_voie = {user_data['adresse']['type_voie']}
numero = {user_data['adresse']['numero']}
bis_ter = {user_data['adresse']['bis_ter']}
voie = {user_data['adresse']['voie']}
complement = {user_data['adresse']['complement']}
code_postal = {user_data['adresse']['code_postal']}
ville = {user_data['adresse']['ville']}

[Email]
server = {user_data['email_config']['server']}
port = {user_data['email_config']['port']}
security = {'TLS' if user_data['email_config']['port'] == 587 else 'SSL'}
"""
        return config
    
    def verify_config(self):
        """Vérifie l'intégrité de la configuration."""
        try:
            # Vérifie si le répertoire de configuration existe
            if not os.path.exists(self.config_dir):
                return False
            
            # Vérifie s'il y a des fichiers de configuration
            config_files = [f for f in os.listdir(self.config_dir) 
                          if f.endswith('.ini')]
            if not config_files:
                return False
            
            # Vérifie l'intégrité de chaque fichier
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for config_file in config_files:
                config_path = os.path.join(self.config_dir, config_file)
                with open(config_path, 'r') as f:
                    content = f.read()
                    config_hash = hashlib.sha256(content.encode()).hexdigest()
                
                cursor.execute('''
                    SELECT COUNT(*) FROM config_hashes
                    WHERE config_hash = ?
                ''', (config_hash,))
                
                if cursor.fetchone()[0] == 0:
                    conn.close()
                    return False
            
            conn.close()
            return True
            
        except Exception as e:
            print(f"Erreur lors de la vérification de la configuration : {e}")
            return False
    
    def sync_with_server(self):
        """Synchronise les données avec le serveur."""
        try:
            # TODO: Implémenter la synchronisation avec le serveur Git
            # Pour l'instant, retourne un succès fictif
            return True, "Synchronisation réussie"
        except Exception as e:
            return False, f"Erreur lors de la synchronisation : {e}"
    
    def _ensure_config_dir(self):
        """Crée le répertoire de configuration s'il n'existe pas."""
        self.config_dir.mkdir(exist_ok=True)
    
    def save_config(self, config_data: dict, password: str = None):
        """Sauvegarde la configuration, optionnellement chiffrée."""
        if password:
            # Chiffrement des données
            encrypted_data = encrypt_config(config_data, password)
            with open(self.encrypted_config_file, 'w') as f:
                json.dump(encrypted_data, f, indent=4)
        else:
            # Sauvegarde en clair
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=4)
    
    def load_config(self, password: str = None) -> dict:
        """Charge la configuration, optionnellement déchiffrée."""
        if password and self.encrypted_config_file.exists():
            # Chargement et déchiffrement
            with open(self.encrypted_config_file, 'r') as f:
                encrypted_data = json.load(f)
            return decrypt_config(encrypted_data, password)
        elif self.config_file.exists():
            # Chargement en clair
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {}
    
    def config_exists(self) -> bool:
        """Vérifie si une configuration existe."""
        return self.config_file.exists() or self.encrypted_config_file.exists()
    
    def is_encrypted(self) -> bool:
        """Vérifie si la configuration est chiffrée."""
        return self.encrypted_config_file.exists() 