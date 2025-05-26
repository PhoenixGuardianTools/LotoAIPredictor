import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import uuid
import hashlib
import json

class LicenseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialise la table des licences clients si elle n'existe pas."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS licence_client (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    uuid TEXT UNIQUE,
                    licence_type TEXT,
                    date_expiration TEXT,
                    status TEXT,
                    date_activation TEXT,
                    machine_info TEXT
                )
            """)
    
    def generate_license_key(self, client_id, duration_days=30):
        """
        Génère une nouvelle clé de licence pour un client.
        
        Args:
            client_id (str): Identifiant unique du client
            duration_days (int): Durée de validité en jours
            
        Returns:
            str: Clé de licence générée
        """
        # Génération d'une clé unique
        key_base = f"{client_id}_{datetime.now().timestamp()}"
        license_key = hashlib.sha256(key_base.encode()).hexdigest()[:16]
        
        # Calcul de la date d'expiration
        expiration_date = (datetime.now() + timedelta(days=duration_days)).strftime('%Y-%m-%d')
        
        return license_key, expiration_date
    
    def activate_license(self, license_key, machine_info):
        """
        Active une licence sur une machine.
        
        Args:
            license_key (str): Clé de licence
            machine_info (dict): Informations sur la machine
            
        Returns:
            bool: True si l'activation a réussi, False sinon
        """
        try:
            # Vérification si la licence existe déjà
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id FROM licence_client
                    WHERE uuid = ?
                """, (license_key,))
                
                if cursor.fetchone():
                    return False
                
                # Activation de la licence
                cursor.execute("""
                    INSERT INTO licence_client (
                        uuid, licence_type, date_expiration,
                        status, date_activation, machine_info
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    license_key,
                    'standard',
                    (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
                    'active',
                    datetime.now().strftime('%Y-%m-%d'),
                    json.dumps(machine_info)
                ))
                
                return True
                
        except Exception as e:
            print(f"⚠️ Erreur lors de l'activation de la licence : {e}")
            return False
    
    def deactivate_license(self, license_key):
        """
        Désactive une licence.
        
        Args:
            license_key (str): Clé de licence
            
        Returns:
            bool: True si la désactivation a réussi, False sinon
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE licence_client
                    SET status = 'inactive'
                    WHERE uuid = ?
                """, (license_key,))
                
                return cursor.rowcount > 0
                
        except Exception as e:
            print(f"⚠️ Erreur lors de la désactivation de la licence : {e}")
            return False
    
    def get_license_info(self, license_key):
        """
        Récupère les informations d'une licence.
        
        Args:
            license_key (str): Clé de licence
            
        Returns:
            dict: Informations de la licence ou None si non trouvée
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT licence_type, date_expiration, status,
                           date_activation, machine_info
                    FROM licence_client
                    WHERE uuid = ?
                """, (license_key,))
                
                result = cursor.fetchone()
                if not result:
                    return None
                    
                return {
                    'type': result[0],
                    'expiration': result[1],
                    'status': result[2],
                    'activation': result[3],
                    'machine_info': json.loads(result[4])
                }
                
        except Exception as e:
            print(f"⚠️ Erreur lors de la récupération des informations de licence : {e}")
            return None
    
    def check_license_validity(self, license_key):
        """
        Vérifie la validité d'une licence.
        
        Args:
            license_key (str): Clé de licence
            
        Returns:
            bool: True si la licence est valide, False sinon
        """
        info = self.get_license_info(license_key)
        if not info:
            return False
            
        # Vérification du statut
        if info['status'] != 'active':
            return False
            
        # Vérification de la date d'expiration
        expiration_date = datetime.strptime(info['expiration'], '%Y-%m-%d')
        if expiration_date < datetime.now():
            return False
            
        return True 