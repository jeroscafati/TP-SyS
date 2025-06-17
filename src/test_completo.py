from utils.obtener_sintetizar_ri import sintetizar_RI
from utils.otras_func import array_multicanal_a_1d
from utils.suavizado_y_filtros import hilbert_transform
import soundfile as sf
from utils.flujo_completo import obtener_parametros_de_RI
import matplotlib.pyplot as plt
import numpy as np

def graficar_resultados(fs, parametros, debug_data, referencias=None):
    """
    Genera gráficos detallados para cada banda de frecuencia.

    Parámetros:
    -----------
    fs : int
        Frecuencia de muestreo.
    parametros : dict
        Diccionario con los parámetros acústicos finales.
    debug_data : dict
        Diccionario con los datos intermedios de la función principal.
    referencias : dict, opcional
        Diccionario con los valores de referencia para comparar en los títulos.
    """
    ri_filtradas = debug_data['ri_filtradas']
    curvas_db = debug_data['curvas_decay_db']
    datos_lundeby = debug_data['datos_lundeby']
    # datos_regresion = debug_data['datos_regresion'] # Para futuras mejoras

    for freq, decay_curve in curvas_db.items():
        # Preparar datos para el gráfico
        ri_banda = ri_filtradas[freq]
        tiempo_ri = np.arange(len(ri_banda)) / fs
        
        # Envolvente en dB de la RI filtrada
        envolvente_db = 20 * np.log10(np.abs(hilbert_transform(ri_banda)))
        envolvente_db -= np.max(envolvente_db) # Normalizar a 0 dB

        # Datos de la curva de Schroeder y Lundeby
        lundeby_info = datos_lundeby[freq]
        tiempo_schroeder = lundeby_info['tiempo_rms'] # Asumiendo que lundeby lo devuelve
        nivel_ruido = lundeby_info['nivel_ruido']
        tiempo_cruce = lundeby_info['tiempo_cruce']
        slope = lundeby_info['slope']
        intercept = lundeby_info['intercept']
        tiempo_sch_full = np.arange(len(decay_curve)) / fs
        # Crear la figura
        plt.figure(figsize=(14, 8))
        
        # 1. Graficar la RI filtrada en dB
        plt.plot(tiempo_ri, envolvente_db,'c-', color='r',alpha=0.5, label='Envolvente RI (dB)')
        
        # 2. Graficar la curva de decaimiento de Schroeder
        plt.plot(tiempo_sch_full,decay_curve, 'b-', linewidth=2, label='Curva de Schroeder')
        
        # 3. Graficar la línea de regresión de Lundeby (que aproxima el T60)
        tiempo_plot_reg = np.array([0, tiempo_cruce * 1.1])
        linea_regresion = slope * tiempo_plot_reg + intercept
        plt.plot(tiempo_plot_reg, linea_regresion, 'k--', linewidth=2.5, label=f'Regresión Lundeby (T60 ≈ {-60/slope:.2f}s)')

        # 4. Marcar el ruido y el punto de cruce
        plt.axhline(nivel_ruido, color='r', linestyle=':', label=f'Nivel de Ruido ({nivel_ruido:.1f} dB)')
        plt.axvline(tiempo_cruce, color='g', linestyle=':', label=f'Cruce Lundeby ({tiempo_cruce:.2f} s)')

        # Configuración del gráfico
        titulo = f'Análisis para la Banda de {freq} Hz\n'
        if referencias and freq in referencias:
            ref = referencias[freq]
            if isinstance(ref, dict) and 'T60' in ref: # Para el caso de archivo real
                 titulo += f"T60 Calculado: {parametros[freq]['T60_from_T30']:.2f}s | T60 Tabulado: {ref['T60']}s"
            else: # Para el caso sintético
                 titulo += f"T60 Calculado: {parametros[freq]['T60_from_T30']:.2f}s | T60 Original: {ref[0]}s"

        plt.title(titulo)
        plt.xlabel('Tiempo (s)')
        plt.ylabel('Nivel (dB)')
        plt.grid(True, which='both', linestyle='--', alpha=0.6)
        plt.legend()
        plt.ylim(max(nivel_ruido - 20, -100), 5) # Límite dinámico del eje Y
        plt.xlim(0, max(tiempo_cruce * 1.2, 1.0)) # Límite dinámico del eje X
        
        plt.show()


freq_t60 = {31.5: (2.0,1.0), 63:(2.5,1.0), 
            125:(2.8,1.0), 250:(2.2,1.0), 
            500: (1.8,1.0), 1000:(2.0,1.0), 
            2000: (1.2,1.0), 4000: (1.0,1.0), 
            8000: (0.8,1.0), 16000: (0.5,1.0)}

audio, fs_audio = sf.read('audios/clifford_tower_S1R1_Bformat.wav')
#diccionario de valores para comparar, tabulados de OPENAIR.
tab = {125:{'T60':2.17,'EDT':1.93,'D50':23.39,'C80':-2.80},
            250:{'T60':2.34,'EDT':2.68,'D50':17.03,'C80':-3.44}, 
            500: {'T60':2.61,'EDT':2.93,'D50':31.20,'C80':-1.76}, 
            1000:{'T60':2.39,'EDT':2.38,'D50':39.95,'C80':-0.19}, 
            2000: {'T60':2.05,'EDT':1.78,'D50':63.71,'C80':4.13}, 
            4000: {'T60':1.40,'EDT':0.90,'D50':76.52,'C80':7.09}, 
            8000: {'T60':1.02,'EDT':0.63,'D50':81.03,'C80':8.74}}



