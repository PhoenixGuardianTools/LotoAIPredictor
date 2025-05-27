import schedule
import time
import threading
from datetime import datetime
from core.insights import check_draw_results, display_morning_predictions, collect_anonymous_feedback
from core.database import init_db, validate_latest_draws, update_fdj_data

def launch_in_background():
    """Lance le scheduler en arrière-plan."""
    def run_scheduler():
        # Vérification des tirages à minuit
        schedule.every().day.at("00:00").do(check_draw_results)
        
        # Affichage des prédictions à 9h
        schedule.every().day.at("09:00").do(display_morning_predictions)
        
        # Collecte des feedbacks anonymes toutes les heures
        schedule.every().hour.do(collect_anonymous_feedback)
        
        # Vérification de la base de données toutes les 6 heures
        schedule.every(6).hours.do(init_db)
        schedule.every(6).hours.do(validate_latest_draws)
        
        # Mise à jour FDJ tous les jours de la semaine (lundi à samedi) à 00:01
        schedule.every().monday.at("00:01").do(update_fdj_data)
        schedule.every().tuesday.at("00:01").do(update_fdj_data)
        schedule.every().wednesday.at("00:01").do(update_fdj_data)
        schedule.every().thursday.at("00:01").do(update_fdj_data)
        schedule.every().friday.at("00:01").do(update_fdj_data)
        schedule.every().saturday.at("00:01").do(update_fdj_data)
        
        while True:
            schedule.run_pending()
            time.sleep(60)
    
    # Lancement du scheduler dans un thread séparé
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    print("📅 Scheduler démarré avec succès")
    return scheduler_thread
