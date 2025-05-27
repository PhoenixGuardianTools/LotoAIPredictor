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

    # Tirages
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tirages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            jeu TEXT,
            date_tirage TEXT,
            numeros TEXT,
            etoiles TEXT,
            rangs TEXT,
            gains TEXT
        )
    """)

    # Grilles jouées
    cur.execute("""
        CREATE TABLE IF NOT EXISTS grilles_jouees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            jeu TEXT,
            date TEXT,
            grille TEXT,
            model_version TEXT,
            gain_brut REAL DEFAULT 0,
            cout REAL DEFAULT 2.5,
            gain_net REAL DEFAULT 0,
            rang TEXT DEFAULT 'NA'
        )
    """)

    # Favoris (pour l'interface)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS favoris (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            jeu TEXT,
            grille TEXT
        )
    """)

    # Paramètres clients (licence, uuid, jours restants, etc.)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS licence_client (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uuid TEXT,
            licence_type TEXT,
            date_expiration TEXT,
            status TEXT
        )
    """)

    # Feedback utilisateurs
    cur.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uuid TEXT,
            date TEXT,
            sujet TEXT,
            message TEXT
        )
    """)

    # Table entreprise / admin
    cur.execute("""
        CREATE TABLE IF NOT EXISTS entreprise (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT,
            siret TEXT,
            tva TEXT,
            email TEXT,
            site TEXT,
            tel TEXT,
            logo_path TEXT
        )
    """)

    # **Ajout des règles des jeux**
    cur.execute("""
        CREATE TABLE IF NOT EXISTS jeux (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT UNIQUE,
            numbers_range TEXT,
            numbers_count INTEGER,
            special_range TEXT,
            special_count INTEGER,
            draw_days TEXT
        )
    """)

    # **Ajout des statistiques des jeux**
    cur.execute("""
        CREATE TABLE IF NOT EXISTS statistiques (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            jeu TEXT,
            date TEXT,
            numeros TEXT,
            special TEXT,
            ratio_gain REAL,
            indice_confiance REAL
        )
    """)

    # **Ajout des tables pour les codes promo**
    cur.execute("""
        CREATE TABLE IF NOT EXISTS promo_codes (
            id INTEGER PRIMARY KEY,
            code TEXT UNIQUE,
            event TEXT,
            discount INTEGER,
            start_date TEXT,
            end_date TEXT,
            is_active BOOLEAN,
            created_at TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS promo_usage (
            id INTEGER PRIMARY KEY,
            code TEXT,
            user_uuid TEXT,
            machine_id TEXT,
            used_at TEXT,
            is_purchase BOOLEAN DEFAULT 0,
            FOREIGN KEY (code) REFERENCES promo_codes (code)
        )
    """)

    # **Mise à jour des règles en base**
    latest_rules = fetch_latest_rules()
    if latest_rules:
        for jeu, regles in latest_rules.items():
            cur.execute("""
                INSERT OR REPLACE INTO jeux (nom, numbers_range, numbers_count, special_range, special_count, draw_days)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (jeu, str(regles["numbers_range"]), regles["numbers_count"], str(regles["special_range"]), regles["special_count"], str(regles["draw_days"])))

    conn.commit()
    conn.close()

    # Vérification et mise à jour initiale
    print("🔄 Vérification des données FDJ...")
    if not check_data_freshness():
        print("📥 Données non à jour, lancement de la mise à jour initiale...")
        success = download_fdj_data()
        notify_update_status(success, is_initial=True)
    else:
        print("✅ Données à jour")

    # Démarrage des mises à jour automatiques
    schedule_fdj_updates()

# ------------------------
# Vérification des tirages existants
# ------------------------
def validate_latest_draws():
    """Vérifie que les derniers tirages sont conformes aux règles en base."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT jeu, date_tirage, numeros, etoiles FROM tirages ORDER BY date_tirage DESC LIMIT 10")
    tirages = cursor.fetchall()

    for jeu, date, numeros, etoiles in tirages:
        draw = {"numbers": list(map(int, numeros.split(","))), "special": list(map(int, etoiles.split(",")))}
        if not validate_draw_format(jeu, draw):
            print(f"⚠️ Tirage du {date} pour {jeu} non conforme aux règles en base !")

    conn.close()

# ------------------------
# Sauvegarde et récupération des statistiques
# ------------------------
def save_statistics(jeu, date, numeros, special, ratio_gain, indice_confiance):
    """Enregistre les statistiques d'un tirage dans la base de données."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO statistiques (jeu, date, numeros, special, ratio_gain, indice_confiance)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (jeu, date, numeros, special, ratio_gain, indice_confiance))

def get_statistics(jeu):
    """Récupère les statistiques des 10 dernières années pour un jeu donné."""
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute("""
            SELECT date, numeros, special, ratio_gain, indice_confiance
            FROM statistiques
            WHERE jeu = ?
            ORDER BY date DESC
            LIMIT 100
        """, (jeu,))
        return rows.fetchall()

def get_recent_draws(jeu, limit=10):
    """Récupère les tirages récents pour un jeu donné."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT date_tirage, numeros, etoiles
            FROM tirages
            WHERE jeu = ?
            ORDER BY date_tirage DESC
            LIMIT ?
        """, (jeu, limit))
        return cursor.fetchall()

def save_grille(jeu, grille, model_version="advanced"):
    """
    Sauvegarde une grille jouée dans la base de données.
    
    Args:
        jeu (str): Nom du jeu
        grille (dict): Dictionnaire contenant les numéros et numéros spéciaux
        model_version (str): Version du modèle utilisé pour la prédiction
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        numeros = ",".join(map(str, grille["numbers"]))
        special = ",".join(map(str, grille["special"]))
        
        # Vérifier si la grille existe déjà pour ce jeu
        cursor.execute("""
            SELECT id FROM grilles_jouees 
            WHERE jeu = ? AND grille = ?
        """, (jeu, numeros + "|" + special))
        
        if cursor.fetchone() is None:  # Si la grille n'existe pas déjà
            cursor.execute("""
                INSERT INTO grilles_jouees (jeu, date, grille, model_version)
                VALUES (?, ?, ?, ?)
            """, (jeu, date, numeros + "|" + special, model_version))
            conn.commit()
            return True
        return False

