import random
import numpy as np
from core.statistics import (
    get_frequent_numbers,
    detect_repeating_patterns,
    apply_lunar_cycle_weight,
    detect_positive_sequences,
    detect_fractal_patterns,
    game_theory_analysis,
    evaluate_periodic_trends,
    bayesian_adjustment,
    markov_trend_prediction,
    neural_network_weighting
)

def generate_model_d_grid(game_config, history_df, draw_date=None):
    # 1. Enrichissement des données historiques
    frequent_nums, frequent_stars = get_frequent_numbers(history_df, game_config)
    pattern_nums = detect_repeating_patterns(history_df, game_config)
    adjusted_freq = apply_lunar_cycle_weight(frequent_nums, draw_date)
    positive_bias = detect_positive_sequences(history_df, game_config)
    
    # 2. Ajout des nouvelles analyses avancées
    fractal_bonus = detect_fractal_patterns(history_df, game_config)
    game_theory_weights = game_theory_analysis(history_df, game_config)
    period_trends = evaluate_periodic_trends(history_df, game_config)
    bayesian_weights = bayesian_adjustment(adjusted_freq, history_df)
    markov_predictions = markov_trend_prediction(history_df, game_config)
    neural_weights = neural_network_weighting(history_df, game_config)

    def smart_draw(pool, freq_map, pattern_bonus, bias_map, fractal_map, theory_map, period_map, bayes_map, markov_map, nn_map, count):
        weights = []
        for n in pool:
            freq = freq_map.get(n, 1)
            bias = bias_map.get(n, 1)
            fractal = fractal_map.get(n, 1)
            theory = theory_map.get(n, 1)
            period = period_map.get(n, 1)
            bayesian = bayes_map.get(n, 1)
            markov = markov_map.get(n, 1)
            neural = nn_map.get(n, 1)
            bonus = 2 if n in pattern_bonus else 1
            
            # Pondération adaptative et prédictive
            weight = freq * bias * bonus * fractal * theory * period * bayesian * markov * neural
            weights.append(weight)
        
        # Normalisation des poids
        weights = np.array(weights) / np.sum(weights)
        
        return sorted(random.choices(pool, weights=weights, k=count))

    # 3. Application du tirage optimisé
    nums = smart_draw(game_config['pool'], adjusted_freq, pattern_nums, positive_bias, fractal_bonus, game_theory_weights, period_trends, bayesian_weights, markov_predictions, neural_weights, game_config['numbers'])
    stars = smart_draw(game_config['stars_pool'], frequent_stars, set(), {}, {}, {}, {}, {}, {}, {}, game_config['stars']) if game_config['stars'] > 0 else []

    return {
        'numbers': nums,
        'stars': stars
    }
