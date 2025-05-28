import sqlite3
from datetime import datetime
from pathlib import Path
from core.regles import fetch_latest_rules, validate_draw_format
import pandas as pd
import requests
import os
import schedule
import time
import threading
import configparser
from core.encryption import decrypt_ini
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup
import zipfile  
import shutil   
import tempfile 

# Définition du chemin de la base de données
DB_PATH = Path(__file__).resolve().parent.parent / "data" / "phoenix.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# ------------------------
# Initialisation de la base de données
# ------------------------
def init_db():
    """Initialise la base de données et démarre les mises à jour automatiques"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    try:
        # Tables des jeux
        cur.execute("""
            CREATE TABLE IF NOT EXISTS loto (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date_tirage TEXT NOT NULL,
                boule_1 INTEGER NOT NULL,
                boule_2 INTEGER NOT NULL,
                boule_3 INTEGER NOT NULL,
                boule_4 INTEGER NOT NULL,
                boule_5 INTEGER NOT NULL,
                boule_6 INTEGER,
                boule_complementaire INTEGER,
                numero_joker TEXT,
                numero_jokerplus TEXT,
                nombre_gagnants_rang1 INTEGER,
                rapport_rang1 REAL,
                nombre_gagnants_rang2 INTEGER,
                rapport_rang2 REAL,
                nombre_gagnants_rang3 INTEGER,
                rapport_rang3 REAL,
                nombre_gagnants_rang4 INTEGER,
                rapport_rang4 REAL,
                nombre_gagnants_rang5 INTEGER,
                rapport_rang5 REAL,
                nombre_gagnants_rang6 INTEGER,
                rapport_rang6 REAL,
                nombre_gagnants_rang7 INTEGER,
                rapport_rang7 REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(date_tirage)
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS euromillions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date_tirage TEXT NOT NULL,
                boule_1 INTEGER NOT NULL,
                boule_2 INTEGER NOT NULL,
                boule_3 INTEGER NOT NULL,
                boule_4 INTEGER NOT NULL,
                boule_5 INTEGER NOT NULL,
                etoile_1 INTEGER NOT NULL,
                etoile_2 INTEGER NOT NULL,
                nombre_gagnants_rang1 INTEGER,
                rapport_rang1 REAL,
                nombre_gagnants_rang2 INTEGER,
                rapport_rang2 REAL,
                nombre_gagnants_rang3 INTEGER,
                rapport_rang3 REAL,
                nombre_gagnants_rang4 INTEGER,
                rapport_rang4 REAL,
                nombre_gagnants_rang5 INTEGER,
                rapport_rang5 REAL,
                nombre_gagnants_rang6 INTEGER,
                rapport_rang6 REAL,
                nombre_gagnants_rang7 INTEGER,
                rapport_rang7 REAL,
                nombre_gagnants_rang8 INTEGER,
                rapport_rang8 REAL,
                nombre_gagnants_rang9 INTEGER,
                rapport_rang9 REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(date_tirage)
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS eurodreams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date_tirage TEXT NOT NULL,
                boule_1 INTEGER NOT NULL,
                boule_2 INTEGER NOT NULL,
                boule_3 INTEGER NOT NULL,
                boule_4 INTEGER NOT NULL,
                boule_5 INTEGER NOT NULL,
                boule_6 INTEGER NOT NULL,
                numero_dream INTEGER NOT NULL,
                nombre_gagnants_rang1 INTEGER,
                rapport_rang1 REAL,
                nombre_gagnants_rang2 INTEGER,
                rapport_rang2 REAL,
                nombre_gagnants_rang3 INTEGER,
                rapport_rang3 REAL,
                nombre_gagnants_rang4 INTEGER,
                rapport_rang4 REAL,
                nombre_gagnants_rang5 INTEGER,
                rapport_rang5 REAL,
                nombre_gagnants_rang6 INTEGER,
                rapport_rang6 REAL,
                nombre_gagnants_rang7 INTEGER,
                rapport_rang7 REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(date_tirage)
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS keno (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date_tirage TEXT NOT NULL,
                boule_1 INTEGER NOT NULL,
                boule_2 INTEGER NOT NULL,
                boule_3 INTEGER NOT NULL,
                boule_4 INTEGER NOT NULL,
                boule_5 INTEGER NOT NULL,
                boule_6 INTEGER NOT NULL,
                boule_7 INTEGER NOT NULL,
                boule_8 INTEGER NOT NULL,
                boule_9 INTEGER NOT NULL,
                boule_10 INTEGER NOT NULL,
                boule_11 INTEGER NOT NULL,
                boule_12 INTEGER NOT NULL,
                boule_13 INTEGER NOT NULL,
                boule_14 INTEGER NOT NULL,
                boule_15 INTEGER NOT NULL,
                boule_16 INTEGER NOT NULL,
                boule_17 INTEGER NOT NULL,
                boule_18 INTEGER NOT NULL,
                boule_19 INTEGER NOT NULL,
                boule_20 INTEGER NOT NULL,
                numero_jackpot INTEGER,
                montant_jackpot REAL,
                multiplicateur INTEGER,
                numero_jokerplus TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(date_tirage)
            )
        """)

        # Tables de gestion
        cur.execute("""
            CREATE TABLE IF NOT EXISTS grilles_jouees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                jeu TEXT NOT NULL,
                date TEXT NOT NULL,
                grille TEXT NOT NULL,
                model_version TEXT,
                gain_brut REAL DEFAULT 0,
                cout REAL DEFAULT 2.5,
                gain_net REAL DEFAULT 0,
                rang TEXT DEFAULT 'NA',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(jeu, date, grille)
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS favoris (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                jeu TEXT NOT NULL,
                grille TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(jeu, grille)
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                prenom TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                telephone TEXT,
                adresse TEXT,
                ville TEXT,
                code_postal TEXT,
                pays TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS licences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                date_debut TEXT NOT NULL,
                date_fin TEXT NOT NULL,
                statut TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (client_id) REFERENCES clients (id),
                UNIQUE(client_id, type, date_debut)
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER NOT NULL,
                montant REAL NOT NULL,
                devise TEXT NOT NULL,
                statut TEXT NOT NULL,
                methode_paiement TEXT NOT NULL,
                reference TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (client_id) REFERENCES clients (id)
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS factures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER NOT NULL,
                transaction_id INTEGER NOT NULL,
                numero TEXT UNIQUE NOT NULL,
                montant REAL NOT NULL,
                tva REAL NOT NULL,
                total REAL NOT NULL,
                statut TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (client_id) REFERENCES clients (id),
                FOREIGN KEY (transaction_id) REFERENCES transactions (id),
                UNIQUE(transaction_id)
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS promotions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL,
                reduction REAL NOT NULL,
                date_debut TEXT NOT NULL,
                date_fin TEXT NOT NULL,
                statut TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS parrainages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parrain_id INTEGER NOT NULL,
                filleul_id INTEGER NOT NULL,
                statut TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (parrain_id) REFERENCES clients (id),
                FOREIGN KEY (filleul_id) REFERENCES clients (id),
                UNIQUE(parrain_id, filleul_id)
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cle TEXT UNIQUE NOT NULL,
                valeur TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Commit des tables
        conn.commit()

        # Migration des données existantes
        migrate_existing_data()

        # Démarrage des mises à jour automatiques
        start_auto_updates()

    except Exception as e:
        print(f"Erreur lors de l'initialisation de la base de données : {e}")
        conn.rollback()
    finally:
        conn.close()

def migrate_existing_data():
    """Migre les données des anciennes bases vers phoenix.db"""
    try:
        # Chemins des anciennes bases
        base_dir = Path(__file__).resolve().parent.parent
        loto_db = base_dir / "data" / "database" / "loto.db"
        
        if loto_db.exists():
            print("Migration des données du Loto...")
            loto_conn = sqlite3.connect(loto_db)
            loto_cur = loto_conn.cursor()
            phoenix_conn = sqlite3.connect(DB_PATH)
            phoenix_cur = phoenix_conn.cursor()
            
            # Tables à migrer avec leurs mappings
            tables_mapping = {
                'loto': {
                    'source': 'loto',
                    'columns': {
                        'date_tirage': 'date_tirage',
                        'boule_1': 'boule_1',
                        'boule_2': 'boule_2',
                        'boule_3': 'boule_3',
                        'boule_4': 'boule_4',
                        'boule_5': 'boule_5',
                        'boule_6': 'boule_6',
                        'boule_complementaire': 'boule_complementaire',
                        'numero_joker': 'numero_joker',
                        'nombre_de_gagnant_au_rang1': 'nombre_gagnants_rang1',
                        'rapport_du_rang1': 'rapport_rang1',
                        'nombre_de_gagnant_au_rang2': 'nombre_gagnants_rang2',
                        'rapport_du_rang2': 'rapport_rang2',
                        'nombre_de_gagnant_au_rang3': 'nombre_gagnants_rang3',
                        'rapport_du_rang3': 'rapport_rang3',
                        'nombre_de_gagnant_au_rang4': 'nombre_gagnants_rang4',
                        'rapport_du_rang4': 'rapport_rang4',
                        'nombre_de_gagnant_au_rang5': 'nombre_gagnants_rang5',
                        'rapport_du_rang5': 'rapport_rang5',
                        'nombre_de_gagnant_au_rang6': 'nombre_gagnants_rang6',
                        'rapport_du_rang6': 'rapport_rang6',
                        'nombre_de_gagnant_au_rang7': 'nombre_gagnants_rang7',
                        'rapport_du_rang7': 'rapport_rang7',
                        'numero_jokerplus': 'numero_jokerplus'
                    }
                },
                'euromillions': {
                    'source': 'euromillions',
                    'columns': {
                        'date_tirage': 'date_tirage',
                        'boule_1': 'boule_1',
                        'boule_2': 'boule_2',
                        'boule_3': 'boule_3',
                        'boule_4': 'boule_4',
                        'boule_5': 'boule_5',
                        'etoile_1': 'etoile_1',
                        'etoile_2': 'etoile_2',
                        'nombre_de_gagnant_au_rang1': 'nombre_gagnants_rang1',
                        'rapport_du_rang1': 'rapport_rang1',
                        'nombre_de_gagnant_au_rang2': 'nombre_gagnants_rang2',
                        'rapport_du_rang2': 'rapport_rang2',
                        'nombre_de_gagnant_au_rang3': 'nombre_gagnants_rang3',
                        'rapport_du_rang3': 'rapport_rang3',
                        'nombre_de_gagnant_au_rang4': 'nombre_gagnants_rang4',
                        'rapport_du_rang4': 'rapport_rang4',
                        'nombre_de_gagnant_au_rang5': 'nombre_gagnants_rang5',
                        'rapport_du_rang5': 'rapport_rang5',
                        'nombre_de_gagnant_au_rang6': 'nombre_gagnants_rang6',
                        'rapport_du_rang6': 'rapport_rang6',
                        'nombre_de_gagnant_au_rang7': 'nombre_gagnants_rang7',
                        'rapport_du_rang7': 'rapport_rang7',
                        'nombre_de_gagnant_au_rang8': 'nombre_gagnants_rang8',
                        'rapport_du_rang8': 'rapport_rang8',
                        'nombre_de_gagnant_au_rang9': 'nombre_gagnants_rang9',
                        'rapport_du_rang9': 'rapport_rang9'
                    }
                },
                'eurodreams': {
                    'source': 'eurodreams',
                    'columns': {
                        'date_tirage': 'date_tirage',
                        'boule_1': 'boule_1',
                        'boule_2': 'boule_2',
                        'boule_3': 'boule_3',
                        'boule_4': 'boule_4',
                        'boule_5': 'boule_5',
                        'boule_6': 'boule_6',
                        'numero_dream': 'numero_dream',
                        'nombre_de_gagnant_au_rang1_Euro_Dreams_en_france': 'nombre_gagnants_rang1',
                        'rapport_du_rang1_Euro_Dreams': 'rapport_rang1',
                        'nombre_de_gagnant_au_rang2_Euro_Dreams_en_france': 'nombre_gagnants_rang2',
                        'rapport_du_rang2_Euro_Dreams': 'rapport_rang2',
                        'nombre_de_gagnant_au_rang3_Euro_Dreams_en_france': 'nombre_gagnants_rang3',
                        'rapport_du_rang3_Euro_Dreams': 'rapport_rang3',
                        'nombre_de_gagnant_au_rang4_Euro_Dreams_en_france': 'nombre_gagnants_rang4',
                        'rapport_du_rang4_Euro_Dreams': 'rapport_rang4',
                        'nombre_de_gagnant_au_rang5_Euro_Dreams_en_france': 'nombre_gagnants_rang5',
                        'rapport_du_rang5_Euro_Dreams': 'rapport_rang5',
                        'nombre_de_gagnant_au_rang6_Euro_Dreams_en_france': 'nombre_gagnants_rang6',
                        'rapport_du_rang6_Euro_Dreams': 'rapport_rang6',
                        'nombre_de_gagnant_au_rang7_Euro_Dreams_en_france': 'nombre_gagnants_rang7',
                        'rapport_du_rang7_Euro_Dreams': 'rapport_rang7'
                    }
                },
                'keno': {
                    'source': 'keno',
                    'columns': {
                        'date_tirage': 'date_tirage',
                        'numero_jackpot': 'numero_jackpot',
                        'montant_du_jackpot_du_tirage': 'montant_jackpot',
                        'multiplicateur': 'multiplicateur',
                        'numero_jokerplus': 'numero_jokerplus'
                    }
                }
            }
            
            # Ajout dynamique des colonnes boule_1 à boule_20 pour le Keno
            for i in range(1, 21):
                tables_mapping['keno']['columns'][f'boule{i}'] = f'boule_{i}'
            
            # Migration de chaque table
            for table_name, mapping in tables_mapping.items():
                print(f"Migration de la table {table_name}...")
                
                # Récupération des données
                loto_cur.execute(f"SELECT * FROM {mapping['source']}")
                rows = loto_cur.fetchall()
                
                if rows:
                    # Récupération des colonnes
                    loto_cur.execute(f"PRAGMA table_info({mapping['source']})")
                    columns = loto_cur.fetchall()
                    source_columns = [col[1] for col in columns]
                    
                    # Création de la requête d'insertion
                    target_columns = [mapping['columns'][col] for col in source_columns if col in mapping['columns']]
                    placeholders = ", ".join(["?" for _ in target_columns])
                    insert_sql = f"INSERT OR IGNORE INTO {table_name} ({', '.join(target_columns)}) VALUES ({placeholders})"
                    
                    # Préparation des données
                    data_to_insert = []
                    for row in rows:
                        values = []
                        for i, col in enumerate(source_columns):
                            if col in mapping['columns']:
                                values.append(row[i])
                        data_to_insert.append(tuple(values))
                    
                    # Insertion des données
                    phoenix_cur.executemany(insert_sql, data_to_insert)
                    print(f"{len(data_to_insert)} lignes migrées pour {table_name}")
            
            loto_conn.close()
            phoenix_conn.commit()
            phoenix_conn.close()
            
            # Suppression de l'ancienne base
            os.remove(loto_db)
            print(f"Base de données {loto_db} supprimée.")
            
    except Exception as e:
        print(f"Erreur lors de la migration : {e}")

def get_db_connection():
    """Retourne une connexion à la base de données."""
    return sqlite3.connect(DB_PATH)

def get_user_permissions():
    """Récupère les permissions de l'utilisateur depuis la base de données."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Récupération de la licence active
        cur.execute("""
            SELECT l.type, l.date_fin
            FROM licences l
            JOIN clients c ON l.client_id = c.id
            WHERE l.statut = 'active'
            AND l.date_fin > datetime('now')
            ORDER BY l.date_fin DESC
            LIMIT 1
        """)
        
        result = cur.fetchone()
        if result:
            return {
                'type': result[0],
                'date_fin': result[1],
                'is_valid': True
            }
        return {
            'type': 'free',
            'date_fin': None,
            'is_valid': False
        }
    finally:
        conn.close()

def get_machine_uuid():
    """Récupère l'UUID de la machine depuis la base de données."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT valeur FROM config WHERE cle = 'machine_uuid'")
        result = cur.fetchone()
        if result:
            return result[0]
        return None
    finally:
        conn.close()

def start_auto_updates():
    """Démarre les mises à jour automatiques en arrière-plan."""
    def update_task():
        while True:
            try:
                update_database()
                time.sleep(3600)  # Mise à jour toutes les heures
            except Exception as e:
                print(f"Erreur lors de la mise à jour automatique : {e}")
                time.sleep(300)  # Attente de 5 minutes en cas d'erreur

    thread = threading.Thread(target=update_task, daemon=True)
    thread.start()

def update_database():
    """Met à jour la base de données avec les dernières données."""
    try:
        # Récupération des règles mises à jour
        rules = fetch_latest_rules()
        if not rules:
            return

        # Mise à jour des tirages
        conn = get_db_connection()
        cur = conn.cursor()

        for jeu, tirage in rules.items():
            if validate_draw_format(jeu, tirage):
                cur.execute("""
                    INSERT OR IGNORE INTO tirages (jeu, date_tirage, numeros, etoiles, rangs, gains)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    jeu,
                    tirage['date'],
                    ','.join(map(str, tirage['numeros'])),
                    ','.join(map(str, tirage.get('etoiles', []))),
                    ','.join(map(str, tirage.get('rangs', []))),
                    ','.join(map(str, tirage.get('gains', [])))
                ))
            
            conn.commit()
        conn.close()
            
    except Exception as e:
        print(f"Erreur lors de la mise à jour de la base de données : {e}")

def get_working_dataset(jeu=None):
    """Récupère le dataset de travail pour un jeu spécifique"""
    conn = get_db_connection()
    try:
        if jeu:
            query = f"SELECT * FROM {jeu} ORDER BY date_tirage DESC"
            df = pd.read_sql_query(query, conn)
            
            # Nettoyer les dates invalides
            df['date'] = pd.to_datetime(df['date_tirage'], errors='coerce')
            df = df.dropna(subset=['date'])
            
            # Convertir les colonnes numériques
            numeric_cols = [col for col in df.columns if col.startswith('boule_') or col.startswith('etoile_')]
            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            return df
        else:
            return None
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
