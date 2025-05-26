import sqlite3
import json
from datetime import datetime

DB = "SECURITY/app_data.db"

def export_tirages():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT jeu, date, numeros, gain_total FROM tirages ORDER BY date DESC LIMIT 10
    """)
    data = [
        {
            "jeu": row[0],
            "date": row[1],
            "numeros": row[2],
            "gain": row[3]
        } for row in cursor.fetchall()
    ]
    with open("web/stats/tirages_recents.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    conn.close()

def export_ratios():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    result = []

    for jeu in ["loto", "euromillion", "eurodream"]:
        cursor.execute("SELECT COUNT(*), SUM(gain) FROM grilles WHERE jeu=?", (jeu,))
        tests, gains = cursor.fetchone()
        couts = tests * 2.5 if jeu == "loto" else tests * 2.5 if jeu == "eurodream" else tests * 2.5
        net = (gains or 0) - couts
        result.append({
            "jeu": jeu,
            "tests": tests,
            "gains": round(gains or 0, 2),
            "couts": round(couts, 2),
            "net": round(net, 2)
        })

    with open("web/stats/ratio_jeux.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    conn.close()

def export_resume():
    with open("web/stats/ratio_jeux.json", encoding="utf-8") as f:
        ratios = json.load(f)
    net_total = sum(j["net"] for j in ratios)
    tests_total = sum(j["tests"] for j in ratios)
    resume = {
        "resume": f"Ratio moyen de gain net : {round(net_total, 2)} € / {tests_total} grilles testées."
    }
    with open("web/stats/performance.json", "w", encoding="utf-8") as f:
        json.dump(resume, f, indent=2, ensure_ascii=False)

def export_all():
    export_tirages()
    export_ratios()
    export_resume()
    print("📁 Fichiers web exportés.")

if __name__ == "__main__":
    export_all()
