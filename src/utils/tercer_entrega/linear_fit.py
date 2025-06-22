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
