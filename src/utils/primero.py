import numpy as np
import pandas as pd
import soundfile as sf
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from soundfile import write

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

def generar_sweep_inverse(duracion,fs=44100 ,f_inferior=20 ,f_superior=20000):

    
    """
    Genera un barrido logarítmico de frecuencias (sine sweep) y un filtro inverso, entre f_inferior y f_superior.

    Parámetros
    ----------
    duracion : float
        Duración del barrido en segundos.
    fs : int, opcional
        Frecuencia de muestreo en Hz. Por defecto es 44100 Hz.
    f_inferior : float, opcional
        Frecuencia inferior del barrido en Hz. Por defecto es 20 Hz.
    f_superior : float, opcional
        Frecuencia superior del barrido en Hz. Por defecto es 20000 Hz.

    Returns
    -------
    sweep : np.ndarray
        Señal generada del barrido logarítmico normalizada.

    inverse_sweep : np.ndarray
        Señal generada del barrido logarítmico inverso normalizada.
    
    fs : int
        Frecuencia de muestreo utilizada.

    Ejemplo
    -------
    Generar un barrido logarítmico de frecuencias entre 20 Hz y 20000 Hz durante 10 segundos:

        sweep, inverse, fs = generar_sweep_inverse(10)
    """
    R = np.log(f_superior/f_inferior)
    muestras = int(duracion * fs)
    L = duracion/R
    K = L * 2 * np.pi * f_inferior

    #Generacion de vectores con numpy
    t = np.linspace(0, duracion, muestras, endpoint=False)
    sweep = np.sin(K * (np.exp(t/L) - 1 ))
    #Generacion de vectores con numpy
    m_t = f_inferior/((K/L) *(np.exp(t/L)))
    m_t *= sweep[::-1]
    inverse_sweep = m_t

    # Normalización, para evitar saturacion al reproducir
    sweep /= np.max(np.abs(sweep))
    inverse_sweep /= np.max(np.abs(inverse_sweep))

    return sweep.astype(np.float32), inverse_sweep.astype(np.float32), fs

def wav_to_b64(signal, fs):
    buf = BytesIO()
    write(buf, signal, fs, format='WAV')
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('ascii')