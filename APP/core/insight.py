def detect_patterns(draws):
    # Exemples : motifs de répétition, hot/cold, fréquences
    return {"hot_numbers": [...], "sequences": [...]}

def detect_cycles(draws):
    # Exemples de détection par cycle lunaire ou hebdomadaire
    return {"lunar_cycle_effect": True}

def suggest_play_strategy(draws=None, patterns=None, cycles=None):
    # Stratégie basée sur motifs & cycles
    if not patterns:
        return "Jouez des numéros équilibrés cette semaine."
    if patterns.get("hot_numbers") and cycles.get("lunar_cycle_effect"):
        return "Semaine propice à jouer des numéros fréquents."
    return "Aucune tendance forte détectée. Privilégiez les favoris."
