def display_ascii_header():
    print("\n" + "=" * 50)
    print("🧠  Bienvenue dans LotoAiPredictor - Console Mode")
    print("=" * 50 + "\n")

def display_grilles(grilles):
    for i, g in enumerate(grilles, 1):
        print(f"Grille {i} : {g}")

def display_gain_report(gain_brut, cout, gain_net):
    print("\n📈 Résumé des gains")
    print("-" * 30)
    print(f"Gain brut total : {gain_brut:.2f} €")
    print(f"Coût total      : {cout:.2f} €")
    print(f"Gain net        : {'+' if gain_net >= 0 else '-'}{abs(gain_net):.2f} €")
    print("-" * 30 + "\n")
