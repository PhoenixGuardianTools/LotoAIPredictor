import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict
import openai
from core.mailer import send_email

class NewsletterManager:
    def __init__(self):
        self.templates_path = Path("PROMOTIONS/newsletter_templates.json")
        self.history_path = Path("PROMOTIONS/newsletter_history.json")
        self.openai_key = "..."  # À configurer
        
        openai.api_key = self.openai_key
        
    def _load_templates(self) -> Dict:
        """Charge les templates de newsletter."""
        if self.templates_path.exists():
            with open(self.templates_path, 'r') as f:
                return json.load(f)
        return {
            "templates": [
                {
                    "name": "Mise à jour",
                    "prompt": "Génère une newsletter amusante pour annoncer une mise à jour",
                    "style": "technique"
                },
                {
                    "name": "Promotion",
                    "prompt": "Génère une newsletter promotionnelle engageante",
                    "style": "commercial"
                },
                {
                    "name": "Événement",
                    "prompt": "Génère une newsletter pour un événement spécial",
                    "style": "festif"
                }
            ]
        }
        
    def _load_history(self) -> Dict:
        """Charge l'historique des newsletters."""
        if self.history_path.exists():
            with open(self.history_path, 'r') as f:
                return json.load(f)
        return {"newsletters": []}
        
    def _save_history(self, newsletter: Dict):
        """Sauvegarde une newsletter dans l'historique."""
        history = self._load_history()
        history["newsletters"].append({
            **newsletter,
            "sent_at": datetime.now().isoformat()
        })
        with open(self.history_path, 'w') as f:
            json.dump(history, f, indent=2)
            
    def generate_newsletter(self, template_name: str, context: Dict) -> str:
        """Génère une newsletter avec l'IA."""
        templates = self._load_templates()
        template = next((t for t in templates["templates"] if t["name"] == template_name), None)
        
        if not template:
            raise ValueError(f"Template {template_name} non trouvé")
            
        # Construction du prompt pour l'IA
        prompt = f"""
        Style: {template['style']}
        Contexte: {json.dumps(context, indent=2)}
        
        Génère une newsletter amusante et engageante avec:
        - Un titre accrocheur
        - Une introduction captivante
        - Le contenu principal
        - Un appel à l'action
        - Une signature
        
        Format: HTML
        """
        
        # Génération avec GPT-4
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Tu es un expert en marketing et copywriting."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        return response.choices[0].message.content
        
    def send_newsletter(self, subject: str, content: str, recipients: List[str], is_test: bool = False):
        """Envoie la newsletter aux destinataires."""
        if is_test:
            # Envoi de test à un seul destinataire
            send_email(subject, content, recipients[0])
        else:
            # Envoi en masse
            for recipient in recipients:
                send_email(subject, content, recipient)
                
        # Sauvegarde dans l'historique
        self._save_history({
            "subject": subject,
            "content": content,
            "recipients": recipients,
            "is_test": is_test
        })
        
    def get_newsletter_stats(self) -> Dict:
        """Récupère les statistiques des newsletters."""
        history = self._load_history()
        total_sent = len(history["newsletters"])
        total_recipients = sum(len(n["recipients"]) for n in history["newsletters"])
        
        return {
            "total_newsletters": total_sent,
            "total_recipients": total_recipients,
            "last_sent": history["newsletters"][-1]["sent_at"] if history["newsletters"] else None
        } 