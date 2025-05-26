from flask import Flask, render_template, request
from utils.primero import generar_sweep_inverse, wav_to_b64


app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='/')

@app.route('/')
def home_page():
    return render_template('home.html')

@app.route('/probar', methods=['GET'])
def probar_page():
    return render_template('probar.html')

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

@app.route('/info')
def info_page():
    return render_template('info.html')

if __name__=='__main__':
    app.run(debug=True)