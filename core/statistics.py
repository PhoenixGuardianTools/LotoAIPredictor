"""
Module d'analyse statistique pour la prédiction des jeux de loterie.

Organisation des 26 modules par catégories :

1. Modules de base (6) :
   - FrequencyProcessor : Analyse des fréquences d'apparition des numéros
   - PatternProcessor : Détection des motifs répétitifs dans les tirages
   - SequenceProcessor : Analyse des séquences croissantes
   - AnomalyProcessor : Détection des anomalies statistiques
   - PeriodicTrendProcessor : Analyse des tendances périodiques
   - MonteCarloProcessor : Simulation Monte Carlo des probabilités

2. Analyse probabiliste et bayésienne (3) :
   - bayesian_adjustment : Ajustement bayésien des probabilités
   - markov_trend_prediction : Prédiction par chaînes de Markov
   - adaptive_probability_adjustment : Ajustement adaptatif des probabilités

3. Analyse temporelle et cyclique (4) :
   - apply_lunar_cycle_weight : Pondération selon phase lunaire
   - detect_long_term_cycles : Détection de cycles longs
   - wavelet_decomposition_trends : Analyse par décomposition en ondelettes
   - fft_spectral_analysis : Analyse spectrale FFT

4. Analyse statistique avancée (2) :
   - analyze_standard_deviation : Analyse d'écart-type
   - permutation_test_pattern_significance : Test de significativité des motifs

5. Analyse IA et apprentissage (3) :
   - neural_network_weighting : Pondération par réseau neuronal
   - evolutionary_algorithm_tuning : Ajustement par algorithme évolutionnaire
   - cluster_number_selection : Sélection par clustering

6. Optimisation (3) :
   - game_theory_analysis : Analyse selon théorie des jeux
   - optimize_loto_weights : Optimisation des poids pour le loto
   - bayesian_network_integration : Fusion bayésienne des signaux

7. Modules utilitaires (2) :
   - combine_weights : Agrégation pondérée des poids
   - detect_fractal_patterns : Analyse fractale des motifs

Total : 26 modules

Architecture :
- Utilise le pattern Factory pour la création des processeurs
- Implémente le polymorphisme via la classe DataProcessor
- Utilise des décorateurs pour le logging, la validation et le cache
- Interface unifiée pour tous les processeurs via la méthode process()
"""

from abc import ABC, abstractmethod
import numpy as np
import pandas as pd
from collections import defaultdict
import pywt
from datetime import datetime
from typing import Dict, List, Set, Union, Any, Tuple, Optional
import functools
import logging
import time
from functools import lru_cache
from .clean_data import (
    DataProcessor,
    DataProcessorFactory,
    clean_numeric_data,
    prepare_dataframe,
    normalize_dates,
    remove_outliers,
    validate_game_config,
    prepare_analysis_data
)

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_data(func):
    """Décorateur pour valider les données d'entrée."""
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if not isinstance(self.history, (dict, pd.DataFrame)):
            logger.error("Format d'historique invalide")
            return {}
        if not isinstance(self.game_config, dict):
            logger.error("Configuration de jeu invalide")
            return {}
        return func(self, *args, **kwargs)
    return wrapper

def log_execution(func):
    """Décorateur pour logger l'exécution des méthodes."""
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        start_time = time.time()
        logger.info(f"Début de l'exécution de {func.__name__}")
        try:
            result = func(self, *args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"Fin de l'exécution de {func.__name__} en {execution_time:.2f} secondes")
            return result
        except Exception as e:
            logger.error(f"Erreur dans {func.__name__}: {str(e)}")
            raise
    return wrapper

def cache_result(ttl_seconds=3600):
    """Décorateur pour mettre en cache les résultats avec un TTL."""
    def decorator(func):
        cache = {}
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            current_time = time.time()
            
            if key in cache:
                result, timestamp = cache[key]
                if current_time - timestamp < ttl_seconds:
                    logger.debug(f"Utilisation du cache pour {func.__name__}")
                    return result
            
            result = func(self, *args, **kwargs)
            cache[key] = (result, current_time)
            return result
        return wrapper
    return decorator