def get_grilles_jouees(jeu=None, limit=100):
    """
    Récupère l'historique des grilles jouées.
    
    Args:
        jeu (str, optional): Nom du jeu pour filtrer les grilles
        limit (int): Nombre maximum de grilles à récupérer
    
    Returns:
        list: Liste des grilles jouées avec leurs détails
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        if jeu:
            cursor.execute("""
                SELECT id, jeu, date, grille, model_version, gain_brut, cout, gain_net, rang
                FROM grilles_jouees
                WHERE jeu = ?
                ORDER BY date DESC
                LIMIT ?
            """, (jeu, limit))
        else:
            cursor.execute("""
                SELECT id, jeu, date, grille, model_version, gain_brut, cout, gain_net, rang
                FROM grilles_jouees
                ORDER BY date DESC
                LIMIT ?
            """, (limit,))
        
        grilles = cursor.fetchall()
        result = []
        for grille in grilles:
            numeros, special = grille[3].split("|")
            result.append({
                "id": grille[0],
                "jeu": grille[1],
                "date": grille[2],
                "numbers": list(map(int, numeros.split(","))),
                "special": list(map(int, special.split(","))),
                "model_version": grille[4],
                "gain_brut": grille[5],
                "cout": grille[6],
                "gain_net": grille[7],
                "rang": grille[8]
            })
        return result

def update_grille_gains(grille_id, gain_brut, rang):
    """
    Met à jour les gains d'une grille après un tirage.
    
    Args:
        grille_id (int): ID de la grille
        gain_brut (float): Gain brut réalisé
        rang (str): Rang obtenu
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE grilles_jouees
            SET gain_brut = ?, gain_net = gain_brut - cout, rang = ?
            WHERE id = ?
        """, (gain_brut, rang, grille_id))
        conn.commit()

def get_statistiques_grilles(jeu=None):
    """
    Calcule les statistiques globales des grilles jouées.
    
    Args:
        jeu (str, optional): Nom du jeu pour filtrer les statistiques
    
    Returns:
        dict: Statistiques des grilles (gains totaux, nombre de grilles, etc.)
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        if jeu:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_grilles,
                    SUM(cout) as total_cout,
                    SUM(gain_brut) as total_gain_brut,
                    SUM(gain_net) as total_gain_net,
                    AVG(gain_net) as moyenne_gain_net,
                    COUNT(CASE WHEN gain_net > 0 THEN 1 END) as grilles_gagnantes,
                    COUNT(CASE WHEN rang = '1er' THEN 1 END) as grilles_premier_rang
                FROM grilles_jouees
                WHERE jeu = ?
            """, (jeu,))
        else:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_grilles,
                    SUM(cout) as total_cout,
                    SUM(gain_brut) as total_gain_brut,
                    SUM(gain_net) as total_gain_net,
                    AVG(gain_net) as moyenne_gain_net,
                    COUNT(CASE WHEN gain_net > 0 THEN 1 END) as grilles_gagnantes,
                    COUNT(CASE WHEN rang = '1er' THEN 1 END) as grilles_premier_rang
                FROM grilles_jouees
            """)
        
        stats = cursor.fetchone()
        return {
            "total_grilles": stats[0],
            "total_cout": stats[1] or 0,
            "total_gain_brut": stats[2] or 0,
            "total_gain_net": stats[3] or 0,
            "moyenne_gain_net": stats[4] or 0,
            "grilles_gagnantes": stats[5],
            "grilles_premier_rang": stats[6],
            "taux_reussite": round((stats[5] / stats[0] * 100) if stats[0] > 0 else 0, 2)
        }

def get_meilleures_grilles(jeu=None, limit=10):
    """
    Récupère les meilleures grilles jouées (gain net le plus élevé).
    
    Args:
        jeu (str, optional): Nom du jeu pour filtrer les grilles
        limit (int): Nombre maximum de grilles à récupérer
    
    Returns:
        list: Liste des meilleures grilles
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        if jeu:
            cursor.execute("""
                SELECT id, jeu, date, grille, model_version, gain_brut, cout, gain_net, rang
                FROM grilles_jouees
                WHERE jeu = ? AND gain_net > 0
                ORDER BY gain_net DESC
                LIMIT ?
            """, (jeu, limit))
        else:
            cursor.execute("""
                SELECT id, jeu, date, grille, model_version, gain_brut, cout, gain_net, rang
                FROM grilles_jouees
                WHERE gain_net > 0
                ORDER BY gain_net DESC
                LIMIT ?
            """, (limit,))
        
        grilles = cursor.fetchall()
        result = []
        for grille in grilles:
            numeros, special = grille[3].split("|")
            result.append({
                "id": grille[0],
                "jeu": grille[1],
                "date": grille[2],
                "numbers": list(map(int, numeros.split(","))),
                "special": list(map(int, special.split(","))),
                "model_version": grille[4],
                "gain_brut": grille[5],
                "cout": grille[6],
                "gain_net": grille[7],
                "rang": grille[8]
            })
        return result

def get_performance_modeles(jeu=None):
    """
    Analyse la performance des différents modèles de prédiction.
    
    Args:
        jeu (str, optional): Nom du jeu pour filtrer l'analyse
    
    Returns:
        dict: Statistiques de performance par modèle
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        if jeu:
            cursor.execute("""
                SELECT 
                    model_version,
                    COUNT(*) as total_grilles,
                    SUM(gain_net) as total_gain_net,
                    AVG(gain_net) as moyenne_gain_net,
                    COUNT(CASE WHEN gain_net > 0 THEN 1 END) as grilles_gagnantes,
                    COUNT(CASE WHEN rang = '1er' THEN 1 END) as grilles_premier_rang
                FROM grilles_jouees
                WHERE jeu = ?
                GROUP BY model_version
            """, (jeu,))
        else:
            cursor.execute("""
                SELECT 
                    model_version,
                    COUNT(*) as total_grilles,
                    SUM(gain_net) as total_gain_net,
                    AVG(gain_net) as moyenne_gain_net,
                    COUNT(CASE WHEN gain_net > 0 THEN 1 END) as grilles_gagnantes,
                    COUNT(CASE WHEN rang = '1er' THEN 1 END) as grilles_premier_rang
                FROM grilles_jouees
                GROUP BY model_version
            """)
        
        result = {}
        for row in cursor.fetchall():
            result[row[0]] = {
                "total_grilles": row[1],
                "total_gain_net": row[2] or 0,
                "moyenne_gain_net": row[3] or 0,
                "grilles_gagnantes": row[4],
                "grilles_premier_rang": row[5],
                "taux_reussite": round((row[4] / row[1] * 100) if row[1] > 0 else 0, 2)
            }
        return result

