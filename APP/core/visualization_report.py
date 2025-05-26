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

def generate_daily_insights(history_df):
    """Génère un rapport ASCII et des graphiques des tendances."""
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
                 🎲 RAPPORT DU JOUR 🎲
                   {now.strftime('%d %B %Y')}
    ================================================

    🔍 **Analyse des tendances**
    - 🔁 Patterns détectés : {repeating_patterns}
    - 🌙 Influence lunaire : {lunar_effects}
    - 📈 Cycles détectés : {periodic_trends}
    - ⚠️ Anomalies identifiées : {anomalies_detected}
    - 📊 Écart-type : {std_dev_analysis}
    - 🔄 Cycles longs détectés : {long_term_cycles}

    📌 **Recommandations optimisées**
    - Affiner les pondérations basées sur les tendances du jour.
    - Ajuster les sélections en fonction des cycles détectés.
    - Vérifier les anomalies avant validation des grilles.

    🕛 Rapport mis à jour automatiquement chaque jour à minuit !
    ================================================
    """
    print(report)

    # Visualisation des tendances
    fig, ax = plt.subplots()
    cycle_values = [long_term_cycles.get(num, 0) for num in range(1, 50)]
    ax.bar(range(1, 50), cycle_values)
    ax.set_title("Fréquence des numéros sur 10 ans")
    ax.set_xlabel("Numéro")
    ax.set_ylabel("Occurrences")
    plt.savefig("trend_report.png")

    # Sauvegarde ASCII
    with open("daily_report.txt", "w", encoding="utf-8") as f:
        f.write(report)

# Génération du rapport
generate_daily_insights(history_df)
