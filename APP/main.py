from ui.gui import launch_app
from core.database import init_db
from core.scheduler import launch_in_background
from APP.LICENSE_ADMIN.license_watcher import check_expiration_alert
from core.predictions import generate_predictions
from core.visualization_report import generate_daily_insights
import time
import threading

def schedule_visualization():
    """Planifie l'affichage des tendances chaque jour à 9h."""
    while True:
        now = time.localtime()
        if now.tm_hour == 9 and now.tm_min == 0:
            print("📊 Génération de la visualisation des tendances du jour...")
            generate_daily_insights()
            time.sleep(60)  # Évite les multiples exécutions dans la même minute
        else:
            time.sleep(10)  # Vérification périodique toutes les 10 secondes

def main():
    print("=== Lancement de LotoAiPredictor ===")
    
    # Initialisation des modules
    init_db()
    check_expiration_alert()
    launch_in_background()

    # Lancement du suivi automatique de la visualisation à 9h
    threading.Thread(target=schedule_visualization, daemon=True).start()
    
    # Génération des prévisions
    print("\n📊 **Génération des prévisions optimisées** 📊")
    predictions = generate_predictions(history_df)
    for game, numbers in predictions.items():
        print(f"{game} : {numbers}")

    # Lancement de l'interface utilisateur
    launch_app()

if __name__ == "__main__":
    main()
