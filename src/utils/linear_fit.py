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

def parametros_por_octava(regs, ir=None, fs=None):
    """
    Calcula parámetros acústicos por banda de octava a partir de ajustes lineales ya realizados.

    Argumentos:
    - regs: dict con llaves de frecuencia (e.g. '250', '500', ...) y como valor otro dict con:
        - 'slope': pendiente en dB/s
        - 'intercept': ordenada de la recta (opcional)
      Ejemplo:
        regs = {
            '250': {'slope': m_250, 'intercept': b_250},
            '500': {'slope': m_500, 'intercept': b_500},
            ...
        }
    - ir: (opcional) señal de RI para calcular D50 y C80
    - fs: (opcional) frecuencia de muestreo en Hz

    Retorna:
      dict: para cada frecuencia, un sub-dict con:
        'EDT', 'T60_T10', 'T60_T20', 'T60_T30', 'D50', 'C80'
    """
    results = {}
    for freq, info in regs.items():
        slope = info['slope']
        # 1) EDT: caída 0→-10 dB
        edt = -10.0 / slope
        # 2) T10: caída -5→-15 dB (10 dB)
        t10 = -10.0 / slope
        T60_t10 = 6.0 * t10
        # T20: caída -5→-25 dB (20 dB)
        t20 = -20.0 / slope
        T60_t20 = 3.0 * t20
        # T30: caída -5→-35 dB (30 dB)
        t30 = -30.0 / slope
        T60_t30 = 2.0 * t30

        d50 = None
        c80 = None
        if ir is not None and fs is not None:
            e2 = ir**2
            n50 = int(0.05 * fs)
            d50 = np.sum(e2[:n50]) / np.sum(e2)
            n80 = int(0.08 * fs)
            c80 = 10 * np.log10(np.sum(e2[:n80]) / np.sum(e2[n80:]))

        results[freq] = {
            'EDT': edt,
            'T60_from_T10': T60_t10,
            'T60_from_T20': T60_t20,
            'T60_from_T30': T60_t30,
            'D50': d50,
            'C80': c80
        }
    return results

def calcular_parametros_acusticos(signal_db, fs):
    """
    Calcula todos los parámetros acústicos a partir de una curva de decaimiento.
    
    Argumentos:
    - signal_db: Array con la curva de decaimiento de Schroeder en dB.
    - fs: Frecuencia de muestreo.

    Retorna:
    - dict con los parámetros calculados para esa curva.
    """
    #Vector de tiempo
    t = np.arange(len(signal_db))/fs

    #Normalizar para que el máximo sea 0 dB
    signal_db_norm = signal_db - np.max(signal_db)

    # 1) EDT: tramo  0  → -10 dB
    edt = regresion_lineal_en_intervalo(t, signal_db_norm,  0, -10)
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