import numpy as np
from core.database import get_statistics
from core.regles import JEUX_REGLES

def generate_predictions(game_name=None):
    """
    Génère des prédictions expérimentales basées sur une approche probabiliste.
    
    Args:
        game_name (str, optional): Nom du jeu pour lequel générer des prédictions.
                                 Si None, génère pour tous les jeux.
    
    Returns:
        dict: Dictionnaire contenant les prédictions pour chaque jeu
    """
    predictions = {}
    games = [game_name] if game_name else JEUX_REGLES.keys()
    
    for game in games:
        if game not in JEUX_REGLES:
            continue
            
        rules = JEUX_REGLES[game]
        stats = get_statistics(game)
        
        # Calcul des probabilités conditionnelles
        number_probs = {}
        special_probs = {}
        
        for stat in stats:
            numbers = list(map(int, stat[1].split(",")))
            specials = list(map(int, stat[2].split(",")))
            
            # Mise à jour des probabilités
            for num in numbers:
                if num not in number_probs:
                    number_probs[num] = {"count": 0, "co_occurrences": {}}
                number_probs[num]["count"] += 1
                
                for other_num in numbers:
                    if other_num != num:
                        number_probs[num]["co_occurrences"][other_num] = number_probs[num]["co_occurrences"].get(other_num, 0) + 1
            
            for spec in specials:
                if spec not in special_probs:
                    special_probs[spec] = {"count": 0, "co_occurrences": {}}
                special_probs[spec]["count"] += 1
                
                for other_spec in specials:
                    if other_spec != spec:
                        special_probs[spec]["co_occurrences"][other_spec] = special_probs[spec]["co_occurrences"].get(other_spec, 0) + 1
        
        # Normalisation des probabilités
        total_draws = len(stats)
        for num in number_probs:
            number_probs[num]["prob"] = number_probs[num]["count"] / total_draws
            for other_num in number_probs[num]["co_occurrences"]:
                number_probs[num]["co_occurrences"][other_num] /= number_probs[num]["count"]
        
        for spec in special_probs:
            special_probs[spec]["prob"] = special_probs[spec]["count"] / total_draws
            for other_spec in special_probs[spec]["co_occurrences"]:
                special_probs[spec]["co_occurrences"][other_spec] /= special_probs[spec]["count"]
        
        # Sélection des numéros avec la meilleure probabilité combinée
        def get_combined_prob(numbers):
            if not numbers:
                return 0
            prob = number_probs[numbers[0]]["prob"]
            for i in range(1, len(numbers)):
                prev_num = numbers[i-1]
                curr_num = numbers[i]
                if curr_num in number_probs[prev_num]["co_occurrences"]:
                    prob *= number_probs[prev_num]["co_occurrences"][curr_num]
                else:
                    prob *= number_probs[curr_num]["prob"]
            return prob
        
        # Génération des prédictions
        all_numbers = list(number_probs.keys())
        best_combination = []
        best_prob = 0
        
        # Recherche de la meilleure combinaison
        for _ in range(100):  # Limite le nombre d'essais
            combination = np.random.choice(all_numbers, rules["numbers_count"], replace=False)
            prob = get_combined_prob(combination)
            if prob > best_prob:
                best_prob = prob
                best_combination = combination
        
        # Sélection des numéros spéciaux
        special_numbers = sorted(special_probs.items(), key=lambda x: x[1]["prob"], reverse=True)
        predicted_specials = [spec for spec, _ in special_numbers[:rules["special_count"]]]
        
        predictions[game] = {
            "numbers": sorted(best_combination),
            "special": sorted(predicted_specials),
            "confidence": round(best_prob, 2)
        }
    
    return predictions 