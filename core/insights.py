import datetime
import time
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd  # Si tu veux charger l'historique ici
from core.statistics import (
    detect_repeating_patterns,
    apply_lunar_cycle_weight,
    evaluate_periodic_trends,
    analyze_standard_deviation,
    detect_anomalies,
    detect_long_term_cycles,
    get_correlations_numeros,
    get_sequences_gagnantes,
    get_tendances_numeros
)
from core.database import get_working_dataset, get_statistiques_grilles, get_grilles_jouees
from core.models.model_advanced import generate_model_h_optimized_grid
from collections import Counter
import ephem

def generate_insight_report(history_df):
    """Génère un rapport ASCII et une visualisation des tendances chaque jour."""
    now = datetime.datetime.now()
    lunar_effects = apply_lunar_cycle_weight(history_df, now)
    repeating_patterns = detect_repeating_patterns(history_df)
    periodic_trends = evaluate_periodic_trends(history_df)
    anomalies_detected = detect_anomalies(history_df)
    std_dev_analysis = analyze_standard_deviation(history_df)
    long_term_cycles = detect_long_term_cycles(history_df)

    # Rapport ASCII
    report = f"""
    ================================================
                 📊 RAPPORT DES TENDANCES 📊
                  {now.strftime('%d %B %Y')}
    ================================================

    🔍 **Analyse des tendances sur 10 ans**
    - 🔁 Patterns récurrents détectés : {repeating_patterns}
    - 🌙 Effet lunaire sur les jeux : {lunar_effects}
    - 📈 Cycles détectés : {periodic_trends}
    - ⚠️ Anomalies statistiques : {anomalies_detected}
    - 📊 Écart-type sur les tirages : {std_dev_analysis}
    - 🔄 Cycles longs identifiés : {long_term_cycles}

    📌 **Recommandations basées sur l'analyse**
    - Affiner les pondérations basées sur les tendances observées.
    - Ajuster les stratégies de jeu en fonction des cycles récurrents.
    - Optimiser la sélection des numéros en suivant les anomalies détectées.

    🕛 Rapport mis à jour automatiquement chaque jour à minuit !
    ================================================
    """
    print(report)

    # Visualisation graphique des tendances
    fig, ax = plt.subplots(figsize=(10, 5))
    cycle_values = [long_term_cycles.get(num, 0) for num in range(1, 50)]
    ax.bar(range(1, 50), cycle_values, color='steelblue')
    ax.set_title("Fréquence des numéros sur 10 ans")
    ax.set_xlabel("Numéro")
    ax.set_ylabel("Occurrences")
    plt.xticks(range(1, 50, 5))
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.savefig("trend_visualization.png")

    # Sauvegarde ASCII
    with open("daily_insight.txt", "w", encoding="utf-8") as f:
        f.write(report)

def detect_patterns(history_df, game_config):
    """Détecte les motifs complexes dans les tirages (combinaisons, séquences, etc.)."""
    patterns = {
        'consecutive': [],  # Numéros consécutifs
        'sum_patterns': [],  # Sommes caractéristiques
        'distribution': {},  # Distribution des numéros
        'hot_cold': {'hot': [], 'cold': []}  # Numéros chauds/froids
    }
    
    # Analyser les 10 derniers tirages pour les numéros chauds/froids
    recent_draws = history_df.tail(365)
    all_numbers = [num for draw in recent_draws['numbers'] for num in draw]
    number_counts = Counter(all_numbers)
    
    # Déterminer les numéros chauds (apparus plus de 2 fois) et froids (jamais apparus)
    for num in game_config['pool']:
        if number_counts[num] >= 2:
            patterns['hot_cold']['hot'].append(num)
        elif number_counts[num] == 0:
            patterns['hot_cold']['cold'].append(num)
    
    # Analyser les motifs de numéros consécutifs
    for draw in history_df['numbers']:
        sorted_draw = sorted(draw)
        for i in range(len(sorted_draw)-1):
            if sorted_draw[i+1] - sorted_draw[i] == 1:
                patterns['consecutive'].append((sorted_draw[i], sorted_draw[i+1]))
    
    # Analyser les sommes caractéristiques
    for draw in history_df['numbers']:
        total = sum(draw)
        if total not in patterns['sum_patterns']:
            patterns['sum_patterns'].append(total)
    
    # Analyser la distribution des numéros
    for num in game_config['pool']:
        appearances = history_df['numbers'].apply(lambda x: num in x).sum()
        patterns['distribution'][num] = appearances / len(history_df)
    
    return patterns

