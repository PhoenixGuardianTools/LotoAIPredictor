import pandas as pd
import numpy as np
from datetime import datetime
import logging
from typing import Dict, List, Union, Any, Optional
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
    detect_long_term_cycles,
    wavelet_decomposition_trends,
    fft_spectral_analysis,
    combine_weights,
    analyse
)

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_module_weights(history_df: pd.DataFrame, game_config: Dict[str, Any], draw_date: Optional[datetime] = None) -> Dict[str, Dict[int, float]]:
    """
    Génère les poids pour différents modules d'analyse.
    
    Args:
        history_df: DataFrame contenant l'historique des tirages
        game_config: Configuration du jeu
        draw_date: Date du tirage (optionnel)
        
    Returns:
        Dictionnaire des poids par module
    """
    try:
        base_modules = {
            'freq_nums': get_frequent_numbers({'data': history_df}, game_config)[0],
            'pattern_nums': detect_repeating_patterns({'data': history_df}, game_config),
            'lunar_cycle': apply_lunar_cycle_weight(get_frequent_numbers({'data': history_df}, game_config)[0], draw_date) if draw_date else {},
            'positive_seq': detect_positive_sequences({'data': history_df}, game_config),
            'fractal': detect_fractal_patterns({'data': history_df}, game_config),
            'game_theory': game_theory_analysis({'data': history_df}, game_config),
            'periodic_trends': evaluate_periodic_trends({'data': history_df}, game_config),
            'bayesian': bayesian_adjustment(get_frequent_numbers({'data': history_df}, game_config)[0], {'data': history_df}),
            'markov': markov_trend_prediction({'data': history_df}, game_config),
            'neural_net': neural_network_weighting({'data': history_df}, game_config),
            'anomalies': detect_anomalies({'data': history_df}, game_config),
            'loto_opt': optimize_loto_weights({'data': history_df}, game_config),
            'std_dev': analyze_standard_deviation({'data': history_df}, game_config),
            'adaptive_prob': adaptive_probability_adjustment({'data': history_df}, game_config),
            'evolutionary': evolutionary_algorithm_tuning({'data': history_df}, game_config),
            'monte_carlo': monte_carlo_simulation({'data': history_df}, game_config),
            'clustering': cluster_number_selection({'data': history_df}, game_config),
            'long_term_cycles': detect_long_term_cycles({'data': history_df}, game_config),
            'wavelet': wavelet_decomposition_trends({'data': history_df}, game_config),
            'fft': fft_spectral_analysis({'data': history_df}, game_config)
        }
        
        return base_modules
        
    except Exception as e:
        logger.error(f"Erreur lors de la génération des poids: {e}")
        return {}

def generate_model_optimized_grid(game_config: Dict[str, Any], history_df: pd.DataFrame, draw_date: Optional[datetime] = None) -> List[int]:
    """
    Génère une grille optimisée en utilisant plusieurs modèles.
    
    Args:
        game_config: Configuration du jeu
        history_df: DataFrame contenant l'historique des tirages
        draw_date: Date du tirage (optionnel)
        
    Returns:
        Liste des numéros optimisés
    """
    try:
        # Récupération des poids de différents modules
        weights = generate_module_weights(history_df, game_config, draw_date)
        
        # Combinaison des poids
        combined_weights = combine_weights(weights)
        
        # Sélection des numéros avec les poids les plus élevés
        sorted_nums = sorted(combined_weights.items(), key=lambda x: x[1], reverse=True)
        selected_nums = [int(num) for num, _ in sorted_nums[:game_config['columns']]]
        
        # Ajout des numéros bonus si nécessaire
        if game_config.get('bonus', 0) > 0:
            bonus_nums = [int(num) for num, _ in sorted_nums[game_config['columns']:game_config['columns'] + game_config['bonus']]]
            selected_nums.extend(bonus_nums)
            
        return selected_nums
        
    except Exception as e:
        logger.error(f"Erreur lors de la génération de la grille optimisée: {e}")
        return []
