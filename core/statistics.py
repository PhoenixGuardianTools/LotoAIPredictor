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
from typing import Dict, List, Set, Union, Any, Tuple
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

def combine_weights(weights_dict):
    """
    Combine les poids de tous les modules en score global pondéré.
    """
    score = 0.0
    poids_modules = {
        'freq_nums': 0.3,
        'pattern_nums': 0.15,
        'lunar_cycle': 0.05,
        'positive_seq': 0.1,
        'fractal': 0.05,
        'game_theory': 0.05,
        'periodic_trends': 0.05,
        'bayesian': 0.05,
        'markov': 0.05,
        'neural_net': 0.05,
        'anomalies': 0.03,
        'loto_opt': 0.03,
        'std_dev': 0.02,
        'adaptive_prob': 0.02,
        'evolutionary': 0.02,
        'monte_carlo': 0.02,
        'clustering': 0.02,
        'long_term_cycles': 0.02,
        'permutation_test': 0.01,
        'wavelet': 0.01,
        'fft': 0.01,
        'bayes_net': 0.02,
    }

    for module_name, weight in poids_modules.items():
        module_value = weights_dict.get(module_name, 0)
        if isinstance(module_value, dict):
            module_score = sum(module_value.values())
        elif isinstance(module_value, (int, float)):
            module_score = module_value
        else:
            module_score = 0
        score += weight * module_score

    return score

def detect_fractal_patterns(history, game_config):
    """
    Analyse fractale pour motifs auto-similaires.
    """
    fractal_scores = {}
    return fractal_scores
