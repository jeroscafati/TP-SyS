from utils.primer_entrega.funcs import generar_sweep_inverse, ruidoRosa_voss_editado, grabar_reproducir,medir_latencia
from utils.tercer_entrega.otras_func import array_multicanal_a_1d
from utils.segunda_entrega.obtener_sintetizar_ri import obtener_RI_por_deconvolucion
import soundfile as sf

if __name__ == "__main__":
    print("\n<-----------SELECCIONAR MODO-------------->\n")
    print("Presionar 1 para generar señales (sweep,inverse sweep, pink noise)")
    print("Presionar 2 para grabar reproducir un sine sweep (opcional: Medir latencia)")
    print('Presionar 3 para obtener una RI a partir de sine sweep grabado en sala de informatica\n')
    opcion = input("Ingrese su opción: ")

    match opcion:
        case '1':
            print("\n<-----------SELECCIONAR-------------->\n")
            print("Desea generar tambien ruido rosa?")
            opcion2 = input('Seleccione (Y/n):')

            if opcion2.lower() == 'y':
                ruido_rosa = True
            else:
                ruido_rosa = False
    
            t = float(input("ingrese duracion de las señales en segundos:"))
            fs = int(input("ingrese la frecuencia de muestreo:"))
            f_inf = int(input("ingrese la frecuencia inferior:"))
            f_sup = int(input("ingrese la frecuencia superior:"))
            generar_sweep_inverse(t,fs,f_inf,f_sup,write_wav=True)
            if ruido_rosa:
                ruidoRosa_voss_editado(t,fs)
            print('\nAudios guardados en:\nTP-SyS/audios/temp')
        case '2':
            print("\n<-----------SELECCIONAR-------------->\n")
            t = float(input("ingrese duracion del sweep en segundos:"))
            fs = int(input("ingrese la frecuencia de muestreo:"))
            f_inf = int(input("ingrese la frecuencia inferior:"))
            f_sup = int(input("ingrese la frecuencia superior:"))

            sweep, i,f = generar_sweep_inverse(t,fs,f_inf,f_sup,write_wav=False)
            grabar_reproducir(sweep,fs)
            print('Grabacion finalizada,\n se guardo en TP-SyS/audios/temp')

            print('\n queres medir la latencia de tu dispositivo?')
            opcion3 = input('seleccione (Y/n):')

            if opcion3.lower() == 'y':
                medir_latencia()
            else:
                print('progama finalizado.')
        case '3':
            sweep,fs = sf.read("audios/sweep_aulaInformatica.wav") 
            sweep_1d = array_multicanal_a_1d(sweep)
            
            filter, fs1 = sf.read("audios/filtro_inverso.wav")
            filter_1d = array_multicanal_a_1d(filter)

            obtener_RI_por_deconvolucion(sweep_1d, filter_1d, 
                                                    exportar_wav=True)
            print('Operacion finalizada.')
            print('\nAudio guardado en:\nTP-SyS/audios/temp')