def handle_errors(func):
    """Décorateur pour gérer les erreurs de manière uniforme."""
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except ValueError as e:
            logger.error(f"Erreur de validation: {str(e)}")
            return {}
        except Exception as e:
            logger.error(f"Erreur inattendue dans {func.__name__}: {str(e)}")
            return {}
    return wrapper

class StatisticalProcessor(DataProcessor):
    """Classe de base pour les processeurs statistiques."""
    
    def __init__(self, history: Union[Dict, pd.DataFrame], game_config: Dict[str, Any]):
        super().__init__(history)
        self.game_config = game_config
        self.data = self._prepare_data()
        
    def _prepare_data(self) -> pd.DataFrame:
        """Prépare les données pour l'analyse."""
        data, success = prepare_analysis_data(self.history, self.game_config)
        if not success:
            logger.error("Échec de la préparation des données")
            return pd.DataFrame()
        return data
        
    def validate(self) -> bool:
        """Valide les données d'entrée."""
        if not isinstance(self.history, (dict, pd.DataFrame)):
            logger.error("Format d'historique invalide")
            return False
        if not isinstance(self.game_config, dict):
            logger.error("Configuration de jeu invalide")
            return False
        return True
        
    @abstractmethod
    @log_execution
    @handle_errors
    def process(self) -> Dict:
        """Méthode abstraite pour l'analyse statistique."""
        pass

class FrequencyProcessor(StatisticalProcessor):
    """Processeur pour l'analyse des fréquences."""
    
    @cache_result(ttl_seconds=1800)
    def process(self) -> Dict:
        """Analyse les fréquences d'apparition des numéros."""
        if self.data.empty:
            return {}, 0
            
        numbers = clean_numeric_data(self.data)
        if len(numbers) == 0:
            return {}, 0
            
        counts = pd.Series(numbers).value_counts(normalize=True)
        self.processed_data = counts.to_dict()
        return self.processed_data, counts.max()

class PatternProcessor(StatisticalProcessor):
    """Processeur pour l'analyse des motifs."""
    
    def __init__(self, history: Union[Dict, pd.DataFrame], game_config: Dict[str, Any], window_size: int = 3):
        super().__init__(history, game_config)
        self.window_size = window_size
        
    @cache_result(ttl_seconds=3600)
    def process(self) -> Set:
        """Analyse les motifs répétitifs."""
        if self.data.empty:
            return set()
            
        patterns = set()
        draws = self.data.values.tolist()
        
        for i in range(len(draws) - self.window_size + 1):
            pattern = tuple(draws[i:i + self.window_size])
            if pattern in patterns:
                continue
                
            for j in range(i + self.window_size, len(draws) - self.window_size + 1):
                if tuple(draws[j:j + self.window_size]) == pattern:
                    patterns.add(pattern)
                    break
                    
        self.processed_data = patterns
        return patterns

class SequenceProcessor(StatisticalProcessor):
    """Processeur pour l'analyse des séquences."""
    
    def __init__(self, history: Union[Dict, pd.DataFrame], game_config: Dict[str, Any], min_length: int = 3):
        super().__init__(history, game_config)
        self.min_length = min_length
        
    @cache_result(ttl_seconds=1800)
    def process(self) -> Set:
        """Analyse les séquences croissantes."""
        if self.data.empty:
            return set()
            
        sequences = set()
        draws = self.data.values.tolist()
        
        for draw in draws:
            for i in range(len(draw) - self.min_length + 1):
                sequence = draw[i:i + self.min_length]
                if all(sequence[j] < sequence[j + 1] for j in range(len(sequence) - 1)):
                    sequences.add(tuple(sequence))
                    
        self.processed_data = sequences
        return sequences

