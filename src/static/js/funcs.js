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
    
    // Clear previous results and build new layout
    resultadosDiv.innerHTML = `
        <div class="card shadow mb-4">
            <div class="card-header fondo-azul text-white">
                <h4 class="mb-0"><i class="bi bi-graph-up me-2"></i>Resultados del Análisis</h4>
            </div>
            <div class="card-body">
                <div class="alert alert-info" role="alert">
                    <i class="bi bi-info-circle-fill me-2"></i>
                    A continuación se muestran los parámetros acústicos calculados para la señal analizada, junto con las visualizaciones correspondientes.
                </div>
                
                <div class="table-responsive mb-5">
                    <h5 class="mb-3">Parámetros Acústicos por Banda de Frecuencia</h5>
                    <table class="table table-hover table-bordered" id="tablaResultados">
                        <thead class="table-light">
                            <tr id="encabezadosFrecuencias"></tr>
                        </thead>
                        <tbody id="cuerpoTabla" class="table-group-divider"></tbody>
                    </table>
                </div>

                <div class="mt-5">
                    <h5 class="mb-4 pb-2 border-bottom"><i class="bi bi-graph-up me-2"></i>Visualizaciones</h5>
                    <p class="text-muted mb-4">Los siguientes gráficos muestran diferentes aspectos de la señal analizada, incluyendo su comportamiento en el dominio del tiempo y la frecuencia, así como el análisis detallado de la respuesta al impulso.</p>
                    
                    <div class="row g-4 mb-4">
                        <div class="col-lg-6">
                            <div class="card h-100 shadow-sm">
                                <div class="card-header bg-light">
                                    <h6 class="mb-0">Dominio Temporal</h6>
                                </div>
                                <div class="card-body text-center">
                                    <img src="/static/img/temp/time_domain_plot.png" alt="Dominio temporal" class="img-fluid rounded">
                                    <p class="text-muted mt-2 mb-0">Representación de la señal en el dominio del tiempo</p>
                                </div>
                            </div>
                        </div>
                        <div class="col-lg-6">
                            <div class="card h-100 shadow-sm">
                                <div class="card-header bg-light">
                                    <h6 class="mb-0">Envolvente suavizada (Hilbert + media móvil)</h6>
                                </div>
                                <div class="card-body text-center">
                                    <img src="/static/img/temp/time_domain_plot_hilbert.png" alt="Envolvente suavizada con promedio móvil" class="img-fluid rounded">
                                    <p class="text-muted mt-2 mb-0">Señal con su envolvente calculada mediante transformada de Hilbert</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="row g-4">
                        <div class="col-lg-6">
                            <div class="card h-100 shadow-sm">
                                <div class="card-header bg-light">
                                    <h6 class="mb-0">Análisis de Respuesta al Impulso</h6>
                                </div>
                                <div class="card-body text-center">
                                    <img src="/static/img/temp/grafico_1000.png" alt="Respuesta al impulso" class="img-fluid rounded">
                                    <p class="text-muted mt-2 mb-0">Señal filtrada a 1kHz con integración de Schroeder</p>
                                </div>
                            </div>
                        </div>
                        <div class="col-lg-6">
                            <div class="card h-100 shadow-sm">
                                <div class="card-header bg-light">
                                    <h6 class="mb-0">Espectro de Frecuencias</h6>
                                </div>
                                <div class="card-body text-center">
                                    <img src="/static/img/temp/freq_domain_plot.png" alt="Espectro de frecuencias" class="img-fluid rounded">
                                    <p class="text-muted mt-2 mb-0">Distribución de energía en el dominio de la frecuencia</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="alert alert-light mt-4" role="alert">
            <div class="d-flex align-items-center">
                <i class="bi bi-lightbulb-fill text-warning me-2"></i>
                <div>
                    <strong>Consejo:</strong> Para obtener los mejores resultados, asegúrese de que la señal de entrada tenga una buena relación señal/ruido y esté libre de distorsiones.
                </div>
            </div>
        </div>`;
    
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
