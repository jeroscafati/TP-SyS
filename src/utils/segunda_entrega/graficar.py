import numpy as np
import matplotlib.pyplot as plt
import io
from flask import Response

def fig_to_png_response(fig):
    """
    Convierte una figura de Matplotlib (`fig`) a un Response de Flask
    conteniendo el PNG en memoria.
    """

    # 1. Crear un buffer en memoria
    buf = io.BytesIO()

    # 2. Ajustar contornos y guardar la figura en el buffer en formato PNG
    fig.tight_layout()
    fig.savefig(buf, format="png")

    # 3. Reposicionar el puntero del buffer al inicio
    buf.seek(0)

    # 4. Cerrar la figura para liberar memoria (importante en aplicaciones que generan muchos gráficos)
    plt.close(fig)

    # 5. Devolver el contenido del buffer como un Response de Flask
    return Response(buf.getvalue(), mimetype="image/png")

def graficar_dominio_temporal(signal, fs=44100):
    """
    Crea y devuelve un objeto Matplotlib Figure con el gráfico
    de la señal en el dominio temporal.

    Parámetros
    ----------
    signal : array-like
        Señal a graficar en el dominio temporal.
    fs : int, opcional
        Frecuencia de muestreo de la señal. Por defecto: 44100 Hz.

    Retorna
    -------
    fig : matplotlib.figure.Figure
        Figura que contiene el plot de la señal en el dominio temporal.
    """
    # 1) Calcular el eje de tiempo
    t = np.arange(len(signal)) / fs

    # 2) Crear figura y axes 
    fig, ax = plt.subplots(figsize=(10, 4))

    # 3) Graficar sobre ese axes
    ax.plot(t, signal, color='m')
    ax.set_title('Señal en el dominio temporal')
    ax.set_xlabel('Tiempo [s]')
    ax.set_ylabel('Amplitud')
    ax.grid(True)

    return fig


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




