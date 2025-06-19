# Trabajo Práctico - Desarrollo de software para el cálculo de parámetros acústicos ISO 3382
![Logo](/src/static/img/preview.png)
##  Descripción
Sistema integral para el análisis acústico de espacios arquitectónicos mediante el cálculo de parámetros acústicos según la normativa ISO 3382 (UNE-EN ISO 3382, 2010). La aplicación permite la generación, medición y análisis de respuestas al impulso en entornos acústicos.

##  Características principales
- Generación de señales de excitación (sweep senoidal y su inverso)
- Análisis de Respuestas al Impulso (RI)
- Cálculo de parámetros acústicos en bandas de octava y tercio de octava
- Interfaz web intuitiva para visualización de resultados
- Exportación de informes y datos

##  Instalación

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/jeroscafati/TP-SyS.git
   cd TP-SyS
   ```

2. Crear y activar entorno virtual (recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

##  Uso

1. Iniciar la aplicación:
   ```bash
   python src/main.py
   ```

2. Abrir en el navegador:
   ```
   http://localhost:5000
   ```

##  Tecnologías utilizadas
- **Backend**: Python, Flask
- **Procesamiento de audio**: NumPy, SciPy
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Visualización**: Matplotlib, Chart.js

##  Parámetros calculados
- Tiempo de reverberación (T60)
- Claridad (C80)
- Definición (D50)
- Relación de energía temprana (EDT)

##  Integrantes del grupo
- **Corzini**: Stéfano
- **Ferreyra**: Florencia
- **Molina**: Lara
- **Scafati**: Jerónimo

## Docentes
* **Lic. Miriam Sassano**
* **Ing. Antonio Greco**
* **Ing. Maximiliano Yommi**

<small>Trabajo práctico realizado para la materia <strong>Señales y Sistemas</strong>. <i>Universidad Nacional de Tres de Febrero, Primer cuatrimestre 2025</i>
</small>
