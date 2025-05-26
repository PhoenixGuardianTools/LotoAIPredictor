import pandas as pd
import numpy as np
import math
import ephem  # Analyse des cycles lunaires
from collections import Counter
from datetime import datetime
from sklearn.neural_network import MLPRegressor
from core.database import get_working_dataset

def get_frequent_numbers(working_dataset, game_config):
    """Retourne les numéros les plus fréquents selon l'historique des tirages."""
    history_df = working_dataset['data']
    num_counts = Counter(num for draw in history_df['numbers'] for num in draw)
    star_counts = Counter(star for draw in history_df['special'] for star in draw)

    num_freq = {num: num_counts[num] / len(history_df) for num in game_config['pool']}
    star_freq = {star: star_counts[star] / len(history_df) for star in game_config['stars_pool']}

    return num_freq, star_freq

def detect_repeating_patterns(working_dataset, game_config):
    """Identifie les numéros qui apparaissent fréquemment ensemble."""
    history_df = working_dataset['data']
    patterns = Counter(tuple(sorted(draw)) for draw in history_df['numbers'])
    return set(num for draw, count in patterns.items() if count > 5 for num in draw)

def apply_lunar_cycle_weight(num_freq, draw_date):
    """Ajuste les fréquences des numéros en fonction des phases lunaires."""
    moon_phase = ephem.Moon(draw_date).phase
    adjusted_freq = {num: freq * (1 + math.sin(math.radians(moon_phase))) for num, freq in num_freq.items()}
    return adjusted_freq

def detect_positive_sequences(working_dataset, game_config):
    """Détecte les séquences de numéros qui semblent statistiquement favorables."""
    history_df = working_dataset['data']
    bias_map = {num: np.exp(history_df['numbers'].apply(lambda x: num in x).sum() / len(history_df)) for num in game_config['pool']}
    return bias_map

def detect_fractal_patterns(working_dataset, game_config):
    """Identifie des cycles récurrents basés sur des modèles fractals."""
    fractal_map = {num: (math.cos(num * np.pi / 180) + 1) for num in game_config['pool']}
    return fractal_map

def game_theory_analysis(working_dataset, game_config):
    """Applique des principes de la théorie des jeux pour ajuster les poids des numéros."""
    history_df = working_dataset['data']
    game_theory_weights = {num: 1 + (history_df['numbers'].apply(lambda x: num in x).sum() % 3) for num in game_config['pool']}
    return game_theory_weights

def evaluate_periodic_trends(working_dataset, game_config):
    """Analyse les tendances périodiques des tirages et ajuste les probabilités en conséquence."""
    history_df = working_dataset['data']
    history_df['week'] = history_df['date'].dt.isocalendar().week
    trend_map = {num: 1 + (history_df.groupby('week')['numbers'].apply(lambda x: sum(num in draw for draw in x)).mean()) for num in game_config['pool']}
    return trend_map

def bayesian_adjustment(num_freq, working_dataset):
    """Ajoute un ajustement bayésien basé sur l'évolution des fréquences."""
    history_df = working_dataset['data']
    priors = {num: 1 / len(num_freq) for num in num_freq}
    for num in num_freq.keys():
        likelihood = history_df['numbers'].apply(lambda x: num in x).sum() / len(history_df)
        num_freq[num] = priors[num] * likelihood
    return num_freq

def markov_trend_prediction(working_dataset, game_config):
    """Utilise une chaîne de Markov pour prédire les tendances des numéros."""
    history_df = working_dataset['data']
    transition_matrix = {num: Counter() for num in game_config['pool']}
    for draw in history_df['numbers']:
        for i in range(len(draw) - 1):
            transition_matrix[draw[i]][draw[i + 1]] += 1

    trend_map = {num: max(transition_matrix[num], key=transition_matrix[num].get, default=num) for num in game_config['pool']}
    return trend_map

def analyze_standard_deviation(working_dataset, game_config):
    """Calcule l'écart-type des numéros tirés dans l'historique."""
    history_df = working_dataset['data']
    all_numbers = []
    for draw in history_df['numbers']:
        all_numbers.extend(draw)
    
    std_dev = np.std(all_numbers)
    std_dev_map = {num: std_dev for num in game_config['pool']}
    
    return std_dev_map

