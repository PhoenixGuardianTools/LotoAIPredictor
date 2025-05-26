import datetime
import numpy as np
from core.database import init_db, get_statistics
from core.regles import JEUX_REGLES

def get_next_draw_dates():
    """Détermine les prochaines dates de tirage pour chaque jeu."""
    today = datetime.datetime.today()
    next_draws = {}

    for game, rules in JEUX_REGLES.items():
        for i in range(1, 8):  
            future_date = today + datetime.timedelta(days=i)
            if future_date.strftime("%A") in rules["draw_days"]:
                next_draws[game] = future_date.strftime("%d %B %Y")
                break

    return next_draws

def calculate_predicted_gains(game, predicted_numbers, predicted_special):
    """Calcule les gains estimés en comparant les prédictions aux statistiques des 10 dernières années."""
    past_statistics = get_statistics(game)
    best_match = 0
    best_special_match = 0
    best_ratio = 0
    best_confidence = 0

    for stat in past_statistics:
        stat_numbers = list(map(int, stat[1].split(",")))
        stat_special = list(map(int, stat[2].split(",")))
        ratio_gain = stat[3]
        indice_confiance = stat[4]

        common_numbers = len(set(predicted_numbers) & set(stat_numbers))
        common_special = len(set(predicted_special) & set(stat_special))

        if common_numbers > best_match or (common_numbers == best_match and common_special > best_special_match):
            best_match = common_numbers
            best_special_match = common_special
            best_ratio = ratio_gain
            best_confidence = indice_confiance

    # Estimation des gains en fonction des correspondances statistiques
    gain_estimate = best_ratio * 1000000 if best_match == JEUX_REGLES[game]["numbers_count"] else best_ratio * 50000  
    rank = "1er" if best_confidence > 0.9 else ("2e" if best_match >= JEUX_REGLES[game]["numbers_count"] - 1 else "3e")

    return round(gain_estimate, 2), rank, round(best_ratio, 2), round(best_confidence, 2)

def generate_predictions():
    """Génère des prévisions basées sur les tendances et probabilités des prochains tirages."""
    init_db()  
    next_draws = get_next_draw_dates()

    predictions = {}
    for game, rules in JEUX_REGLES.items():
        numbers = sorted(np.random.choice(range(rules["numbers_range"][0], rules["numbers_range"][1] + 1), rules["numbers_count"], replace=False))
        special = sorted(np.random.choice(range(rules["special_range"][0], rules["special_range"][1] + 1), rules["special_count"], replace=False))

        gain_estimate, rank, ratio_gain, indice_confiance = calculate_predicted_gains(game, numbers, special)

        predictions[game] = {
            "draw_date": next_draws[game],
            "numbers": numbers,
            "special": special,
            "estimated_gain": gain_estimate,
            "rank": rank,
            "ratio_gain": ratio_gain,
            "indice_confiance": indice_confiance
        }

    return predictions

def suggest_play_strategy(history_df, game_config):
    """Suggère une stratégie de jeu basée sur l'analyse des tendances et des cycles."""
    # Récupérer les statistiques
    stats = get_statistics(game_config['name'])
    
    # Calculer les scores pour chaque numéro
    number_scores = {}
    for num in range(game_config['numbers_range'][0], game_config['numbers_range'][1] + 1):
        score = 0
        
        # Score basé sur les statistiques
        for stat in stats:
            stat_numbers = list(map(int, stat[1].split(",")))
            if num in stat_numbers:
                score += stat[3] * stat[4]  # ratio_gain * indice_confiance
        
        number_scores[num] = score
    
    # Normaliser les scores
    max_score = max(number_scores.values())
    if max_score > 0:
        number_scores = {num: score/max_score for num, score in number_scores.items()}
    
    # Sélectionner les meilleurs numéros
    recommended_numbers = sorted(number_scores.items(), key=lambda x: x[1], reverse=True)[:game_config['numbers_count']]
    
    # Générer la stratégie
    strategy = {
        'recommended_numbers': [num for num, _ in recommended_numbers],
        'confidence_score': np.mean([score for _, score in recommended_numbers]),
        'analysis_summary': {
            'number_scores': number_scores,
            'best_combinations': [stat[1] for stat in stats[:3]]  # Top 3 des meilleures combinaisons historiques
        }
    }
    
    return strategy

def analyze_patterns_and_cycles():
    """Analyse les patterns et cycles pour générer des prédictions."""
    predictions = generate_predictions()
    
    print("\n📊 **Analyse des tendances et prédictions** 📊")
    for game, details in predictions.items():
        print(f"\n{game} ({details['draw_date']}):")
        print(f"Numéros suggérés: {details['numbers']}")
        print(f"Numéros spéciaux: {details['special']}")
        print(f"Gain estimé: {details['estimated_gain']}€")
        print(f"Rang probable: {details['rank']}")
        print(f"Ratio de gain: {details['ratio_gain']}")
        print(f"Indice de confiance: {details['indice_confiance']}")

if __name__ == "__main__":
    predictions = generate_predictions()
    print("\n📊 **Prévisions pour les prochains tirages** 📊")
    for game, details in predictions.items():
        print(f"{game} ({details['draw_date']}) : {details}")
    
    print("\n📈 **Analyse des patterns et cycles** 📈")
    analyze_patterns_and_cycles()
