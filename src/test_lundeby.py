from utils.segunda_entrega.obtener_sintetizar_ri import sintetizar_RI
import numpy as np
import matplotlib.pyplot as plt
from utils.tercer_entrega.schroeder_lundeby import lundeby


def test_lundeby(freq_t60, piso_ruido_db):
    """
    Test de validación mejorado para la función Lundeby.

    - Es parametrizable.
    - Evita cálculos redundantes pidiendo datos de depuración.
    - Grafica la regresión final para un mejor análisis visual.
    - Añade una validación cuantitativa comparando el T60.
    """
    print(f"\n--- INICIANDO TEST CON PISO DE RUIDO = {piso_ruido_db} dB ---")

    # 1) Sintetizar RI con los parámetros dados
    # (Asumo que sintetizar_RI puede tomar un T60 de banda ancha si el dict tiene una sola entrada)
    ri_dict = sintetizar_RI(freq_t60, piso_ruido_db=piso_ruido_db)
    audio = ri_dict['audio_data']
    fs = ri_dict['fs']

    # 2) Aplicar Lundeby pidiendo los datos de depuración
    resultado = lundeby(audio, fs, return_debug_data=True)

    # 3) Extraer los resultados para graficar y analizar
    # No necesitamos recalcular nada, ¡ya lo tenemos!
    sch_db = resultado['schroeder_db']
    tiempo_rms = resultado['tiempo_rms']
    tiempo_cruce = resultado['tiempo_cruce']
    nivel_ruido = resultado['nivel_ruido']
    slope = resultado['slope']
    intercept = resultado['intercept']

    # 4) Validación Cuantitativa: Comparar T60
    # Obtenemos el T60 "real" del primer valor en nuestro diccionario de síntesis
    t60_real = list(freq_t60.values())[0][0]
    t60_estimado = -60.0 / slope
    error_t60 = 100 * (t60_estimado - t60_real) / t60_real

    print(f"  T60 Teórico de la RI Sintética : {t60_real:.2f} s")
    print(f"  T60 Estimado por la pendiente de Lundeby: {t60_estimado:.2f} s")
    print(f"  Error relativo: {error_t60:.2f} %")

    # 5) Graficar (Gráfico Enriquecido)
    plt.figure(figsize=(12, 7))
    plt.plot(tiempo_rms, sch_db, label="Curva de Decaimiento (Schroeder)", alpha=0.7)
    
    # Graficar la línea de ruido
    plt.axhline(nivel_ruido, color='red', linestyle='--', label=f"Nivel de Ruido Estimado ({nivel_ruido:.1f} dB)")
    
    # Graficar el punto de cruce
    plt.axvline(tiempo_cruce, color='green', linestyle=':', linewidth=2.5, label=f"Punto de Cruce ({tiempo_cruce:.2f} s)")
    
    # *** MEJORA CLAVE: Graficar la recta de regresión final ***
    tiempo_plot = np.array([0, tiempo_rms[-1]])
    linea_regresion = slope * tiempo_plot + intercept
    plt.plot(tiempo_plot, linea_regresion, 'k-', linewidth=2, label=f"Regresión Final (Pendiente={slope:.1f} dB/s)")

    plt.title(f"Validación del Método de Lundeby (Ruido a {piso_ruido_db} dB)")
    plt.xlabel("Tiempo [s]")
    plt.ylabel("Nivel [dB]")
    plt.ylim(min(nivel_ruido - 20, -80), 5)
    plt.xlim(0, tiempo_rms[-1] * 1.1)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # --- Ejecutar el test para diferentes escenarios ---
    
    # Escenario 1: Ruido bajo, decaimiento claro
    freq_t60_caso1 = {1000: (2.0, 1.0)} # T60 de 2.0s en la banda de 1kHz
    test_lundeby(freq_t60_caso1, piso_ruido_db=-80)
    
    # Escenario 2: Ruido alto, la señal se pierde antes
    freq_t60_caso2 = {1000: (2.0, 1.0)} # Misma IR
    test_lundeby(freq_t60_caso2, piso_ruido_db=-45)
