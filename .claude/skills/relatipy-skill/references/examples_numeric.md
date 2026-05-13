# Ejemplos — `relatipy.numeric`

Los fragmentos siguientes están alineados con la API pública y con patrones de `tests/` y docstrings. Ajusta masas y `astropy.units` según tu caso.

## Métrica y tensores

```python
import numpy as np
from relatipy.numeric.metrics import Schwarzschild, Kerr

# Masa como float (convención del validador / masa de referencia) o Quantity
sch = Schwarzschild(1.0)
xs = np.array([0.0, 10.0, np.pi / 2, 0.0])  # (t, r, theta, phi) según la métrica
g = sch.metric(xs)
gamma = sch.get_christoffel_symbols(xs)

kerr = Kerr(1.0, 0.5)  # spin adimensional a/M = 0.5
print(kerr.isco_prograde, kerr.isco_retrograde)
```

## Coordenadas y registro dinámico

```python
from relatipy.numeric.coordinates import BoyerLindquist, coordinate_systems
import numpy as np

assert "BoyerLindquist" in coordinate_systems

bl = BoyerLindquist(
    np.array([0.0, 10.0, np.pi / 2, 0.0]),
    vels=np.array([0.01, 0.0, 0.0]),
    a=0.5,
    from_dxs_dt=False,
)
cart = bl.convert_to("Cartesian")  # usa `a` almacenado en el estado Boyer–Lindquist
```

## Geodésica con `Geodesic`

```python
import numpy as np
from relatipy.numeric.metrics import Kerr
from relatipy.numeric.coordinates import BoyerLindquist
from relatipy.numeric.geodesic import Geodesic

mass, a_star = 1.0, 0.5
metric = Kerr(mass, a_star)
geo = Geodesic(metric)

ic = BoyerLindquist(
    np.array([0.0, 10.0, np.pi / 2, 0.0]),
    vels=np.array([0.0, 0.0, 0.01]),
    a=a_star,
    from_dxs_dt=False,
)

taus = np.linspace(0.0, 500.0, 200)
path = geo.get_path(ic, taus, integrator="Radau", adaptative=True)
# path es un objeto de coordenadas; convertir según necesidad:
path_xyz = path.convert_to("Cartesian", mass=mass)
```

### Integradores destacados

- **`integrator="Radau"`** (por defecto): SciPy `solve_ivp` con método Radau.
- **`integrator="Yoshida6"`**: esquema simpléctico de orden 6; ver `relatipy.numeric.geodesic.integrators`.
- **`integrator="Radau2"`**: Kerr en Boyer–Lindquist con proyección de restricciones (ver docstrings en `geodesic.py`).

## Yoshida6 (API de alto nivel)

```python
import numpy as np
import astropy.units as u
from relatipy.numeric.metrics import Kerr
from relatipy.numeric.coordinates import OrbitalElements
from relatipy.numeric.geodesic.integrators import Yoshida6Integrator, yoshida6_integrate_geodesic

M = 1.989e30 * u.kg
metric = Kerr(M, 0.5)
oe = OrbitalElements(t=0, a=50.0, e=0.2, inc=90.0, Omega=0.0, omega=0.0, f=0.0, mass=M)

integrator = Yoshida6Integrator(metric)
# O la función conveniencia yoshida6_integrate_geodesic(metric, ...)
```

Patrones de aserción y definición de energía conservada para Kerr vs Schwarzschild: `tests/numeric/geodesic/test_yoshida6.py`.

## Elementos orbitales y periodos largos

Para integración multi-orbita con muestreo por periodo, usar `Geodesic.get_path_periodic` con `OrbitalElements` (requiere `_get_period` en las CI). Ver docstring de `get_path_periodic` en `geodesic.py` y tests de Schwarzschild.

## Validación cruzada y constantes

- Comparación métrica Kerr vs EinsteinPy: `tests/numeric/metrics/test_kerr_metric.py`.
- Unidades y validador: `tests/numeric/utils/test_dimensions.py`.
- Notebook de flujo mixto: `notebooks/confirmation.ipynb`.
