from utils.segunda_entrega.obtener_sintetizar_ri import sintetizar_RI
from utils.tercer_entrega.otras_func import array_multicanal_a_1d
from utils.segunda_entrega.graph import graficar_dominio_temporal,graficar_espectro,graficar_resultados
import soundfile as sf
from utils.params_from_ri import obtener_parametros_de_RI

#<-------RI sintetica para validar software--------->
freq_t60 = {31.5: (2.0,1.0), 63:(2.5,1.0), 
            125:(2.8,1.0), 250:(2.2,1.0), 
            500: (1.8,1.0), 1000:(2.0,1.0), 
            2000: (1.2,1.0), 4000: (1.0,1.0), 
            8000: (0.8,1.0), 16000: (0.5,1.0)}
piso_rudio_db = -50

#<-------- DATOS RI REALES/ comparacion con softwares profesionales ------>

audio, fs_audio = sf.read('audios/clifford_tower_S1R1_Bformat.wav')
#diccionario de valores para comparar, tabulados de OPENAIR.
tab_clifford_tower = {125:{'T60':2.17,'EDT':1.93,'D50':23.39,'C80':-2.80},
            250:{'T60':2.34,'EDT':2.68,'D50':17.03,'C80':-3.44}, 
            500: {'T60':2.61,'EDT':2.93,'D50':31.20,'C80':-1.76}, 
            1000:{'T60':2.39,'EDT':2.38,'D50':39.95,'C80':-0.19}, 
            2000: {'T60':2.05,'EDT':1.78,'D50':63.71,'C80':4.13}, 
            4000: {'T60':1.40,'EDT':0.90,'D50':76.52,'C80':7.09}, 
            8000: {'T60':1.02,'EDT':0.63,'D50':81.03,'C80':8.74}}

tab_alcuin_college = {125:{'T60':1.99,'EDT':1.51,'D50':0.46,'C80':1.04},
            250:{'T60':1.49,'EDT':1.89,'D50':0.32,'C80':-1.86}, 
            500: {'T60':1.61,'EDT':1.89,'D50':0.47,'C80':0.44}, 
            1000:{'T60':1.83,'EDT':1.89,'D50':0.61,'C80':2.48}, 
            2000: {'T60':1.77,'EDT':1.89,'D50':0.34,'C80':-1.58}, 
            4000: {'T60':1.52,'EDT':1.51,'D50':0.61,'C80':3.67}, 
            8000: {'T60':1.2,'EDT':1.51,'D50':0.65,'C80':3.74}}

tab_lyons_concert_hall = {125:{'T60':2.18,'EDT':1.7,'D50':0.25,'C80':-0.66},
            250:{'T60':2.05,'EDT':2.21,'D50':0.12,'C80':-3.54}, 
            500: {'T60':1.89,'EDT':2.08,'D50':0.15,'C80':-2.86}, 
            1000:{'T60':1.86,'EDT':2.08,'D50':0.19,'C80':-2.84}, 
            2000: {'T60':1.69,'EDT':1.82,'D50':0.2,'C80':-2.37}, 
            4000: {'T60':1.28,'EDT':1.44,'D50':0.33,'C80':0.46}, 
            8000: {'T60':0.9,'EDT':1.06,'D50':0.41,'C80':2.63}}


if __name__ == "__main__":
    print("\n<-----------SELECCIONAR MODO-------------->\n")
    print("Presionar 1 para sintetizar RI y calcular parámetros acústicos")
    print("Presionar 2 para analizar parametros acusticos de RI real\n")
    opcion = input("Ingrese su opción: ")

    print("\n<----------GENERAR GRAFICOS-------------->\n")
    print("Quiere visualizar la señal en gráficos? (Y/n)")
    graf = input('Ingrese opcion: ')
    if graf.lower() == "y":
        graf_bool = True
    else:
        graf_bool = False

    match opcion:
        case '1':
            ri = sintetizar_RI(freq_t60,piso_ruido_db=piso_rudio_db)
            param = obtener_parametros_de_RI(ri['audio_data'],
                                                          ri['fs'],
                                                            banda='octava',
                                                            ventana_suavizado_ms=5,
                                                            debug_mode=graf_bool)
            

            if graf_bool:
                parametros_acusticos, datos_graf = param
                graficar_resultados(1000,datos_graf,ri['fs'])
                graficar_dominio_temporal(ri['audio_data'],ri['fs'])
                graficar_dominio_temporal(ri['audio_data'],ri['fs'],hilbert=True)
                graficar_espectro(ri['audio_data'],ri['fs'])

            else: 
                parametros_acusticos = param
            
            print("\n<--------RESULTADOS-------------->\n")
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
            print("Graficos guardados en la siguiente carpeta:\nTP-SyS/img/temp")
        case '2':
            print("\n<--------RECINTO-------------->\n")
            print("Seleccione RI a analizar:")
            print("1) Clifford's Tower, York ")
            print("2) Alcuin College, University of York")
            print('3) Jack Lyons Concert Hall (University of York)')
            opcion_ri = input("Ingrese su opción: ")

            if opcion_ri == '1':
                audio, fs_audio = sf.read('audios/clifford_tower_S1R1_Bformat.wav')
                tab = tab_clifford_tower

            elif opcion_ri == '2':
                audio, fs_audio = sf.read('audios/alcuin_s1r1_bformat.wav')
                tab = tab_alcuin_college

            elif opcion_ri == '3':
                audio, fs_audio = sf.read('audios/rir_jack_lyons_lp1_96k.wav')
                tab = tab_lyons_concert_hall
        
            audio1d = array_multicanal_a_1d(audio)
            param = obtener_parametros_de_RI(audio1d,
                                                            fs_audio,
                                                            banda='octava',
                                                            ventana_suavizado_ms=5,
                                                            debug_mode= graf_bool)
            
            if graf_bool:
                parametros_acusticos, datos_graf = param
                graficar_resultados(1000,datos_graf,fs_audio)
                graficar_dominio_temporal(audio1d,fs_audio)
                graficar_dominio_temporal(audio1d,fs_audio,hilbert=True)
                graficar_espectro(audio1d,fs_audio)

            else: 
                parametros_acusticos = param

            print("\n<--------RESULTADOS-------------->\n")
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
            print("Graficos guardados en la siguiente carpeta:\nTP-SyS/img/temp")
