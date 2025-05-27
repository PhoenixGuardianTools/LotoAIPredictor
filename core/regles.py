import requests

# Définition des règles des jeux
JEUX_REGLES = {
    "EuroDreams": {
        "numbers_range": (1, 40),
        "numbers_count": 6,
        "special_range": (1, 5),
        "special_count": 1,
        "draw_days": ["Monday", "Thursday"]
    },
    "Loto": {
        "numbers_range": (1, 49),
        "numbers_count": 5,
        "special_range": (1, 10),
        "special_count": 1,
        "draw_days": ["Monday", "Wednesday", "Saturday"]
    },
    "Euromillions": {
        "numbers_range": (1, 50),
        "numbers_count": 5,
        "special_range": (1, 12),
        "special_count": 2,
        "draw_days": ["Tuesday", "Friday"]
    }
}

def fetch_latest_rules():
    """Importe les règles à jour depuis la base en ligne de la Française des Jeux."""
    url = "https://www.fdj.fr/jeux-de-tirage"
    response = requests.get(url)
    if response.status_code == 200:
        return JEUX_REGLES  # À remplacer par un parsing réel des règles mises à jour
    return None

def validate_draw_format(game, draw):
    """Vérifie que le format du tirage est conforme aux règles du jeu."""
    rules = JEUX_REGLES.get(game)
    if not rules:
        return False

    numbers_valid = all(rules["numbers_range"][0] <= n <= rules["numbers_range"][1] for n in draw["numbers"])
    special_valid = all(rules["special_range"][0] <= s <= rules["special_range"][1] for s in draw["special"])

    return numbers_valid and special_valid

"""
Règles des jeux FDJ
"""

LOTO_RULES = {
    'name': 'LOTO',
    'numbers': {
        'main': {'count': 5, 'min': 1, 'max': 90},
        'chance': {'count': 1, 'min': 1, 'max': 10}
    },
    'price': 2.20,
    'draw_days': ['Lundi', 'Mercredi', 'Samedi'],
    'jackpot_min': 2000000,
    'url': 'https://www.fdj.fr/jeux-de-tirage/loto/historique'
}

EUROMILLIONS_RULES = {
    'name': 'EUROMILLIONS',
    'numbers': {
        'main': {'count': 5, 'min': 1, 'max': 50},
        'stars': {'count': 2, 'min': 1, 'max': 12}
    },
    'price': 2.50,
    'draw_days': ['Mardi', 'Vendredi'],
    'jackpot_min': 17000000,
    'url': 'https://www.fdj.fr/jeux-de-tirage/euromillions-my-million/historique'
}

KENO_RULES = {
    'name': 'KENO',
    'numbers': {
        'main': {'count': 10, 'min': 1, 'max': 70}
    },
    'price': 2.00,
    'draw_days': ['Tous les jours'],
    'jackpot_max': 200000,
    'url': 'https://www.fdj.fr/jeux-de-tirage/keno/historique'
}

EURODREAMS_RULES = {
    'name': 'EURODREAMS',
    'numbers': {
        'main': {'count': 6, 'min': 1, 'max': 40},
        'dream': {'count': 1, 'min': 1, 'max': 5}
    },
    'price': 2.50,
    'draw_days': ['Lundi', 'Jeudi'],
    'jackpot_min': 20000000,
    'url': 'https://www.fdj.fr/jeux-de-tirage/eurodreams/historique'
}

# Dictionnaire de tous les jeux disponibles
GAMES = {
    'LOTO': LOTO_RULES,
    'EUROMILLIONS': EUROMILLIONS_RULES,
    'KENO': KENO_RULES,
    'EURODREAMS': EURODREAMS_RULES
}
