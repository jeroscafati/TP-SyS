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
        Longitud (muestras) de la ventana de promedio.
    
    Retorna:
    --------
    y : ndarray
        Señal suavizada.
    """
    if L < 1:
        raise ValueError("La longitud L debe ser mayor o igual a 1")

    # Creamos la ventana deslizante
    kernel = np.ones(L) / L

    # Convolucionamos
    y = np.convolve(x, kernel, mode='same')  
    return y
