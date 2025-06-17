from pathlib import Path
import numpy as np

def get_output_filepath(filename: str,
                        levels_up: int = 2,
                        subdirs: list = ('temp_request', 'audio')):
    """
    Construye la ruta absoluta para el archivo de salida, 
    subiendo `levels_up` niveles desde la ubicación de este script,
    y descendiendo por los subdirectorios indicados. 
    Se crea el directorio destino si no existe.

    Parámetros
    ----------
    filename : str
        Nombre del archivo (p. ej. 'sonido.wav').
    levels_up : int
        Cuántos niveles subir desde la carpeta del script (__file__).
        Por defecto 2 (src/utils → src → proyecto).
    subdirs : list of str
        Lista de nombres de subdirectorios bajo la raíz del proyecto
        donde se guardará el archivo.

    Retorna
    -------
    Path
        Ruta completa al archivo de salida.
    """
    # 1. Directorio donde está este script
    script_dir = Path(__file__).resolve().parent

    # 2. Subir niveles hasta la raíz del proyecto
    project_root = script_dir
    for _ in range(levels_up):
        project_root = project_root.parent

    # 3. Construir ruta completa
    out_dir = project_root.joinpath(*subdirs)
    out_file = out_dir / filename

    # 4. Asegurar existencia del directorio
    out_dir.mkdir(parents=True, exist_ok=True)

    return out_file

def array_multicanal_a_1d(array):
    """
    Colapsa un array de forma (m, n) a (m,) reduciendo las columnas.

    Parámetros:
    -----------
    x : ndarray, forma (m, n)
        Array de entrada.

    Retorna:
    --------
    y : ndarray, forma (1, n)
        Array con una sola fila, promediada de cada columna.
    """
    if array.ndim == 1:
        y = array
    elif array.shape[1] == 1:
        y = np.squeeze(array)
    else:
        y = np.mean(array, axis=1)
    return y