def detect_cycles(history_df, game_config):
    """Détecte les cycles courts et moyens dans les tirages."""
    cycles = {
        'weekly': {},    # Cycles hebdomadaires
        'monthly': {},   # Cycles mensuels
        'seasonal': {},  # Cycles saisonniers
        'lunar': {}      # Cycles lunaires
    }
    
    # Convertir les dates en datetime si ce n'est pas déjà fait
    if not pd.api.types.is_datetime64_any_dtype(history_df['date']):
        history_df['date'] = pd.to_datetime(history_df['date'])
    
    # Cycles hebdomadaires
    history_df['weekday'] = history_df['date'].dt.weekday
    for num in game_config['pool']:
        weekday_counts = history_df[history_df['numbers'].apply(lambda x: num in x)].groupby('weekday').size()
        if not weekday_counts.empty:
            cycles['weekly'][num] = weekday_counts.to_dict()
    
    # Cycles mensuels
    history_df['month'] = history_df['date'].dt.month
    for num in game_config['pool']:
        month_counts = history_df[history_df['numbers'].apply(lambda x: num in x)].groupby('month').size()
        if not month_counts.empty:
            cycles['monthly'][num] = month_counts.to_dict()
    
    # Cycles saisonniers
    history_df['season'] = history_df['date'].dt.month % 12 // 3 + 1
    for num in game_config['pool']:
        season_counts = history_df[history_df['numbers'].apply(lambda x: num in x)].groupby('season').size()
        if not season_counts.empty:
            cycles['seasonal'][num] = season_counts.to_dict()
    
    # Cycles lunaires
    for num in game_config['pool']:
        lunar_phases = []
        for date in history_df[history_df['numbers'].apply(lambda x: num in x)]['date']:
            moon = ephem.Moon(date)
            lunar_phases.append(moon.phase)
        if lunar_phases:
            cycles['lunar'][num] = {
                'mean_phase': np.mean(lunar_phases),
                'std_phase': np.std(lunar_phases)
            }
    
    return cycles

def suggest_play_strategy(history_df, game_config):
    """Suggère une stratégie de jeu basée sur l'analyse des tendances et des cycles."""
    # Récupérer toutes les analyses
    patterns = detect_patterns(history_df, game_config)
    cycles = detect_cycles(history_df, game_config)
    anomalies = detect_anomalies(history_df, game_config)
    std_dev = analyze_standard_deviation(history_df, game_config)
    
    # Calculer les scores pour chaque numéro
    number_scores = {}
    for num in game_config['pool']:
        score = 0
        
        # Score basé sur les patterns
        if num in patterns['hot_cold']['hot']:
            score += 2
        elif num in patterns['hot_cold']['cold']:
            score += 1
        
        # Score basé sur les cycles
        if num in cycles['weekly']:
            current_weekday = datetime.datetime.now().weekday()
            if current_weekday in cycles['weekly'][num]:
                score += cycles['weekly'][num][current_weekday]
        
        # Score basé sur les anomalies
        if num in anomalies and anomalies[num]['is_anomaly']:
            score += abs(anomalies[num]['z_score'])
        
        # Score basé sur l'écart-type
        if num in std_dev:
            score += std_dev[num]
        
        number_scores[num] = score
    
    # Normaliser les scores
    max_score = max(number_scores.values())
    if max_score > 0:
        number_scores = {num: score/max_score for num, score in number_scores.items()}
    
    # Générer la stratégie
    strategy = {
        'recommended_numbers': sorted(number_scores.items(), key=lambda x: x[1], reverse=True)[:5],
        'confidence_score': np.mean(list(number_scores.values())),
        'analysis_summary': {
            'hot_numbers': patterns['hot_cold']['hot'],
            'cold_numbers': patterns['hot_cold']['cold'],
            'consecutive_pairs': patterns['consecutive'],
            'current_cycles': {k: v for k, v in cycles['weekly'].items() if datetime.datetime.now().weekday() in v}
        }
    }
    
    return strategy

