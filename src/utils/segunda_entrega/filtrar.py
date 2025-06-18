from scipy import signal
import numpy as np
from ..constantes.filtros import (
    FRECUENCIAS_OCTAVA,
    FRECUENCIAS_TERCIO_OCTAVA,
    FACTOR_ANCHO_OCTAVA,
    FACTOR_ANCHO_TERCIO_OCTAVA
)


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
        G = FACTOR_ANCHO_OCTAVA
        frecuencias_centrales = FRECUENCIAS_OCTAVA
    elif tipo_filtro == 'tercio_octava':
        G = FACTOR_ANCHO_TERCIO_OCTAVA
        frecuencias_centrales = FRECUENCIAS_TERCIO_OCTAVA
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