/**
 * Envía el formulario de validación de funcionamiento
 * @param {string} apiUrl - URL del endpoint de la API (opcional, por defecto es '/validar_funcionamiento')
 */
function uploadFile() {
    const file = document.getElementById('file').files[0];
    if (file) {
        const formData = new FormData();
        formData.append('file', file);
        
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
    encabezadosFrecuencias.innerHTML = '<th>Frecuencia (Hz)</th>';
    cuerpoTabla.innerHTML = '';
    
    // Get all parameter names (EDT, T20, etc.)
    const parametros = Object.keys(data);
    
    // Add parameter headers
    parametros.forEach(param => {
        encabezadosFrecuencias.innerHTML += `<th>${param}</th>`;
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
        
        cuerpoTabla.appendChild(fila);
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
