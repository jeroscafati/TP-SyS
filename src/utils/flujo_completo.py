from utils.linear_fit_y_db_scale import escala_log
from utils.suavizado_y_filtros import filtro_promedio_movil, hilbert_transform, filtrar_signal
from utils.schroeder_lundeby import integral_schroeder, lundeby
from utils.param_acusticos import calcular_parametros_acusticos

def obtener_parametros_de_RI(ri,fs,banda='octava',ventana_suavizado_ms=5,debug_mode = False):
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
          - 'T60_from_T10'   : Tiempo de reverberación estimado de -5 a -15 dB (s)          
          - 'T60_from_T20'   : Tiempo de reverberación estimado de -5 a -25 dB (s)
          - 'T60_from_T30'   : Tiempo de reverberación estimado de -5 a -35 dB (s)
          - 'C80'            : Claridad C80 en dB
          - 'D50'            : Porcentaje de energía en los primeros 50 ms
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
    
    #2.5 Lundeby
    lundeby_ = {}
    datos_lundeby = {}
    #Analizamos si estamos en modo depuracion
    for freq,signal in suavizado_octavas.items():
            res = lundeby(signal, fs, return_debug_data=debug_mode)
            lundeby_[freq] = res
            #Analizamos si estamos en modo depuracion
            if debug_mode:
                datos_lundeby[freq] = res
                t_lundaby = res['idx_cruce']
                lundeby_[freq] = t_lundaby     

    #3. Schroeder
    curva_decay = {}
    for freq,signal in suavizado_octavas.items():
        curva_decay[freq] = integral_schroeder(signal,fs,lundeby_[freq])

    #4. Escala log
    curva_decay_db = {}
    for freq,signal in curva_decay.items():
        curva_decay_db[freq] = escala_log(signal['schroeder'])
   
    
    #5. Calcular parámetros acústicos
    parametros_acusticos = {}
    datos_regresion = {}
    for freq, signal in curva_decay_db.items():
        resultado = calcular_parametros_acusticos(signal,
                                                            p2=curva_decay[freq]['p2'],
                                                            fs=fs,
                                                            return_regs=debug_mode)
        if debug_mode:
             param_dict, debug_dict = resultado
             datos_regresion[freq] = debug_dict
             parametros_acusticos[freq] = param_dict 
        else:
            parametros_acusticos[freq] = resultado
    if not debug_mode:
        return parametros_acusticos
    else:
         datos_debug = {
              'ri_filtradas': ri_octavas,
              'curvas_decay_db': curva_decay_db,
              'datos_lundeby': datos_lundeby,
              'datos_regresion': datos_regresion }
         
         return (parametros_acusticos,datos_debug)