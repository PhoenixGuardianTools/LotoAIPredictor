import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from pathlib import Path
import json
from datetime import datetime

def visualize_report(report, report_type):
    """
    Crée des visualisations pour un rapport.
    
    Args:
        report (dict): Rapport à visualiser
        report_type (str): Type de rapport ('daily', 'weekly', 'monthly')
    """
    # Créer le répertoire de sortie
    output_dir = Path("reports/visualizations")
    output_dir.mkdir(exist_ok=True)
    
    # Nom de base pour les fichiers
    base_filename = f"{report['jeu']}_{report['date'] if 'date' in report else report['mois']}"
    
    # 1. Évolution des gains
    if 'tendances' in report and 'evolution_gains' in report['tendances']:
        plt.figure(figsize=(12, 6))
        gains = report['tendances']['evolution_gains']
        plt.plot(range(len(gains)), gains, marker='o')
        plt.title(f"Évolution des gains - {report['jeu']}")
        plt.xlabel("Tirage")
        plt.ylabel("Gains (€)")
        plt.grid(True)
        plt.savefig(output_dir / f"{base_filename}_gains.png")
        plt.close()
    
    # 2. Fréquence des numéros
    if 'tendances' in report and 'frequence_numeros' in report['tendances']:
        plt.figure(figsize=(15, 8))
        freq = report['tendances']['frequence_numeros']
        numbers = list(freq.keys())
        frequencies = list(freq.values())
        
        # Trier par fréquence
        sorted_indices = sorted(range(len(frequencies)), key=lambda i: frequencies[i], reverse=True)
        numbers = [numbers[i] for i in sorted_indices]
        frequencies = [frequencies[i] for i in sorted_indices]
        
        # Créer le graphique à barres
        bars = plt.bar(range(len(numbers)), frequencies)
        plt.title(f"Fréquence des numéros - {report['jeu']}")
        plt.xlabel("Numéro")
        plt.ylabel("Fréquence")
        plt.xticks(range(len(numbers)), numbers, rotation=45)
        
        # Ajouter les valeurs au-dessus des barres
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig(output_dir / f"{base_filename}_frequence.png")
        plt.close()
    
    # 3. Heatmap des patterns
    if 'tendances' in report and 'patterns_detectes' in report['tendances']:
        patterns = report['tendances']['patterns_detectes']
        if 'consecutive' in patterns and patterns['consecutive']:
            # Créer une matrice de co-occurrence
            max_num = max(max(pair) for pair in patterns['consecutive'])
            matrix = pd.DataFrame(0, index=range(1, max_num + 1), columns=range(1, max_num + 1))
            
            for pair in patterns['consecutive']:
                matrix.loc[pair[0], pair[1]] += 1
                matrix.loc[pair[1], pair[0]] += 1
            
            plt.figure(figsize=(12, 10))
            sns.heatmap(matrix, annot=True, cmap='YlOrRd', fmt='d')
            plt.title(f"Patterns de numéros consécutifs - {report['jeu']}")
            plt.xlabel("Numéro")
            plt.ylabel("Numéro")
            plt.tight_layout()
            plt.savefig(output_dir / f"{base_filename}_patterns.png")
            plt.close()
    
    # 4. Distribution des gains
    if 'statistiques' in report:
        plt.figure(figsize=(10, 6))
        gains = [report['statistiques']['gains_totaux']]
        plt.hist(gains, bins=20, alpha=0.7, color='skyblue')
        plt.title(f"Distribution des gains - {report['jeu']}")
        plt.xlabel("Gains (€)")
        plt.ylabel("Fréquence")
        plt.grid(True, alpha=0.3)
        plt.savefig(output_dir / f"{base_filename}_distribution_gains.png")
        plt.close()
    
    # 5. Graphique de performance (pour les rapports mensuels)
    if 'analyse_performance' in report:
        perf = report['analyse_performance']
        metrics = ['ROI', 'Tendance']
        values = [perf['roi'], 1 if perf['tendance'] == 'positive' else -1]
        
        plt.figure(figsize=(8, 6))
        bars = plt.bar(metrics, values)
        plt.title(f"Performance - {report['jeu']}")
        plt.ylabel("Valeur")
        
        # Colorer les barres en fonction de la valeur
        for bar, value in zip(bars, values):
            if value > 0:
                bar.set_color('green')
            else:
                bar.set_color('red')
        
        plt.grid(True, alpha=0.3)
        plt.savefig(output_dir / f"{base_filename}_performance.png")
        plt.close()
    
    # 6. Créer un dashboard HTML
    create_html_dashboard(report, report_type, output_dir / f"{base_filename}_dashboard.html")

def create_html_dashboard(report, report_type, output_path):
    """
    Crée un dashboard HTML pour visualiser tous les graphiques.
    
    Args:
        report (dict): Rapport à visualiser
        report_type (str): Type de rapport
        output_path (Path): Chemin de sortie du fichier HTML
    """
    base_filename = output_path.stem.replace('_dashboard', '')
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dashboard - {report['jeu']} - {report_type}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .header {{ text-align: center; margin-bottom: 30px; }}
            .grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }}
            .card {{ border: 1px solid #ddd; padding: 15px; border-radius: 5px; }}
            .card img {{ width: 100%; height: auto; }}
            .card h3 {{ margin-top: 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Dashboard {report_type.title()} - {report['jeu']}</h1>
                <p>Généré le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            <div class="grid">
                <div class="card">
                    <h3>Évolution des gains</h3>
                    <img src="{base_filename}_gains.png" alt="Évolution des gains">
                </div>
                <div class="card">
                    <h3>Fréquence des numéros</h3>
                    <img src="{base_filename}_frequence.png" alt="Fréquence des numéros">
                </div>
                <div class="card">
                    <h3>Patterns de numéros</h3>
                    <img src="{base_filename}_patterns.png" alt="Patterns de numéros">
                </div>
                <div class="card">
                    <h3>Distribution des gains</h3>
                    <img src="{base_filename}_distribution_gains.png" alt="Distribution des gains">
                </div>
    """
    
    if 'analyse_performance' in report:
        html_content += f"""
                <div class="card">
                    <h3>Performance</h3>
                    <img src="{base_filename}_performance.png" alt="Performance">
                </div>
        """
    
    html_content += """
            </div>
        </div>
    </body>
    </html>
    """
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content) 