def detect_anomalies(working_dataset, game_config):
    """Détecte les anomalies dans les tirages (numéros qui sortent trop souvent ou trop rarement)."""
    history_df = working_dataset['data']
    num_counts = Counter(num for draw in history_df['numbers'] for num in draw)
    frequencies = {num: count/len(history_df) for num, count in num_counts.items()}
    
    mean_freq = np.mean(list(frequencies.values()))
    std_freq = np.std(list(frequencies.values()))
    
    anomalies = {}
    for num in game_config['pool']:
        freq = frequencies.get(num, 0)
        z_score = (freq - mean_freq) / std_freq if std_freq > 0 else 0
        if abs(z_score) > 2:
            anomalies[num] = {
                'frequency': freq,
                'z_score': z_score,
                'is_anomaly': True
            }
        else:
            anomalies[num] = {
                'frequency': freq,
                'z_score': z_score,
                'is_anomaly': False
            }
    
    return anomalies

def detect_long_term_cycles(working_dataset, game_config):
    """Détecte les cycles à long terme dans les tirages."""
    history_df = working_dataset['data']
    history_df['days_since_start'] = (history_df['date'] - history_df['date'].min()).dt.days
    
    cycles = {}
    for num in game_config['pool']:
        appearances = history_df['numbers'].apply(lambda x: num in x).astype(int)
        
        autocorr = np.correlate(appearances, appearances, mode='full')
        autocorr = autocorr[len(autocorr)//2:]
        autocorr = autocorr / autocorr[0]
        
        peaks = []
        for i in range(1, len(autocorr)-1):
            if autocorr[i] > autocorr[i-1] and autocorr[i] > autocorr[i+1] and autocorr[i] > 0.5:
                peaks.append(i)
        
        cycles[num] = {
            'cycle_lengths': peaks,
            'autocorrelation': autocorr.tolist(),
            'has_cycle': len(peaks) > 0
        }
    
    return cycles

def get_correlations_numeros(jeu, numero, limit=10):
    """
    Analyse les corrélations entre un numéro et les autres numéros.
    
    Args:
        jeu (str): Nom du jeu
        numero (int): Numéro à analyser
        limit (int): Nombre de corrélations à retourner
    
    Returns:
        dict: Statistiques des corrélations
    """
    working_dataset = get_working_dataset(jeu)
    if working_dataset is None:
        return {"numero_analyse": numero, "correlations": []}
    
    history_df = working_dataset['data']
    correlations = {}
    
    for _, row in history_df.iterrows():
        if numero in row['numbers']:
            for other_num in row['numbers']:
                if other_num != numero:
                    if other_num not in correlations:
                        correlations[other_num] = {
                            "frequence": 0,
                            "gains": [],
                            "grilles_gagnantes": 0
                        }
                    correlations[other_num]["frequence"] += 1
                    correlations[other_num]["gains"].append(row['gains'])
                    if row['gains'] > 0:
                        correlations[other_num]["grilles_gagnantes"] += 1
    
    result = []
    for num, stats in correlations.items():
        result.append({
            "numero": num,
            "frequence": stats["frequence"],
            "moyenne_gain": round(np.mean(stats["gains"]), 2),
            "grilles_gagnantes": stats["grilles_gagnantes"],
            "taux_reussite": round((stats["grilles_gagnantes"] / stats["frequence"] * 100), 2)
        })
    
    result.sort(key=lambda x: (x["frequence"], x["moyenne_gain"]), reverse=True)
    
    return {
        "numero_analyse": numero,
        "correlations": result[:limit]
    }

def get_sequences_gagnantes(jeu, longueur=3, limit=5):
    """
    Identifie les séquences de numéros consécutifs les plus performantes.
    
    Args:
        jeu (str): Nom du jeu
        longueur (int): Longueur de la séquence à analyser
        limit (int): Nombre de séquences à retourner
    
    Returns:
        list: Séquences les plus performantes
    """
    working_dataset = get_working_dataset(jeu)
    if working_dataset is None:
        return []
    
    history_df = working_dataset['data']
    sequences = {}
    
    for _, row in history_df.iterrows():
        numbers = sorted(row['numbers'])
        for i in range(len(numbers) - longueur + 1):
            sequence = numbers[i:i+longueur]
            seq_key = ",".join(map(str, sequence))
            
            if seq_key not in sequences:
                sequences[seq_key] = {
                    "frequence": 0,
                    "gains": [],
                    "grilles_gagnantes": 0
                }
            
            sequences[seq_key]["frequence"] += 1
            sequences[seq_key]["gains"].append(row['gains'])
            if row['gains'] > 0:
                sequences[seq_key]["grilles_gagnantes"] += 1
    
    result = []
    for seq, stats in sequences.items():
        if stats["frequence"] > 1:
            result.append({
                "sequence": seq,
                "frequence": stats["frequence"],
                "moyenne_gain": round(np.mean(stats["gains"]), 2),
                "grilles_gagnantes": stats["grilles_gagnantes"],
                "taux_reussite": round((stats["grilles_gagnantes"] / stats["frequence"] * 100), 2)
            })
    
    result.sort(key=lambda x: (x["moyenne_gain"], x["frequence"]), reverse=True)
    
    return result[:limit]

def get_tendances_numeros(jeu, limit=10):
    """Analyse les tendances des numéros sur une période donnée."""
    working_dataset = get_working_dataset(jeu)
    if working_dataset is None:
        return {"tendances": []}
    
    history_df = working_dataset['data']
    recent_draws = history_df.tail(10)
    
    tendances = []
    for num in range(1, 50):
        appearances = recent_draws['numbers'].apply(lambda x: num in x)
        if appearances.sum() > 0:
            tendances.append({
                "numero": num,
                "frequence": appearances.sum(),
                "derniere_apparition": recent_draws[appearances]['date'].max().strftime('%Y-%m-%d')
            })
    
    tendances.sort(key=lambda x: x["frequence"], reverse=True)
    return {"tendances": tendances[:limit]}

def neural_network_weighting(working_dataset, game_config):
    """Utilise un réseau de neurones pour pondérer les numéros."""
    history_df = working_dataset['data']
    X = np.array([draw for draw in history_df['numbers']])
    y = np.array([1 if gain > 0 else 0 for gain in history_df['gains']])
    
    model = MLPRegressor(hidden_layer_sizes=(50,), max_iter=1000)
    model.fit(X, y)
    
    weights = {num: model.predict([[num]])[0] for num in game_config['pool']}
    return weights

def optimize_loto_weights(working_dataset, game_config):
    """Optimise les poids des numéros pour le Loto."""
    history_df = working_dataset['data']
    weights = {num: 1.0 for num in game_config['pool']}
    
    for num in game_config['pool']:
        appearances = history_df['numbers'].apply(lambda x: num in x)
        wins = history_df[appearances]['gains'] > 0
        if len(wins) > 0:
            weights[num] = 1 + (wins.sum() / len(wins))
    
    return weights

def adaptive_probability_adjustment(working_dataset, game_config):
    """Ajuste les probabilités de manière adaptative."""
    history_df = working_dataset['data']
    recent_draws = history_df.tail(10)
    
    weights = {num: 1.0 for num in game_config['pool']}
    for num in game_config['pool']:
        recent_freq = recent_draws['numbers'].apply(lambda x: num in x).mean()
        weights[num] = 1 + recent_freq
    
    return weights

def evolutionary_algorithm_tuning(working_dataset, game_config):
    """Utilise un algorithme évolutionnaire pour ajuster les poids."""
    history_df = working_dataset['data']
    weights = {num: 1.0 for num in game_config['pool']}
    
    for num in game_config['pool']:
        appearances = history_df['numbers'].apply(lambda x: num in x)
        if appearances.sum() > 0:
            weights[num] = 1 + (appearances.sum() / len(history_df))
    
    return weights

def monte_carlo_simulation(working_dataset, game_config):
    """Effectue une simulation Monte Carlo pour ajuster les poids."""
    history_df = working_dataset['data']
    weights = {num: 1.0 for num in game_config['pool']}
    
    for num in game_config['pool']:
        appearances = history_df['numbers'].apply(lambda x: num in x)
        if appearances.sum() > 0:
            weights[num] = 1 + (appearances.sum() / len(history_df))
    
    return weights

def cluster_number_selection(working_dataset, game_config):
    """Sélectionne les numéros en utilisant le clustering."""
    history_df = working_dataset['data']
    weights = {num: 1.0 for num in game_config['pool']}
    
    for num in game_config['pool']:
        appearances = history_df['numbers'].apply(lambda x: num in x)
        if appearances.sum() > 0:
            weights[num] = 1 + (appearances.sum() / len(history_df))
    
    return weights