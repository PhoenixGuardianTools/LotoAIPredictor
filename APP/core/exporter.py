import sqlite3
import pandas as pd

def export_to_excel():
    conn = sqlite3.connect("SECURITY/app_data.db")
    grilles = pd.read_sql("SELECT * FROM grilles", conn)
    tirages = pd.read_sql("SELECT * FROM tirages", conn)

    with pd.ExcelWriter("EXPORTS/stats_weekly.xlsx") as writer:
        grilles.to_excel(writer, sheet_name="Grilles", index=False)
        tirages.to_excel(writer, sheet_name="Tirages", index=False)

    conn.close()
    print("Export Excel effectué.")