class AnomalyProcessor(StatisticalProcessor):
    """Processeur pour l'analyse des anomalies."""
    
    @cache_result(ttl_seconds=900)
    def process(self) -> Dict:
        """Détecte les anomalies statistiques."""
        if self.data.empty:
            return {}
            
        clean_data = remove_outliers(self.data)
        anomalies = {}
        
        for column in self.data.columns:
            if column in clean_data.columns:
                outliers = self.data[~self.data.index.isin(clean_data.index)][column]
                if not outliers.empty:
                    anomalies[column] = outliers.to_dict()
                    
        self.processed_data = anomalies
        return anomalies

class PeriodicTrendProcessor(StatisticalProcessor):
    """Processeur pour l'analyse des tendances périodiques."""
    
    @cache_result(ttl_seconds=3600)
    def process(self) -> Dict:
        """Analyse les tendances périodiques."""
        if self.data.empty:
            return {}
            
        data = normalize_dates(self.data)
        if data.empty:
            return {}
            
        trends = {}
        day_trends = data.groupby('day_of_week').mean()
        month_trends = data.groupby('month').mean()
        
        trends['daily'] = day_trends.to_dict()
        trends['monthly'] = month_trends.to_dict()
        
        self.processed_data = trends
        return trends

class MonteCarloProcessor(StatisticalProcessor):
    """Processeur pour l'analyse Monte Carlo."""
    
    def __init__(self, history: Union[Dict, pd.DataFrame], game_config: Dict[str, Any], n_simulations: int = 1000):
        super().__init__(history, game_config)
        self.n_simulations = n_simulations
        
    @cache_result(ttl_seconds=1800)
    def process(self) -> Dict:
        """Effectue une simulation Monte Carlo."""
        if self.data.empty:
            return {}
            
        results = {}
        freq_processor = FrequencyProcessor(self.history, self.game_config)
        freq_dict, _ = freq_processor.process()
        
        for _ in range(self.n_simulations):
            numbers = np.random.choice(
                list(freq_dict.keys()),
                size=self.game_config['columns'],
                p=list(freq_dict.values()),
                replace=False
            )
            
            for num in numbers:
                results[num] = results.get(num, 0) + 1
                
        total = sum(results.values())
        if total > 0:
            results = {k: v/total for k, v in results.items()}
            
        self.processed_data = results
        return results

class StatisticalProcessorFactory:
    """Factory pour créer les processeurs statistiques."""
    
    _processors = {
        'frequency': FrequencyProcessor,
        'pattern': PatternProcessor,
        'sequence': SequenceProcessor,
        'anomaly': AnomalyProcessor,
        'periodic': PeriodicTrendProcessor,
        'monte_carlo': MonteCarloProcessor
    }
    
    @classmethod
    def register_processor(cls, name: str, processor_class: type):
        """Enregistre un nouveau processeur."""
        cls._processors[name] = processor_class
    
    @classmethod
    def create_processor(cls, processor_type: str, history: Union[Dict, pd.DataFrame], game_config: Dict[str, Any], **kwargs) -> StatisticalProcessor:
        """Crée un processeur statistique selon le type demandé."""
        if processor_type not in cls._processors:
            raise ValueError(f"Type de processeur inconnu: {processor_type}")
            
        return cls._processors[processor_type](history, game_config, **kwargs)

# Fonctions d'interface pour la compatibilité avec le code existant
@lru_cache(maxsize=128)
def get_frequent_numbers(history, game_config):
    processor = StatisticalProcessorFactory.create_processor('frequency', history, game_config)
    return processor.process()

@lru_cache(maxsize=128)
def detect_repeating_patterns(history, game_config):
    processor = StatisticalProcessorFactory.create_processor('pattern', history, game_config)
    return processor.process()

@lru_cache(maxsize=128)
def detect_positive_sequences(history, game_config):
    processor = StatisticalProcessorFactory.create_processor('sequence', history, game_config)
    return processor.process()

@lru_cache(maxsize=128)
def detect_anomalies(history, game_config):
    processor = StatisticalProcessorFactory.create_processor('anomaly', history, game_config)
    return processor.process()

@lru_cache(maxsize=128)
def evaluate_periodic_trends(history, game_config):
    processor = StatisticalProcessorFactory.create_processor('periodic', history, game_config)
    return processor.process()

