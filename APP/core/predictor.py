import random
import datetime
from models.model_advanced import generate_predictions as model_a_generate
from models.model_experimental import generate_predictions as model_b_generate
from core.utils import get_today_game_info


# Modèle actif par défaut (A = avancé, B = expérimental en test)
ACTIVE_MODEL = "A"

def get_active_model():
    return ACTIVE_MODEL


def set_active_model(model: str):
    global ACTIVE_MODEL
    if model in ["A", "B"]:
        ACTIVE_MODEL = model
    else:
        raise ValueError("Modèle non reconnu. Utilisez 'A' ou 'B'.")


def generate_grille(game_name, date=None):
    """
    Génére une grille prédictive en fonction du modèle actif.

    Args:
        game_name (str): Nom du jeu (e.g. "loto", "euromillion").
        date (datetime): Optionnel, pour analyse temporelle (cycles, historique).

    Returns:
        dict: Une grille prédictive structurée.
    """
    if date is None:
        date = datetime.date.today()

    if ACTIVE_MODEL == "A":
        return model_a_generate(game_name, date)
    elif ACTIVE_MODEL == "B":
        return model_b_generate(game_name, date)
    else:
        raise ValueError("Modèle actif invalide.")


def generate_multiple_grids(game_name, n=3, model=None, date=None):
    """
    Génére plusieurs grilles pour un jeu donné.

    Args:
        game_name (str): Nom du jeu.
        n (int): Nombre de grilles à générer.
        model (str): Optionnel, "A" ou "B".
        date (datetime): Date optionnelle.

    Returns:
        list[dict]: Liste de grilles.
    """
    original_model = ACTIVE_MODEL
    if model:
        set_active_model(model)

    grilles = [generate_grille(game_name, date) for _ in range(n)]

    set_active_model(original_model)
    return grilles
