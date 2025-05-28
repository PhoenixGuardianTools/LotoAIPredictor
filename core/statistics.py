# core/statistics.py (extraits modifiés/ajoutés)

import numpy as np
from scipy.stats import norm
from statsmodels.tsa.seasonal import seasonal_decompose
import pywt

# Importation conditionnelle de TensorFlow
# try:
#     from tensorflow.keras.models import Sequential
#     from tensorflow.keras.layers import LSTM, Dense
#     from tensorflow.keras.optimizers import Adam
#     TENSORFLOW_AVAILABLE = True
# except ImportError:
#     TENSORFLOW_AVAILABLE = False
#     print("TensorFlow n'est pas disponible. Les fonctionnalités LSTM seront désactivées.")

def permutation_test_pattern_significance(history_df, game_config, n_perm=1000):
    """Test permutation sur patterns pour valider leur signification statistique."""
    patterns = detect_repeating_patterns(history_df, game_config)
    if not patterns:
        return {}

    observed_counts = {p: sum(history_df['numbers'].apply(lambda x: set(p).issubset(x))) for p in patterns}

    permuted_counts = []
    for _ in range(n_perm):
        shuffled = history_df['numbers'].sample(frac=1, replace=False).reset_index(drop=True)
        counts = {p: sum(shuffled.apply(lambda x: set(p).issubset(x))) for p in patterns}
        permuted_counts.append(counts)

    p_values = {}
    for p in patterns:
        perm_vals = [pc[p] for pc in permuted_counts]
        obs = observed_counts[p]
        p_val = np.mean([1 if val >= obs else 0 for val in perm_vals])
        p_values[p] = p_val
    return p_values

# def lstm_prediction_weight(history_df, game_config):
#     """Utilise un LSTM sur la série temporelle des tirages pour pondérer les numéros."""
#     if not TENSORFLOW_AVAILABLE:
#         print("TensorFlow n'est pas disponible. Retour des poids par défaut.")
#         return {num: 1.0 for num in game_config['pool']}
#     
#     try:
#         from tensorflow.keras.preprocessing.sequence import pad_sequences
#         
#         # Préparer séquences
#         seqs = [list(map(int, draw)) for draw in history_df['numbers']]
#         max_len = game_config['numbers']
# 
#         X = pad_sequences(seqs, maxlen=max_len, padding='post')
#         y = np.zeros((len(X), game_config['pool']))
# 
#         for i, seq in enumerate(X):
#             for num in seq:
#                 if num > 0:
#                     y[i, num-1] = 1
# 
#         model = Sequential()
#         model.add(LSTM(64, input_shape=(max_len, 1), activation='relu'))
#         model.add(Dense(game_config['pool'], activation='sigmoid'))
#         model.compile(loss='binary_crossentropy', optimizer=Adam())
# 
#         # Reshape X pour LSTM
#         X = np.expand_dims(X, axis=2)
#         model.fit(X, y, epochs=5, verbose=0)
# 
#         # Prédiction moyenne des poids par numéro
#         preds = model.predict(X[-1].reshape(1, max_len,1))[0]
#         weights = {num+1: float(preds[num]) for num in range(game_config['pool'])}
#         return weights
#     except Exception as e:
#         print(f"Erreur lors de l'utilisation du LSTM : {str(e)}")
#         return {num: 1.0 for num in game_config['pool']}

def wavelet_decomposition_trends(history_df, game_config):
    """Décompose les tirages en composantes via Wavelet et analyse les tendances."""
    all_nums = [num for draw in history_df['numbers'] for num in draw]
    coeffs = pywt.wavedec(all_nums, 'db1', level=3)
    trends = coeffs[0]  # Approximation coefficients

    weights = {}
    norm_trends = (trends - np.min(trends)) / (np.max(trends) - np.min(trends) + 1e-6)
    for i,num in enumerate(game_config['pool'][:len(norm_trends)]):
        weights[num] = norm_trends[i]
    return weights

def fft_spectral_analysis(history_df, game_config):
    """Analyse FFT sur la série temporelle des numéros."""
    all_nums = [num for draw in history_df['numbers'] for num in draw]
    fft_vals = np.abs(np.fft.fft(all_nums))
    fft_norm = fft_vals / (np.max(fft_vals) + 1e-6)
    weights = {}
    for i, num in enumerate(game_config['pool'][:len(fft_norm)]):
        weights[num] = fft_norm[i]
    return weights

def get_frequent_numbers(*args, **kwargs):
    return {}
def detect_repeating_patterns(*args, **kwargs):
    return []
def apply_lunar_cycle_weight(*args, **kwargs):
    return {}
def detect_positive_sequences(*args, **kwargs):
    return []
def detect_fractal_patterns(*args, **kwargs):
    return {}
def game_theory_analysis(*args, **kwargs):
    return {}
def evaluate_periodic_trends(*args, **kwargs):
    return {}
def bayesian_adjustment(*args, **kwargs):
    return {}
def markov_trend_prediction(*args, **kwargs):
    return {}
def neural_network_weighting(*args, **kwargs):
    return {}
def detect_anomalies(*args, **kwargs):
    return []
def optimize_loto_weights(*args, **kwargs):
    return {}
def analyze_standard_deviation(*args, **kwargs):
    return {}
def adaptive_probability_adjustment(*args, **kwargs):
    return {}
def evolutionary_algorithm_tuning(*args, **kwargs):
    return {}
def monte_carlo_simulation(*args, **kwargs):
    return {}
def cluster_number_selection(*args, **kwargs):
    return {}
def detect_long_term_cycles(*args, **kwargs):
    return []