@lru_cache(maxsize=128)
def monte_carlo_simulation(history, game_config):
    processor = StatisticalProcessorFactory.create_processor('monte_carlo', history, game_config)
    return processor.process()

# ---------------------------
# Analyse probabiliste et bayésienne
# ---------------------------

def bayesian_adjustment(frequent_nums, history):
    """
    Ajustement bayésien des probabilités selon historique.
    """
    adjusted_probs = {}
    return adjusted_probs

def markov_trend_prediction(history, game_config):
    """
    Prédiction basée sur chaînes de Markov.
    """
    markov_probs = {}
    return markov_probs

def adaptive_probability_adjustment(history, game_config):
    """
    Ajustement adaptatif des probabilités en fonction de l'évolution.
    """
    adaptive_probs = {}
    return adaptive_probs

# ---------------------------
# Analyse temporelle et cyclique
# ---------------------------

def apply_lunar_cycle_weight(frequent_nums, draw_date):
    """
    Pondération selon phase lunaire à la date du tirage.
    """
    lunar_weights = {}
    return lunar_weights

def detect_long_term_cycles(history, game_config):
    """
    Détection de cycles longs (plusieurs mois ou années).
    """
    long_term_cycles = {}
    return long_term_cycles

def wavelet_decomposition_trends(history, game_config):
    """
    Analyse des tendances via décomposition en ondelettes.
    """
    all_nums = [num for draw in history['numbers'] for num in draw]
    coeffs = pywt.wavedec(all_nums, 'db1', level=3)
    trends = coeffs[0]
    weights = {}
    norm_trends = (trends - np.min(trends)) / (np.max(trends) - np.min(trends) + 1e-6)
    for i, num in enumerate(game_config['pool'][:len(norm_trends)]):
        weights[num] = norm_trends[i]
    return weights

def fft_spectral_analysis(history, game_config):
    """
    Analyse spectrale FFT des tirages.
    """
    all_nums = [num for draw in history['numbers'] for num in draw]
    fft_vals = np.abs(np.fft.fft(all_nums))
    fft_norm = fft_vals / (np.max(fft_vals) + 1e-6)
    weights = {}
    for i, num in enumerate(game_config['pool'][:len(fft_norm)]):
        weights[num] = fft_norm[i]
    return weights

# ---------------------------
# Analyse statistique avancée
# ---------------------------

def analyze_standard_deviation(history, game_config):
    """
    Analyse d'écart-type des tirages.
    """
    if isinstance(history, dict) and 'data' in history:
        data = history['data']
    else:
        data = history
        
    if not isinstance(data, pd.DataFrame):
        return {}
        
    # Calculer l'écart-type pour chaque position
    std_devs = data.std()
    
    # Normaliser les écarts-types
    max_std = std_devs.max()
    if max_std == 0:
        return {}
        
    normalized_stds = std_devs / max_std
    
    return normalized_stds.to_dict()

def permutation_test_pattern_significance(history, game_config):
    """
    Test de permutation pour la significativité des motifs.
    """
    p_values = {}
    return p_values

# ---------------------------
# Analyse IA et apprentissage
# ---------------------------

def neural_network_weighting(history, game_config):
    """
    Pondération par réseau neuronal supervisé.
    """
    nn_weights = {}
    return nn_weights

def evolutionary_algorithm_tuning(history, game_config):
    """
    Ajustement par algorithme évolutionnaire.
    """
    evo_weights = {}
    return evo_weights

def cluster_number_selection(history, game_config):
    """
    Sélection par clustering (ex: K-means) des numéros.
    """
    clusters = {}
    return clusters

# ---------------------------
# Optimisation et autres modules
# ---------------------------

def game_theory_analysis(history, game_config):
    """
    Analyse selon théorie des jeux.
    """
    gt_results = {}
    return gt_results

def optimize_loto_weights(history, game_config):
    """
    Optimisation globale des poids pour la grille loto.
    """
    optimized_weights = {}
    return optimized_weights

# ---------------------------
# Nouveau module (26e)
# ---------------------------

