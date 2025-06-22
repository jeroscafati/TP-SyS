import numpy as np
from utils.segunda_entrega.escala_log import escala_log
from utils.tercer_entrega.linear_fit import regresion_lineal_en_intervalo

def calcular_rms_por_bloques(ir, fs, ms_bloque=20):
    """
    Divide una respuesta al impulso en bloques de duración fija y calcula el valor RMS de cada uno.

    Parámetros
    ----------
    ir : np.ndarray
        Vector con la respuesta al impulso discreta (dominio del tiempo).
    fs : int
        Frecuencia de muestreo en Hz.
    ms_bloque : float, opcional
        Duración de cada bloque en milisegundos. Por defecto 20 ms.

    Retorna
    -------
    rms_por_bloque : np.ndarray
        Array de forma (num_bloques,) con el valor RMS calculado en cada bloque.
    tamano_bloque : int
        Número de muestras que componen cada bloque (equivalente a ms_bloque·fs/1000).

    Notas
    -----
    - Se descartan las muestras sobrantes al final si la longitud de `ir` no es múltiplo exacto
      del tamaño de bloque.
    - El RMS de un bloque se obtiene como sqrt(mean(ir_bloque**2)).
    """
    # 1)Cantidad de muestras que tiene cada bloque
    tamano_bloque = int(fs * ms_bloque / 1000)

    # 2) Cantidad de bloques completos que caben en la señal
    num_bloques = len(ir) // tamano_bloque

    # 3) Cortamos la señal para quedarnos solo con num_bloques * tamano_bloque muestras,
    ir_recortada = ir[: num_bloques * tamano_bloque]

    # 4) La transformamos en una matriz de forma (num_bloques, tamano_bloque):
    #    cada fila es un bloque sucesivo de la señal.
    ir_bloques = ir_recortada.reshape(num_bloques, tamano_bloque)

    # 5) Ahora, para cada bloque (cada fila), calculamos su RMS:
    #    RMS = sqrt( mean( muestras^2 ) )
    #    axis=1 indica "por fila".
    rms_por_bloque = np.sqrt(np.mean(ir_bloques**2, axis=1))

    return {'rms_por_bloque':rms_por_bloque,'tamano_bloque': tamano_bloque}

