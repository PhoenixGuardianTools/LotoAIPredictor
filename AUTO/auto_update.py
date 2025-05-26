import datetime
from core.update_engine import update_results
from core.stats import update_gains
from TOOLS.export_web_data import export_all

def log(msg):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    with open("AUTO/log/auto.log", "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {msg}\n")

def auto_update():
    try:
        update_results()
        log("✔ Tirages mis à jour")
        update_gains()
        log("✔ Gains mis à jour")
        export_all()
        log("✔ Export Web mis à jour")
    except Exception as e:
        log(f"❌ Erreur : {e}")

if __name__ == "__main__":
    auto_update()
