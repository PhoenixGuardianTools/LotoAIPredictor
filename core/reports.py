import datetime
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import json
import os
from core.insights import (
    analyze_metadata_insights,
    optimize_predictions,
    generate_daily_report,
    suggest_play_strategy
)
from core.database import get_working_dataset, get_statistiques_grilles
from ui.tabs.ascii_display import display_ascii_report
from ui.tabs.visualization_report import visualize_report
from web.upload_report import upload_to_web

class ReportGenerator:
    def __init__(self):
        self.reports_dir = Path("reports")
        self.reports_dir.mkdir(exist_ok=True)
        
        # Sous-répertoires pour différents types de rapports
        self.daily_dir = self.reports_dir / "daily"
        self.weekly_dir = self.reports_dir / "weekly"
        self.monthly_dir = self.reports_dir / "monthly"
        self.excel_dir = self.reports_dir / "excel"
        
        for directory in [self.daily_dir, self.weekly_dir, self.monthly_dir, self.excel_dir]:
            directory.mkdir(exist_ok=True)
    
    def generate_daily_report(self, jeu):
        """
        Génère un rapport quotidien pour un jeu spécifique.
        
        Args:
            jeu (str): Nom du jeu
        
        Returns:
            dict: Rapport quotidien
        """
        working_dataset = get_working_dataset(jeu)
        if working_dataset is None:
            return None
        
        # Analyse des métadonnées
        insights = analyze_metadata_insights(jeu)
        if not insights:
            return None
        
        # Optimisation des prédictions
        predictions = optimize_predictions(jeu)
        
        # Génération de la stratégie
        strategy = suggest_play_strategy(working_dataset['data'], working_dataset['metadata'])
        
        # Création du rapport
        report = {
            'date': datetime.datetime.now().strftime("%Y-%m-%d"),
            'jeu': jeu,
            'insights': insights,
            'predictions': predictions,
            'strategy': strategy,
            'statistiques': get_statistiques_grilles(jeu)
        }
        
        # Sauvegarde et affichage du rapport
        self._process_report(report, 'daily')
        
        return report
    
    def generate_weekly_report(self, jeu):
        """
        Génère un rapport hebdomadaire pour un jeu spécifique.
        
        Args:
            jeu (str): Nom du jeu
        
        Returns:
            dict: Rapport hebdomadaire
        """
        working_dataset = get_working_dataset(jeu)
        if working_dataset is None:
            return None
        
        # Analyse des 7 derniers jours
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=7)
        
        weekly_data = working_dataset['data'][
            (working_dataset['data']['date'] >= start_date) &
            (working_dataset['data']['date'] <= end_date)
        ]
        
        report = {
            'date_debut': start_date.strftime("%Y-%m-%d"),
            'date_fin': end_date.strftime("%Y-%m-%d"),
            'jeu': jeu,
            'statistiques': {
                'nombre_tirages': len(weekly_data),
                'gains_totaux': weekly_data['gains'].sum(),
                'moyenne_gains': weekly_data['gains'].mean(),
                'meilleur_gain': weekly_data['gains'].max(),
                'grilles_gagnantes': len(weekly_data[weekly_data['gains'] > 0])
            },
            'tendances': self._analyze_weekly_trends(weekly_data),
            'recommandations': self._generate_weekly_recommendations(weekly_data)
        }
        
        # Sauvegarde et affichage du rapport
        self._process_report(report, 'weekly')
        
        return report
    
    def generate_monthly_report(self, jeu):
        """
        Génère un rapport mensuel pour un jeu spécifique.
        
        Args:
            jeu (str): Nom du jeu
        
        Returns:
            dict: Rapport mensuel
        """
        working_dataset = get_working_dataset(jeu)
        if working_dataset is None:
            return None
        
        # Analyse du mois en cours
        now = datetime.datetime.now()
        start_date = datetime.datetime(now.year, now.month, 1)
        
        monthly_data = working_dataset['data'][
            working_dataset['data']['date'] >= start_date
        ]
        
        report = {
            'mois': now.strftime("%B %Y"),
            'jeu': jeu,
            'statistiques': {
                'nombre_tirages': len(monthly_data),
                'gains_totaux': monthly_data['gains'].sum(),
                'moyenne_gains': monthly_data['gains'].mean(),
                'meilleur_gain': monthly_data['gains'].max(),
                'grilles_gagnantes': len(monthly_data[monthly_data['gains'] > 0])
            },
            'analyse_performance': self._analyze_monthly_performance(monthly_data),
            'tendances': self._analyze_monthly_trends(monthly_data),
            'recommandations': self._generate_monthly_recommendations(monthly_data)
        }
        
        # Sauvegarde et affichage du rapport
        self._process_report(report, 'monthly')
        
        return report
    
    def _process_report(self, report, report_type):
        """
        Traite un rapport : sauvegarde, affichage, export et visualisation.
        
        Args:
            report (dict): Rapport à traiter
            report_type (str): Type de rapport ('daily', 'weekly', 'monthly')
        """
        # Sauvegarde JSON
        self._save_report(report, report_type)
        
        # Affichage ASCII
        display_ascii_report(report, report_type)
        
        # Export Excel
        self._export_to_excel(report, report_type)
        
        # Visualisation
        visualize_report(report, report_type)
        
        # Upload vers le site web
        upload_to_web(report, report_type)
    
    def _save_report(self, report, report_type):
        """
        Sauvegarde un rapport dans le répertoire approprié.
        
        Args:
            report (dict): Rapport à sauvegarder
            report_type (str): Type de rapport ('daily', 'weekly', 'monthly')
        """
        # Déterminer le répertoire de destination
        if report_type == 'daily':
            directory = self.daily_dir
        elif report_type == 'weekly':
            directory = self.weekly_dir
        else:
            directory = self.monthly_dir
        
        # Créer le nom du fichier
        filename = f"{report['jeu']}_{report['date'] if 'date' in report else report['mois']}.json"
        
        # Sauvegarder le rapport
        with open(directory / filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=4)
    
    def _export_to_excel(self, report, report_type):
        """
        Exporte un rapport au format Excel.
        
        Args:
            report (dict): Rapport à exporter
            report_type (str): Type de rapport
        """
        # Créer un DataFrame pour chaque section du rapport
        dfs = {}
        
        # Statistiques
        if 'statistiques' in report:
            dfs['Statistiques'] = pd.DataFrame([report['statistiques']])
        
        # Tendances
        if 'tendances' in report:
            for key, value in report['tendances'].items():
                if isinstance(value, dict):
                    dfs[f'Tendances_{key}'] = pd.DataFrame([value])
                elif isinstance(value, list):
                    dfs[f'Tendances_{key}'] = pd.DataFrame(value)
        
        # Prédictions
        if 'predictions' in report:
            dfs['Predictions'] = pd.DataFrame(report['predictions'])
        
        # Recommandations
        if 'recommandations' in report:
            dfs['Recommandations'] = pd.DataFrame({'Recommandation': report['recommandations']})
        
        # Créer le nom du fichier Excel
        filename = f"{report['jeu']}_{report['date'] if 'date' in report else report['mois']}.xlsx"
        excel_path = self.excel_dir / filename
        
        # Exporter vers Excel
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            for sheet_name, df in dfs.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    def _analyze_weekly_trends(self, data):
        """Analyse les tendances hebdomadaires."""
        trends = {
            'evolution_gains': data['gains'].tolist(),
            'frequence_numeros': self._calculate_number_frequency(data),
            'patterns_detectes': self._detect_patterns(data)
        }
        return trends
    
    def _analyze_monthly_trends(self, data):
        """Analyse les tendances mensuelles."""
        trends = {
            'evolution_gains': data['gains'].tolist(),
            'frequence_numeros': self._calculate_number_frequency(data),
            'patterns_detectes': self._detect_patterns(data),
            'cycles': self._analyze_cycles(data)
        }
        return trends
    
    def _calculate_number_frequency(self, data):
        """Calcule la fréquence d'apparition des numéros."""
        all_numbers = []
        for draw in data['numbers']:
            all_numbers.extend(draw)
        return pd.Series(all_numbers).value_counts().to_dict()
    
    def _detect_patterns(self, data):
        """Détecte les patterns dans les tirages."""
        patterns = {
            'consecutive': [],
            'sum_patterns': [],
            'distribution': {}
        }
        
        for draw in data['numbers']:
            # Patterns consécutifs
            sorted_draw = sorted(draw)
            for i in range(len(sorted_draw)-1):
                if sorted_draw[i+1] - sorted_draw[i] == 1:
                    patterns['consecutive'].append((sorted_draw[i], sorted_draw[i+1]))
            
            # Patterns de somme
            total = sum(draw)
            if total not in patterns['sum_patterns']:
                patterns['sum_patterns'].append(total)
        
        return patterns
    
    def _analyze_cycles(self, data):
        """Analyse les cycles dans les tirages."""
        cycles = {
            'weekly': {},
            'monthly': {}
        }
        
        data['weekday'] = data['date'].dt.weekday
        data['month'] = data['date'].dt.month
        
        for num in range(1, 50):  # Ajuster selon le jeu
            if num in data['numbers'].explode().unique():
                # Cycles hebdomadaires
                weekday_counts = data[data['numbers'].apply(lambda x: num in x)].groupby('weekday').size()
                if not weekday_counts.empty:
                    cycles['weekly'][num] = weekday_counts.to_dict()
                
                # Cycles mensuels
                month_counts = data[data['numbers'].apply(lambda x: num in x)].groupby('month').size()
                if not month_counts.empty:
                    cycles['monthly'][num] = month_counts.to_dict()
        
        return cycles
    
    def _generate_weekly_recommendations(self, data):
        """Génère des recommandations basées sur l'analyse hebdomadaire."""
        recommendations = []
        
        # Analyse des gains
        gains_positifs = len(data[data['gains'] > 0])
        taux_gains = (gains_positifs / len(data)) * 100 if len(data) > 0 else 0
        
        if taux_gains > 30:
            recommendations.append("📈 Taux de gains positifs élevé - Stratégie agressive recommandée")
        else:
            recommendations.append("⚠️ Taux de gains positifs faible - Stratégie conservatrice recommandée")
        
        # Analyse des numéros les plus fréquents
        freq = self._calculate_number_frequency(data)
        top_numbers = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:5]
        recommendations.append(f"🎯 Numéros les plus fréquents: {', '.join(map(str, [n for n, _ in top_numbers]))}")
        
        return recommendations
    
    def _generate_monthly_recommendations(self, data):
        """Génère des recommandations basées sur l'analyse mensuelle."""
        recommendations = self._generate_weekly_recommendations(data)
        
        # Ajout d'analyses spécifiques au mois
        cycles = self._analyze_cycles(data)
        
        # Analyse des cycles hebdomadaires
        current_weekday = datetime.datetime.now().weekday()
        weekday_recommendations = []
        for num, weekdays in cycles['weekly'].items():
            if current_weekday in weekdays:
                weekday_recommendations.append(num)
        
        if weekday_recommendations:
            recommendations.append(f"📅 Numéros favorables ce jour: {', '.join(map(str, weekday_recommendations))}")
        
        return recommendations
    
    def _analyze_monthly_performance(self, data):
        """Analyse la performance mensuelle."""
        performance = {
            'roi': (data['gains'].sum() / (len(data) * 2.5)) * 100,  # ROI basé sur un coût de 2.5€ par grille
            'meilleure_periode': data.loc[data['gains'].idxmax()]['date'].strftime("%Y-%m-%d"),
            'pire_periode': data.loc[data['gains'].idxmin()]['date'].strftime("%Y-%m-%d"),
            'tendance': 'positive' if data['gains'].diff().mean() > 0 else 'negative'
        }
        return performance

def generate_all_reports():
    """Génère tous les rapports pour tous les jeux."""
    generator = ReportGenerator()
    
    for jeu in ['EuroDreams', 'Loto', 'Euromillions']:
        # Rapports quotidiens
        generator.generate_daily_report(jeu)
        
        # Rapports hebdomadaires (si c'est le jour approprié)
        if datetime.datetime.now().weekday() == 0:  # Lundi
            generator.generate_weekly_report(jeu)
        
        # Rapports mensuels (si c'est le premier jour du mois)
        if datetime.datetime.now().day == 1:
            generator.generate_monthly_report(jeu) 