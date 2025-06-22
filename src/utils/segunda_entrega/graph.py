import matplotlib.pyplot as plt
import numpy as np
from ..tercer_entrega.otras_func import get_output_filepath
from .escala_log import escala_log
from ..tercer_entrega.suavizado import hilbert_transform,filtro_promedio_movil

def graficar_dominio_temporal(signal, fs, hilbert=False):
    """
    Grafica la señal en el dominio temporal.

    Parámetros
    ----------
    signal : array_like
        Señal a graficar.
    fs : int
        Frecuencia de muestreo de la señal (Hz).
    hilbert : bool, opcional
        Si es True, calcula y grafica la envolvente de la señal a través de la transformada de Hilbert.
        Por defecto: False.

    Returns
    -------
    None
        La función no retorna nada. Muestra una gráfica de la señal en el dominio temporal.

    Ejemplo
    -------
    Graficar el dominio temporal de una señal de ruido rosa.

        import numpy as np
        import matplotlib.pyplot as plt

        fs = 44100
        t = np.linspace(0, 10, 441000)  # 10 segundos con fs = 44100 Hz
        x = ruidoRosa_voss(10)
        graficar_dominio_temporal(x, fs)
    """
    t = np.arange(len(signal)) / fs
    plt.figure(figsize=(10, 4))
    if hilbert:
        envolvente = filtro_promedio_movil(hilbert_transform(signal), L=50)
    plt.plot(t, signal, color='m', label='Señal original')
    if hilbert:
        plt.plot(t, envolvente, color='b', alpha=0.8, linewidth=2, label='Envolvente')
        indice_max = np.argmax(envolvente)
        plt.xlim(t[indice_max] - 0.005, t[indice_max] + 0.1)
    plt.xlabel('Tiempo (s)', fontsize=12)
    plt.ylabel('Amplitud', fontsize=12)
    plt.grid(True, which='both', linestyle='--', alpha=0.6)
    plt.legend(fontsize=12)
    plt.tight_layout()
    out_file = get_output_filepath(
        'time_domain_plot_hilbert.png' if hilbert else 'time_domain_plot.png',
        3, ('img', 'temp')
    )
    plt.savefig(out_file, dpi=300, bbox_inches="tight")