def get_grilles_en_cours(jeu=None):
    """
    Récupère les grilles qui n'ont pas encore été vérifiées (rang = 'NA').
    
    Args:
        jeu (str, optional): Nom du jeu pour filtrer les grilles
    
    Returns:
        list: Liste des grilles en attente de vérification
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        if jeu:
            cursor.execute("""
                SELECT id, jeu, date, grille, model_version
                FROM grilles_jouees
                WHERE jeu = ? AND rang = 'NA'
                ORDER BY date DESC
            """, (jeu,))
        else:
            cursor.execute("""
                SELECT id, jeu, date, grille, model_version
                FROM grilles_jouees
                WHERE rang = 'NA'
                ORDER BY date DESC
            """)
        
        grilles = cursor.fetchall()
        result = []
        for grille in grilles:
            numeros, special = grille[3].split("|")
            result.append({
                "id": grille[0],
                "jeu": grille[1],
                "date": grille[2],
                "numbers": list(map(int, numeros.split(","))),
                "special": list(map(int, special.split(","))),
                "model_version": grille[4]
            })
        return result

def get_tendances_numeros(jeu, limit=10):
    """
    Analyse les tendances des numéros les plus joués et gagnants.
    
    Args:
        jeu (str): Nom du jeu
        limit (int): Nombre de numéros à retourner
    
    Returns:
        dict: Statistiques des numéros les plus performants
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        # Analyse des numéros gagnants
        cursor.execute("""
            WITH RECURSIVE split_numbers AS (
                SELECT 
                    grille,
                    gain_net,
                    rang,
                    substr(grille, 1, instr(grille, '|')-1) as numbers,
                    substr(grille, instr(grille, '|')+1) as special
                FROM grilles_jouees
                WHERE jeu = ? AND gain_net > 0
            )
            SELECT 
                value as numero,
                COUNT(*) as frequence,
                AVG(gain_net) as moyenne_gain,
                COUNT(CASE WHEN rang = '1er' THEN 1 END) as premier_rang
            FROM split_numbers, json_each('["' || replace(numbers, ',', '","') || '"]')
            GROUP BY value
            ORDER BY moyenne_gain DESC, frequence DESC
            LIMIT ?
        """, (jeu, limit))
        
        numeros_gagnants = cursor.fetchall()
        
        # Analyse des numéros spéciaux gagnants
        cursor.execute("""
            WITH RECURSIVE split_numbers AS (
                SELECT 
                    grille,
                    gain_net,
                    rang,
                    substr(grille, 1, instr(grille, '|')-1) as numbers,
                    substr(grille, instr(grille, '|')+1) as special
                FROM grilles_jouees
                WHERE jeu = ? AND gain_net > 0
            )
            SELECT 
                value as numero,
                COUNT(*) as frequence,
                AVG(gain_net) as moyenne_gain,
                COUNT(CASE WHEN rang = '1er' THEN 1 END) as premier_rang
            FROM split_numbers, json_each('["' || replace(special, ',', '","') || '"]')
            GROUP BY value
            ORDER BY moyenne_gain DESC, frequence DESC
            LIMIT ?
        """, (jeu, limit))
        
        special_gagnants = cursor.fetchall()
        
        return {
            "numeros_gagnants": [
                {
                    "numero": row[0],
                    "frequence": row[1],
                    "moyenne_gain": round(row[2], 2),
                    "premier_rang": row[3]
                } for row in numeros_gagnants
            ],
            "special_gagnants": [
                {
                    "numero": row[0],
                    "frequence": row[1],
                    "moyenne_gain": round(row[2], 2),
                    "premier_rang": row[3]
                } for row in special_gagnants
            ]
        }

def get_evolution_gains(jeu, periode="mois"):
    """
    Analyse l'évolution des gains sur une période donnée.
    
    Args:
        jeu (str): Nom du jeu
        periode (str): 'jour', 'semaine', 'mois' ou 'annee'
    
    Returns:
        list: Évolution des gains sur la période
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        # Définition de la période
        if periode == "jour":
            format_date = "%Y-%m-%d"
            group_by = "date(date)"
        elif periode == "semaine":
            format_date = "%Y-%W"
            group_by = "strftime('%Y-%W', date)"
        elif periode == "mois":
            format_date = "%Y-%m"
            group_by = "strftime('%Y-%m', date)"
        else:  # année
            format_date = "%Y"
            group_by = "strftime('%Y', date)"
        
        cursor.execute(f"""
            SELECT 
                {group_by} as periode,
                COUNT(*) as nombre_grilles,
                SUM(gain_brut) as total_gain_brut,
                SUM(gain_net) as total_gain_net,
                COUNT(CASE WHEN gain_net > 0 THEN 1 END) as grilles_gagnantes
            FROM grilles_jouees
            WHERE jeu = ?
            GROUP BY {group_by}
            ORDER BY periode DESC
        """, (jeu,))
        
        return [
            {
                "periode": row[0],
                "nombre_grilles": row[1],
                "total_gain_brut": row[2] or 0,
                "total_gain_net": row[3] or 0,
                "grilles_gagnantes": row[4],
                "taux_reussite": round((row[4] / row[1] * 100) if row[1] > 0 else 0, 2)
            } for row in cursor.fetchall()
        ]

def get_combinaisons_frequentes(jeu, limit=5):
    """
    Identifie les combinaisons de numéros les plus fréquentes et performantes.
    
    Args:
        jeu (str): Nom du jeu
        limit (int): Nombre de combinaisons à retourner
    
    Returns:
        list: Combinaisons les plus performantes
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            WITH RECURSIVE split_numbers AS (
                SELECT 
                    grille,
                    gain_net,
                    rang,
                    substr(grille, 1, instr(grille, '|')-1) as numbers
                FROM grilles_jouees
                WHERE jeu = ?
            )
            SELECT 
                numbers,
                COUNT(*) as frequence,
                AVG(gain_net) as moyenne_gain,
                COUNT(CASE WHEN gain_net > 0 THEN 1 END) as grilles_gagnantes,
                COUNT(CASE WHEN rang = '1er' THEN 1 END) as premier_rang
            FROM split_numbers
            GROUP BY numbers
            HAVING frequence > 1
            ORDER BY moyenne_gain DESC, frequence DESC
            LIMIT ?
        """, (jeu, limit))
        
        return [
            {
                "combinaison": row[0],
                "frequence": row[1],
                "moyenne_gain": round(row[2], 2),
                "grilles_gagnantes": row[3],
                "premier_rang": row[4],
                "taux_reussite": round((row[3] / row[1] * 100) if row[1] > 0 else 0, 2)
            } for row in cursor.fetchall()
        ]

def get_statistiques_periodiques(jeu, date_debut, date_fin):
    """
    Analyse les statistiques sur une période spécifique.
    
    Args:
        jeu (str): Nom du jeu
        date_debut (str): Date de début (format YYYY-MM-DD)
        date_fin (str): Date de fin (format YYYY-MM-DD)
    
    Returns:
        dict: Statistiques détaillées sur la période
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_grilles,
                SUM(cout) as total_cout,
                SUM(gain_brut) as total_gain_brut,
                SUM(gain_net) as total_gain_net,
                COUNT(CASE WHEN gain_net > 0 THEN 1 END) as grilles_gagnantes,
                COUNT(CASE WHEN rang = '1er' THEN 1 END) as grilles_premier_rang,
                AVG(gain_net) as moyenne_gain_net,
                MAX(gain_net) as meilleur_gain,
                MIN(gain_net) as pire_gain
            FROM grilles_jouees
            WHERE jeu = ? AND date BETWEEN ? AND ?
        """, (jeu, date_debut, date_fin))
        
        stats = cursor.fetchone()
        return {
            "total_grilles": stats[0],
            "total_cout": stats[1] or 0,
            "total_gain_brut": stats[2] or 0,
            "total_gain_net": stats[3] or 0,
            "grilles_gagnantes": stats[4],
            "grilles_premier_rang": stats[5],
            "moyenne_gain_net": round(stats[6] or 0, 2),
            "meilleur_gain": stats[7] or 0,
            "pire_gain": stats[8] or 0,
            "taux_reussite": round((stats[4] / stats[0] * 100) if stats[0] > 0 else 0, 2),
            "roi": round(((stats[3] or 0) / (stats[1] or 1) * 100), 2)  # Return on Investment
        }

def get_sequences_gagnantes(jeu, longueur=3, limit=5):
    """
    Identifie les séquences de numéros consécutifs les plus performantes.
    
    Args:
        jeu (str): Nom du jeu
        longueur (int): Longueur de la séquence à analyser
        limit (int): Nombre de séquences à retourner
    
    Returns:
        list: Séquences les plus performantes
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            WITH RECURSIVE split_numbers AS (
                SELECT 
                    grille,
                    gain_net,
                    substr(grille, 1, instr(grille, '|')-1) as numbers
                FROM grilles_jouees
                WHERE jeu = ?
            ),
            sequences AS (
                SELECT 
                    numbers,
                    gain_net,
                    json_group_array(value) as sequence
                FROM split_numbers, json_each('["' || replace(numbers, ',', '","') || '"]')
                GROUP BY numbers
                HAVING json_array_length(sequence) >= ?
            )
            SELECT 
                sequence,
                COUNT(*) as frequence,
                AVG(gain_net) as moyenne_gain,
                COUNT(CASE WHEN gain_net > 0 THEN 1 END) as grilles_gagnantes
            FROM sequences
            GROUP BY sequence
            HAVING frequence > 1
            ORDER BY moyenne_gain DESC, frequence DESC
            LIMIT ?
        """, (jeu, longueur, limit))
        
        return [
            {
                "sequence": row[0],
                "frequence": row[1],
                "moyenne_gain": round(row[2], 2),
                "grilles_gagnantes": row[3],
                "taux_reussite": round((row[3] / row[1] * 100) if row[1] > 0 else 0, 2)
            } for row in cursor.fetchall()
        ]

def ajouter_favori(jeu, grille):
    """
    Ajoute une grille aux favoris.
    
    Args:
        jeu (str): Nom du jeu
        grille (dict): Dictionnaire contenant les numéros et numéros spéciaux
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        numeros = ",".join(map(str, grille["numbers"]))
        special = ",".join(map(str, grille["special"]))
        
        cursor.execute("""
            INSERT INTO favoris (jeu, grille)
            VALUES (?, ?)
        """, (jeu, numeros + "|" + special))
        conn.commit()

