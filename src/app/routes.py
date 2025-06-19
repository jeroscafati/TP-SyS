from flask import render_template, request, jsonify
import io
import soundfile as sf
from utils.primer_entrega.generacion_sonidos import generar_sweep_inverse, wav_to_b64
from utils.params_from_ri import obtener_parametros_de_RI
from utils.segunda_entrega.graph import graficar_resultados,graficar_dominio_temporal,graficar_espectro
from utils.segunda_entrega.obtener_sintetizar_ri import sintetizar_RI
from utils.tercer_entrega.otras_func import array_multicanal_a_1d
from utils.constantes.filtros import FRECUENCIAS_OCTAVA
from . import app  

# Limitar tamaño máximo del body a 50MB
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

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

            parametros_acusticos,datos_graf = obtener_parametros_de_RI(ri['audio_data'],
                                                          ri['fs'],
                                                          banda='octava',
                                                          ventana_suavizado_ms=5,
                                                          debug_mode=True)
            
            graficar_resultados(1000,datos_graf,ri['fs'])
            graficar_dominio_temporal(ri['audio_data'],ri['fs'])
            graficar_dominio_temporal(ri['audio_data'],ri['fs'],hilbert=True)
            graficar_espectro(ri['audio_data'],ri['fs'])

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
    wav_file = request.files['file']
    
    if not wav_file:
        return jsonify(error='No se recibió audio_wav'), 400

    try:
        audio_data, fs = sf.read(io.BytesIO(wav_file.read()))
    except RuntimeError as e:
        return jsonify(error=f'Error al leer WAV: {str(e)}'), 400

    audio_data_mono = array_multicanal_a_1d(audio_data)
    parametros_acusticos, datos_graf = obtener_parametros_de_RI(audio_data_mono, fs, banda='octava', ventana_suavizado_ms=5,debug_mode=True)
    
    # Graficos
    graficar_resultados(1000,datos_graf,fs)
    graficar_dominio_temporal(audio_data_mono,fs)
    graficar_dominio_temporal(audio_data_mono,fs,hilbert=True)
    graficar_espectro(audio_data_mono,fs)

    return jsonify({
        "status": "success",
        "data": parametros_acusticos
    }), 200