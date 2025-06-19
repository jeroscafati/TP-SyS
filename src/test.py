from utils.segunda_entrega.graph import graficar_resultados
from utils.segunda_entrega.obtener_sintetizar_ri import sintetizar_RI
from utils.params_from_ri import obtener_parametros_de_RI
frecuencias = {125: (2.8,1.0), 250:(2.2,1.0), 500:(1.8,1.0)}
ri = sintetizar_RI(frecuencias)
param, datos = obtener_parametros_de_RI(ri['audio_data'],ri['fs'],banda='octava',ventana_suavizado_ms=5,debug_mode=True)
graficar_resultados(500,datos,ri['fs'])