def get_favoris(jeu=None):
    """
    Récupère les grilles favorites.
    
    Args:
        jeu (str, optional): Nom du jeu pour filtrer les favoris
    
    Returns:
        list: Liste des grilles favorites
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        if jeu:
            cursor.execute("""
                SELECT id, jeu, grille
                FROM favoris
                WHERE jeu = ?
                ORDER BY id DESC
            """, (jeu,))
        else:
            cursor.execute("""
                SELECT id, jeu, grille
                FROM favoris
                ORDER BY id DESC
            """)
        
        favoris = cursor.fetchall()
        result = []
        for fav in favoris:
            numeros, special = fav[2].split("|")
            result.append({
                "id": fav[0],
                "jeu": fav[1],
                "numbers": list(map(int, numeros.split(","))),
                "special": list(map(int, special.split(",")))
            })
        return result

def supprimer_favori(favori_id):
    """
    Supprime une grille des favoris.
    
    Args:
        favori_id (int): ID de la grille favorite à supprimer
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM favoris WHERE id = ?", (favori_id,))
        conn.commit()

def get_statistiques_favoris(jeu=None):
    """
    Analyse les statistiques des grilles favorites.
    
    Args:
        jeu (str, optional): Nom du jeu pour filtrer l'analyse
    
    Returns:
        dict: Statistiques des grilles favorites
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        if jeu:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_favoris,
                    COUNT(DISTINCT jeu) as nombre_jeux,
                    GROUP_CONCAT(DISTINCT jeu) as jeux
                FROM favoris
                WHERE jeu = ?
            """, (jeu,))
        else:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_favoris,
                    COUNT(DISTINCT jeu) as nombre_jeux,
                    GROUP_CONCAT(DISTINCT jeu) as jeux
                FROM favoris
            """)
        
        stats = cursor.fetchone()
        return {
            "total_favoris": stats[0],
            "nombre_jeux": stats[1],
            "jeux": stats[2].split(",") if stats[2] else []
        }

def get_historical_data(jeu, years=10):
    """
    Récupère les données historiques des X dernières années pour un jeu donné.
    
    Args:
        jeu (str): Nom du jeu
        years (int): Nombre d'années de données à récupérer
    
    Returns:
        pandas.DataFrame: DataFrame contenant les données historiques
    """
    with sqlite3.connect(DB_PATH) as conn:
        # Calcul de la date de début
        start_date = (datetime.now() - pd.DateOffset(years=years)).strftime("%Y-%m-%d")
        
        # Récupération des tirages
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                date_tirage,
                numeros,
                etoiles,
                rangs,
                gains
            FROM tirages
            WHERE jeu = ? AND date_tirage >= ?
            ORDER BY date_tirage ASC
        """, (jeu, start_date))
        
        # Conversion en DataFrame
        columns = ['date', 'numbers', 'special', 'ranks', 'gains']
        data = cursor.fetchall()
        df = pd.DataFrame(data, columns=columns)
        
        # Conversion des types
        df['date'] = pd.to_datetime(df['date'])
        df['numbers'] = df['numbers'].apply(lambda x: list(map(int, x.split(','))))
        df['special'] = df['special'].apply(lambda x: list(map(int, x.split(','))))
        df['gains'] = df['gains'].apply(lambda x: float(x) if x else 0.0)
        
        # Vérification de la cohérence des données
        if len(df) == 0:
            print(f"⚠️ Aucune donnée trouvée pour {jeu} sur les {years} dernières années")
        else:
            print(f"✅ {len(df)} tirages récupérés pour {jeu} du {df['date'].min().strftime('%Y-%m-%d')} au {df['date'].max().strftime('%Y-%m-%d')}")
        
        return df

