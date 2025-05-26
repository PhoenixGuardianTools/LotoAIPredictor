import sys
import os
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Ajouter le répertoire parent au PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from core.export import export_to_excel, export_to_pdf

def create_sample_report():
    """Crée un exemple de rapport avec toutes les nouvelles fonctionnalités."""
    # Date du prochain tirage
    next_draw = datetime.now() + timedelta(days=2)
    
    # Créer le rapport
    report = {
        'jeu': 'Loto',
        'date': next_draw.strftime('%Y-%m-%d'),
        'jour_tirage': 'Mardi',
        'cagnotte': 13000000.00,  # 13 millions d'euros
        'gains_bruts': 2500.00,
        'cout_investi': 1000.00,
        'gain_net': 1500.00,
        'gain_net_cumule': 3500.00,
        'ratio_gain': 1.5,  # 150% de retour sur investissement
        'indice_confiance_global': 0.85,  # Sur une échelle de 0 à 1
        
        'predictions': [
            {
                'numbers': [7, 13, 24, 35, 42],
                'special': [1, 10],
                'score': 0.92,
                'indice_confiance': 0.95,
                'gain_estime': 5000.00,
                'jackpot_predit': True
            },
            {
                'numbers': [3, 11, 22, 33, 45],
                'special': [2, 8],
                'score': 0.88,
                'indice_confiance': 0.82,
                'gain_estime': 2500.00,
                'jackpot_predit': False
            },
            {
                'numbers': [5, 15, 25, 35, 45],
                'special': [3, 9],
                'score': 0.85,
                'indice_confiance': 0.78,
                'gain_estime': 1800.00,
                'jackpot_predit': False
            }
        ],
        
        'gains_predits': {
            'rangs': ['Rang 1', 'Rang 2', 'Rang 3', 'Rang 4', 'Rang 5'],
            'gains': [13000000.00, 100000.00, 5000.00, 500.00, 50.00],
            'probabilites': [0.0000001, 0.000001, 0.0001, 0.001, 0.01]
        },
        
        'historique': [
            {'date': '2024-03-01', 'gain': 1000.00},
            {'date': '2024-03-08', 'gain': 500.00},
            {'date': '2024-03-15', 'gain': 2000.00},
            {'date': '2024-03-22', 'gain': 1500.00},
            {'date': '2024-03-29', 'gain': 2500.00}
        ]
    }
    
    return report

def main():
    # Créer le rapport
    report = create_sample_report()
    
    # Exporter en Excel
    excel_path = export_to_excel(report, 'daily')
    print(f"Rapport Excel exporté : {excel_path}")
    
    # Exporter en PDF
    pdf_path = export_to_pdf(report, 'daily')
    print(f"Rapport PDF exporté : {pdf_path}")

if __name__ == "__main__":
    main() 