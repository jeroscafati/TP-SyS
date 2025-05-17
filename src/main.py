from flask import Flask, render_template, request
from io import BytesIO
import base64
from utils.primero import generar_sweep
from soundfile import write

app = Flask(__name__)

@app.route('/')
def home_page():
    return render_template('home.html')

@app.route('/probar', methods=['GET'])
def probar_page():
    return render_template('probar.html')

@app.route('/generar', methods=['POST'])
def generar():
    duracion = float(request.form['duracion'])
    f1 = float(request.form['f_inferior'])
    f2 = float(request.form['f_superior'])

    sweep, fs = generar_sweep(duracion=duracion,fs=44100,f_inferior=f1, f_superior=f2)
    buf = BytesIO()
    write(buf, sweep, fs, format='WAV')
    buf.seek(0)
    data_b64 = base64.b64encode(buf.read()).decode('ascii')
    return render_template(
        'resultado.html',
        audio_b64=data_b64,
        filename=f'sweep_{duracion:.1f}s_{int(f1)}-{int(f2)}.wav')


@app.route('/info')
def info_page():
    return render_template('info.html')

if __name__=='__main__':
    app.run(debug=True)