# core/model_b.py

import random
from core.statistics import (
    get_frequent_numbers,
    detect_repeating_patterns,
    apply_lunar_cycle_weight,
    detect_positive_sequences
)

def generate_model_b_grid(game_config, history_df, draw_date=None):
    # 1. Données historiques enrichies
    frequent_nums, frequent_stars = get_frequent_numbers(history_df, game_config)
    pattern_nums = detect_repeating_patterns(history_df, game_config)
    adjusted_freq = apply_lunar_cycle_weight(frequent_nums, draw_date)
    positive_bias = detect_positive_sequences(history_df, game_config)

    def smart_draw(pool, freq_map, pattern_bonus, bias_map, count):
        weights = []
        for n in pool:
            freq = freq_map.get(n, 1)
            bias = bias_map.get(n, 1)
            bonus = 2 if n in pattern_bonus else 1
            weights.append(freq * bias * bonus)
        return sorted(random.choices(pool, weights=weights, k=count))

    nums = smart_draw(game_config['pool'], adjusted_freq, pattern_nums, positive_bias, game_config['numbers'])
    stars = smart_draw(game_config['stars_pool'], frequent_stars, set(), {}, game_config['stars']) if game_config['stars'] > 0 else []

    return {
        'numbers': nums,
        'stars': stars
    }
