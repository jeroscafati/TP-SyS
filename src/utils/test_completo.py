from generar_ri import sintetizar_RI,escala_log,filtrar_signal
from suavizado import filtro_promedio_movil, hilbert_transform
from schroeder_lundeby import integral_schroeder
from linear_fit import regresion_lineal,calcular_parametros_acusticos
import numpy as np
from graph import graficar_dominio_temporal,graficar_espectro
import matplotlib.pyplot as plt
freq_t60 = {31.5: (2.0,1.0), 63:(2.5,1.0), 
            125:(2.8,1.0), 250:(2.2,1.0), 
            500: (1.8,1.0), 1000:(2.0,1.0), 
            2000: (1.2,1.0), 4000: (1.0,1.0), 
            8000: (0.8,1.0), 16000: (0.5,1.0)}
def sintetizar_y_calcular_parametros_acusticos(freq_t60, piso_ruido_db=-50):
    """
    Sintetiza una respuesta al impulso (RI) y calcula los parámetros acústicos
    a partir de la curva de decaimiento obtenida.
    
    Parámetros:
    - freq_t60: dict con frecuencias y sus respectivos T60 y A.
    - piso_ruido_db: nivel de ruido en dB.
    
    Retorna:
    - dict con los parámetros acústicos calculados.
    """
    #1. Sintetizar RI
    ri_sintetizada = sintetizar_RI(freq_t60,piso_ruido_db=piso_ruido_db)
    fs = ri_sintetizada['fs']

    #2 Filtro de octava
    ri_octavas = filtrar_signal(ri_sintetizada['audio_data'], fs, tipo_filtro='octava')

    #3. Suavizado promedio movil
    suavizado_octavas = {}
    for freq,signal in ri_octavas.items():
        suavizado_octavas[freq] = filtro_promedio_movil(hilbert_transform(signal),L=250)
    

    #4. Schroeder
    curva_decay = {}
    for freq,signal in suavizado_octavas.items():
        curva_decay[freq] = integral_schroeder(signal,fs)

    #5. Escala log
    curva_decay_db = {}
    for freq,signal in curva_decay.items():
        curva_decay_db[freq] = escala_log(signal)
   
    
    #6. Calcular parámetros acústicos
    parametros_acusticos = {}
    for freq, signal in curva_decay_db.items():
        parametros_acusticos[freq] = calcular_parametros_acusticos(signal, fs)

    #8. Mostrar resultados
    for freq, params in parametros_acusticos.items():
        print(f"Frecuencia: {freq} Hz")
        print(f"ORIGINAL: {freq_t60[freq][0]} s")
        print(f"t60 de T30: {params['T60_from_T30']:.2f} s")
        print(f"t60 de T20: {params['T60_from_T20']:.2f} s")
        print(f"t60 de T10: {params['T60_from_T10']:.2f} s")
        print(f"EDT: {params['EDT']:.2f} s")
        print('-'*30)

def graficar_cosas(freq_t60, piso_ruido_db=-50,banda=1000):
    #1. Sintetizar RI
    ri_sintetizada = sintetizar_RI(freq_t60,piso_ruido_db=piso_ruido_db)
    fs = ri_sintetizada['fs']

    #2 Filtro de octava
    ri_octavas = filtrar_signal(ri_sintetizada['audio_data'], fs, tipo_filtro='octava')
    ri_banda = ri_octavas[banda]

    #3. Suavizado promedio movil
    hilbert = hilbert_transform(ri_banda)

    media_movil = filtro_promedio_movil(hilbert,L=250)

    #4. Schroeder
    curva_decay = integral_schroeder(media_movil, fs)
    # Graficar dominio temporal
    t1 = np.arange(len(ri_banda)) / fs
    t2 = np.arange(len(hilbert)) / fs
    t3 = np.arange(len(media_movil)) / fs
    t4 = np.arange(len(curva_decay)) / fs
    plt.figure(figsize=(10, 4))
    plt.plot(t1, ri_banda, color='m',label='RI')
    plt.plot(t2, hilbert, color='b', label='Hilbert')
    plt.plot(t3, media_movil, color='g', label='Media Móvil')
    plt.plot(t4, curva_decay, color='r', label='Curva de Decaimiento')
    plt.title('Señal en el dominio temporal')
    plt.xlabel('Tiempo [s]')
    plt.ylabel('Amplitud')
    plt.grid(True)
    plt.legend()
    plt.savefig('test1khz.png',dpi=300, bbox_inches="tight")
    
if __name__ == "__main__":
    print("Presionar 1 para sintetizar RI y calcular parámetros acústicos")
    print("Presionar 2 para cargar RI y calcular parámetros acústicos")
    opcion = input("Ingrese su opción: ")
    match opcion:
        case '1':
            sintetizar_y_calcular_parametros_acusticos(freq_t60)
        case '2':
            graficar_cosas(freq_t60)


