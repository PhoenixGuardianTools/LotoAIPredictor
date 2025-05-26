import datetime
import schedule
import time
from core.database import update_draws_and_results
from core.analytics import analyze_patterns_and_cycles
from core.predictor import retrain_models
from utils.network import is_connected

def daily_update_routine():
    if not is_connected():
        print("Pas de connexion internet. Mise à jour reportée.")
        return

    print("⏳ Mise à jour quotidienne à minuit...")
    update_draws_and_results()
    retrain_models()
    analyze_patterns_and_cycles()
    print("✅ Mise à jour terminée.")

def schedule_nightly_updates():
    schedule.every().day.at("00:00").do(daily_update_routine)

    while True:
        schedule.run_pending()
        time.sleep(60)