if __name__ == "__main__":
    print("Presionar 1 para sintetizar RI y calcular parámetros acústicos (MUCHOS GRAFICOS)")
    print("Presionar 2 para cargar RI y calcular parámetros acústicos (MUCHOS GRAFICOS)")
    print("Presionar 3 para sintetizar RI y calcular parámetros acústicos (MUCHA DATA)")
    print("Presionar 4 para cargar RI y calcular parámetros acústicos (MUCHA DATA)")
    opcion = input("Ingrese su opción: ")

    # Preguntar si se desean los gráficos
    if opcion == ('1' or '2'):
        ver_graficos_input = input("¿Desea ver los gráficos de depuración? (Y/n): ").lower()
        ver_graficos = (ver_graficos_input == 'y')
    
    match opcion:
        case '1':
            ri_dict = sintetizar_RI(freq_t60, piso_ruido_db=-50)
            
            # Llamada a la función principal con el modo debug
            resultado = obtener_parametros_de_RI(ri_dict['audio_data'],
                                                 ri_dict['fs'],
                                                 banda='octava',
                                                 ventana_suavizado_ms=5,
                                                 debug_mode=ver_graficos)
            
            if ver_graficos:
                parametros_acusticos, datos_debug = resultado
            else:
                parametros_acusticos = resultado

            # ... (tu código para imprimir los resultados no cambia) ...
            for freq, params in parametros_acusticos.items():
                print(f"Frecuencia: {freq} Hz")
                print(f"ORIGINAL: {freq_t60[freq][0]} s")
                #... etc
                print('-'*30)

            # Si el usuario lo pidió, mostrar los gráficos
            if ver_graficos:
                graficar_resultados(ri_dict['fs'], parametros_acusticos, datos_debug, referencias=freq_t60)

        case '2':
            audio1d = array_multicanal_a_1d(audio)
            
            # Llamada a la función principal con el modo debug
            resultado = obtener_parametros_de_RI(audio1d,
                                                 fs_audio,
                                                 banda='octava',
                                                 ventana_suavizado_ms=5,
                                                 debug_mode=ver_graficos)

            if ver_graficos:
                parametros_acusticos, datos_debug = resultado
            else:
                parametros_acusticos = resultado

            # ... (tu código para imprimir los resultados no cambia) ...
            for freq, params in parametros_acusticos.items():
                if freq in tab:
                    print(f"Frecuencia: {freq} Hz")
                    #... etc
                    print('-'*50)

            # Si el usuario lo pidió, mostrar los gráficos
            if ver_graficos:
                graficar_resultados(fs_audio, parametros_acusticos, datos_debug, referencias=tab)
        case '3':
            ri = sintetizar_RI(freq_t60,piso_ruido_db=-50)
            parametros_acusticos = obtener_parametros_de_RI(ri['audio_data'],
                                                          ri['fs'],
                                                            banda='octava',
                                                            ventana_suavizado_ms=5)
            for freq, params in parametros_acusticos.items():
                print(f"Frecuencia: {freq} Hz")
                print(f"ORIGINAL: {freq_t60[freq][0]} s")
                print(f"t60 de T30: {params['T60_from_T30']:.2f} s")
                print(f"t60 de T20: {params['T60_from_T20']:.2f} s")
                print(f"t60 de T10: {params['T60_from_T10']:.2f} s")
                print(f"EDT: {params['EDT']:.2f} s")
                print(f"D50: {params['D50']:.2f}%")
                print(f"C80: {params['C80']:.2f}")
                print('-'*30)
        case '4':
            audio1d = array_multicanal_a_1d(audio)
            parametros_acusticos = obtener_parametros_de_RI(audio1d,
                                                            fs_audio,
                                                            banda='octava',
                                                            ventana_suavizado_ms=5)
            for freq, params in parametros_acusticos.items():
                print(f"Frecuencia: {freq} Hz")
                print(f"T60 TABULADO:{tab[freq]['T60']}s")
                print(f"t60 de T30: {params['T60_from_T30']:.2f}s/ {100*(params['T60_from_T30']-tab[freq]['T60'])/tab[freq]['T60']:.1f}% de dif.")
                print(f"t60 de T20: {params['T60_from_T20']:.2f}s/ {100*(params['T60_from_T20']-tab[freq]['T60'])/tab[freq]['T60']:.1f}% de dif.")
                print(f"t60 de T10: {params['T60_from_T10']:.2f}s/ {100*(params['T60_from_T10']-tab[freq]['T60'])/tab[freq]['T60']:.1f}% de dif.")
                print(f"EDT TABULADO: {tab[freq]['EDT']}s")
                print(f"EDT: {params['EDT']:.2f}s/ {100*(params['EDT']-tab[freq]['EDT'])/tab[freq]['EDT']:.1f}% de dif.")
                print(f"C80 TABULADO: {tab[freq]['C80']}")
                print(f"C80: {params['C80']:.2f}/ {100*(params['C80']-tab[freq]['C80'])/tab[freq]['C80']:.1f}% de dif.")
                print(f"D50 TABULADO: {tab[freq]['D50']}")
                print(f"D50: {params['D50']:.2f}/ {100*(params['D50']-tab[freq]['D50'])/tab[freq]['D50']:.1f}% de dif.")
                print('-'*50)


