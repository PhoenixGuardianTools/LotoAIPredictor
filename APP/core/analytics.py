from core.database import get_recent_draws
from core.insights import detect_patterns, detect_cycles, suggest_play_strategy

def analyze_patterns_and_cycles():
    draws = get_recent_draws(limit=365 * 5)  # 5 années
    if not draws:
        print("Aucun tirage à analyser.")
        return

    patterns = detect_patterns(draws)
    cycles = detect_cycles(draws)

    strategy = suggest_play_strategy(draws, patterns, cycles)
    print("📊 Conseil du jour:", strategy)
