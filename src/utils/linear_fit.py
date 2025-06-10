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

    y_pred = a * x + b
    return y_pred, a, b



