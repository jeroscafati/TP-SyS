import numpy as np
from utils.tercer_entrega.linear_fit import regresion_lineal_en_intervalo

def calcular_D50_C80(p2: np.ndarray, fs: int) -> dict:
    """
    Calcula los parámetros D50 (definición) y C80 (claridad) a partir de la energía de la señal.

    Parámetros
    ----------
    p2 : np.ndarray
        Energía instantánea muestreada, es decir, p(t)**2, de longitud N.
        Debe ser un array 1D de valores no negativos.
    fs : int
        Frecuencia de muestreo en Hz. Debe ser un valor positivo.

    Retorna
    -------
    dict
        Un diccionario con las siguientes claves:
        - 'D50' : float
            Porcentaje de energía en los primeros 50 ms. Rango [0, 100].
        - 'C80' : float
            Claridad C80 en dB, definida como 10*log10(E_early/E_late),
            donde E_early es la energía hasta 80ms y E_late es la energía restante.

    Notas
    -----
    - Si la energía total es cero, D50 se establece a 0.
    - C80 puede ser -inf si no hay energía tardía.
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

    # Evitar log(0): forzar un mínimo valor positivo
    E_late_80_clipped = np.clip(E_late_80, 1e-10, None)

    C80 = 10.0 * np.log10(E_early_80 / E_late_80_clipped)

    return {'D50': D50, 'C80': C80}

def calcular_parametros_acusticos(signal_db, p2: np.ndarray, fs: int, return_regs=False) -> dict:
    """
    Calcula los parámetros acústicos principales a partir de una curva de decaimiento.

    Parámetros
    ----------
    signal_db : np.ndarray
        Curva de decaimiento de Schroeder en escala logarítmica (dB).
    p2 : np.ndarray
        Energía instantánea muestreada, p(t)**2, de la misma longitud que signal_db.
    fs : int
        Frecuencia de muestreo en Hz.
    return_regs : bool, opcional
        Si es True, retorna información adicional sobre las regresiones lineales.
        Por defecto es False.

    Retorna
    -------
    dict or tuple
        Si return_regs es False (por defecto), retorna un diccionario con:
        {
            'EDT': float,            # Early Decay Time (s)
            'T60_from_T10': float,   # T60 estimado del tramo -5 a -15 dB
            'T60_from_T20': float,   # T60 estimado del tramo -5 a -25 dB
            'T60_from_T30': float,   # T60 estimado del tramo -5 a -35 dB
            'D50': float,            # Definición (0-100%)
            'C80': float             # Claridad en dB
        }
        
        Si return_regs es True, retorna una tupla (dic, regs) donde:
        - dic: el diccionario descrito arriba
        - regs: diccionario con los parámetros de las regresiones lineales:
            {
                'EDT': dict,  # Parámetros de la regresión para EDT
                'T10': dict,  # Parámetros de la regresión para T10
                'T20': dict,  # Parámetros de la regresión para T20
                'T30': dict   # Parámetros de la regresión para T30
            }

    Notas
    -----
    - La señal se normaliza internamente para que su máximo sea 0 dB.
    - Los tiempos de reverberación se calculan asumiendo un decaimiento lineal.
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
    