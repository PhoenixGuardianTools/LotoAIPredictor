import schedule
import time
from core.update_engine import daily_update_routine

def launch_in_background():
    print("⏰ Planification des mises à jour à 00:00 chaque jour...")
    schedule.every().day.at("00:00").do(daily_update_routine)

    # Exécution non bloquante
    import threading
    t = threading.Thread(target=run_scheduler)
    t.daemon = True
    t.start()

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(60)
