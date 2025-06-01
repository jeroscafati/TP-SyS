from ipywidgets import Button
from tkinter import Tk, filedialog
from IPython.display import clear_output, display
import soundfile as sf
import numpy as np
from sounds import generar_inverseSweep, generar_sweep


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
    
    # Normalizar la respuesta al impulso
    RI /= np.max(np.abs(RI))
    
    # Exportamos como wav
    sf.write(filename,RI, fs)

    return RI
sweep,fs = sf.read("audios/sweep_aulaInformatica.wav") 
h = sweep.shape[0]/fs
inverse = generar_inverseSweep(h)
ri_sweep_con_filtro = ri_sweep(sweep,inverse, filename="RI_aulaInformatica.wav")