def graficar_espectro(signal, fs,color='r'):
    """
    Grafica el espectro de la señal x (longitud N, muestreo fs) con eje X en escala logarítmica y eje Y en dB.

    Parámetros
    ----------
    signal : array_like
        Señal a graficar.
    fs : int
        Frecuencia de muestreo de la señal (Hz).
    color : str, opcional
        Color de la gráfica. Por defecto es 'r' (rojo).

    Returns
    -------
    None
        La función no retorna nada. Muestra una gráfica del espectro de la señal en el dominio de frecuencias.

    Ejemplo
    -------
    Graficar el espectro de ruido rosa.

        import numpy as np
        import matplotlib.pyplot as plt

        fs = 44100
        t = np.linspace(0, 10, 441000)  # 10 segundos con fs = 44100 Hz
        x = ruidoRosa_voss(10)
        graficar_espectro(x, fs)
    """
    # 1) Calcular FFT y tomar mitad positiva
    N = len(signal)
    X = np.fft.fft(signal)
    Xm = np.abs(X)[: N//2] * (2/N)

    # Evitar log(0) con un valor muy pequeño
    Xm = np.clip(Xm, 1e-12, None)

    # Convertir a decibelios
    YdB = 20 * np.log10(Xm)

    # 2) Construir vector de frecuencias positivas
    f = np.fft.fftfreq(N, d=1/fs)[: N//2]

    # 3) Crear la figura
    plt.figure(figsize=(7, 4))

    # 3.a) Indicar que el eje X será logarítmico
    plt.xscale('log')

    # 3.b) Graficar espectro en dB vs frecuencia
    plt.plot(f, YdB, linewidth=1.5, color=color)
    #plt.fill_between(f, YdB, y2=ax.get_ylim()[0], color=line_color, alpha=0.3)
    plt.grid(True, which='both', ls='--', alpha=0.5)

    # 4) Definir límites del eje X (no puede empezar en 0 si es log)
    plt.xlim(20, fs/2)  # por ejemplo de 20 Hz hasta fs/2
    plt.ylim(-80, 0)  # límites en dB, ajusta según tu señal
    # 5) Poner ticks “personalizados” en frecuencias de interés
    freqs_ticks = [20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000]
    plt.xticks(freqs_ticks, [str(int(f)) for f in freqs_ticks])

    # 6) Etiquetas y título
    plt.xlabel("Frecuencia (Hz, escala log)")
    plt.ylabel("Magnitud (dB)") 
    plt.tight_layout()
    out_file = get_output_filepath(f'freq_domain_plot.png',3,('img','temp'))
    plt.savefig(out_file,dpi=300,bbox_inches="tight")

def graficar_resultados(freq, datos_debug, fs):
    """
    Grafica la RI filtrada en dB, la curva de decaimiento de Schroeder y la línea de regresión de Lundeby,
    que aproxima el T60, para una frecuencia dada.

    Parámetros:
    -----------
    freq : float
        Frecuencia central de la banda a graficar, en Hz.
    datos_debug : dict
        Diccionario que contiene los resultados de la segunda entrega, con las claves
        'ri_filtradas', 'datos_lundeby', 'curvas_decay_db'.
    fs : int
        Frecuencia de muestreo en Hz.

    Efectos secundarios:
    -------------------
    Guarda un archivo PNG llamado 'grafico_<frecuencia>.png' en la ruta especificada
    por get_output_filepath().

    Ejemplo de uso:
    ---------------
    >>> freq = 250
    >>> datos_debug = ...  # resultados de la segunda entrega
    >>> fs = 44100
    >>> graficar_resultados(freq, datos_debug, fs)
    """
    ri_banda = datos_debug['ri_filtradas'][freq]
    tiempo_ri = np.arange(len(ri_banda)) / fs
    
    # Envolvente en dB de la RI filtrada
    envolvente_db = 2 * escala_log(ri_banda)

    # Datos de Lundeby
    lundeby_info = datos_debug['datos_lundeby'][freq]
    nivel_ruido = lundeby_info['nivel_ruido']
    tiempo_cruce = lundeby_info['tiempo_cruce']
    slope = lundeby_info['slope']
    intercept = lundeby_info['intercept']

    # Datos de Schroeder
    tiempo_sch_full = np.arange(len(datos_debug['curvas_decay_db'][freq])) / fs

    # Crear la figura
    plt.figure(figsize=(14, 8))
    
    # 1. Graficar la RI filtrada en dB
    plt.plot(tiempo_ri, envolvente_db, 'b-', alpha=0.5, label=f'RI filtrada en {freq} Hz')
    
    # 2. Graficar la curva de decaimiento de Schroeder
    plt.plot(tiempo_sch_full, datos_debug['curvas_decay_db'][freq], 'b-', linewidth=2, label='Curva de Schroeder')
    
    # 3. Graficar la línea de regresión de Lundeby (que aproxima el T60)
    tiempo_plot_reg = np.array([0, tiempo_cruce * 1.1])
    linea_regresion = slope * tiempo_plot_reg + intercept
    plt.plot(tiempo_plot_reg, linea_regresion, 'k--', linewidth=2.5, 
             label=f'Regresión Lundeby (T60 ≈ {-60/slope:.2f}s)')

    # 4. Marcar el ruido y el punto de cruce
    plt.axhline(nivel_ruido, color='r', linewidth=3, linestyle=':', 
                label=f'Nivel de Ruido ({nivel_ruido:.1f} dB)')
    plt.axvline(tiempo_cruce, color='g', linewidth=3, linestyle=':', 
                label=f'Cruce Lundeby ({tiempo_cruce:.2f} s)')

    # Configuración del gráfico
    plt.xlabel('Tiempo (s)', fontsize=12)
    plt.ylabel('Nivel (dB)', fontsize=12)
    plt.grid(True, which='both', linestyle='--', alpha=0.6)
    plt.legend(fontsize=15)
    plt.ylim(max(nivel_ruido - 40, -120), 2)  # Límite dinámico del eje Y
    plt.xlim(0, max(tiempo_cruce * 1.2, 1.0))  # Límite dinámico del eje X
    out_file = get_output_filepath(f'grafico_{freq}.png', 3, ('img', 'temp'))
    plt.tight_layout()
    plt.savefig(out_file, dpi=300, bbox_inches='tight')
    plt.close()