def bayesian_network_integration(history, game_config):
    """
    Fusion bayésienne pour combiner plusieurs signaux.
    """
    bayes_net_results = {}
    return bayes_net_results

# ---------------------------
# Fonction utilitaire
# ---------------------------

class FractalProcessor(StatisticalProcessor):
    """Processeur pour l'analyse des motifs fractals."""
    
    def __init__(self, history: Union[Dict, pd.DataFrame], game_config: Dict[str, Any]):
        super().__init__(history, game_config)
        self._fractal_scores: Dict[int, float] = {}
        self._window_size: int = 3
        
    @property
    def fractal_scores(self) -> Dict[int, float]:
        """Getter pour les scores fractals."""
        return self._fractal_scores
        
    @fractal_scores.setter
    def fractal_scores(self, value: Dict[int, float]):
        """Setter pour les scores fractals."""
        if not isinstance(value, dict):
            raise ValueError("Les scores fractals doivent être un dictionnaire")
        self._fractal_scores = value
        
    @property
    def window_size(self) -> int:
        """Getter pour la taille de la fenêtre."""
        return self._window_size
        
    @window_size.setter
    def window_size(self, value: int):
        """Setter pour la taille de la fenêtre."""
        if not isinstance(value, int) or value < 1:
            raise ValueError("La taille de la fenêtre doit être un entier positif")
        self._window_size = value
        
    @cache_result(ttl_seconds=3600)
    def process(self) -> Dict[int, float]:
        """Analyse les motifs fractals dans les tirages."""
        if self.data.empty:
            return {}
            
        try:
            # Analyse des motifs auto-similaires
            patterns = self._analyze_fractal_patterns()
            
            # Calcul des scores
            scores = self._calculate_fractal_scores(patterns)
            
            # Normalisation des scores
            self._fractal_scores = self._normalize_scores(scores)
            
            return self._fractal_scores
            
        except Exception as e:
            logger.error(f"Erreur dans l'analyse fractale: {e}")
            return {}
            
    def _analyze_fractal_patterns(self) -> List[Tuple]:
        """Analyse les motifs fractals dans les données."""
        patterns = []
        draws = self.data.values.tolist()
        
        for i in range(len(draws) - self._window_size + 1):
            pattern = tuple(draws[i:i + self._window_size])
            patterns.append(pattern)
            
        return patterns
        
    def _calculate_fractal_scores(self, patterns: List[Tuple]) -> Dict[int, float]:
        """Calcule les scores fractals pour chaque numéro."""
        scores = defaultdict(float)
        
        for pattern in patterns:
            for num in pattern:
                scores[num] += 1
                
        return dict(scores)
        
    def _normalize_scores(self, scores: Dict[int, float]) -> Dict[int, float]:
        """Normalise les scores entre 0 et 1."""
        if not scores:
            return {}
            
        max_score = max(scores.values())
        if max_score == 0:
            return {}
            
        return {num: score/max_score for num, score in scores.items()}

