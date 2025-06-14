import numpy as np

def regresion_lineal(x, y):
    """
    Regresión lineal propia por mínimos cuadrados (forma matricial).

    Parámetros
    ----------
    x : np.ndarray, forma (n,)
    y : np.ndarray, forma (n,)

    Retorna
    -------
    y_pred : np.ndarray
        Predicciones de la recta.
    a, b : float
        Pendiente y ordenada al origen.
    """
    x = np.asarray(x)
    y = np.asarray(y)
    n = len(x)

    Sx  = np.sum(x)
    Sy  = np.sum(y)
    Sxx = np.sum(x * x)
    Sxy = np.sum(x * y)

    a = (n * Sxy - Sx * Sy) / (n * Sxx - Sx**2)
    b = (Sy - a * Sx) / n

    return {'slope':a,'intercept':b}

def regresion_lineal_en_intervalo(x, y, lim_sup, lim_inf):
    """
    Ajusta una recta a y(t) en el tramo [lim_sup, lim_inf] dB.

    Retorna:
    - Dict: {'slope': pendiente, 'intercept': ordenada al origen}
    """
    #1. Selecciona únicamente los elementos que pertenecen a [lim_inf, lim_sup]. 
    mask = (y <= lim_sup) & (y >= lim_inf)

    #2. Ajuste lineal
    ajuste_lineal = regresion_lineal(x[mask], y[mask])
    return ajuste_lineal

def calcular_parametros_acusticos(signal_db, fs):
    """
    Calcula todos los parámetros acústicos a partir de una curva de decaimiento.
    
    Argumentos:
    - signal_db: Array con la curva de decaimiento de Schroeder en dB.
    - fs: Frecuencia de muestreo.

    Retorna:
    - dict con los parámetros calculados para esa curva.
    Dict: {"EDT":,"T60_from_T10":,"T60_from_T20":,"T60_from_T30":}
    """

    #Vector de tiempo
    t = np.arange(len(signal_db))/fs

    #Normalizar para que el máximo sea 0 dB
    signal_db_norm = signal_db - np.max(signal_db)

    # 1) EDT: tramo  -1  → -11 dB
    edt = regresion_lineal_en_intervalo(t, signal_db_norm,  -1, -11)
    edt = -60.0 / edt['slope'] 

    # 2) T10: tramo -5  → -15 dB
    t10 = regresion_lineal_en_intervalo(t, signal_db_norm,  -5, -15)
    t60_from_t10 = -60.0 / t10['slope']


    # 3) T20: tramo -5  → -25 dB
    t20 = regresion_lineal_en_intervalo(t, signal_db_norm,  -5, -25)
    t60_from_t20 = -60.0 / t20['slope']

    # 4) T30: tramo -5  → -35 dB
    m_t30 = regresion_lineal_en_intervalo(t, signal_db_norm,  -5, -35)
    t60_from_t30 = -60.0 / m_t30['slope']

    return {
        'EDT': edt,
        'T60_from_T10': t60_from_t10,
        'T60_from_T20': t60_from_t20,
        'T60_from_T30': t60_from_t30
    }