from generar_ri import sintetizar_RI
from suavizado import array_multicanal_a_1d
import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt
from flujo_completo import obtener_parametros_de_RI

freq_t60 = {31.5: (2.0,1.0), 63:(2.5,1.0), 
            125:(2.8,1.0), 250:(2.2,1.0), 
            500: (1.8,1.0), 1000:(2.0,1.0), 
            2000: (1.2,1.0), 4000: (1.0,1.0), 
            8000: (0.8,1.0), 16000: (0.5,1.0)}

audio, fs_audio = sf.read('audios/clifford_tower_S1R1_Bformat.wav')
#diccionario de valores para comparar, tabulados OPENAIR.
tab = {125:{'T60':2.17,'EDT':1.93,'D50':23.39,'C80':-2.80},
            250:{'T60':2.34,'EDT':2.68,'D50':17.03,'C80':-3.44}, 
            500: {'T60':2.61,'EDT':2.93,'D50':31.20,'C80':-1.76}, 
            1000:{'T60':2.39,'EDT':2.38,'D50':39.95,'C80':-0.19}, 
            2000: {'T60':2.05,'EDT':1.78,'D50':63.71,'C80':4.13}, 
            4000: {'T60':1.40,'EDT':0.90,'D50':76.52,'C80':7.09}, 
            8000: {'T60':1.02,'EDT':0.63,'D50':81.03,'C80':8.74}}

if __name__ == "__main__":
    print("Presionar 1 para sintetizar RI y calcular parámetros acústicos")
    print("Presionar 2 para cargar RI y calcular parámetros acústicos")
    opcion = input("Ingrese su opción: ")
    match opcion:
        case '1':
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
                print('-'*30)
        case '2':
            audio1d = array_multicanal_a_1d(audio)
            parametros_acusticos = obtener_parametros_de_RI(audio1d,
                                                            fs_audio,
                                                            banda='octava',
                                                            ventana_suavizado_ms=5)
            for freq, params in parametros_acusticos.items():
                print(f"Frecuencia: {freq} Hz")
                print(f'T60 TABULADO:{tab[freq]['T60']}s')
                print(f"t60 de T30: {params['T60_from_T30']:.2f}s/ {100*(params['T60_from_T30']-tab[freq]['T60'])/tab[freq]['T60']:.1f}% de dif.")
                print(f"t60 de T20: {params['T60_from_T20']:.2f}s/ {100*(params['T60_from_T20']-tab[freq]['T60'])/tab[freq]['T60']:.1f}% de dif.")
                print(f"t60 de T10: {params['T60_from_T10']:.2f}s/ {100*(params['T60_from_T10']-tab[freq]['T60'])/tab[freq]['T60']:.1f}% de dif.")
                print(f"EDT TABULADO: {tab[freq]["EDT"]}s")
                print(f"EDT: {params['EDT']:.2f}s/ {100*(params['EDT']-tab[freq]['EDT'])/tab[freq]['EDT']:.1f}% de dif.")
                print('-'*50)


