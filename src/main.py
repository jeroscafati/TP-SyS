from flask import Flask, render_template, request, Response
import numpy as np
import matplotlib.pyplot as plt
import io
from utils.generacion_sonidos import generar_sweep_inverse, wav_to_b64
from utils.graficar import fig_to_png_response, graficar_dominio_temporal, graficar_espectro

app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='/')
app.secret_key = 'salchipapa'

@app.route('/')
def home_page():
    return render_template('home.html')

@app.route('/probar', methods=['GET'])
def probar_page():
    return render_template('probar.html')

@app.route("/analizar_RI", methods=['GET'])
def analizar_RI_page():
    return render_template('analizar_RI.html')

@app.route('/generar', methods=['POST'])
def generar():
    duracion = float(request.form.get('duracion'))
    f1 = float(request.form.get('f_inferior'))
    f2 = float(request.form.get('f_superior'))

    sweep, inverse_sweep, fs = generar_sweep_inverse(duracion=duracion,fs=44100,f_inferior=f1, f_superior=f2)
    
    sweep_b64 = wav_to_b64(sweep, fs)
    inverse_b64 = wav_to_b64(inverse_sweep, fs)
    return render_template(
        'resultado.html',
        audio_sweep_b64=sweep_b64,
        audio_inverse_b64=inverse_b64,
        filename_sweep=f'sweep_{duracion:.1f}s_{int(f1)}-{int(f2)}.wav',
        filename_inverse=f'inverse_{duracion:.1f}s_{int(f1)}-{int(f2)}.wav')
    
@app.route('/file_upload', methods=['POST'])
def file_upload():
    return "chetomal"

@app.route("/plot")
def plot():
    # 1. Obtenemos el ID de la señal desde los parámetros de la URL (ej: /plot?id=tono_440hz)
    signal_id = request.args.get('id')
    if not signal_id:
        abort(400, "Error: Falta el parámetro 'id' de la señal.")

    # 2. Recuperamos los datos de la señal y la fs desde la sesión
    fs = session.get('fs', 44100) # Usamos un valor por defecto por si acaso
    signal_data = session.get('signals', {}).get(signal_id)
    
    if not signal_data:
        abort(404, "Error: No se encontró una señal con ese ID.")

    # 3. Convertimos la lista de vuelta a un array de NumPy
    signal_a_graficar = np.array(signal_data)

    # 4. Generamos el gráfico y lo devolvemos
    fig = graficar_dominio_temporal(signal_a_graficar, fs)
    return fig_to_png_response(fig)

if __name__=='__main__':
    app.run(debug=True)