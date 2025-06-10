import numpy as np
def hilbert_transform(s_t):
    """
    Suaviza una señal obteniendo su envolvente a través de una implementación
    de la Transformada de Hilbert.

    Args:
    s_t (np.ndarray): La señal de entrada.

    Returns:
    np.ndarray: La envolvente de la señal (envolvente).
    """

    N = len(s_t)

    # Llevamosal dominio de frecuencias s(t)->S(w)
    S_w = np.fft.fft(s_t)

    # h representa a (1+sgn(w))
    h = np.zeros(N)

    #frecuencias positivas:
    # En el array FFT,ellas van desde 1 hasta la mitad
    h[1:N//2] = 2
    h[0]=1
    #Para la frecuencia de Nyquist del punto medio (solo  si N es par),  no tiene un conjugado negativo.
    if N % 2 == 0:
        h[N // 2] = 1

    #obtenemos la señal analitica como S_a(t)= F⁻¹{(S(w)(1+sgn(w))}
    S_w *= h 
    analitica = np.fft.ifft(S_w)

    #Calculamos la envolvente de la señal
    envolvente = np.abs(analitica)

    return envolvente
def filtro_promedio_movil(x, L):
    """
    Aplica un filtro de promedio móvil de longitud L a una señal x.
    
    Parámetros:
    ------------
    x : ndarray
        Señal de entrada (1D, array de valores reales o complejos).
    L : int
        Longitud de la ventana de promedio.
    
    Retorna:
    --------
    y : ndarray
        Señal filtrada (promediada).
    """
    if L < 1:
        raise ValueError("La longitud L debe ser mayor o igual a 1")

    # Creamos la ventana deslizante
    kernel = np.ones(L) / L

    # Convolucionamos
    y = np.convolve(x, kernel, mode='same')  
    return y

# Ejemplo de uso:
if __name__ == "__main__":
    import soundfile as sf
    # señal de prueba
    x1, fs = sf.read("audios/s1r2.wav")
    #mono
    x = x1[:,0]
    t = np.arange(len(x)) / fs

    L = 5
    
    hilbert = hilbert_transform(x)
    media_movil = filtro_promedio_movil(x,L)
    print(f"longitud original: {len(x)}\n Longitud media_movil: {len(media_movil)}\n Longitud hilbert: {len(hilbert)}")
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(2, 1, figsize=(8, 6), sharex=True)

    # Subplot 0: original vs. media móvil
    axs[0].plot(t, x, label="original")
    axs[0].plot(t, media_movil, label="media_movil")
    axs[0].set_ylabel("Amplitud")
    axs[0].legend()
    axs[0].set_title("Original y Promedio Móvil")

    # Subplot 1: original vs. hilbert
    axs[1].plot(t, x, label="original")
    axs[1].plot(t, hilbert, label="hilbert")
    axs[1].set_xlabel("Tiempo [s]")
    axs[1].set_ylabel("Amplitud")
    axs[1].legend()
    axs[1].set_title("Original y Transformada de Hilbert")

    plt.tight_layout()
    plt.show()
    """
    # Señal de prueba: seno modulada
    t = np.linspace(0, 1, 500, endpoint=False)
    carrier = np.sin(2*np.pi*50*t)
    modulator = 1 + 0.5*np.sin(2*np.pi*3*t)
    x = carrier * modulator

    env = hilbert_transform(x)

    plt.figure()
    plt.plot(t, x, label='Señal')
    plt.plot(t, env, label='Envolvente', linewidth=2)
    plt.legend()
    plt.xlabel('Tiempo [s]')
    plt.show()
    """

