import numpy as np
from utils.tercer_entrega.linear_fit_y_db_scale import regresion_lineal_en_intervalo

def calcular_D50_C80(p2: np.ndarray, fs: int) -> dict:
    """
    Calcula D50 y C80 a partir de la señal p²(t).

    Parámetros
    ----------
    p2 : np.ndarray
        Energía instantánea muestreada, es decir, p(t)**2, de longitud N.
    fs : int
        Frecuencia de muestreo en Hz.

    Retorna
    -------
    dict
        {
          'D50' : float,  # porcentaje de energía en los primeros 50 ms
          'C80' : float   # claridad C80 en dB
        }
    """
    
    # --- D50 ---
    #muestras hasta 50 ms
    N50 = int(0.050 * fs)
    # Aseguramos de no exceder la longitud de la señal
    N50 = min(N50, len(p2))         

    E_total = np.sum(p2)               
    E_early_50 = np.sum(p2[:N50])   

    D50 = 100.0 * (E_early_50 / E_total) if E_total > 0 else 0

    # --- C80 ---
    N80 = int(0.080 * fs) 
    N80 = min(N80, len(p2))

    E_early_80 = np.sum(p2[:N80])       
    E_late_80  = np.sum(p2[N80:])     

    C80 = 10.0 * np.log10(E_early_80 / E_late_80)

    return {'D50': D50, 'C80': C80}

def calcular_parametros_acusticos(signal_db, p2: np.ndarray, fs: int, return_regs=False) -> dict:
    """
    Calcula todos los parámetros acústicos a partir de una curva de decaimiento.
    
    Argumentos:
    - signal_db: Array con la curva de decaimiento de Schroeder en dB.
    p2 : np.ndarray
        Energía instantánea muestreada, es decir, p(t)**2, de longitud N.
    schroeder : np.ndarray
        Integral de Schroeder: para cada muestra k, 
        schroeder[k] ≈ ∫_{t_k}^∞ p²(τ) dτ.
    fs : int
        Frecuencia de muestreo en Hz.
    Retorna:
    - dict con los parámetros calculados para esa curva.
    Dict: {"EDT":,"T60_from_T10":,"T60_from_T20":,"T60_from_T30":,'D50':,'C80':}
    """

    #Vector de tiempo
    t = np.arange(len(signal_db))/fs

    #Normalizar para que el máximo sea 0 dB
    signal_db_norm = signal_db - np.max(signal_db)

    # 1) EDT: tramo  -1  → -11 dB
    edt_reg = regresion_lineal_en_intervalo(t, signal_db_norm,  -1, -11)
    edt = -60.0 / edt_reg['slope'] 

    # 2) T10: tramo -5  → -15 dB
    t10_reg = regresion_lineal_en_intervalo(t, signal_db_norm,  -5, -15)
    t60_from_t10 = -60.0 / t10_reg['slope']


    # 3) T20: tramo -5  → -25 dB
    t20_reg = regresion_lineal_en_intervalo(t, signal_db_norm,  -5, -25)
    t60_from_t20 = -60.0 / t20_reg['slope']

    # 4) T30: tramo -5  → -35 dB
    t30_reg = regresion_lineal_en_intervalo(t, signal_db_norm,  -5, -35)
    t60_from_t30 = -60.0 / t30_reg['slope']

    # 5) D50 y C80
    d50_c80 = calcular_D50_C80(p2,fs)

    #6) diccionario
    dic = {
        'EDT': edt,
        'T60_from_T10': t60_from_t10,
        'T60_from_T20': t60_from_t20,
        'T60_from_T30': t60_from_t30,
        'D50': d50_c80['D50'],
        'C80': d50_c80['C80']
    }
    if not return_regs:
        return dic
    
    else:
        datos_reg = {
        'EDT': edt_reg,
        'T10': t10_reg,
        'T20': t20_reg,
        'T30': t30_reg}
        return (dic,datos_reg)
    