def get_working_dataset(jeu, years=10):
    """
    Crée un dataset de travail avec les données historiques et les statistiques associées.
    
    Args:
        jeu (str): Nom du jeu
        years (int): Nombre d'années de données à récupérer
    
    Returns:
        dict: Dictionnaire contenant le DataFrame historique et les statistiques associées
    """
    # Récupération des données historiques
    history_df = get_historical_data(jeu, years)
    
    if len(history_df) == 0:
        return None
    
    # Récupération des statistiques associées
    stats = get_statistics(jeu)
    stats_df = pd.DataFrame(stats, columns=['date', 'numbers', 'special', 'ratio_gain', 'indice_confiance'])
    stats_df['date'] = pd.to_datetime(stats_df['date'])
    
    # Fusion des données
    working_df = pd.merge(
        history_df,
        stats_df,
        on='date',
        how='left',
        suffixes=('', '_stats')
    )
    
    # Ajout des métadonnées
    metadata = {
        'jeu': jeu,
        'date_debut': working_df['date'].min(),
        'date_fin': working_df['date'].max(),
        'nombre_tirages': len(working_df),
        'nombre_annees': years
    }
    
    return {
        'data': working_df,
        'metadata': metadata
    }

def check_data_freshness():
    """
    Vérifie si les données sont à jour.
    Retourne True si les données sont fraîches, False sinon.
    """
    try:
        csv_path = Path(__file__).resolve().parent.parent / "data" / "loto_tirages.csv"
        if not csv_path.exists():
            return False
            
        # Vérification de la date de dernière modification
        last_modified = datetime.fromtimestamp(csv_path.stat().st_mtime)
        now = datetime.now()
        
        # Si les données ont plus de 24h, elles ne sont plus fraîches
        if (now - last_modified).total_seconds() > 86400:  # 24h en secondes
            return False
            
        return True
    except Exception as e:
        print(f"⚠️ Erreur lors de la vérification de fraîcheur des données : {e}")
        return False

def send_email(subject, body, recipient=None):
    """
    Fonction générique pour envoyer un email.
    
    Args:
        subject (str): Sujet de l'email
        body (str): Corps du message
        recipient (str, optional): Destinataire. Si None, utilise l'expéditeur par défaut.
    
    Returns:
        bool: True si l'envoi a réussi, False sinon
    """
    try:
        # Chemin du fichier de configuration
        config_path = Path(__file__).resolve().parent.parent / "SECURITY" / "config_admin.ini.enc"
        
        # Déchiffrement de la configuration
        config = decrypt_ini(config_path)
        
        # Récupération des paramètres SMTP
        smtp_server = config['EMAIL']['smtp_server']
        smtp_port = int(config['EMAIL']['smtp_port'])
        sender_email = config['EMAIL']['sender']
        smtp_password = config['EMAIL']['password']
        
        # Si aucun destinataire n'est spécifié, utiliser l'expéditeur
        if recipient is None:
            recipient = sender_email
        
        # Création du message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient
        msg['Subject'] = subject
        
        # Ajout du corps du message
        msg.attach(MIMEText(body, 'plain'))
        
        # Connexion et envoi
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, smtp_password)
            server.send_message(msg)
        
        return True
        
    except Exception as e:
        print(f"⚠️ Erreur lors de l'envoi de l'email : {e}")
        return False

def send_update_notification(success, is_initial=False, error_message=None):
    """
    Envoie une notification par email sur le statut de la mise à jour.
    """
    try:
        status = "✅" if success else "❌"
        type_update = "initiale" if is_initial else "automatique"
        subject = f"Mise à jour FDJ {type_update} - {'Succès' if success else 'Échec'}"
        
        body = f"""
        {status} Mise à jour {type_update} des données FDJ
        Date : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        Statut : {'Succès' if success else 'Échec'}
        """
        if error_message:
            body += f"\nMessage d'erreur : {error_message}"
        
        return send_email(subject, body)
        
    except Exception as e:
        print(f"⚠️ Erreur lors de l'envoi de la notification : {e}")
        return False

def notify_update_status(success, is_initial=False, error_message=None):
    """
    Envoie une notification sur le statut de la mise à jour.
    """
    try:
        status = "✅" if success else "❌"
        type_update = "initiale" if is_initial else "automatique"
        message = f"{status} Mise à jour {type_update} des données FDJ - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Enregistrement dans un fichier de log
        log_path = Path(__file__).resolve().parent.parent / "logs" / "updates.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"{message}\n")
            if error_message:
                f.write(f"Erreur : {error_message}\n")
            
        print(message)
        
        # Envoi de l'email de notification
        send_update_notification(success, is_initial, error_message)
        
    except Exception as e:
        print(f"⚠️ Erreur lors de l'envoi de la notification : {e}")

