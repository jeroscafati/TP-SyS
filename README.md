# Trabajo Práctico - Desarrollo de software para el cálculo de parámetros acústicos ISO 3382


##  Descripción
Sistema integral para el análisis acústico de espacios arquitectónicos mediante el cálculo de parámetros acústicos según la normativa ISO 3382 (UNE-EN ISO 3382, 2010). La aplicación permite la generación, medición y análisis de respuestas al impulso en entornos acústicos.

##  Características principales
- Generación de señales de excitación (sweep senoidal y su inverso)
- Análisis de Respuestas al Impulso (RI)
- Cálculo de parámetros acústicos en bandas de octava y tercio de octava


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

El software se ejecuta desde dos modulos distintos dependiendo el uso que se le quiere dar.

1. Para Analizar una respuesta al impulso:
   ```bash
   python src/test_parametros_ri.py
   ```

2. Para generar señales u obtener una respuesta al impulso:
   ```bash
   python src/test_generar_signals.py
   ```


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