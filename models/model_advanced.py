import numpy as np
from core.database import get_statistics
from core.regles import JEUX_REGLES

def generate_predictions(game_name=None):
    """
    Génère des prédictions avancées basées sur l'analyse statistique et les patterns.
    
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
        
        # Analyse des statistiques
        number_frequencies = {}
        special_frequencies = {}
        
        for stat in stats:
            numbers = list(map(int, stat[1].split(",")))
            specials = list(map(int, stat[2].split(",")))
            
            for num in numbers:
                number_frequencies[num] = number_frequencies.get(num, 0) + 1
            for spec in specials:
                special_frequencies[spec] = special_frequencies.get(spec, 0) + 1
        
        # Sélection des numéros les plus fréquents
        sorted_numbers = sorted(number_frequencies.items(), key=lambda x: x[1], reverse=True)
        sorted_specials = sorted(special_frequencies.items(), key=lambda x: x[1], reverse=True)
        
        # Génération des prédictions
        predicted_numbers = [num for num, _ in sorted_numbers[:rules["numbers_count"]]]
        predicted_specials = [spec for spec, _ in sorted_specials[:rules["special_count"]]]
        
        # Calcul de la confiance
        total_draws = len(stats)
        confidence = sum(freq for _, freq in sorted_numbers[:rules["numbers_count"]]) / (total_draws * rules["numbers_count"])
        
        predictions[game] = {
            "numbers": sorted(predicted_numbers),
            "special": sorted(predicted_specials),
            "confidence": round(confidence, 2)
        }
    
    return predictions 