def download_fdj_data():
    """
    Pour chaque jeu FDJ :
    - Tente de télécharger et d'intégrer les fichiers ZIP/CSV historiques.
    - Si impossible, scrappe le dernier tirage depuis la page web.
    - Met à jour la base de données uniquement avec les nouveaux tirages.
    """
    from pathlib import Path
    import pandas as pd
    import requests
    import zipfile
    import shutil
    import os
    from bs4 import BeautifulSoup
    import configparser
    import tempfile
    from .regles import GAMES

    # Lecture de la configuration
    config = configparser.ConfigParser()
    config_path = Path(__file__).resolve().parent.parent / "config" / "config.ini"
    config.read(config_path)

    data_dir = Path(__file__).resolve().parent.parent / "data" / "fdj"
    data_dir.mkdir(parents=True, exist_ok=True)

    results = {}

    for game_name, game_rules in GAMES.items():
        print(f"\n📥 Traitement de {game_name}...")
        url = config['FDJ'].get(f'{game_name.upper()}_URL', None)
        if not url:
            print(f"❌ Pas d'URL trouvée pour {game_name}")
            results[game_name] = -1
            continue
        try:
            # Détection du type d'URL
            if url.endswith('.zip') or url.endswith('.csv'):
                # Téléchargement du fichier
                r = requests.get(url, stream=True)
                r.raise_for_status()
                with tempfile.TemporaryDirectory() as tmpdir:
                    tmpdir = Path(tmpdir)
                    local_file = tmpdir / url.split('/')[-1]
                    with open(local_file, 'wb') as f:
                        shutil.copyfileobj(r.raw, f)
                    # Si ZIP, extraction
                    if str(local_file).endswith('.zip'):
                        with zipfile.ZipFile(local_file, 'r') as zip_ref:
                            zip_ref.extractall(tmpdir)
                        csv_files = list(tmpdir.glob('*.csv'))
                    else:
                        csv_files = [local_file]
                    # Fusion des CSV
                    all_data = []
                    for csvf in csv_files:
                        try:
                            df = pd.read_csv(csvf, sep=';', engine='python')
                            all_data.append(df)
                        except Exception as e:
                            print(f"⚠️ Erreur lecture {csvf}: {e}")
                    if all_data:
                        df_all = pd.concat(all_data, ignore_index=True)
                        # Standardisation des colonnes selon le jeu
                        if game_name == 'LOTO':
                            df_all = df_all.rename(columns={
                                'date_de_tirage': 'date',
                                'boule_1': 'n1',
                                'boule_2': 'n2',
                                'boule_3': 'n3',
                                'boule_4': 'n4',
                                'boule_5': 'n5',
                                'numero_chance': 'chance'
                            })
                            df_all['numbers'] = df_all[['n1', 'n2', 'n3', 'n4', 'n5']].values.tolist()
                            df_all['special'] = df_all['chance'].apply(lambda x: [x])
                        elif game_name == 'EUROMILLIONS':
                            df_all = df_all.rename(columns={
                                'date_de_tirage': 'date',
                                'boule_1': 'n1',
                                'boule_2': 'n2',
                                'boule_3': 'n3',
                                'boule_4': 'n4',
                                'boule_5': 'n5',
                                'etoile_1': 'e1',
                                'etoile_2': 'e2'
                            })
                            df_all['numbers'] = df_all[['n1', 'n2', 'n3', 'n4', 'n5']].values.tolist()
                            df_all['special'] = df_all[['e1', 'e2']].values.tolist()
                        elif game_name == 'EURODREAMS':
                            df_all = df_all.rename(columns={
                                'date_de_tirage': 'date',
                                'boule_1': 'n1',
                                'boule_2': 'n2',
                                'boule_3': 'n3',
                                'boule_4': 'n4',
                                'boule_5': 'n5',
                                'boule_6': 'n6',
                                'numero_dream': 'dream'
                            })
                            df_all['numbers'] = df_all[['n1', 'n2', 'n3', 'n4', 'n5', 'n6']].values.tolist()
                            df_all['special'] = df_all['dream'].apply(lambda x: [x])
                        elif game_name == 'KENO':
                            df_all = df_all.rename(columns={
                                'date_de_tirage': 'date',
                                'numero_1': 'n1',
                                'numero_2': 'n2',
                                'numero_3': 'n3',
                                'numero_4': 'n4',
                                'numero_5': 'n5',
                                'numero_6': 'n6',
                                'numero_7': 'n7',
                                'numero_8': 'n8',
                                'numero_9': 'n9',
                                'numero_10': 'n10'
                            })
                            df_all['numbers'] = df_all[[f'n{i}' for i in range(1, 11)]].values.tolist()
                            df_all['special'] = [[]] * len(df_all)
                        # Conversion des dates
                        if 'date' not in df_all.columns and 'date_de_tirage' in df_all.columns:
                            df_all = df_all.rename(columns={'date_de_tirage': 'date'})
                        df_all['date'] = pd.to_datetime(df_all['date'])
                        df_all = df_all.sort_values('date')
                        # Sauvegarde dans le CSV compilé
                        csv_path = data_dir / f"{game_name.lower()}_tirages.csv"
                        df_all.to_csv(csv_path, sep=';', index=False)
                        # Mise à jour de la base de données (comme avant)
                        with sqlite3.connect(DB_PATH) as conn:
                            cursor = conn.cursor()
                            cursor.execute("SELECT MAX(date_tirage) FROM tirages WHERE jeu = ?", (game_name,))
                            last_date = cursor.fetchone()[0]
                            if last_date:
                                last_date = datetime.strptime(last_date, '%Y-%m-%d')
                                new_draws = df_all[df_all['date'] > last_date]
                            else:
                                new_draws = df_all
                            for _, row in new_draws.iterrows():
                                cursor.execute("""
                                    INSERT INTO tirages (jeu, date_tirage, numeros, etoiles)
                                    VALUES (?, ?, ?, ?)
                                """, (
                                    game_name,
                                    row['date'].strftime('%Y-%m-%d'),
                                    ','.join(map(str, row['numbers'])),
                                    ','.join(map(str, row['special']))
                                ))
                            conn.commit()
                        results[game_name] = len(new_draws)
                        print(f"✅ {len(new_draws)} nouveaux tirages ajoutés pour {game_name}")
                    else:
                        print(f"⚠️ Aucun CSV exploitable pour {game_name}")
                        results[game_name] = 0
            else:
                # Fallback scraping
                print(f"🌐 Scraping pour {game_name}...")
                r = requests.get(url)
                r.raise_for_status()
                soup = BeautifulSoup(r.text, 'html.parser')
                
                # Extraction selon le jeu
                numbers = []
                special = []
                date = datetime.now()
                
                if game_name == 'LOTO':
                    print(f"\n🔍 Analyse de la page pour {game_name}...")
                    # Recherche de la section du dernier tirage
                    tirage_section = soup.find('div', {'class': 'loto-result'})
                    if not tirage_section:
                        print("Recherche avec 'loto-resultat'...")
                        tirage_section = soup.find('div', {'class': 'loto-resultat'})
                    if not tirage_section:
                        print("Recherche avec 'resultat-loto'...")
                        tirage_section = soup.find('div', {'class': 'resultat-loto'})
                    
                    if tirage_section:
                        print("Section trouvée, recherche des numéros...")
                        # Extraction des numéros principaux
                        number_elements = tirage_section.find_all('div', {'class': ['number', 'boule', 'numero']})
                        if not number_elements:
                            print("Recherche des numéros dans les spans...")
                            number_elements = tirage_section.find_all('span', {'class': ['number', 'boule', 'numero']})
                        
                        print(f"Éléments trouvés : {len(number_elements)}")
                        if number_elements:
                            print(f"Classes trouvées : {[elem.get('class', []) for elem in number_elements]}")
                            print(f"Textes trouvés : {[elem.text.strip() for elem in number_elements]}")
                        
                        numbers = [int(num.text.strip()) for num in number_elements[:5]]
                        print(f"Numéros extraits : {numbers}")
                        
                        # Extraction du numéro chance
                        chance_element = tirage_section.find('div', {'class': ['chance', 'numero-chance']})
                        if not chance_element:
                            print("Recherche du numéro chance dans les spans...")
                            chance_element = tirage_section.find('span', {'class': ['chance', 'numero-chance']})
                        
                        if chance_element:
                            print(f"Numéro chance trouvé : {chance_element.text.strip()}")
                            special = [int(chance_element.text.strip())]
                        else:
                            print("❌ Numéro chance non trouvé")
                            special = []
                        
                        # Extraction de la date
                        date_element = tirage_section.find('div', {'class': ['date', 'date-tirage']})
                        if not date_element:
                            print("Recherche de la date dans les spans...")
                            date_element = tirage_section.find('span', {'class': ['date', 'date-tirage']})
                        
                        if date_element:
                            date_str = date_element.text.strip()
                            print(f"Date trouvée : {date_str}")
                            try:
                                date = datetime.strptime(date_str, '%d/%m/%Y')
                            except ValueError:
                                try:
                                    date = datetime.strptime(date_str, '%Y-%m-%d')
                                except ValueError:
                                    print(f"⚠️ Format de date non reconnu : {date_str}")
                    else:
                        print("❌ Section de tirage non trouvée")
                        print("Contenu de la page :")
                        print(soup.prettify()[:1000])  # Affiche les 1000 premiers caractères
                
                elif game_name == 'EUROMILLIONS':
                    # Recherche de la section du dernier tirage
                    tirage_section = soup.find('div', {'class': 'euromillions-result'})
                    if not tirage_section:
                        tirage_section = soup.find('div', {'class': 'euromillions-resultat'})
                    if not tirage_section:
                        tirage_section = soup.find('div', {'class': 'resultat-euromillions'})
                    
                    if tirage_section:
                        # Extraction des numéros principaux
                        number_elements = tirage_section.find_all('div', {'class': ['number', 'boule', 'numero']})
                        if not number_elements:
                            number_elements = tirage_section.find_all('span', {'class': ['number', 'boule', 'numero']})
                        numbers = [int(num.text.strip()) for num in number_elements[:5]]
                        
                        # Extraction des étoiles
                        star_elements = tirage_section.find_all('div', {'class': ['star', 'etoile']})
                        if not star_elements:
                            star_elements = tirage_section.find_all('span', {'class': ['star', 'etoile']})
                        special = [int(star.text.strip()) for star in star_elements[:2]]
                        
                        # Extraction de la date
                        date_element = tirage_section.find('div', {'class': ['date', 'date-tirage']})
                        if not date_element:
                            date_element = tirage_section.find('span', {'class': ['date', 'date-tirage']})
                        if date_element:
                            date_str = date_element.text.strip()
                            try:
                                date = datetime.strptime(date_str, '%d/%m/%Y')
                            except ValueError:
                                try:
                                    date = datetime.strptime(date_str, '%Y-%m-%d')
                                except ValueError:
                                    print(f"⚠️ Format de date non reconnu pour {game_name}: {date_str}")
                
                elif game_name == 'EURODREAMS':
                    # Recherche de la section du dernier tirage
                    tirage_section = soup.find('div', {'class': 'eurodreams-result'})
                    if not tirage_section:
                        tirage_section = soup.find('div', {'class': 'eurodreams-resultat'})
                    if not tirage_section:
                        tirage_section = soup.find('div', {'class': 'resultat-eurodreams'})
                    
                    if tirage_section:
                        # Extraction des numéros principaux
                        number_elements = tirage_section.find_all('div', {'class': ['number', 'boule', 'numero']})
                        if not number_elements:
                            number_elements = tirage_section.find_all('span', {'class': ['number', 'boule', 'numero']})
                        numbers = [int(num.text.strip()) for num in number_elements[:6]]
                        
                        # Extraction du numéro Dream
                        dream_element = tirage_section.find('div', {'class': ['dream', 'numero-dream']})
                        if not dream_element:
                            dream_element = tirage_section.find('span', {'class': ['dream', 'numero-dream']})
                        if dream_element:
                            special = [int(dream_element.text.strip())]
                        
                        # Extraction de la date
                        date_element = tirage_section.find('div', {'class': ['date', 'date-tirage']})
                        if not date_element:
                            date_element = tirage_section.find('span', {'class': ['date', 'date-tirage']})
                        if date_element:
                            date_str = date_element.text.strip()
                            try:
                                date = datetime.strptime(date_str, '%d/%m/%Y')
                            except ValueError:
                                try:
                                    date = datetime.strptime(date_str, '%Y-%m-%d')
                                except ValueError:
                                    print(f"⚠️ Format de date non reconnu pour {game_name}: {date_str}")
                
                elif game_name == 'KENO':
                    # Recherche de la section du dernier tirage
                    tirage_section = soup.find('div', {'class': 'keno-result'})
                    if not tirage_section:
                        tirage_section = soup.find('div', {'class': 'keno-resultat'})
                    if not tirage_section:
                        tirage_section = soup.find('div', {'class': 'resultat-keno'})
                    
                    if tirage_section:
                        # Extraction des 10 numéros
                        number_elements = tirage_section.find_all('div', {'class': ['number', 'boule', 'numero']})
                        if not number_elements:
                            number_elements = tirage_section.find_all('span', {'class': ['number', 'boule', 'numero']})
                        numbers = [int(num.text.strip()) for num in number_elements[:10]]
                        
                        # Le Keno n'a pas de numéro spécial
                        special = []
                        
                        # Extraction de la date
                        date_element = tirage_section.find('div', {'class': ['date', 'date-tirage']})
                        if not date_element:
                            date_element = tirage_section.find('span', {'class': ['date', 'date-tirage']})
                        if date_element:
                            date_str = date_element.text.strip()
                            try:
                                date = datetime.strptime(date_str, '%d/%m/%Y')
                            except ValueError:
                                try:
                                    date = datetime.strptime(date_str, '%Y-%m-%d')
                                except ValueError:
                                    print(f"⚠️ Format de date non reconnu pour {game_name}: {date_str}")
                
                # Vérification que nous avons bien tous les numéros requis
                if not numbers or len(numbers) != GAMES[game_name]['numbers_count']:
                    print(f"⚠️ Nombre de numéros incorrect pour {game_name}")
                    results[game_name] = -1
                    continue
                
                if game_name != 'KENO' and (not special or len(special) != GAMES[game_name]['special_count']):
                    print(f"⚠️ Nombre de numéros spéciaux incorrect pour {game_name}")
                    results[game_name] = -1
                    continue
                
                # Mise à jour de la base de données si nouveau tirage
                with sqlite3.connect(DB_PATH) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT MAX(date_tirage) FROM tirages WHERE jeu = ?", (game_name,))
                    last_date = cursor.fetchone()[0]
                    
                    if last_date:
                        last_date = datetime.strptime(last_date, '%Y-%m-%d')
                        if date > last_date:
                            cursor.execute("""
                                INSERT INTO tirages (jeu, date_tirage, numeros, etoiles)
                                VALUES (?, ?, ?, ?)
                            """, (
                                game_name,
                                date.strftime('%Y-%m-%d'),
                                ','.join(map(str, numbers)),
                                ','.join(map(str, special))
                            ))
                            conn.commit()
                            results[game_name] = 1
                            print(f"✅ Nouveau tirage scrappé pour {game_name}")
                        else:
                            print(f"ℹ️ Pas de nouveau tirage pour {game_name}")
                            results[game_name] = 0
                    else:
                        cursor.execute("""
                            INSERT INTO tirages (jeu, date_tirage, numeros, etoiles)
                            VALUES (?, ?, ?, ?)
                        """, (
                            game_name,
                            date.strftime('%Y-%m-%d'),
                            ','.join(map(str, numbers)),
                            ','.join(map(str, special))
                        ))
                        conn.commit()
                        results[game_name] = 1
                        print(f"✅ Premier tirage scrappé pour {game_name}")
        except Exception as e:
            print(f"❌ Erreur lors du traitement de {game_name}: {str(e)}")
            results[game_name] = -1
    return all(results.values()) > 0

