import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "phoenix.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# ------------------------
# Database initialization
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

    conn.commit()
    conn.close()

# ------------------------
# Saving and retrieval
# ------------------------

def save_draw_result(jeu, date_tirage, numeros, etoiles, rangs, gains):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO tirages (jeu, date_tirage, numeros, etoiles, rangs, gains)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (jeu, date_tirage, numeros, etoiles, rangs, gains))

def save_grille(jeu, date, grille, model_version, gain_brut=0, cout=2.5, gain_net=0, rang='NA'):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO grilles_jouees (jeu, date, grille, model_version, gain_brut, cout, gain_net, rang)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (jeu, date, grille, model_version, gain_brut, cout, gain_net, rang))

def save_favorite(jeu, grille):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO favoris (jeu, grille) VALUES (?, ?)
        """, (jeu, grille))

def save_manual_grid(jeu, grille, date=None):
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO grilles_jouees (jeu, date, grille, model_version)
            VALUES (?, ?, ?, ?)
        """, (jeu, date, grille, "manual"))

def get_draw_results(jeu):
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute("""
            SELECT date_tirage, numeros, etoiles FROM tirages
            WHERE jeu = ?
            ORDER BY date_tirage DESC
        """, (jeu,))
        return rows.fetchall()

def get_all_favorites():
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute("SELECT jeu, grille FROM favoris")
        return rows.fetchall()

def get_user_stats():
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute("""
            SELECT jeu, COUNT(*), SUM(gain_brut), SUM(cout), SUM(gain_net)
            FROM grilles_jouees
            GROUP BY jeu
        """)
        return rows.fetchall()

def get_latest_draw_date(jeu):
    with sqlite3.connect(DB_PATH) as conn:
        result = conn.execute("""
            SELECT MAX(date_tirage) FROM tirages WHERE jeu = ?
        """, (jeu,)).fetchone()
        return result[0] if result else None
