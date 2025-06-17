import numpy as np
from scipy import signal

def hilbert_transform(s_t):
    """
    Suaviza una señal obteniendo su envolvente a través de una implementación
    de la Transformada de Hilbert.

    Args:
    s_t (np.ndarray): La señal de entrada.

    Returns:
    np.ndarray: La envolvente de la señal (envolvente).
    """

    N = len(s_t)

    # Llevamosal dominio de frecuencias s(t)->S(w)
    S_w = np.fft.fft(s_t)

    # h representa a (1+sgn(w))
    h = np.zeros(N)

    #frecuencias positivas:
    # En el array FFT,ellas van desde 1 hasta la mitad
    h[1:N//2] = 2
    h[0]=1
    #Para la frecuencia de Nyquist del punto medio (solo  si N es par),  no tiene un conjugado negativo.
    if N % 2 == 0:
        h[N // 2] = 1

    #obtenemos la señal analitica como S_a(t)= F⁻¹{(S(w)(1+sgn(w))}
    S_w *= h 
    analitica = np.fft.ifft(S_w)

    #Calculamos la envolvente de la señal
    envolvente = np.abs(analitica)

    return envolvente

def filtro_promedio_movil(x, L):
    """
    Aplica un filtro de promedio móvil de longitud L a una señal x.
    
    Parámetros:
    ------------
    x : ndarray
        Señal de entrada (1D, array de valores reales o complejos).
    L : int
        Longitud (muestras) de la ventana de promedio.
    
    Retorna:
    --------
    y : ndarray
        Señal suavizada.
    """
    if L < 1:
        raise ValueError("La longitud L debe ser mayor o igual a 1")

    # Creamos la ventana deslizante
    kernel = np.ones(L) / L

    # Convolucionamos
    y = np.convolve(x, kernel, mode='same')  
    return y

def filtrar_signal(audiodata, fs, tipo_filtro='octava', orden_filtro=4):
    """
    Filtra una señal de audio en bandas de octava o tercio de octava según la norma IEC 61260.

    Args:
        audiodata (np.array): La señal de audio a filtrar.
        fs (int): Frecuencia de muestreo de la señal de audio (Hz).
        tipo_filtro (str): 'octava' para filtros de octava, 'tercio_octava' para tercios de octava.
        orden_filtro (int): El grado del filtro IIR.

    Returns:
        dict: Un diccionario donde las claves son las frecuencias centrales (Hz)
              y los valores son las señales de audio filtradas para esa banda.
    """

    if tipo_filtro == 'octava':
        G = 1.0 / 2.0
        # Frecuencias centrales de octava
        frecuencias_centrales = [125, 250, 500, 1000, 2000, 4000, 8000]
    elif tipo_filtro == 'tercio_octava':
        G = 1.0 / 6.0
        # Frecuencias centrales de tercio de octava
        frecuencias_centrales = [125, 160, 200, 250,
                                 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000,
                                 2500, 3150, 4000, 5000, 6300, 8000]
    else:
        raise ValueError("El tipo_filtro debe ser 'octava' o 'tercio_octava'")

    factor = np.power(2, G)
    señales_filtradas = {}


    for centerFrequency_Hz in frecuencias_centrales:
        lowerCutoffFrequency_Hz = centerFrequency_Hz / factor
        upperCutoffFrequency_Hz = centerFrequency_Hz * factor

        sos = signal.iirfilter(orden_filtro,
                               [lowerCutoffFrequency_Hz, upperCutoffFrequency_Hz],
                               rs=60,
                               btype='band',
                               analog=False,
                               ftype='butter', 
                               fs=fs,
                               output='sos')

        # Aplicando el filtro al audio
        filt_signal = signal.sosfiltfilt(sos, audiodata)
        señales_filtradas[centerFrequency_Hz] = filt_signal
        
    return señales_filtradas