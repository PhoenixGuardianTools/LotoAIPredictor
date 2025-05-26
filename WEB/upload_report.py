import requests
import json
from pathlib import Path
import os
from datetime import datetime

def upload_to_web(report, report_type):
    """
    Upload un rapport vers le site web.
    
    Args:
        report (dict): Rapport à uploader
        report_type (str): Type de rapport ('daily', 'weekly', 'monthly')
    """
    # Configuration
    api_url = os.getenv('WEB_API_URL', 'http://localhost:8000/api')
    api_key = os.getenv('WEB_API_KEY', '')
    
    if not api_url or not api_key:
        print("⚠️ Configuration API manquante pour l'upload web")
        return
    
    # Préparation des données
    data = {
        'type': report_type,
        'game': report['jeu'],
        'date': report.get('date', report.get('mois', datetime.now().strftime("%Y-%m-%d"))),
        'content': report,
        'visualizations': get_visualization_paths(report, report_type)
    }
    
    # Headers
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
    try:
        # Upload du rapport
        response = requests.post(
            f"{api_url}/reports",
            json=data,
            headers=headers
        )
        
        if response.status_code == 200:
            print(f"✅ Rapport {report_type} uploadé avec succès pour {report['jeu']}")
        else:
            print(f"❌ Erreur lors de l'upload du rapport: {response.status_code}")
            print(f"Message: {response.text}")
    
    except Exception as e:
        print(f"❌ Erreur lors de l'upload du rapport: {str(e)}")

def get_visualization_paths(report, report_type):
    """
    Récupère les chemins des visualisations pour un rapport.
    
    Args:
        report (dict): Rapport
        report_type (str): Type de rapport
    
    Returns:
        dict: Chemins des visualisations
    """
    base_filename = f"{report['jeu']}_{report['date'] if 'date' in report else report['mois']}"
    vis_dir = Path("reports/visualizations")
    
    visualizations = {
        'gains': str(vis_dir / f"{base_filename}_gains.png"),
        'frequence': str(vis_dir / f"{base_filename}_frequence.png"),
        'patterns': str(vis_dir / f"{base_filename}_patterns.png"),
        'distribution_gains': str(vis_dir / f"{base_filename}_distribution_gains.png"),
        'dashboard': str(vis_dir / f"{base_filename}_dashboard.html")
    }
    
    # Ajouter le graphique de performance pour les rapports mensuels
    if report_type == 'monthly':
        visualizations['performance'] = str(vis_dir / f"{base_filename}_performance.png")
    
    return visualizations 