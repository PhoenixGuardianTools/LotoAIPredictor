import sqlite3
from datetime import datetime
from pathlib import Path
from APP.core.regles import fetch_latest_rules, validate_draw_format

# Définition du chemin de la base de données
DB_PATH = Path(__file__).resolve().parent.parent / "data" / "phoenix.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# ------------------------
# Initialisation de la base de données
# ------------------------
def init_db():
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
