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
    
    Esta función aplica un banco de filtros paso banda a la señal de audio de entrada,
    dividiéndola en diferentes bandas de frecuencia según el tipo de filtro especificado.
    Utiliza filtros Butterworth implementados como cascada de secciones de segundo orden (SOS).

    Args:
        audiodata (np.array): La señal de audio a filtrar. Debe ser un array 1D de numpy.
        fs (int): Frecuencia de muestreo de la señal de audio en Hz (ej: 44100, 48000).
        tipo_filtro (str, optional): Tipo de filtro a aplicar. Debe ser:
            - 'octava': Para filtros de octava (ancho de banda de 1 octava)
            - 'tercio_octava': Para filtros de tercio de octava (ancho de banda de 1/3 de octava)
            Por defecto es 'octava'.
        orden_filtro (int, optional): Orden del filtro IIR Butterworth. Un valor más alto
            proporciona una pendiente más pronunciada pero puede introducir más retardo.
            Por defecto es 4.

    Returns:
        dict: Un diccionario donde:
            - Claves: Frecuencias centrales de las bandas en Hz (float)
            - Valores: Arrays de numpy con las señales de audio filtradas para cada banda

    Raises:
        ValueError: Si el tipo_filtro no es 'octava' ni 'tercio_octava'.

    Example:
        >>> # Filtrado de señal de audio con filtros de octava
        >>> señales_filtradas = filtrar_signal(audio_data, fs=44100, tipo_filtro='octava')
        >>> # Acceder a la señal filtrada para 1000 Hz
        >>> señal_1k = señales_filtradas[1000.0]
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