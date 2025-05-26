# core/model_a.py

import random
from core.statistics import get_frequent_numbers

def generate_model_a_grid(game_config, history_df):
    # Fréquences historiques pour pondérer le tirage
    frequent_nums, frequent_stars = get_frequent_numbers(history_df, game_config)

    def weighted_draw(pool, freq_map, draw_count):
        return sorted(
            random.choices(pool, weights=[freq_map.get(n, 1) for n in pool], k=draw_count)
        )

    nums = weighted_draw(game_config['pool'], frequent_nums, game_config['numbers'])
    stars = weighted_draw(game_config['stars_pool'], frequent_stars, game_config['stars']) if game_config['stars'] > 0 else []
    
    return {
        'numbers': nums,
        'stars': stars
    }
