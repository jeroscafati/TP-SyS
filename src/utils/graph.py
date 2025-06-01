import matplotlib.pyplot as plt

def graficar_dominio_temporal(t, signal):
    """
    Grafica la señal en el dominio temporal.

    Parámetros
    ----------
    t : array_like
        Vector de tiempo correspondiente a la señal (en segundos).
    signal : array_like
        Señal a graficar.

    Returns
    -------
    None
        La función no retorna nada. Muestra una gráfica de la señal en el dominio temporal.

    Ejemplo
    -------
    Graficar el dominio temporal de una señal de ruido rosa.

        import numpy as np
        import matplotlib.pyplot as plt

        t = np.linspace(0, 10, 441000)  # 10 segundos con fs = 44100 Hz
        x = ruidoRosa_voss(10)
        graficar_dominio_temporal(t, x)
    """
    plt.figure(figsize=(10, 4))
    plt.plot(t, signal, color='m')
    plt.title('Señal en el dominio temporal')
    plt.xlabel('Tiempo [s]')
    plt.ylabel('Amplitud')
    plt.grid(True)
    plt.show()
    return None

