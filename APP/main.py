from ui.gui import launch_app
from core.database import init_db
from core.scheduler import launch_in_background
from core.license_watcher import check_expiration_alert
from core.feedback_uploader import send_feedback

def main():
    print("=== Lancement de LotoAiPredictor ===")
    init_db()
    check_expiration_alert()
    launch_in_background()
    send_feedback()
    launch_app()

if __name__ == "__main__":
    main()