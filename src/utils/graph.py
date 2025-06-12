import matplotlib.pyplot as plt

def graficar_dominio_temporal(t, signal):
    """
    Grafica la señal en el dominio temporal.

    Parámetros
    ----------
    t : array_like
        Vector de tiempo correspondiente a la señal (en segundos).
    signal : array_like
        Señal a graficar.

    Returns
    -------
    None
        La función no retorna nada. Muestra una gráfica de la señal en el dominio temporal.

    Ejemplo
    -------
    Graficar el dominio temporal de una señal de ruido rosa.

        import numpy as np
        import matplotlib.pyplot as plt

        t = np.linspace(0, 10, 441000)  # 10 segundos con fs = 44100 Hz
        x = ruidoRosa_voss(10)
        graficar_dominio_temporal(t, x)
    """
    plt.figure(figsize=(10, 4))
    plt.plot(t, signal, color='m')
    plt.title('Señal en el dominio temporal')
    plt.xlabel('Tiempo [s]')
    plt.ylabel('Amplitud')
    plt.grid(True)
    plt.show()
    return None

def graficar_espectro(x, fs):
    """
    Calcula el espectro de la señal x (longitud N, muestreo fs) y lo grafica
    con eje X en escala logarítmica y eje Y en dB.
    """
    # 1) Calcular FFT y tomar mitad positiva
    N = len(x)
    X = np.fft.fft(x)
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
    plt.plot(f, YdB, linewidth=1.5, color='blue')
    ax.fill_between(f, YdB, y2=ax.get_ylim()[0], color=line_color, alpha=0.3)
    plt.grid(True, which='both', ls='--', alpha=0.5)

    # 4) Definir límites del eje X (no puede empezar en 0 si es log)
    plt.xlim(20, fs/2)  # por ejemplo de 20 Hz hasta fs/2

    # 5) Poner ticks “personalizados” en frecuencias de interés
    freqs_ticks = [20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000]
    plt.xticks(freqs_ticks, [str(int(f)) for f in freqs_ticks])

    # 6) Etiquetas y título
    plt.xlabel("Frecuencia (Hz, escala log)")
    plt.ylabel("Magnitud (dB)")
    plt.tight_layout()
    plt.savefig("mi_grafico.png", dpi=300, bbox_inches="tight")