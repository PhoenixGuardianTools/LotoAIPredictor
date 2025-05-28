import random
import numpy as np

# Supposons que les fonctions suivantes soient définies dans core.statistics
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
    neural_network_weighting,
    detect_anomalies,
    optimize_loto_weights,
    analyze_standard_deviation,
    adaptive_probability_adjustment,
    evolutionary_algorithm_tuning,
    monte_carlo_simulation,
    cluster_number_selection,
    detect_long_term_cycles
)

def generate_model_h_optimized_grid(game_config, history_df, draw_date=None):
    """Génère une grille optimisée adaptée à chaque jeu."""
    # Étapes analytiques communes
    frequent_nums, frequent_stars = get_frequent_numbers(history_df, game_config)
    pattern_nums = detect_repeating_patterns(history_df, game_config)
    adjusted_freq = apply_lunar_cycle_weight(frequent_nums, draw_date)
    positive_bias = detect_positive_sequences(history_df, game_config)

    # Pondérations avancées
    fractal_bonus = detect_fractal_patterns(history_df, game_config)
    game_theory_weights = game_theory_analysis(history_df, game_config)
    period_trends = evaluate_periodic_trends(history_df, game_config)
    bayesian_weights = bayesian_adjustment(adjusted_freq, history_df)
    markov_predictions = markov_trend_prediction(history_df, game_config)
    neural_weights = neural_network_weighting(history_df, game_config)
    anomaly_correction = detect_anomalies(history_df, game_config)
    loto_adjustments = optimize_loto_weights(history_df, game_config)
    std_dev_analysis = analyze_standard_deviation(history_df, game_config)
    probability_adjustment = adaptive_probability_adjustment(history_df, game_config)
    evolutionary_tuning = evolutionary_algorithm_tuning(history_df, game_config)
    monte_carlo_results = monte_carlo_simulation(history_df, game_config)
    clustered_numbers = cluster_number_selection(history_df, game_config)
    long_term_cycles = detect_long_term_cycles(history_df)

    def smart_draw(pool, *weight_maps, count):
        weights = [np.prod([wm.get(n, 1) for wm in weight_maps]) for n in pool]
        weights = np.array(weights) / np.sum(weights)
        return sorted(random.choices(pool, weights=weights, k=count))

    # Numéros principaux
    nums = smart_draw(
        range(1, game_config['pool'] + 1),
        adjusted_freq, pattern_nums, positive_bias, fractal_bonus,
        game_theory_weights, period_trends, bayesian_weights, markov_predictions,
        neural_weights, anomaly_correction, loto_adjustments, std_dev_analysis,
        probability_adjustment, evolutionary_tuning, monte_carlo_results,
        clustered_numbers, long_term_cycles,
        count=game_config['numbers']
    )

    # Étoiles / jokers / complémentaires (si présents)
    stars = []
    if game_config.get('stars', 0) > 0:
        stars = smart_draw(
            range(1, game_config['starPool'] + 1),
            frequent_stars,
            count=game_config['stars']
        )

    return {
        'numbers': nums,
        'stars': stars
    }
