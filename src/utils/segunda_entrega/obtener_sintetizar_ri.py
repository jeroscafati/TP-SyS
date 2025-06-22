import soundfile as sf
import numpy as np
from ..tercer_entrega.otras_func import get_output_filepath

def sintetizar_RI(frecuencias: dict,
                  fs: int = 44100,
                  piso_ruido_db: float = -60.0,
                  delay_s: float = 0.5,
                  exportar_wav: bool = False):
    """
    Sintetiza una respuesta al impulso (RI) multibanda con ruido y la guarda como WAV.

    La RI sintetizada se construye como la suma de decaimientos exponenciales modulados
    en frecuencia para cada banda, con adición de ruido blanco, un retraso inicial aleatorio,
    y normalización al valor máximo.

    Parámetros:
    -----------
    frecuencias : dict
        Diccionario donde cada clave es la frecuencia central (Hz) y cada valor es una tupla
        (T60, A) con:
            - T60 (float): tiempo de reverberación (s) para esa frecuencia.
            - A   (float): amplitud inicial de la banda.
    fs : int, opcional
        Frecuencia de muestreo en Hz. Por defecto 44100.
    piso_ruido_db : float, opcional
        Nivel RMS del ruido blanco en dBFS (referido a la amplitud máxima = 0 dBFS).
        Por defecto -60 dB.
    delay_s : float, opcional
        Duración del retraso inicial agregado en segundos (antes de la RI).
        Por defecto 0.5 s.
    exportar_wav : bool, opcional
        Si True, exporta la RI sintetizada como WAV.
        Por defecto False.
    Retorna:
    --------
    dict:
        'audio_data' (np.ndarray): señal sintetizada con forma (n_samples,) y valores en [-1,1].
        'fs'         (int)      : frecuencia de muestreo retornada.

    Efectos secundarios:
    ---------------------
    - Guarda un archivo WAV llamado 'ri_sintetizada.wav' en la ruta especificada
      por get_output_filepath().

    Ejemplo de uso:
    ---------------
    >>> freqs = {125: (2.8,1.0), 250:(2.2,1.0), 500:(1.8,1.0)}
    >>> resultado = sintetizar_RI(freqs, fs=48000, piso_ruido_db=-50, delay_s=0.2)
    >>> audio = resultado['audio_data']
    >>> print(audio.shape, resultado['fs'])  # (n_samples,)
    """
    
    # 1.Duración RI
    #  20% más que el T60 máximo
    t60max = max(v[0] for v in frecuencias.values())
    segundos = (1.2 * t60max)
    t = np.arange(0, segundos, 1/fs)  
    
    # 2.Sintetizar RI
    ri = np.zeros_like(t)
    factor = 3 * np.log(10)

    for freq, (t60, A) in frecuencias.items():
        tau_i = factor/ t60
        ri += A* np.exp(-tau_i * t) * np.cos(2 * np.pi * freq * t)
       
    # 3.Añadir ruido blanco
    rms_ruido = 10 ** (piso_ruido_db / 20)
    ruido = rms_ruido * np.random.randn(len(t))

    #4. Sumar RI y Ruido
    ri_ruido = ri + ruido

    #5 Retrasar RI
    delay = rms_ruido * np.random.rand(int(delay_s * fs))
    ri_ruido = np.concatenate((delay, ri_ruido))

    #6 Normalizar RI
    ri_ruido /= np.max(np.abs(ri_ruido))
    
    #7 Exportar RI
    #Ruta del archivo
    if exportar_wav:
        out_file = get_output_filepath('ri_sintetizada.wav',levels_up=3,subdirs=('audios','temp'))
        
        # Guardar la señal sintetizada como un archivo WAV
        ri_int16 = (ri_ruido * 32767).astype(np.int16)
        sf.write(str(out_file), ri_int16, fs)

    return {'audio_data':ri_ruido,
            'fs':fs}

def obtener_RI_por_deconvolucion(grabacion, 
                            filtro_inverso,
                            fs=44100,
                            exportar_wav=False,
                            filename="RI_por_deconvolucion.wav"):
    """
    Devuelve la respuesta al impulso h[n] = (grabacion * filtro_inverso) en el dominio del tiempo,
    usando multiplicación de espectros (FFT).

    Parámetros
    ----------
    grabacion : array_like (1D)
        Arreglo de muestras de la señal grabada y[n] (por ejemplo, el sine‐sweep captado con micrófono).

    filtro_inverso : array_like (1D)
        Arreglo de muestras del filtro inverso k[n] que diseñaste para deconvolucionar el sine‐sweep.

    Returns
    -------
    h : ndarray (1D)
        Respuesta al impulso lineal h[n] = y[n] * k[n], de longitud len(grabacion) + len(filtro_inverso) - 1.
        Es un array real (dtype float) con la RI normalizada

    """
    # 1. Longitud que debería tener la convolución lineal:
    N_lineal = len(grabacion) + len(filtro_inverso) - 1
    
    # 2. Elegimos N_FFT como la siguiente potencia de 2 mayor a N_lineal (por eficiencia).
    
    N_FFT = 1 << int(np.ceil(np.log2(N_lineal)))
    
    #3. FFT de ambas señales completando el tamaño a N_FFT 
    FFT_grab = np.fft.fft(grabacion,      n=N_FFT)
    FFT_filt = np.fft.fft(filtro_inverso, n=N_FFT)
    
    RI = np.real(np.fft.ifft(FFT_grab * FFT_filt))
    RI = RI[:N_lineal]
    
    #4. Normalizar la respuesta al impulso
    RI /= np.max(np.abs(RI))
    
    if exportar_wav:
        #5 Convertir a PCM16 para exportar
        ri_int16 = (RI * 32767).astype(np.int16)
        out_file = get_output_filepath(filename,levels_up=3,subdirs=('audios','temp'))
        sf.write(out_file, ri_int16, fs)

    return {'audio_data': RI,
             'fs': fs}


