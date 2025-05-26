import json
from datetime import datetime, timedelta
from pathlib import Path
import calendar
import requests
from typing import Dict, List, Optional

class PromoManager:
    def __init__(self):
        self.promo_path = Path("PROMOTIONS/promo_templates.json")
        self.events_path = Path("PROMOTIONS/events.json")
        self.notifications_path = Path("PROMOTIONS/notifications.json")
        self.last_notification_path = Path("PROMOTIONS/last_notification.json")
        
    def _load_events(self) -> Dict:
        """Charge les événements du calendrier."""
        if self.events_path.exists():
            with open(self.events_path, 'r') as f:
                return json.load(f)
        return {
            "events": [
                {
                    "name": "Fête des Mères",
                    "date": "2024-05-26",
                    "message": "🎁 Offrez à votre maman une chance de gagner !"
                },
                {
                    "name": "Fête des Pères",
                    "date": "2024-06-16",
                    "message": "🎁 Faites plaisir à votre papa !"
                },
                {
                    "name": "Saint-Valentin",
                    "date": "2024-02-14",
                    "message": "❤️ Offrez l'amour et la chance à votre moitié !"
                },
                {
                    "name": "Noël",
                    "date": "2024-12-25",
                    "message": "🎄 Le plus beau des cadeaux : la chance de gagner !"
                },
                {
                    "name": "Nouvel An",
                    "date": "2025-01-01",
                    "message": "✨ Commencez l'année avec de la chance !"
                },
                {
                    "name": "Pâques",
                    "date": "2024-03-31",
                    "message": "🥚 Les œufs de Pâques cachent peut-être le gros lot !"
                },
                {
                    "name": "Fête Nationale",
                    "date": "2024-07-14",
                    "message": "🎆 Célébrez la France avec un tirage spécial !"
                },
                {
                    "name": "Black Friday",
                    "date": "2024-11-29",
                    "message": "🛍️ Les meilleures offres de l'année !"
                }
            ]
        }
        
    def _load_notifications(self) -> Dict:
        """Charge l'historique des notifications."""
        if self.notifications_path.exists():
            with open(self.notifications_path, 'r') as f:
                return json.load(f)
        return {"notifications": []}
        
    def _save_notification(self, user_id: str, message: str):
        """Sauvegarde une notification envoyée."""
        notifications = self._load_notifications()
        notifications["notifications"].append({
            "user_id": user_id,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        with open(self.notifications_path, 'w') as f:
            json.dump(notifications, f, indent=2)
            
    def _get_current_event(self) -> Optional[Dict]:
        """Récupère l'événement en cours."""
        events = self._load_events()
        today = datetime.now().date()
        
        for event in events["events"]:
            event_date = datetime.strptime(event["date"], "%Y-%m-%d").date()
            if event_date == today:
                return event
        return None
        
    def _should_notify(self, user_id: str, days_left: int) -> bool:
        """Détermine si une notification doit être envoyée."""
        if not self.last_notification_path.exists():
            return True
            
        with open(self.last_notification_path, 'r') as f:
            last = json.load(f)
            
        if user_id not in last:
            return True
            
        last_time = datetime.fromisoformat(last[user_id])
        now = datetime.now()
        
        # Une notification par jour maximum
        if (now - last_time).days < 1:
            return False
            
        # Notification à 30, 15, 7, 3, 2, 1 jours
        return days_left in [30, 15, 7, 3, 2, 1]
        
    def _update_last_notification(self, user_id: str):
        """Met à jour la dernière notification."""
        if self.last_notification_path.exists():
            with open(self.last_notification_path, 'r') as f:
                last = json.load(f)
        else:
            last = {}
            
        last[user_id] = datetime.now().isoformat()
        
        with open(self.last_notification_path, 'w') as f:
            json.dump(last, f, indent=2)
            
    def get_promo_message(self, user_id: str, days_left: int) -> Optional[str]:
        """Génère un message de promotion personnalisé."""
        if not self._should_notify(user_id, days_left):
            return None
            
        event = self._get_current_event()
        if event:
            message = f"{event['message']} Profitez de -15% avec le code SPECIAL !"
        else:
            if days_left == 1:
                message = "⚠️ Votre licence expire demain ! Renouvelez maintenant pour -20% !"
            elif days_left <= 3:
                message = "⏰ Plus que quelques jours ! Profitez de -15% sur votre renouvellement !"
            elif days_left <= 7:
                message = "🎁 Une semaine pour renouveler avec -10% !"
            else:
                message = "💫 Renouvelez votre licence et bénéficiez de -5% !"
                
        self._save_notification(user_id, message)
        self._update_last_notification(user_id)
        
        return message
        
    def get_newsletter_content(self, version: str) -> str:
        """Génère le contenu de la newsletter."""
        return f"""
        🚀 Mise à jour {version}
        
        Découvrez les nouvelles fonctionnalités :
        - Amélioration des prédictions
        - Interface plus intuitive
        - Nouvelles statistiques
        
        Restez connecté pour plus d'actualités !
        """
        
    def send_newsletter(self, user_email: str, content: str):
        """Envoie la newsletter à un utilisateur."""
        # TODO: Implémenter l'envoi de newsletter
        pass 