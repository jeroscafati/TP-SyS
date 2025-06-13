from generar_ri import filtrar_signal
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
# --- SCRIPT DE TESTEO ---

# 1. Parámetros de prueba
fs = 48000  # Frecuencia de muestreo
duracion = 1  # 1 segundo
N = fs * duracion
t = np.linspace(0, duracion, N, endpoint=False)

# Frecuencia de banda a testear
fc_test = 1000

# --- Test con Tonos Puros ---
print("--- TESTEANDO FILTRO DE OCTAVA DE 1000 Hz CON TONOS PUROS ---")

def testear_tono(freq_tono):
    # Generar tono
    tono = np.sin(2 * np.pi * freq_tono * t)
    
    # Filtrar
    resultado_filtrado = filtrar_signal(tono, fs, tipo_filtro='octava', orden_filtro=4)
    tono_filtrado = resultado_filtrado[fc_test]
    
    # Calcular atenuación en dB
    # Usamos RMS para una medida robusta de la amplitud
    rms_entrada = np.sqrt(np.mean(tono**2))
    rms_salida = np.sqrt(np.mean(tono_filtrado**2))
    atenuacion_db = 20 * np.log10(rms_salida / rms_entrada)
    
    print(f"Tono de {freq_tono} Hz: Atenuación = {atenuacion_db:.2f} dB")

# Prueba 1: Passband (frecuencia central)
testear_tono(1000)

# Prueba 2: Stopband (frecuencias lejanas)
testear_tono(100)
testear_tono(8000)

# Prueba 3: Bandas adyacentes
testear_tono(500) # Centro de la banda de octava inferior
testear_tono(2000) # Centro de la banda de octava superior

print("\n")


# --- Test de Respuesta en Frecuencia con Impulso ---
print("--- GENERANDO GRÁFICO DE RESPUESTA EN FRECUENCIA ---")

# Generar un impulso
impulso = np.zeros(N)
impulso[0] = 1.0

# Filtrar el impulso para obtener la respuesta de todos los filtros
filtros_octava = filtrar_signal(impulso, fs, tipo_filtro='octava', orden_filtro=4)

# Graficar la respuesta de algunos filtros
plt.figure(figsize=(12, 8))
plt.title('Respuesta en Frecuencia de Filtros de Octava (Orden 4)')

for fc, respuesta_impulso in filtros_octava.items():
    # Solo graficamos algunas para no saturar el plot
    if fc in [63, 250, 1000, 4000]:
        # Calcular la respuesta en frecuencia via FFT
        w, h = signal.freqz(respuesta_impulso, worN=8000, fs=fs) # freqz es ideal para esto
        
        # Convertir a dB
        db = 20 * np.log10(np.abs(h))
        
        plt.plot(w, db, label=f'Banda de {fc} Hz')

plt.xscale('log')
plt.xlabel('Frecuencia (Hz)')
plt.ylabel('Magnitud (dB)')
plt.grid(True, which='both', linestyle='--')
plt.legend()
plt.ylim(-80, 5) # Limitar eje Y para ver mejor la forma del filtro
plt.tight_layout()
plt.savefig("test:filtro.png", dpi=300, bbox_inches="tight")