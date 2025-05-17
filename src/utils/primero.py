import numpy as np
import pandas as pd
import soundfile as sf
import matplotlib.pyplot as plt

def ruidoRosa_voss(t, ncols=16, fs=44100):
    """
    Genera ruido rosa utilizando el algoritmo de Voss-McCartney(https://www.dsprelated.com/showabstract/3933.php).

    .. Nota:: si 'ruidoRosa.wav' existe, este será sobreescrito

    Parametros
    ----------
    t : float
        Valor temporal en segundos, este determina la duración del ruido generado.
    rcols: int
        Determina el número de fuentes a aleatorias a agregar.
    fs: int
        Frecuencia de muestreo en Hz de la señal. Por defecto el valor es 44100 Hz.

    returns: NumPy array
        Datos de la señal generada.

    Ejemplo
    -------
    Generar un `.wav` desde un numpy array de 10 segundos con ruido rosa a una
    frecuencia de muestreo de 44100 Hz.

        import numpy as np
        import soundfile as sf
        from scipy import signal

        ruidoRosa_voss(10)
    """

    nrows = int(t*fs)
    array = np.full((nrows, ncols), np.nan)
    array[0, :] = np.random.random(ncols)
    array[:, 0] = np.random.random(nrows)

    # el numero total de cambios es nrows
    n = nrows
    cols = np.random.geometric(0.5, n)
    cols[cols >= ncols] = 0
    rows = np.random.randint(nrows, size=n)
    array[rows, cols] = np.random.random(n)

    df = pd.DataFrame(array)
    filled = df.ffill(axis=0)
    total = filled.sum(axis=1)

    ## Centrado de el array en 0
    total = total - total.mean()

    ## Normalizado
    valor_max = max(abs(max(total)), abs(min(total)))
    total = total / valor_max

    # Agregar generación de archivo de audio .wav
    sf.write('ruidoRosa.wav', total,fs)
    return total

def plot_signal(signal, fs=44100, start=0.0, end=None):
    """
    Visualiza el dominio temporal de una señal.

    Parámetros
    ----------
    signal : numpy.ndarray
        Vector de datos de la señal.
    fs : int, opcional
        Frecuencia de muestreo en Hz (por defecto 44100).
    start : float, opcional
        Tiempo inicial en segundos para la visualización (por defecto 0.0).
    end : float or None, opcional
        Tiempo final en segundos para la visualización. Si es None, muestra hasta el final.
    """
    # Convertir tiempos a índices
    start_idx = int(start * fs)
    end_idx = int(end * fs) if end is not None else len(signal)

    t = np.linspace(start, start + (end_idx - start_idx) / fs,
                    num=end_idx - start_idx, endpoint=False)

    plt.style.use('ggplot')
    plt.figure(figsize=(10, 4))
    plt.plot(t, signal[start_idx:end_idx])
    plt.xlabel('Tiempo [s]')
    plt.ylabel('Amplitud')
    plt.title('Dominio temporal de la señal')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def generar_sweep(duracion,fs=44100 ,f_inferior=20 ,f_superior=20000):

    R = np.log(f_superior/f_inferior)
    muestras = int(duracion * fs)
    L = duracion/R
    K = L * 2 * np.pi * f_inferior

    #Generacion de vectores con numpy
    t = np.linspace(0, duracion, muestras, endpoint=False)
    sweep = np.sin(K * (np.exp(t/L) - 1 ))

    # Normalización, para evitar saturacion al reproducir
    sweep /= np.max(np.abs(sweep))

    return sweep.astype(np.float32), fs

def generar_inv_Sweep(duracion, fs=44100, f_inferior=20, f_superior=20000):
    R = np.log(f_superior / f_inferior)
    L = duracion / R
    K = L * 2 * np.pi * f_inferior
    muestras = int(duracion * fs)

    # Generacion de vectores con numpy
    t = np.linspace(0, duracion, muestras, endpoint=False)
    w_t = 2 * np.pi * f_inferior * np.exp(t/L)

    sweep = np.sin(K * (np.exp(t / L) - 1))