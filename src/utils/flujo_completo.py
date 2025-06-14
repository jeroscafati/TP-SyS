from generar_ri import sintetizar_RI,escala_log,filtrar_signal
from suavizado import filtro_promedio_movil, hilbert_transform
from schroeder_lundeby import integral_schroeder
from linear_fit import calcular_parametros_acusticos

def obtener_parametros_de_RI(ri,fs,banda='octava',ventana_suavizado_ms=5):
    """
    Procesa una respuesta al impulso multibanda y calcula sus parámetros acústicos.

    Esta función toma la señal de respuesta al impulso sintetizada o cargada,
    la filtra en bandas de octava (o tercio de octava), extrae la envolvente
    mediante transformada de Hilbert y promedio móvil, aplica la integración
    inversa de Schroeder, la convierte a escala logarítmica y finalmente estima
    los principales tiempos de reverberación (EDT, T20, T30, etc.) para cada banda.

    Parámetros:
    -----------
    signal : Array 1d que contiene la señal de respuesta.
    fs : int
        Frecuencia de muestreo de la señal (Hz).
    banda : {'octava', 'tercio_octava'}, opcional
        Por defecto 'octava'.
    ventana_suavizado_ms : float, opcional
        Duración de la ventana de promedio móvil para suavizar la envolvente,
        en milisegundos. Por defecto 5 ms.

    Retorna:
    --------
    parametros_acusticos : dict
        Diccionario cuyos keys son las frecuencias centrales de cada banda (Hz)
        y cuyos values son a su vez diccionarios con los parámetros acústicos
        calculados:
          - 'EDT'            : Early Decay Time (s)
          - 'T60_from_T20'   : Tiempo de reverberación estimado de -5 a -25 dB (s)
          - 'T60_from_T30'   : Tiempo de reverberación estimado de -5 a -35 dB (s)
          - ...              : otros parámetros e

    Ejemplo de uso:
    ---------------
    >>> result = obtener_parametros_de_RI(ri_sintetizada, fs=48000,
                                          banda='tercio_octava',
                                          ventana_suavizado_ms=10)
    >>> print(result[1000]['T60_from_T30'])
    1.23
    """

    ventana_suavizado_muestras = int(ventana_suavizado_ms*1e-3 * fs)
    
    #1 Filtro de banda
    ri_octavas = filtrar_signal(ri, fs, tipo_filtro=banda)

    #2. Suavizado envolvente + promedio movil
    suavizado_octavas = {}
    for freq,signal in ri_octavas.items():
        suavizado_octavas[freq] = filtro_promedio_movil(hilbert_transform(signal),L=ventana_suavizado_muestras)
    
    #3. Schroeder
    curva_decay = {}
    for freq,signal in suavizado_octavas.items():
        curva_decay[freq] = integral_schroeder(signal,fs)

    #4. Escala log
    curva_decay_db = {}
    for freq,signal in curva_decay.items():
        curva_decay_db[freq] = escala_log(signal)
   
    
    #5. Calcular parámetros acústicos
    parametros_acusticos = {}
    for freq, signal in curva_decay_db.items():
        parametros_acusticos[freq] = calcular_parametros_acusticos(signal, fs)

    return parametros_acusticos