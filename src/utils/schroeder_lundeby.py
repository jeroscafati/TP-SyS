import numpy as np
from linear_fit import regresion_lineal
from utils.generar_ri import escala_log
from suavizado import filtro_promedio_movil

def metodo_lundeby(ir,fs,
                   win_ms=50,
                    initial_excess_db=7.5,
                    slope_fit_range_db=(0, 10),
                    refine_excess_db=7.5,
                    refine_range_db=(10, 20),
                    intervals_per_10db=5,
                    conv_thresh_ms=1.0,
                    max_iters=20):
    
    # --- Paso 1 ----------------------------------
    #ventana de segundos a muestras
    win_samp = int(win_ms * 1e-3 * fs)
    
    ### RMS de ir²
    rms = np.sqrt(filtro_promedio_movil(ir**2,win_samp))
    # tiempos centrales de ventana (aprox.)
    n = len(ir)
    step = win_samp
    times = np.arange(0, n, step) / fs
    # escala dB normalizada
    env_db = escala_log(rms)
    # --- Paso 2: estimación inicial de ruido -----------------------------
    idx0 = int(0.9 * len(env_db))
    noise_db = np.mean(env_db[idx0:])

    # --- Paso 3 y 4: pendiente inicial y cruce ----------------------------
    fit_lo = noise_db + initial_excess_db
    fit_hi = 0
    mask = (env_db <= fit_hi) & (env_db >= fit_lo)
    slope, intercept, *_ = linregress(times[mask], env_db[mask])
    t_c = (noise_db - intercept) / slope

    # --- Pasos 5-10: refinamiento iterativo ------------------------------
    for _ in range(max_iters):
        prev_t = t_c
        # Paso 5: dividir decaimiento en intervalos locales
        total_decay = 0 - noise_db
        n_int = max(int(intervals_per_10db * (total_decay / 10)), 1)
        db_bins = np.linspace(0, noise_db, n_int + 1)
        interval_times = (db_bins - intercept) / slope
        # (Paso 6: opcional recalcular RMS por intervalo)
        # Paso 7: refinar ruido desde cruce+exceso
        thr_db = noise_db + refine_excess_db
        idx = np.where(env_db <= thr_db)[0]
        if idx.size == 0:
            break
        noise_db = np.mean(env_db[idx[0]:idx[0] + int(noise_tail_frac*len(env_db))])
        # Paso 8: re-ajustar pendiente en rango refinado
        fit_lo = noise_db + refine_excess_db
        fit_hi = noise_db + refine_range_db[1]
        mask = (env_db <= fit_hi) & (env_db >= fit_lo)
        if mask.sum() < 2:
            break
        slope, intercept, *_ = linregress(times[mask], env_db[mask])
        # Paso 9: nuevo cruce
        t_c = (noise_db - intercept) / slope
        # Paso 10: convergencia
        if abs(t_c - prev_t) * 1e3 < conv_thresh_ms:
            break

    return max(0.0, t_c)



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

    return schroeder
