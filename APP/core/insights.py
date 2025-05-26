import datetime
import matplotlib.pyplot as plt
import numpy as np
from core.statistics import (
    detect_repeating_patterns,
    apply_lunar_cycle_weight,
    evaluate_periodic_trends,
    analyze_standard_deviation,
    detect_anomalies,
    detect_long_term_cycles
)

def generate_insight_report(history_df):
    """Génère un rapport ASCII et une visualisation des tendances chaque jour."""
    now = datetime.datetime.now()
    lunar_effects = apply_lunar_cycle_weight(history_df, now)
    repeating_patterns = detect_repeating_patterns(history_df)
    periodic_trends = evaluate_periodic_trends(history_df)
    anomalies_detected = detect_anomalies(history_df)
    std_dev_analysis = analyze_standard_deviation(history_df)
    long_term_cycles = detect_long_term_cycles(history_df)

    # Rapport ASCII
    report = f"""
    ================================================
                 📊 RAPPORT DES TENDANCES 📊
                  {now.strftime('%d %B %Y')}
    ================================================

    🔍 **Analyse des tendances sur 10 ans**
    - 🔁 Patterns récurrents détectés : {repeating_patterns}
    - 🌙 Effet lunaire sur les jeux : {lunar_effects}
    - 📈 Cycles détectés : {periodic_trends}
    - ⚠️ Anomalies statistiques : {anomalies_detected}
    - 📊 Écart-type sur les tirages : {std_dev_analysis}
    - 🔄 Cycles longs identifiés : {long_term_cycles}

    📌 **Recommandations basées sur l’analyse**
    - Affiner les pondérations basées sur les tendances observées.
    - Ajuster les stratégies de jeu en fonction des cycles récurrents.
    - Optimiser la sélection des numéros en suivant les anomalies détectées.

    🕛 Rapport mis à jour automatiquement chaque jour à minuit !
    ================================================
    """
    print(report)

    # Visualisation graphique des tendances
    fig, ax = plt.subplots(figsize=(10, 5))
    cycle_values = [long_term_cycles.get(num, 0) for num in range(1, 50)]
    ax.bar(range(1, 50), cycle_values, color='steelblue')
    ax.set_title("Fréquence des numéros sur 10 ans")
    ax.set_xlabel("Numéro")
    ax.set_ylabel("Occurrences")
    plt.xticks(range(1, 50, 5))
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.savefig("trend_visualization.png")

    # Sauvegarde ASCII
    with open("daily_insight.txt", "w", encoding="utf-8") as f:
        f.write(report)

# Génération du rapport à minuit chaque jour
while True:
    now = datetime.datetime.now()
    if now.hour == 0 and now.minute == 0:
        generate_insight_report(history_df)  # Historique des tirages à fournir
        time.sleep(60)  # Empêcher plusieurs exécutions dans la même minute
    else:
        time.sleep(10)  # Vérification toutes les 10 secondes
