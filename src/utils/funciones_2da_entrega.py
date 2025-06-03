from ipywidgets import Button
from tkinter import Tk, filedialog
from IPython.display import clear_output, display
import soundfile as sf
import numpy as np
from sounds import generar_inverseSweep, generar_sweep
from scipy import signal
from graph import graficar_dominio_temporal

def ri_sintetizada(frecuencias: dict,fs=44100):
    """
    Genera una respuesta al impulso sintetizada a partir de un diccionario
    de frecuencias centrales y sus respectivos (T60, Amplitud).

    Parámetros
    ----------
    frecuencias : dict
        Clave = frecuencia central (Hz).
        Valor = tupla (T60_en_segundos, Amplitud).
    fs : int
        Frecuencia de muestreo (por defecto 44100 Hz).

    Retorna
    -------
    ri_sintetizada : ndarray (1D)
        Vector con las muestras de la RI normalizada en [-1, 1].
    """
    # Definimos duracion de RI 20% mayor a T60 por banda mas grande
    t60max = max(v[0] for v in frecuencias.values())
    segundos = 1.2 * t60max
    # Crear un vector de tiempo para la RI sintetizada
    t = np.arange(0, segundos, 1/fs)  
    
    # Inicializar la RI sintetizada
    ri_sintetizada = np.zeros_like(t)
    factor = 3 * np.log(10)

    for freq, (t60, A) in frecuencias.items():
        tau_i = factor/ t60
        ri_sintetizada += A* np.exp(-tau_i * t) * np.cos(2 * np.pi * freq * t)
       
    ri_sintetizada /= np.max(np.abs(ri_sintetizada))
    ri_int16 = (ri_sintetizada * 32767).astype(np.int16)
    sf.write('./audios/ri_sintetizada.wav', ri_int16, fs)
    return ri_sintetizada
def ri_sweep(grabacion, filtro_inverso,filename="RI_sweep.wav",fs=44100):
    """
    Devuelve la respuesta al impulso h[n] = (grabacion * filtro_inverso) en el dominio del tiempo,
    usando multiplicación de espectros (FFT).

    Parámetros
    ----------
    grabacion : array_like (1D)
        Arreglo de muestras de la señal grabada y[n] (por ejemplo, el sine‐sweep captado con micrófono).

    filtro_inverso : array_like (1D)
        Arreglo de muestras del filtro inverso k[n] que diseñaste para deconvolucionar el sine‐sweep.

    Returns
    -------
    h : ndarray (1D)
        Respuesta al impulso lineal h[n] = y[n] * k[n], de longitud len(grabacion) + len(filtro_inverso) - 1.
        Es un array real (dtype float) con la RI normalizada

    """
    # Longitud que debería tener la convolución lineal:
    N_lineal = len(grabacion) + len(filtro_inverso) - 1
    
    # Elegimos N_FFT como la siguiente potencia de 2 mayor a N_lineal (por eficiencia).
    
    N_FFT = 1 << int(np.ceil(np.log2(N_lineal)))
    
    # FFT de ambas señales completando el tamaño a N_FFT 
    FFT_grab = np.fft.fft(grabacion,      n=N_FFT)
    FFT_filt = np.fft.fft(filtro_inverso, n=N_FFT)
    
    RI = np.real(np.fft.ifft(FFT_grab * FFT_filt))
    RI = RI[:N_lineal]
    
    # Normalizar la respuesta al impulso
    RI /= np.max(np.abs(RI))
    
    # Exportamos como wav
    sf.write(filename,RI, fs)

    return RI
sweep,fs = sf.read("audios/sweep_aulaInformatica.wav") 
#h = sweep.shape[0]/fs
#inverse = generar_inverseSweep(h)
#ri_sweep_con_filtro = ri_sweep(sweep,inverse, filename="RI_aulaInformatica.wav")
def filtros_norma_IEC61260(audiodata, fs, tipo_filtro='octava', orden_filtro=4):
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
        frecuencias_centrales = [31.5, 63, 125, 250, 500, 1000, 2000, 4000, 8000]
    elif tipo_filtro == 'tercio_octava':
        G = 1.0 / 6.0
        # Frecuencias centrales de tercio de octava
        frecuencias_centrales = [25, 31.5, 40, 50, 63, 80, 100, 125, 160, 200, 250,
                                 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000,
                                 2500, 3150, 4000, 5000, 6300, 8000, 10000, 12500, 16000, 20000]
    else:
        raise ValueError("El tipo_filtro debe ser 'octava' o 'tercio_octava'")

    factor = np.power(2, G)
    señales_filtradas = {}

    print(f"Filtrando con filtros de {tipo_filtro}s (Orden: {orden_filtro})...")

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
        filt_signal = signal.sosfilt(sos, audiodata)
        señales_filtradas[centerFrequency_Hz] = filt_signal
        print(f"  Filtrada banda de {centerFrequency_Hz} Hz (cortes: {lowerCutoffFrequency_Hz:.2f}-{upperCutoffFrequency_Hz:.2f} Hz)")

    return señales_filtradas
def escala_log(ri):
    """
    Convierte la respuesta al impulso (ri) a escala logarítmica normalizada

    parámetros:
    ri (numpy array): señal de respuesta al impulso

    retorna:
    - r: (numpy array) señal transformada a escala logarítmica
    """

    a_max = np.max(np.abs(ri)) 
    
    # Calcular la señal en escala logarítmica
    r = 20 * np.log10(np.abs(ri) / a_max) 
    
    return r

"""audiodata, fs = sf.read("audios/ri_sintetizada.wav")
señales_octava = filtros_norma_IEC61260(audiodata, fs, tipo_filtro='octava', orden_filtro=4)
#sf.write("RI_125HZ.wav",señales_octava.get(125),fs)
escala_log = escala_log(señales_octava.get(125))
t = np.arange(len(escala_log)) / 44100
graficar_dominio_temporal(t,escala_log)
"""