def is_data_fresh():
    """
    Vérifie si les données de tous les jeux sont à jour.
    Retourne True si toutes les données sont fraîches, False sinon.
    """
    from pathlib import Path
    from datetime import datetime, timedelta
    from .regles import GAMES

    data_dir = Path(__file__).resolve().parent.parent / "data" / "fdj"
    
    # Si le dossier n'existe pas, les données ne sont pas fraîches
    if not data_dir.exists():
        return False
    
    # Vérification pour chaque jeu
    for game_name in GAMES.keys():
        csv_path = data_dir / f"{game_name.lower()}_tirages.csv"
        
        # Si le fichier n'existe pas, les données ne sont pas fraîches
        if not csv_path.exists():
            return False
            
        # Vérification de la date de dernière modification
        last_modified = datetime.fromtimestamp(csv_path.stat().st_mtime)
        now = datetime.now()
        
        # Si les données ont plus de 24h, elles ne sont plus fraîches
        if (now - last_modified).total_seconds() > 86400:  # 24h en secondes
            return False
    
    return True

def update_rules():
    """
    Met à jour les règles des jeux dans la base de données.
    """
    from .regles import GAMES
    
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            
            for jeu, regles in GAMES.items():
                cursor.execute("""
                    INSERT OR REPLACE INTO jeux (
                        nom, 
                        numbers_range, 
                        numbers_count, 
                        special_range, 
                        special_count, 
                        draw_days
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    jeu,
                    str(regles["numbers_range"]),
                    regles["numbers_count"],
                    str(regles["special_range"]),
                    regles["special_count"],
                    str(regles["draw_days"])
                ))
            
            conn.commit()
            print("✅ Règles des jeux mises à jour avec succès")
            return True
            
    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour des règles : {str(e)}")
        return False

def schedule_fdj_updates():
    """
    Planifie la mise à jour automatique des données FDJ.
    Les mises à jour sont programmées tous les jours de la semaine (lundi à samedi) à 00:01.
    """
    # Mise à jour tous les jours de la semaine (lundi à samedi)
    schedule.every().monday.at("00:01").do(update_fdj_data)
    schedule.every().tuesday.at("00:01").do(update_fdj_data)
    schedule.every().wednesday.at("00:01").do(update_fdj_data)
    schedule.every().thursday.at("00:01").do(update_fdj_data)
    schedule.every().friday.at("00:01").do(update_fdj_data)
    schedule.every().saturday.at("00:01").do(update_fdj_data)
    
    def run_scheduler():
        """Fonction qui exécute le planificateur en arrière-plan"""
        while True:
            schedule.run_pending()
            time.sleep(60)  # Vérifie toutes les minutes
    
    # Démarrage du planificateur dans un thread séparé
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    print("📅 Planificateur de mise à jour FDJ démarré")
    return scheduler_thread

def check_admin_license():
    """
    Vérifie si l'utilisateur a une licence admin valide.
    Retourne True si la licence admin est valide, False sinon.
    """
    try:
        license_path = Path(__file__).resolve().parent.parent / "LICENSE_ADMIN" / "license.ini.enc"
        if not license_path.exists():
            return False
            
        # Déchiffrement de la licence
        config = decrypt_ini(license_path)
        
        # Vérification de la licence illimitée
        if config['LICENSE']['type'] != 'unlimited':
            return False
            
        # Vérification de la date d'expiration
        expiration_date = datetime.strptime(config['LICENSE']['expiration'], '%Y-%m-%d')
        if expiration_date < datetime.now():
            return False
            
        return True
        
    except Exception as e:
        print(f"⚠️ Erreur lors de la vérification de la licence admin : {e}")
        return False

def check_client_license():
    """
    Vérifie si l'utilisateur a une licence client valide.
    Retourne un tuple (bool, dict) : (validité de la licence, infos de la licence)
    """
    try:
        # Récupération de l'UUID de la machine
        machine_uuid = get_machine_uuid()
        
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT licence_type, date_expiration, status
                FROM licence_client
                WHERE uuid = ?
            """, (machine_uuid,))
            
            result = cursor.fetchone()
            if not result:
                return False, None
                
            licence_type, expiration_date, status = result
            
            # Vérification de la date d'expiration
            if datetime.strptime(expiration_date, '%Y-%m-%d') < datetime.now():
                return False, None
                
            # Vérification du statut
            if status != 'active':
                return False, None
                
            return True, {
                'type': licence_type,
                'expiration': expiration_date,
                'status': status
            }
            
    except Exception as e:
        print(f"⚠️ Erreur lors de la vérification de la licence client : {e}")
        return False, None