def analyze_metadata_insights(jeu):
    """
    Analyse les métadonnées pour extraire des insights pertinents.
    
    Args:
        jeu (str): Nom du jeu à analyser
    
    Returns:
        dict: Insights et recommandations basés sur les métadonnées
    """
    working_dataset = get_working_dataset(jeu)
    if working_dataset is None:
        return None
    
    metadata = working_dataset['metadata']
    data = working_dataset['data']
    
    # Analyse de la période
    total_days = (metadata['date_fin'] - metadata['date_debut']).days
    draws_per_year = metadata['nombre_tirages'] / (total_days / 365)
    
    # Analyse des gains
    gains_stats = {
        'total_gains': data['gains'].sum(),
        'moyenne_gains': data['gains'].mean(),
        'max_gains': data['gains'].max(),
        'gains_positifs': len(data[data['gains'] > 0]),
        'taux_gains_positifs': len(data[data['gains'] > 0]) / len(data) * 100
    }
    
    # Analyse des rangs
    ranks_stats = data['ranks'].value_counts().to_dict()
    
    # Analyse des tendances temporelles
    data['month'] = data['date'].dt.month
    monthly_stats = data.groupby('month')['gains'].agg(['mean', 'sum', 'count']).to_dict()
    
    # Analyse des corrélations avec les gains
    correlations = {}
    for num in range(1, 50):  # Ajuster selon le jeu
        if num in data['numbers'].explode().unique():
            corr = data[data['numbers'].apply(lambda x: num in x)]['gains'].mean()
            correlations[num] = corr
    
    return {
        'metadata': metadata,
        'gains_stats': gains_stats,
        'ranks_stats': ranks_stats,
        'monthly_stats': monthly_stats,
        'correlations': correlations,
        'draws_per_year': draws_per_year
    }

def optimize_predictions(jeu, max_grilles=3):
    """
    Optimise les prédictions pour maximiser le gain net avec un nombre limité de grilles.
    
    Args:
        jeu (str): Nom du jeu
        max_grilles (int): Nombre maximum de grilles à générer
    
    Returns:
        list: Liste des grilles optimisées avec leurs statistiques
    """
    working_dataset = get_working_dataset(jeu)
    if working_dataset is None:
        return []
    
    # Analyse des tendances
    tendances = get_tendances_numeros(jeu)
    correlations = get_correlations_numeros(jeu, tendances['numeros_gagnants'][0]['numero'])
    sequences = get_sequences_gagnantes(jeu)
    
    # Génération des grilles optimisées
    grilles = []
    for _ in range(max_grilles):
        grille = generate_model_h_optimized_grid(
            game_config=working_dataset['metadata'],
            history_df=working_dataset['data'],
            draw_date=datetime.datetime.now()
        )
        
        # Calcul des statistiques pour cette grille
        stats = {
            'numbers': grille['numbers'],
            'special': grille['special'],
            'score_tendance': sum(1 for n in grille['numbers'] if n in [t['numero'] for t in tendances['numeros_gagnants']]),
            'score_correlation': sum(1 for n in grille['numbers'] if n in [c['numero'] for c in correlations['correlations']]),
            'score_sequence': sum(1 for s in sequences if all(n in grille['numbers'] for n in map(int, s['sequence'].split(','))))
        }
        
        grilles.append(stats)
    
    return grilles

def check_draw_results():
    """
    Vérifie les résultats des tirages à minuit.
    """
    now = datetime.datetime.now()
    if now.hour == 0:  # Minuit
        for jeu in ['EuroDreams', 'Loto', 'Euromillions']:
            # Récupération des derniers résultats
            # Mise à jour de la base de données
            # Mise à jour des exports
            # Mise à jour des statistiques
            # Mise à jour des prédictions
            pass

def display_morning_predictions():
    """
    Affiche les prédictions et demande au joueur s'il veut jouer.
    """
    now = datetime.datetime.now()
    if now.hour == 9:  # 9h du matin
        for jeu in ['EuroDreams', 'Loto', 'Euromillions']:
            # Optimisation des prédictions
            predictions = optimize_predictions(jeu)
            
            print(f"\n=== PRÉDICTIONS DU JOUR - {jeu} ===")
            print("\n🎯 Grilles recommandées:")
            for i, pred in enumerate(predictions, 1):
                print(f"  Grille {i}: {pred['numbers']} + {pred['special']}")
                print(f"    Score: {pred['score_tendance'] + pred['score_correlation'] + pred['score_sequence']}")
        
        # Demande au joueur
        print("\nVoulez-vous jouer ces grilles ? (O/N)")
        # Logique de réponse et de jeu

def store_custom_grid(jeu, grille):
    """
    Stocke une grille personnalisée du joueur.
    
    Args:
        jeu (str): Nom du jeu
        grille (dict): Grille à stocker
    """
    # Stockage dans la base de données
    # Mise à jour des statistiques
    # Alimentation du modèle si gain
    pass

def collect_anonymous_feedback():
    """
    Collecte les feedbacks anonymes des clients.
    """
    # Récupération des données anonymes
    # Stockage dans la base de données
    # Mise à jour des statistiques
    pass

# Si tu veux garder la génération automatique, il faut charger l'historique ici :
# Exemple :
# history_df = pd.read_csv("data/history.csv")
# while True:
#     now = datetime.datetime.now()
#     if now.hour == 0 and now.minute == 0:
#         generate_insight_report(history_df)
#         time.sleep(60)
#     else:
#         time.sleep(10)
