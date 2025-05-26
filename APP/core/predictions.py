import datetime
import numpy as np
from core.statistics import (
    detect_long_term_cycles,
    get_frequent_numbers,
    detect_anomalies,
    evaluate_periodic_trends,
    markov_trend_prediction
)

def generate_predictions(history_df):
    """Génère des prévisions basées sur les tendances et probabilités des prochains tirages."""
    now = datetime.datetime.now()
    
    # Analyse statistique avancée
    frequent_nums, _ = get_frequent_numbers(history_df)
    anomalies = detect_anomalies(history_df)
    periodic_trends = evaluate_periodic_trends(history_df)
    long_term_cycles = detect_long_term_cycles(history_df)
    markov_predictions = markov_trend_prediction(history_df)

    # Sélection des numéros optimisés
    top_numbers = sorted(frequent_nums[:6])  # Les numéros les plus présents
    cycle_numbers = sorted(long_term_cycles.keys()[:6])  # Numéros influencés par les cycles longs
    anomaly_numbers = sorted(anomalies.keys()[:6])  # Numéros ayant des irrégularités détectées
    markov_numbers = sorted(markov_predictions.keys()[:6])  # Prédictions de tendances

    # Génération des grilles
    predictions = {
        "EuroDreams": sorted(set(top_numbers + cycle_numbers)),
        "Euromillions": sorted(set(cycle_numbers + markov_numbers)),
        "Loto": sorted(set(anomaly_numbers + periodic_trends.keys()[:6]))
    }

    return predictions

# Exécution des prévisions
if __name__ == "__main__":
    predictions = generate_predictions(history_df)
    print("\n📊 **Prévisions pour les prochains tirages** 📊")
    for game, numbers in predictions.items():
        print(f"{game} : {numbers}")
