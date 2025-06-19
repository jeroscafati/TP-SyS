/**
 * Envía el formulario de validación de funcionamiento
 * @param {string} apiUrl - URL del endpoint de la API (opcional, por defecto es '/validar_funcionamiento')
 */
function uploadFile() {
    const fileInput = document.getElementById('file');
    const file = fileInput.files[0];
    if (file) {
        const formData = new FormData();
        formData.append('file', file);
        
        // Find the form that contains the file input
        const form = fileInput.closest('form');
        const submitBtn = form.querySelector('button[type="submit"], button[type="button"]');
        const originalBtnText = submitBtn.innerHTML;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Procesando...';
        
        fetch('/file_upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.status == 'success') {
                mostrarResultados(data.data);
            } else {
                console.error('Error al cargar el audio:', data.error);
            }
        })
        .catch(error => {
            console.error('Error al cargar el audio:', error);
        })
        .finally(() => {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalBtnText;
        });
    }
}

function enviarFormulario(apiUrl = '/validar_funcionamiento') {
    const form = document.getElementById('sintetizarRI');
    const formData = new FormData(form);
    
    // Get the form values
    const ruidoPisoDb = parseFloat(form.querySelector('#ruido_piso_db').value);
    
    // Prepare the data object with all required fields
    const datos = {
        ruido_piso_db: ruidoPisoDb,
        frecuencias: {}
    };
    
    // Get all frequency inputs and group them by frequency
    const t60Inputs = form.querySelectorAll('[name^="t60_"]');
    t60Inputs.forEach(input => {
        const freq = input.name.split('_')[1];
        const t60 = parseFloat(input.value);
        const ampInput = form.querySelector(`[name="amp_${freq}"]`);
        const amp = parseFloat(ampInput.value);
        datos.frecuencias[freq] = [t60, amp];
    });
    
    console.log('Enviando datos:', datos);
    
    // Show loading state
    const submitBtn = form.querySelector('button[type="button"]');
    const originalBtnText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Procesando...';
    
    fetch(apiUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(datos)
    })
    .then(response => {
        if (!response.ok) {
            return response.text().then(text => { throw new Error(text) });
        }
        return response.json();
    })
    .then(data => {
        console.log('Success:', data);
        mostrarResultados(data.data);
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error al procesar la solicitud: ' + error.message);
    })
    .finally(() => {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalBtnText;
    });
}

function mostrarResultados(data) {
    const resultadosDiv = document.getElementById('resultados');
    const encabezadosFrecuencias = document.getElementById('encabezadosFrecuencias');
    const cuerpoTabla = document.getElementById('cuerpoTabla');
    
    // Clear previous results
    resultadosDiv.innerHTML = `
        <div class="table-responsive">
            <table class="table table-bordered table-striped" id="tablaResultados">
                <thead class="table-dark">
                    <tr id="encabezadosFrecuencias"></tr>
                </thead>
                <tbody id="cuerpoTabla"></tbody>
            </table>
        </div>
        <h3>Gráficos</h3>
        <p>Estos gráficos muestran el dominio temporal y de frecuencia de la señal, así como el análisis de respuesta al impulso.</p>
        <div class="mt-4 text-center">
        <div class="row">
            <div class="col">
            <img src="/static/img/temp/time_domain_plot.png" alt="Dominio temporal de la señal" class="img-fluid rounded shadow mb-2">
            <p class="text-muted">Dominio temporal de la señal</p>
            </div>
            <div class="col">
            <img src="/static/img/temp/time_domain_plot_hilbert.png" alt="Dominio temporal de la señal con envolvente" class="img-fluid rounded shadow mb-2">
            <p class="text-muted">Dominio temporal de la señal con envolvente</p>
            </div>
        </div>
        <div class="row">
            <img src="/static/img/temp/grafico_1000.png" alt="Análisis de respuesta al impulso" class="img-fluid rounded shadow mb-2">
            <p class="text-muted">Figura en escala dB de señal filtrada a 1kHz, con su correspondiente señal de Schroeder</p>
        </div>
    `;
    
    // Get references to the recreated elements
    const newEncabezadosFrecuencias = document.getElementById('encabezadosFrecuencias');
    const newCuerpoTabla = document.getElementById('cuerpoTabla');
    
    // Clear table headers and body
    newEncabezadosFrecuencias.innerHTML = '<th>Frecuencia (Hz)</th>';
    newCuerpoTabla.innerHTML = '';
    
    // Get all parameter names (EDT, T20, etc.)
    const parametros = Object.keys(data);
    
    // Add parameter headers
    parametros.forEach(param => {
        newEncabezadosFrecuencias.innerHTML += `<th>${param}</th>`;
    });
    
    // Get all frequencies from the first parameter
    const frecuencias = Object.keys(data[parametros[0]]);
    
    // Add a row for each frequency
    frecuencias.forEach(freq => {
        const fila = document.createElement('tr');
        fila.innerHTML = `<td><strong>${freq}</strong></td>`;
        
        // Add values for each parameter
        parametros.forEach(param => {
            const valor = data[param][freq];
            // Format numbers to 2 decimal places if they're numbers
            const valorFormateado = typeof valor === 'number' ? valor.toFixed(2) : valor;
            fila.innerHTML += `<td>${valorFormateado}</td>`;
        });
        
        newCuerpoTabla.appendChild(fila);
    });
    
    // Show results section
    resultadosDiv.style.display = 'block';
    
    // Scroll to results
    resultadosDiv.scrollIntoView({ behavior: 'smooth' });
}

// Make functions available globally
window.enviarFormulario = enviarFormulario;
window.mostrarResultados = mostrarResultados;
window.uploadFile = uploadFile;
