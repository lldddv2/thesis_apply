# Ejemplos — `relatipy.symbolic`

La capa simbólica usa **SymPy** y **EinsteinPy**. No importa `relatipy.numeric` desde aquí.

## Métrica Kerr simbólica

```python
from relatipy.symbolic.metrics import Kerr

k = Kerr()
g = k.metric()
tensor = g.tensor()
assert tensor.shape == (4, 4)
```

Los símbolos de coordenadas siguen la convención \((x^0, x^1, x^2, x^3) \sim (t, r, \theta, \phi)\) descrita en `src/relatipy/symbolic/metrics/kerr_metric.py` y en `docs/relativity/metric.md`.

## Coordenadas simbólicas

El subpaquete `relatipy.symbolic.coordinates` define bases y charts simbólicos (esféricos, cilíndricos, Boyer–Lindquist, etc.). Explorar módulos bajo `src/relatipy/symbolic/coordinates/` para clases concretas.

## Material didáctico en el repo

- `notebooks/metric.ipynb`, `notebooks/schwarzschild.ipynb` — derivaciones manuales con SymPy.
- `notebooks/confirmation.ipynb` — contraste numérico vs simbólico (`rs.metrics.Kerr` vs `rn.metrics.Kerr` según el notebook).

Cuando documentes una implementación numérica que refleje una ecuación de `docs/relativity/`, enlaza con la convención `~ref(...)` del proyecto.