def lundeby(ri, fs, ms_bloque=20, max_iter=6, tol_cruce=1e-3, return_debug_data=False):
    """
    Implementa el algoritmo de Lundeby para encontrar el punto de cruce entre el
    decaimiento de la respuesta al impulso y el ruido de fondo.

    Parámetros
    ----------
    ri : np.ndarray
        Respuesta al impulso (suavizada).
    fs : float
        Frecuencia de muestreo en Hz.
    ms_bloque : float, opcional
        Duración de cada bloque en milisegundos. Por defecto 20 ms.
    max_iter : int, opcional
        Número máximo de iteraciones. Por defecto 6.
    tol_cruce : float, opcional
        Tolerancia para considerar convergida la iteración. Por defecto 1e-3.
    return_debug_data : bool, opcional
        Si True, devuelve un diccionario con los datos de depuración.

    Retorna
    -------
    idx_cruce : int
        Índice de la muestra que marca el punto de cruce entre el decaimiento y el ruido.
    o
    debug_data : dict
        Diccionario con los datos de depuración:
        'nivel_ruido': float, nivel de ruido final en dB.
        'slope': float, pendiente final de la regresión lineal.
        'intercept': float, ordenada al origen de la regresión lineal.
        'tiempo_cruce': float, tiempo del punto de cruce en segundos.
        'idx_cruce': int, índice de la muestra del punto de cruce.
        'iteraciones': int, número de iteraciones realizadas.
        'convergencia': bool, indica si la iteración convergió.
        'tiempo_rms': np.ndarray, array de tiempos (en segundos) de la señal RMS.
        'schroeder_db': np.ndarray, array con la integral de Schroeder en dB.
    """ 

    # 1) RMS por bloques
    rms = calcular_rms_por_bloques(ri, fs, ms_bloque)
    rms_vals = rms['rms_por_bloque']
    tb = rms['tamano_bloque']
    tiempo_rms = np.arange(len(rms_vals)) * tb / fs

    # 2) Schroeder
    fs_rms = fs / tb
    sch = integral_schroeder(rms_vals, fs=fs_rms)
    sch_db = escala_log(sch['schroeder'])

    # 3) Ruido inicial
    idx0 = int(len(sch_db)*0.9)
    nivel_ruido = np.mean(sch_db[idx0:])

    # 4) Regresión inicial
    nivel_inf = nivel_ruido + 7.5
    reg = regresion_lineal_en_intervalo(
        tiempo_rms, sch_db,
        lim_sup=0, lim_inf=nivel_inf
    )
    slope = reg['slope']; intercept = reg['intercept']

    punto_cruce = (nivel_ruido - intercept) / slope
    prev_cruce = punto_cruce

    # 5) Iteración de Lundeby
    convergencia = False
    for i in range(1, max_iter+1):
        # 5.1) Re-estimar ruido
        t_start = (nivel_ruido + 7.5 - intercept) / slope
        i0 = max(0, min(len(ri), int(t_start * fs)))
        min_len = int(0.1 * len(ri))
        if len(ri) - i0 < min_len:
            i0 = len(ri) - min_len
        nivel_ruido = np.mean(sch_db[int(i0/tb):])

        # 5.2) Nueva regresión
        db_sup = -5.0  # Límite superior FIJO, en la zona limpia del decaimiento.
        db_inf = nivel_ruido + 10.0 # Límite inferior adaptativo, 10 dB sobre el ruido.

        # Control de seguridad: ¿Hay suficiente rango dinámico para la regresión?
        if db_inf >= db_sup:
            print(f"ADVERTENCIA (Iteración {i}): SNR demasiado bajo. No se puede refinar más la pendiente.")
            # Salimos del bucle y nos quedamos con el último valor válido.
            break 
            
        reg = regresion_lineal_en_intervalo(
            tiempo_rms, sch_db,
            lim_sup=db_sup, lim_inf=db_inf
        )
        slope = reg['slope']; intercept = reg['intercept']

        # 5.3) Nuevo punto de cruce
        punto_cruce = (nivel_ruido - intercept) / slope
        idx_cruce   = int(round(punto_cruce * fs))

        # Check convergence
        if abs(punto_cruce - prev_cruce) < tol_cruce:
            convergencia = True
            break
        prev_cruce = punto_cruce
        
    if not return_debug_data:
        return idx_cruce
    else:
        # Si se piden los datos de depuración, devolvemos un diccionario completo
        debug_data = {
        'nivel_ruido': nivel_ruido,
        'slope': slope,
        'intercept': intercept,
        'tiempo_cruce': punto_cruce,
        'idx_cruce':idx_cruce,
        'iteraciones': i,
        'convergencia': convergencia,
        'tiempo_rms': tiempo_rms,
        'schroeder_db':sch_db}
      
        return debug_data
      
def integral_schroeder(p: np.ndarray, fs: float, t_lundeby: int = None) -> dict:
    """
    Calcula la integral de Schroeder hasta el tiempo de Lundeby y descarta
    la energía más allá de ese punto (ruido de fondo).

    Parameters
    ----------
    p : np.ndarray
        Respuesta al impulso (suavizada).
    t_lundeby : int, optional
        Índice de muestra que marca el fin de la parte útil (cruce Lundeby).
    fs : float
        Frecuencia de muestreo en Hz.

    Returns
    -------
    schroeder : np.ndarray
        Integral de Schroeder cortada en t_lundeby:
        S(t) = ∫ₜ^{t_L} p²(τ)dτ.
    p2 : np.ndarray
        Vector de p²(t).
    """
    dt = 1.0 / fs
    p2 = p**2
    if t_lundeby is None:
        t_lundeby = len(p)
    # 1) Energía total hasta t_lundeby:
    E_total_L = np.sum(p2[:t_lundeby]) * dt

    # 2) Energía acumulada hasta cada t:
    E_acum = np.cumsum(p2[:t_lundeby]) * dt

    # 3) Integral de Schroeder hasta t_L:
    #    S(t) = E_total_L - E_acum(t)
    S = E_total_L - E_acum

    # 4) Para t >= t_lundeby, tiramos la curva a 0
    S[t_lundeby:] = 0.0

    return {'schroeder':S,'p2':p2}