class WeightCombiner(StatisticalProcessor):
    """Processeur pour la combinaison des poids."""
    
    def __init__(self, history: Union[Dict, pd.DataFrame], game_config: Dict[str, Any]):
        super().__init__(history, game_config)
        self._weight_factors: Dict[str, float] = {
            'freq_nums': 0.3,
            'pattern_nums': 0.2,
            'lunar_cycle': 0.05,
            'positive_seq': 0.1,
            'fractal': 0.05,
            'game_theory': 0.05,
            'periodic_trends': 0.05,
            'bayesian': 0.05,
            'markov': 0.05,
            'neural_net': 0.05,
            'anomalies': 0.05,
            'loto_opt': 0.05,
            'std_dev': 0.05,
            'adaptive_prob': 0.05,
            'evolutionary': 0.05,
            'monte_carlo': 0.05,
            'clustering': 0.05,
            'long_term_cycles': 0.05,
            'wavelet': 0.05,
            'fft': 0.05
        }
        self._combined_weights: Dict[int, float] = {}
        
    @property
    def weight_factors(self) -> Dict[str, float]:
        """Getter pour les facteurs de poids."""
        return self._weight_factors
        
    @weight_factors.setter
    def weight_factors(self, value: Dict[str, float]):
        """Setter pour les facteurs de poids."""
        if not isinstance(value, dict):
            raise ValueError("Les facteurs de poids doivent être un dictionnaire")
        self._validate_weight_factors(value)
        self._weight_factors = value
        
    @property
    def combined_weights(self) -> Dict[int, float]:
        """Getter pour les poids combinés."""
        return self._combined_weights
        
    @combined_weights.setter
    def combined_weights(self, value: Dict[int, float]):
        """Setter pour les poids combinés."""
        if not isinstance(value, dict):
            raise ValueError("Les poids combinés doivent être un dictionnaire")
        self._combined_weights = value
        
    def _validate_weight_factors(self, factors: Dict[str, float]):
        """Valide que la somme des facteurs de poids est égale à 1."""
        total = sum(factors.values())
        if not (0.99 <= total <= 1.01):  # Tolérance pour les erreurs d'arrondi
            raise ValueError(f"La somme des poids doit être égale à 1, actuellement: {total}")
            
    @cache_result(ttl_seconds=3600)
    def process(self) -> Dict[int, float]:
        """Combine les poids de différents modules avec validation."""
        try:
            total_score = 0
            valid_modules = 0
            
            for module_name, weight in self._weight_factors.items():
                val = self.data.get(module_name, {})
                try:
                    score = self._calculate_module_score(val)
                    if score is not None:
                        total_score += score * weight
                        valid_modules += 1
                except (ValueError, TypeError) as e:
                    logger.error(f"Erreur de calcul pour {module_name}: {e}")
                    continue
                    
            if valid_modules == 0:
                raise ValueError("Aucun module valide trouvé pour le calcul du score")
                
            self._combined_weights = self._normalize_score(total_score / valid_modules)
            return self._combined_weights
            
        except Exception as e:
            logger.error(f"Erreur lors de la combinaison des poids: {e}")
            return {}
            
    def _calculate_module_score(self, value: Any) -> Optional[float]:
        """Calcule le score pour un module donné."""
        if isinstance(value, dict):
            return sum(float(v) for v in value.values() if v is not None)
        elif isinstance(value, (int, float)):
            return float(value)
        return None
        
    def _normalize_score(self, score: float) -> Dict[int, float]:
        """Normalise le score entre 0 et 1."""
        if not (0 <= score <= 1):
            logger.warning(f"Score invalide: {score}")
            score = max(0, min(1, score))
        return {'combined_score': score}

# Enregistrement des nouveaux processeurs
StatisticalProcessorFactory.register_processor('fractal', FractalProcessor)
StatisticalProcessorFactory.register_processor('weight_combiner', WeightCombiner)

# Fonctions d'interface pour la compatibilité avec le code existant
@lru_cache(maxsize=128)
def detect_fractal_patterns(history: Union[Dict, pd.DataFrame], game_config: Dict[str, Any]) -> Dict[int, float]:
    """
    Analyse les motifs fractals dans les tirages.
    
    Args:
        history: Historique des tirages
        game_config: Configuration du jeu
        
    Returns:
        Dict[int, float]: Dictionnaire des poids fractals par numéro
    """
    processor = StatisticalProcessorFactory.create_processor('fractal', history, game_config)
    return processor.process()

@lru_cache(maxsize=128)
def combine_weights(weights_dict: Dict[str, Dict[int, float]]) -> Dict[int, float]:
    """
    Combine les poids de différents modules avec validation.
    
    Args:
        weights_dict: Dictionnaire des poids par module
        
    Returns:
        Dict[int, float]: Dictionnaire des poids combinés par numéro
    """
    processor = StatisticalProcessorFactory.create_processor('weight_combiner', weights_dict, {})
    return processor.process()

from collections import Counter

