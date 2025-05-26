import datetime
import numpy as np
from database import init_db, get_statistics
from regles import JEUX_REGLES

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

if __name__ == "__main__":
    predictions = generate_predictions()
    print("\n📊 **Prévisions pour les prochains tirages** 📊")
    for game, details in predictions.items():
        print(f"{game} ({details['draw_date']}) : {details}")
