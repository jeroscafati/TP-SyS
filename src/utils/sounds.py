import numpy as np
import pandas as pd
import soundfile as sf
import sounddevice as sd

def ruidoRosa_voss_editado(t, fs=44100, ncols=16):
    """
    Genera ruido rosa utilizando el algoritmo de Voss-McCartney.
    El algoritmo genera ruido rosa mezclando varias fuentes de números aleatorios, pero no todas cambian al mismo tiempo. Algunas cambian muy rápido (alta frecuencia), otras más lentamente (baja frecuencia).
    Así se logra que el resultado tenga más energía en bajas frecuencias, como el ruido rosa real.
    
    .. Nota:: si 'ruidoRosa.wav' existe, este será sobreescrito
    
    Parametros
    ----------
    t : float
        Valor temporal en segundos, este determina la duración del ruido generado.
    ncols: int
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
        import pandas as pd
        import soundfile as sf
        
        ruidoRosa_voss(10)
    """
    
    nrows = int(t * fs) # La longitud de la señal es el producto entre su duración en segundos, y cuántas muestras realiza por segundo (fs).

    array = np.full((nrows, ncols), np.nan) # Se crea una tabla de tamaño nrows (tiempo) × ncols (número de generadores). Todo se llena con NaN inicialmente.
    array[0, :] = np.random.random(ncols)
    array[:, 0] = np.random.random(nrows)
    
    n = nrows 
    cols = np.random.geometric(0.5, n)
    cols[cols >= ncols] = 0 
    rows = np.random.randint(nrows, size=n)
    array[rows, cols] = np.random.random(n) # En esas posiciones [row, col], coloca un nuevo número aleatorio. Algunas columnas se actualizarán más que otras, para generar el ruido rosa.
    
    df = pd.DataFrame(array)
    filled = df.fillna(method='ffill', axis=0)
    total = filled.sum(axis=1) # Suma todas las filas, así se obtiene un vector de con el ruido rosa (de más a menos energía en frecuencias).
    
    ## Centrado de el array en 0
    total = total - total.mean() 
    
    ## Normalizado
    valor_max = max(abs(max(total)),abs(min(total)))
    total = total / valor_max
    
    sf.write('./audios/RuidoRosa.wav', total, fs)
    
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

    return sweep, inverse_sweep, fs

def grabar_reproducir(signal,fs=44100):
    """
    Reproduce una señal de audio y graba simultáneamente desde el dispositivo seleccionado.

    Parámetros
    ----------
    signal : np.ndarray
        Array 1D con la señal de audio a reproducir.
    fs : int, opcional
        Frecuencia de muestreo en Hz. Por defecto es 44100 Hz.

    Returns
    --------
    None
        La función guarda directamente el archivo de grabación con nombre "grabacion.wav".

    """
    print("Dispositivos disponibles: ")
    print(sd.query_devices()) # muestra los dispositivos disponibles

    dispositivo = int(input("Ingrese número de dispositivo: "))
    sd.default.device = dispositivo # se usa el dispositivo seleccionado como default
    sd.default.samplerate = fs # se determina la frecuncia de muestreo


    grabacion = sd.playrec(signal, samplerate=fs, channels=1) # reproduzco y grabo a la vez
    sd.wait()

    sf.write("./audios/grabacion.wav", grabacion, fs) #guardo la grabacion

def medir_latencia(fs=44100, duracion=1.0):
    """
    Mide la latencia de reproducción y grabación de la función playrec de sounddevice.
    Se reproduce un impulso y se graba la señal de salida. Luego, se calcula la latencia.

    Parámetros
    ----------
    fs : int
        Frecuencia de muestreo en Hz. Por defecto es 44100 Hz.
    duracion : float
        Duración de la señal en segundos. Por defecto es 1 segundo.
    
    Returns
    -------     
    latencia_ms : float
        Latencia estimada en milisegundos.
    """
    # Crear un pulso (impulso en el tiempo)
    signal = np.zeros(int(fs * duracion))
    signal[100] = 1.0  # Impulso en la muestra 100
    signal = signal.reshape(-1, 1)  # Asegura forma (N, 1) para mono

    print("Reproduciendo y grabando...")
    grabacion = sd.playrec(signal, samplerate=fs, channels=1)
    sd.wait()

    # Procesamiento para encontrar la latencia
    grabado = grabacion.flatten()
    impulso_original = 100

    # Buscar el pico más grande en la grabación
    pico_grabado = np.argmax(np.abs(grabado))

    desfase_muestras = pico_grabado - impulso_original
    latencia_ms = (desfase_muestras / fs) * 1000

    print(f"Desfase: {desfase_muestras} muestras")
    print(f"Latencia estimada: {latencia_ms:.2f} ms")

    return latencia_ms   
