from ui.gui import launch_app
from core.database import init_db
from core.scheduler import launch_in_background
from APP.LICENSE_ADMIN.license_watcher import check_expiration_alert

def main():
    print("=== Lancement de LotoAiPredictor ===")
    init_db()
    check_expiration_alert()
    launch_in_background()
    launch_app()

if __name__ == "__main__":
    main()