def calculate_adjusted_expectancy(grille_nums, grille_bonus, historique_nums, historique_bonus, prob_jackpot, montant_jackpot, facteur_unicite):
    """
    Calcule l'espérance ajustée d'une grille, selon la rareté des numéros et bonus.

    Args:
        grille_nums (list[int]): Numéros principaux de la grille.
        grille_bonus (list[int] or int): Bonus/étoiles de la grille.
        historique_nums (list[int]): Liste complète des numéros historiques.
        historique_bonus (list[int]): Liste complète des bonus historiques.
        prob_jackpot (float): Probabilité officielle de gagner le jackpot.
        montant_jackpot (float): Montant estimé du jackpot.
        facteur_unicite (float): Facteur d'unicité multiplicatif.

    Returns:
        float: Espérance ajustée de la grille.
    """
    total_nums = len(historique_nums)
    total_bonus = len(historique_bonus)

    freq_nums = Counter(historique_nums)
    freq_bonus = Counter(historique_bonus)

    def inv_freq_weight(nums, freq, total):
        return sum(1 - (freq.get(n, 0) / total) for n in nums) / len(nums) if nums else 0

    # Assurer que le bonus est une liste
    if isinstance(grille_bonus, int):
        grille_bonus = [grille_bonus]

    poids_nums = inv_freq_weight(grille_nums, freq_nums, total_nums)
    poids_bonus = inv_freq_weight(grille_bonus, freq_bonus, total_bonus)

    esperance_brute = prob_jackpot * montant_jackpot * facteur_unicite
    esperance_ajustee = esperance_brute * ((poids_nums + poids_bonus) / 2)

    return esperance_ajustee


def analyse(grilles, historique_data, prob_jackpot, montant_jackpot, facteur_unicite):
    """
    Analyse une liste de grilles en calculant leur espérance ajustée.

    Args:
        grilles (list of dict): Chaque dict contient au moins 'nums' (list[int]) et 'bonus' (list[int] or int).
        historique_data (dict): Dictionnaire avec 'nums' et 'bonus' historiques (list[int]).
        prob_jackpot (float): Probabilité officielle du jackpot.
        montant_jackpot (float): Montant estimé du jackpot.
        facteur_unicite (float): Facteur multiplicateur d'unicité.

    Returns:
        list of dict: Grilles enrichies avec la clé 'esperance_ajustee'.
    """
    historique_nums = historique_data.get('nums', [])
    historique_bonus = historique_data.get('bonus', [])

    resultats = []
    for grille in grilles:
        nums = grille.get('nums', [])
        bonus = grille.get('bonus', [])
        esperance = calculate_adjusted_expectancy(nums, bonus, historique_nums, historique_bonus, prob_jackpot, montant_jackpot, facteur_unicite)
        grille['esperance_ajustee'] = esperance
        resultats.append(grille)

    return resultats

