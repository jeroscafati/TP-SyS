import numpy as np
from generar_ri import escala_log
from linear_fit import regresion_lineal_en_intervalo

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

def lundeby(ri,fs):
    # 1) Pre-suavizado calculando RMS en bloques ---
    rms_signal = calcular_rms_por_bloques(ri, fs, ms_bloque=20)
    tiempo_rms = np.arange(len(rms_signal['rms_por_bloque'])) * rms_signal['tamaño_bloque'] / fs
    
    #2) Hacer Schroeder:
    schroeder = integral_schroeder(rms_signal['rms_por_bloque'], fs/rms_signal['tamaño_bloque'])
    
    #3) Convertir a db:
    schroeder_db = escala_log(schroeder)

    # 4) Estimación inicial del ruido (último 10%)
    idx_ruido_inicio = int(len(schroeder_db) * 0.9)
    nivel_ruido_db = np.mean(schroeder_db[idx_ruido_inicio:])

    #5) Regresion lineal
    # desde 0 dB hasta nivel_ruido + 5 db
    nivel_ruido_db += 5 
    reg = regresion_lineal_en_intervalo(tiempo_rms,schroeder_db,lim_sup=0, lim_inf=nivel_ruido_db)

    # 5b) Generar n_subint subintervalos equiespaciados en dB
    #    p.ej. para 5 subint en 10 dB: [-0, -2, -4, -6, -8, -10] dB
    pasos = np.linspace(0, nivel_ruido_db , 6)
    
    # 5c) Para cada nivel de corte en 'pasos', calcula el tiempo correspondiente
    #   regresión "invertida": t = (dB - intercept) / slope
    tiempos_corte = (nivel_ruido_db - reg['intercept'])/ reg['slope']

    # 6) Ahora tienes n_subint intervalos temporales: [t0->t1, t1->t2, …]
    #    Calcula el RMS de la señal original ri en cada uno (o de sch si prefieres)
    rms_sub = []
    for t_a, t_b in zip(tiempos_corte[:-1], tiempos_corte[1:]):
        i0 = int(t_a * fs)
        i1 = int(t_b * fs)
        bloque = ri[i0:i1]
        rms_sub.append(np.sqrt(np.mean(bloque**2)))


    convergencia = False
    iter_count = 0
    prev_punto_cruce = punto_cruce

    while not convergencia and iter_count < max_iter:
        iter_count += 1

        # 7) Estimar ruido de fondo:
        #    - Partir del tiempo t_start = punto_cruce + Δt, donde Δt corresponde a 5–10 dB
        #      por encima del nivel de ruido actual.
        delta_db = 7.5  # por ejemplo 7.5 dB sobre ruido
        t_start = (nivel_ruido + delta_db - intercept) / slope
        idx_start = int(t_start * fs)
        #    - Asegurar longitud mínima: al menos 10% de la RI
        min_len = int(0.1 * len(ri))
        idx_end = len(ri)
        if idx_end - idx_start < min_len:
            idx_start = max(0, idx_end - min_len)
        #    - Recalcular nivel_ruido como la media de sch_db a partir de idx_start
        nivel_ruido = np.mean(sch_db[idx_start:])

        # 8) Estimar nueva pendiente de decaimiento:
        #    - Definir rango dinámico de, digamos, 10–20 dB
        db_inf = nivel_ruido + 5    # 5 dB sobre ruido
        db_sup = nivel_ruido + 15   # 15 dB sobre ruido
        #    - Hacer regresión en [db_sup → db_inf]
        reg = regresion_lineal_en_intervalo(
            tiempo_rms, sch_db,
            lim_sup=db_sup, lim_inf=db_inf
        )
        slope, intercept = reg['slope'], reg['intercept']

        # 9) Calcular nuevo punto de cruce:
        #    t = (nivel_ruido - intercept) / slope
        punto_cruce = (nivel_ruido - intercept) / slope

        # 10) Comprobar convergencia:
        if abs(punto_cruce - prev_punto_cruce) < tol_cruce:
            convergencia = True
        else:
            prev_punto_cruce = punto_cruce

    return {
        'nivel_ruido': nivel_ruido,
        'slope': slope,
        'intercept': intercept,
        'punto_cruce': punto_cruce,
        'iteraciones': iter_count,
        'convergencia': convergencia
    }
    

    #   
def integral_schroeder(p, fs):
    """
    Calcula la integral de Schroeder para una respuesta al impulso discreta.

    p:  np.ndarray
        Respuesta al impulso suavizada.

    return:
    Shroeder:  np.ndarray
        Integral de Schroeder.
    """
    dt = 1 / fs  # Intervalo de muestreo
    p2 = p**2

    termino1 = np.sum(p2) * dt # Integral desde 0 a infinito. Suma todos los elementos del array

    termino2 = np.cumsum(p2) * dt # Integral desde 0 a t. Para cada posición, suma los elementos hasta ese punto

    # Integral de Schroeder: total menos acumulada
    schroeder = termino1 - termino2


    # Cálculo de D50:
    # Número de muestras correspondientes a 50 ms
    muestras_50ms = int(0.050 * fs)

    # Energía temprana (0 a 50 ms)
    energia_50ms = np.sum(p2[:muestras_50ms]) * dt

    # Calculamos el D50:
    D50 = 100 * (energia_50ms / energia_total)

    return schroeder

def calcular_D50_C80(energia_total, fs, dt):
    """
    Calcula el índice de definición D50 a partir de la energía temporal de la respuesta al impulso.

    D50 es el porcentaje de la energía total que llega en los primeros 50ms, y se usa
    como métrica de inteligibilidad en espacios acústicos.

    Parámetros
    ----------
    energia_total : ndarray
        Vector de energía instantánea muestreada (p²(t)·dt) o acumulada hasta cada instante,
        de longitud N.
    fs : int
        Frecuencia de muestreo en Hz.
    dt : float
        Duración de cada intervalo de muestreo en segundos (generalmente 1/fs).

    Retorna
    -------
    dict
        Diccionario con la clave:
          - 'D50' : float
              Índice de definición en porcentaje (%), calculado como
              100·(energía en 0 - 50ms / energía total).
    """
    # Número de muestras correspondientes a 50 ms
    muestras_50ms = int(0.050 * fs)

    # Energía temprana (0 a 50 ms)
    energia_50ms = np.sum(energia_total[:muestras_50ms]) * dt

    # Cálculo de D50
    D50 = 100 * (energia_50ms / energia_total)
    
    #C80:
    t_80ms = int(0.08 * fs)  # 80 ms en muestras
    E0 = schroeder[0]
    E80 = schroeder[t_80ms]
    c80 = 10*np.log10((E0-E80) / E0)
    return {'D50': D50, 'c80':c80}