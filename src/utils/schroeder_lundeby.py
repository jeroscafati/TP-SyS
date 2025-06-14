import numpy as np


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
    #faltamucho...



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
