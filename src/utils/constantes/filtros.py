"""
Módulo que contiene constantes relacionadas con filtros de audio.

Este módulo define las frecuencias centrales y parámetros para filtros
de octava y tercio de octava según la norma IEC 61260.
"""

# Frecuencias centrales estándar para filtros de octava (Hz)
FRECUENCIAS_OCTAVA = [
    125, 250, 500, 1000, 2000, 4000, 8000
]

# Frecuencias centrales estándar para filtros de tercio de octava (Hz)
FRECUENCIAS_TERCIO_OCTAVA = [
    125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600,
    2000, 2500, 3150, 4000, 5000, 6300, 8000
]

# Factores de ancho de banda (G)
FACTOR_ANCHO_OCTAVA = 1.0 / 2.0      # 1/1 de octava
FACTOR_ANCHO_TERCIO_OCTAVA = 1.0 / 6.0  # 1/3 de octava