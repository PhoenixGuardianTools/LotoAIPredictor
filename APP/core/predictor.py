# APP/core/predictor.py

import datetime
from models.model_advanced import generate_predictions as model_a_generate
from models.model_experimental import generate_predictions as model_b_generate

# Modèle actif (modifiable dynamiquement via l'interface)
ACTIVE_MODEL = "A"  # Par défaut, on utilise le modèle avancé

def get_active_model():
    """Retourne le modèle actif."""
    return ACTIVE_MODEL

def set_active_model(model: str):
    """Modifie le modèle actif."""
    global ACTIVE_MODEL
    if model in ["A", "B"]:
        ACTIVE_MODEL = model
    else:
        raise ValueError("Modèle non reconnu. Utilisez 'A' ou 'B'.")

def generate_grille(game_name: str, date: datetime.date = None):
    """
    Génère une grille prédictive pour un jeu donné à une date donnée.

    Args:
        game_name (str): Nom du jeu.
        date (datetime.date, optional): Date d’analyse. Par défaut aujourd’hui.

    Returns:
        dict: Grille prédictive générée par le modèle actif.
    """
    if date is None:
        date = datetime.date.today()

    if ACTIVE_MODEL == "A":
        return model_a_generate(game_name, date)
    elif ACTIVE_MODEL == "B":
        return model_b_generate(game_name, date)
    else:
        raise ValueError("Modèle actif invalide.")

def generate_multiple_grids(game_name: str, n: int = 3, model: str = None, date: datetime.date = None):
    """
    Génère plusieurs grilles prédictives pour un jeu.

    Args:
        game_name (str): Nom du jeu.
        n (int): Nombre de grilles à générer.
        model (str, optional): Forcer un modèle "A" ou "B".
        date (datetime.date, optional): Date spécifique d’analyse.

    Returns:
        list[dict]: Liste de grilles générées.
    """
    original_model = ACTIVE_MODEL
    if model:
        set_active_model(model)

    grilles = [generate_grille(game_name, date) for _ in range(n)]

    set_active_model(original_model)
    return grilles