class ExpectancyProcessor(StatisticalProcessor):
    """Processeur pour l'analyse des espérances ajustées."""
    
    def __init__(self, history: Union[Dict, pd.DataFrame], game_config: Dict[str, Any]):
        super().__init__(history, game_config)
        self._prob_jackpot: float = 0.0
        self._montant_jackpot: float = 0.0
        self._facteur_unicite: float = 1.0
        self._adjusted_expectancies: Dict[str, float] = {}
        
    @property
    def prob_jackpot(self) -> float:
        """Getter pour la probabilité du jackpot."""
        return self._prob_jackpot
        
    @prob_jackpot.setter
    def prob_jackpot(self, value: float):
        """Setter pour la probabilité du jackpot."""
        if not isinstance(value, (int, float)) or value <= 0:
            raise ValueError("La probabilité du jackpot doit être un nombre positif")
        self._prob_jackpot = float(value)
        
    @property
    def montant_jackpot(self) -> float:
        """Getter pour le montant du jackpot."""
        return self._montant_jackpot
        
    @montant_jackpot.setter
    def montant_jackpot(self, value: float):
        """Setter pour le montant du jackpot."""
        if not isinstance(value, (int, float)) or value < 0:
            raise ValueError("Le montant du jackpot doit être un nombre positif")
        self._montant_jackpot = float(value)
        
    @property
    def facteur_unicite(self) -> float:
        """Getter pour le facteur d'unicité."""
        return self._facteur_unicite
        
    @facteur_unicite.setter
    def facteur_unicite(self, value: float):
        """Setter pour le facteur d'unicité."""
        if not isinstance(value, (int, float)) or value <= 0:
            raise ValueError("Le facteur d'unicité doit être un nombre positif")
        self._facteur_unicite = float(value)
        
    @property
    def adjusted_expectancies(self) -> Dict[str, float]:
        """Getter pour les espérances ajustées."""
        return self._adjusted_expectancies
        
    @adjusted_expectancies.setter
    def adjusted_expectancies(self, value: Dict[str, float]):
        """Setter pour les espérances ajustées."""
        if not isinstance(value, dict):
            raise ValueError("Les espérances ajustées doivent être un dictionnaire")
        self._adjusted_expectancies = value
        
    @cache_result(ttl_seconds=3600)
    def process(self) -> Dict[str, float]:
        """Calcule les espérances ajustées pour chaque grille."""
        if self.data.empty:
            return {}
            
        try:
            historique_nums = self.data.get('nums', [])
            historique_bonus = self.data.get('bonus', [])
            
            if not historique_nums or not historique_bonus:
                raise ValueError("Données historiques incomplètes")
                
            total_nums = len(historique_nums)
            total_bonus = len(historique_bonus)
            
            freq_nums = Counter(historique_nums)
            freq_bonus = Counter(historique_bonus)
            
            resultats = {}
            for grille_id, grille in self.data.get('grilles', {}).items():
                nums = grille.get('nums', [])
                bonus = grille.get('bonus', [])
                
                if not nums:
                    continue
                    
                # Calcul des poids
                poids_nums = self._calculate_inverse_frequency_weight(nums, freq_nums, total_nums)
                poids_bonus = self._calculate_inverse_frequency_weight(bonus, freq_bonus, total_bonus)
                
                # Calcul de l'espérance
                esperance_brute = self._prob_jackpot * self._montant_jackpot * self._facteur_unicite
                esperance_ajustee = esperance_brute * ((poids_nums + poids_bonus) / 2)
                
                resultats[grille_id] = esperance_ajustee
                
            self._adjusted_expectancies = resultats
            return resultats
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul des espérances: {e}")
            return {}
            
    def _calculate_inverse_frequency_weight(self, numbers: List[int], frequencies: Counter, total: int) -> float:
        """Calcule le poids inverse de fréquence pour une liste de numéros."""
        if not numbers:
            return 0.0
            
        return sum(1 - (frequencies.get(n, 0) / total) for n in numbers) / len(numbers)

# Enregistrement du nouveau processeur
StatisticalProcessorFactory.register_processor('expectancy', ExpectancyProcessor)

# Fonction d'interface pour la compatibilité avec le code existant
@lru_cache(maxsize=128)
def analyse(grilles: List[Dict], historique_data: Dict, prob_jackpot: float, montant_jackpot: float, facteur_unicite: float) -> List[Dict]:
    """
    Analyse une liste de grilles en calculant leur espérance ajustée.
    
    Args:
        grilles: Liste de grilles à analyser
        historique_data: Données historiques
        prob_jackpot: Probabilité du jackpot
        montant_jackpot: Montant du jackpot
        facteur_unicite: Facteur d'unicité
        
    Returns:
        Liste des grilles avec espérance ajustée
    """
    try:
        processor = StatisticalProcessorFactory.create_processor('expectancy', historique_data, {})
        processor.prob_jackpot = prob_jackpot
        processor.montant_jackpot = montant_jackpot
        processor.facteur_unicite = facteur_unicite
        
        expectancies = processor.process()
        
        # Enrichissement des grilles avec les espérances
        for grille in grilles:
            grille_id = str(hash(tuple(grille.get('nums', []))))
            grille['esperance_ajustee'] = expectancies.get(grille_id, 0.0)
            
        return grilles
        
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse des grilles: {e}")
        return grilles