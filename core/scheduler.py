import schedule
import time
import threading
from datetime import datetime
from core.insights import check_draw_results, display_morning_predictions, collect_anonymous_feedback
from core.database import init_db, validate_latest_draws

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
        
        while True:
            schedule.run_pending()
            time.sleep(60)
    
    # Lancement du scheduler dans un thread séparé
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
