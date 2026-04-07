import numpy as np
from scipy.signal import lombscargle as _scipy_lombscargle


def _extract_coordinate(path, coord_system, coord_name, mass, a):
    """Extrae (times, values) de un path de relatipy según el sistema de coordenadas."""
    times = path[0]

    if coord_system == "OrbitalElements":
        converted = path.convert_to("OrbitalElements", mass=mass)
        values = getattr(converted, coord_name)

    elif coord_system == "BoyerLindquist":
        if a is None:
            raise ValueError("Se requiere 'a' (spin del BH) para convertir a BoyerLindquist.")
        converted = path.convert_to("BoyerLindquist", a=a)
        if isinstance(coord_name, int):
            values = converted[coord_name]
        else:
            values = getattr(converted, coord_name)

    else:
        raise ValueError(
            f"coord_system desconocido: {coord_system!r}. "
            "Opciones válidas: 'OrbitalElements', 'BoyerLindquist'."
        )

    return times, values


def lombscargle_from_path(
    path,
    coord_system="OrbitalElements",
    coord_name="inc",
    *,
    mass=1.0,
    a=None,
    time_scale=None,
    freq_min=0.1,
    freq_max=10.0,
    n_freqs=1200,
    detrend=True,
):
    """Calcula el periodograma de Lomb-Scargle para una coordenada de un path de relatipy.

    Parameters
    ----------
    path : relatipy path object
        Resultado de kerr.geodesic.get_path(...).
    coord_system : str
        Sistema de coordenadas: 'OrbitalElements' (default) o 'BoyerLindquist'.
    coord_name : str or int
        Nombre del atributo (e.g. 'inc', 'e', 'a') para OrbitalElements,
        o índice entero (0=t, 1=r, 2=θ, 3=φ) para BoyerLindquist.
    mass : float
        Masa del agujero negro (para conversión a OrbitalElements).
    a : float or None
        Spin del agujero negro (para conversión a BoyerLindquist).
    time_scale : float or None
        Escala de tiempo (e.g. período orbital). Si se provee, divide los tiempos
        por este valor antes del análisis.
    freq_min, freq_max : float
        Rango de frecuencias en unidades de 1/[unidad de tiempo].
    n_freqs : int
        Número de puntos en la grilla de frecuencias.
    detrend : bool
        Si True, elimina tendencia lineal antes de aplicar Lomb-Scargle.

    Returns
    -------
    freqs : np.ndarray, shape (n_freqs,)
        Grilla de frecuencias.
    powers : np.ndarray, shape (n_freqs,)
        Potencias crudas del periodograma.
    amplitudes : np.ndarray, shape (n_freqs,)
        Amplitudes normalizadas: sqrt(4 * power / N).
    """
    times, values = _extract_coordinate(path, coord_system, coord_name, mass, a)

    t = times / time_scale if time_scale is not None else times.copy()
    y = values.copy()

    if detrend:
        p = np.polyfit(t, y, 1)
        y = y - np.polyval(p, t)

    y = y - np.mean(y)

    freqs = np.linspace(freq_min, freq_max, n_freqs)
    angular_freqs = 2 * np.pi * freqs

    powers = _scipy_lombscargle(t, y, angular_freqs)
    amplitudes = np.sqrt(4 * powers / len(t))

    return freqs, powers, amplitudes


def top_frequencies(freqs, powers, n=5):
    """Devuelve las n frecuencias dominantes y sus potencias en orden descendente.

    Parameters
    ----------
    freqs : np.ndarray
        Grilla de frecuencias (salida de lombscargle_from_path).
    powers : np.ndarray
        Potencias del periodograma (salida de lombscargle_from_path).
    n : int
        Número de frecuencias dominantes a retornar.

    Returns
    -------
    top_freqs : np.ndarray, shape (n,)
    top_powers : np.ndarray, shape (n,)
    """
    idx = np.argsort(powers)[::-1][:n]
    return freqs[idx], powers[idx]
