# Arquitectura RelatiPy

## Layout del código fuente

Raíz del paquete: `src/relatipy/`.

- **`numeric/`** — Núcleo numérico: constantes, sistemas de coordenadas, métricas (`Schwarzschild`, `Kerr`), geodésicas e integradores (SciPy, Yoshida6, Radau2, Mino). Puede incluir extensiones C bajo `numeric/geodesic/integrators/kerr/`.
- **`symbolic/`** — Expresiones con SymPy y EinsteinPy: métrica Kerr simbólica y utilidades de coordenadas simbólicas.
- **`visualization/`** — `_2D` (Matplotlib, `SciSubplot`) y `_3D` (Plotly, órbitas y horizontes).

## Reglas de dependencia

| Origen | Puede importar | No debe importar (convención de diseño) |
|--------|----------------|----------------------------------------|
| `numeric` | NumPy, SciPy, Astropy (cuando aplica), C/ctypes para backends | `symbolic`, `visualization` |
| `symbolic` | SymPy, EinsteinPy | `numeric`, `visualization` |
| `visualization` | Plotly, Matplotlib, **y** `relatipy.numeric` para métricas y geometría | `symbolic` (no requerido para trazado típico) |

## Flujo de datos típico

1. Usuario construye `Schwarzschild` o `Kerr` y condiciones iniciales en `coordinates.*`.
2. `Geodesic(metric).get_path(...)` devuelve una trayectoria como objeto de coordenadas (sistema nativo de la métrica o convertido según la lógica interna).
3. Para figuras 3D, se pasa la trayectoria a `construct_basic_path_plot(R_s, path, ...)` o se construye `PlotKerr(metric)` / `PlotSchwarzschild` para el fondo del agujero negro.

## Puntos de extensión

- Nuevas métricas numéricas: heredar de `BaseMetric` y registrar el sistema de coordenadas válido (`valid_coordinate`).
- Nuevos charts: heredar de `CoordinateBase` y añadir a `coordinate_systems` en `numeric/coordinates/__init__.py`.
- Nuevos integradores: submódulos bajo `numeric/geodesic/integrators/`; exportar en `__init__.py` solo si forman parte de la API estable deseada.
