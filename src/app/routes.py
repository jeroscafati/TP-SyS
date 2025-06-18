from flask import render_template, request, jsonify, session
import numpy as np
from utils.primer_entrega.generacion_sonidos import generar_sweep_inverse, wav_to_b64
from utils.segunda_entrega.graficar import fig_to_png_response, graficar_dominio_temporal
from utils.params_from_ri import obtener_parametros_de_RI
from utils.segunda_entrega.obtener_sintetizar_ri import sintetizar_RI
from utils.constantes.filtros import FRECUENCIAS_OCTAVA
from . import app  

@app.route('/')
def home_page():
    return render_template('home.html')

@app.route('/generar_sonidos', methods=['GET'])
def generar_sonidos_page():
    return render_template('generar_sonidos.html')

@app.route("/analizar_RI", methods=['GET'])
def analizar_RI_page():
    return render_template('analizar_RI.html')

@app.route("/analizar_RI/validar_funcionamiento", methods=['GET','POST'])
def validar_funcionamiento():
    if request.method == 'POST':
        try:
            datos = request.get_json()
            ruido_piso_db = datos['ruido_piso_db']
            frecuencias = datos['frecuencias']

            # Convert string frequency keys to integers
            frecuencias_converted = {int(freq): values for freq, values in frecuencias.items()}
            ri = sintetizar_RI(frecuencias_converted, piso_ruido_db=ruido_piso_db)

            parametros_acusticos = obtener_parametros_de_RI(ri['audio_data'],
                                                          ri['fs'],
                                                          banda='octava',
                                                          ventana_suavizado_ms=5)
            return jsonify({"status": "success", "data": parametros_acusticos}), 200
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 400
    
    # Pass the frequencies to the template for rendering
    return render_template('validar_funcionamiento.html', frecuencias=FRECUENCIAS_OCTAVA)

@app.route('/generar', methods=['POST'])
def generar():
    duracion = float(request.form.get('duracion'))
    f1 = float(request.form.get('f_inferior'))
    f2 = float(request.form.get('f_superior'))

    sweep, inverse_sweep, fs = generar_sweep_inverse(
        duracion=duracion,
        fs=44100,
        f_inferior=f1,
        f_superior=f2
    )
    
    sweep_b64 = wav_to_b64(sweep, fs)
    inverse_b64 = wav_to_b64(inverse_sweep, fs)
    
    return render_template(
        'resultado.html',
        audio_sweep_b64=sweep_b64,
        audio_inverse_b64=inverse_b64,
        filename_sweep=f'sweep_{duracion:.1f}s_{int(f1)}-{int(f2)}.wav',
        filename_inverse=f'inverse_{duracion:.1f}s_{int(f1)}-{int(f2)}.wav'
    )

@app.route('/file_upload', methods=['POST'])
def file_upload():
    return "Funcionalidad de carga de archivos en desarrollo"

@app.route("/plot")
def plot():
    signal_id = request.args.get('id')
    if not signal_id:
        return "Error: Falta el parámetro 'id' de la señal.", 400

    fs = session.get('fs', 44100)
    signal_data = session.get('signals', {}).get(signal_id)
    
    if not signal_data:
        return "Error: No se encontró una señal con ese ID.", 404

    signal_a_graficar = np.array(signal_data)
    fig = graficar_dominio_temporal(signal_a_graficar, fs)
    return fig_to_png_response(fig)
