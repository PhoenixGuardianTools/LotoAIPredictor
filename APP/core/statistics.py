import pandas as pd
import numpy as np
import math
import ephem  # Analyse des cycles lunaires
from collections import Counter
from datetime import datetime
from sklearn.neural_network import MLPRegressor

def get_frequent_numbers(history_df, game_config):
    """Retourne les numéros les plus fréquents selon l'historique des tirages."""
    num_counts = Counter(num for draw in history_df['numbers'] for num in draw)
    star_counts = Counter(star for draw in history_df.get('stars', []) for star in draw)

    num_freq = {num: num_counts[num] / len(history_df) for num in game_config['pool']}
    star_freq = {star: star_counts[star] / len(history_df) for star in game_config['stars_pool']}

    return num_freq, star_freq

def detect_repeating_patterns(history_df, game_config):
    """Identifie les numéros qui apparaissent fréquemment ensemble."""
    patterns = Counter(tuple(sorted(draw)) for draw in history_df['numbers'])
    return set(num for draw, count in patterns.items() if count > 5 for num in draw)  

def apply_lunar_cycle_weight(num_freq, draw_date):
    """Ajuste les fréquences des numéros en fonction des phases lunaires."""
    moon_phase = ephem.Moon(draw_date).phase
    adjusted_freq = {num: freq * (1 + math.sin(math.radians(moon_phase))) for num, freq in num_freq.items()}
    return adjusted_freq

def detect_positive_sequences(history_df, game_config):
    """Détecte les séquences de numéros qui semblent statistiquement favorables."""
    bias_map = {num: np.exp(history_df['numbers'].apply(lambda x: num in x).sum() / len(history_df)) for num in game_config['pool']}
    return bias_map

def detect_fractal_patterns(history_df, game_config):
    """Identifie des cycles récurrents basés sur des modèles fractals."""
    fractal_map = {num: (math.cos(num * np.pi / 180) + 1) for num in game_config['pool']}
    return fractal_map

def game_theory_analysis(history_df, game_config):
    """Applique des principes de la théorie des jeux pour ajuster les poids des numéros."""
    game_theory_weights = {num: 1 + (history_df['numbers'].apply(lambda x: num in x).sum() % 3) for num in game_config['pool']}
    return game_theory_weights

def evaluate_periodic_trends(history_df, game_config):
    """Analyse les tendances périodiques des tirages et ajuste les probabilités en conséquence."""
    history_df['week'] = history_df['date'].dt.week
    trend_map = {num: 1 + (history_df.groupby('week')['numbers'].apply(lambda x: sum(num in draw for draw in x)).mean()) for num in game_config['pool']}
    return trend_map

def bayesian_adjustment(num_freq, history_df):
    """Ajoute un ajustement bayésien basé sur l'évolution des fréquences."""
    priors = {num: 1 / len(num_freq) for num in num_freq}
    for num in num_freq.keys():
        likelihood = history_df['numbers'].apply(lambda x: num in x).sum() / len(history_df)
        num_freq[num] = priors[num] * likelihood
    return num_freq

def markov_trend_prediction(history_df, game_config):
    """Utilise une chaîne de Markov pour prédire les tendances des numéros."""
    transition_matrix = {num: Counter() for num in game_config['pool']}
    for draw in history_df['numbers']:
        for i in range(len(draw) - 1):
            transition_matrix[draw[i]][draw[i + 1]] += 1

    trend_map = {num: max(transition_matrix[num], key=transition_matrix[num].get, default=num) for num in game_config['pool']}
    return trend_map

def neural_network_weighting(history_df, game_config):
    """Utilise un réseau neuronal simple pour optimiser la pondération des numéros."""
    X = np.array([list(map(int, draw)) for draw in history_df['numbers']])
    y = np.array([sum(draw) for draw in history_df['numbers']])  

    model = M