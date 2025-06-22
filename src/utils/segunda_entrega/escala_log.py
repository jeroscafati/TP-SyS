import numpy as np  
    
def escala_log(signal):
    """
    Convierte un array a escala logarítmica normalizada.

    Parámetros:
    signal (numpy array): por ejemplo, señal de respuesta al impulso

    Retorna:
    - signal_db (numpy array): señal convertida a escala logarítmica
    """
    a_max = np.max(np.abs(signal))

    # Normalizar la señal
    signal_norm = np.abs(signal) / a_max

    # Evitar log(0): forzar un mínimo valor positivo
    signal_norm_clipped = np.clip(signal_norm, 1e-10, None)

    # Calcular en escala logarítmica
    signal_db = 10 * np.log10(signal_norm_clipped)

    return signal_db