def get_machine_uuid():
    """
    Génère un UUID unique pour la machine basé sur les caractéristiques matérielles.
    """
    import uuid
    import platform
    import hashlib
    
    # Collecte des informations système
    system_info = {
        'platform': platform.system(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'node': platform.node()
    }
    
    # Création d'une chaîne unique
    unique_string = str(system_info)
    
    # Génération de l'UUID
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, unique_string))

def is_demo_mode():
    """
    Vérifie si l'application est en mode démo.
    Retourne True si en mode démo, False sinon.
    """
    # Si l'utilisateur est admin, pas de mode démo
    if check_admin_license():
        return False
        
    # Vérification de la licence client
    has_license, _ = check_client_license()
    return not has_license

def get_user_permissions():
    """
    Retourne les permissions de l'utilisateur.
    """
    permissions = {
        'is_admin': False,
        'is_client': False,
        'is_demo': True,
        'can_access_crm': False,
        'can_access_billing': False,
        'can_play': True,
        'can_feedback': True,
        'can_settings': True,
        'can_check_license': True
    }
    
    # Vérification des droits admin
    if check_admin_license():
        permissions.update({
            'is_admin': True,
            'is_demo': False,
            'can_access_crm': True,
            'can_access_billing': True
        })
        return permissions
        
    # Vérification des droits client
    has_license, license_info = check_client_license()
    if has_license:
        permissions.update({
            'is_client': True,
            'is_demo': False
        })
        
    return permissions

def update_fdj_data():
    """
    Met à jour les données FDJ en appelant download_fdj_data.
    Retourne True si la mise à jour a réussi, False sinon.
    """
    try:
        return download_fdj_data()
    except Exception as e:
        print(f"Erreur lors de la mise à jour des données FDJ : {e}")
        return False
