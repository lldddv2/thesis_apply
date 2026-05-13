---
name: relatipy-skill
description: >
  Guía de uso y arquitectura de RelatiPy: métricas numéricas (Schwarzschild, Kerr),
  coordenadas, geodésicas e integradores (SciPy, Yoshida6, Radau2, Mino), métrica
  simbólica con SymPy/EinsteinPy, y visualización 2D/3D (Matplotlib, Plotly).
  Usar cuando el usuario trabaje con relatipy, geodésicas Kerr, Boyer-Lindquist,
  ISCO, unidades geométricas, o integración de trayectorias alrededor de agujeros negros.
metadata:
  version: "1.0.0"
  tags:
    - relatipy
    - general-relativity
    - kerr
    - geodesics
    - python
---

# RelatiPy — skill de uso

## Cuándo usar esta skill

- Implementar o depurar flujos con `relatipy.numeric` (métricas, coordenadas, geodésicas).
- Comparar o derivar expresiones con `relatipy.symbolic` (Kerr simbólico).
- Graficar órbitas o horizontes con `relatipy.visualization` (2D Matplotlib, 3D Plotly).
- Aclarar convenciones: unidades geométricas, firma métrica, estado de 8 componentes, spin Kerr.

## Propósito

RelatiPy es una librería Python para explorar geometría relativista (enfoque Kerr) con tres capas separadas: **numérico**, **simbólico** y **visualización**. El código numérico y simbólico no deben mezclarse; la visualización consume resultados numéricos (p. ej. `Kerr` y trayectorias con `convert_to("Cartesian")`).

## Flujo de trabajo recomendado

1. **Elegir capa**: numérico para trayectorias y tensores evaluados; simbólico para álgebra; visualización al final.
2. **Instalar** el paquete en modo editable desde la raíz del repo (compila extensiones C de integradores cuando aplica): `pip install -e .`
3. **Métrica**: `Schwarzschild(mass)` o `Kerr(mass, a)` donde `a` es el spin adimensional \(a/M\) (|a| ≤ 1 para subextremal).
4. **Condiciones iniciales**: clase bajo `relatipy.numeric.coordinates` coherente con la métrica (`Spherical` para Schwarzschild, `BoyerLindquist` para Kerr con el mismo `a` que en la métrica interna; ver doc de `Kerr` para conversión \(a_\*\) → longitud).
5. **Integrar**: `Geodesic(metric).get_path(ic, taus, integrator=..., adaptative=...)` — ver parámetros en el código fuente de `geodesic.py`.
6. **Validar**: tests en `tests/numeric/` y notebooks en `notebooks/` (p. ej. `confirmation.ipynb`).

## API pública estable (resumen)

| Módulo | Import típico | Superficie estable (`__all__` / uso documentado) |
|--------|----------------|--------------------------------------------------|
| Top-level | `import relatipy` | `numeric`, `symbolic`, `visualization`, `__version__` |
| `numeric` | `from relatipy.numeric import metrics, coordinates, geodesic, constants` | `constants`, `coordinates`, `metrics`, `geodesic`, `_c`, `_G` |
| `numeric.metrics` | `from relatipy.numeric.metrics import Schwarzschild, Kerr, BaseMetric` | Esas tres clases |
| `numeric.coordinates` | `Cartesian`, `Spherical`, `BoyerLindquist`, `Cylindrical`, `OrbitalElements`, `coordinate_systems` | Registro `coordinate_systems` para descubrir clases |
| `numeric.geodesic` | `Geodesic` | Integración unificada |
| `numeric.geodesic.integrators` | `Yoshida6Integrator`, `yoshida6_integrate_geodesic` | Yoshida 6 en paquete “público” genérico |
| `numeric.geodesic.integrators.kerr` | Integradores Kerr | Incluye `Yoshida6Integrator`, `yoshida6_integrate_geodesic`, `_integrate_kerr_radau2`, `project_kerr_trajectory`, `_integrate_kerr_mino` (prefijo `_` = API interna pero exportada) |
| `symbolic` | `relatipy.symbolic.metrics`, `.coordinates` | Subpaquetes |
| `symbolic.metrics` | `Kerr` | Métrica Kerr simbólica |
| `visualization._2D` | `SciSubplot` | Figura/estilo Matplotlib |
| `visualization._3D` | `construct_basic_path_plot`, `PlotSchwarzschild`, `PlotKerr`, `OrbitPath`, `EquatorialPlane`, `SquarePlane` | Plotly |

**Nota:** `Minkowski` existe en el código numérico pero no está en `numeric.metrics.__all__`; tratarlo como no estable salvo necesidad explícita.

## Reglas críticas

- **Unidades geométricas**: en fórmulas internas \(G=c=1\); masas y conversiones siguen `relatipy.numeric.constants` y el validador de dimensiones (ver tests `tests/numeric/utils/test_dimensions.py`).
- **Estado geodésico**: vector de 8 componentes \([q^0,q^1,q^2,q^3,u^0,u^1,u^2,u^3]\) (posición + cuadrivelocidad contravariante).
- **Integradores Kerr**: `Radau2` y proyección de restricciones asumen Boyer–Lindquist; revisar docstrings de `Geodesic._project_constraints` para \(E\), \(L_z\), \(Q\).
- **Energía conservada en tests Yoshida**: para Kerr usar \(E = -g_{0\mu} u^\mu\), no confundir con helpers tipo factor de redshift \( -g_{00}\) (ver comentarios en `tests/numeric/geodesic/test_yoshida6.py`).
- **Contribuir código**: convenciones en `docs/development/convention.md`; referencias teóricas con `~ref(docs/relativity/...#sección)~` según `docs/development/documentation_convention.md`.

## Comandos útiles

Desde la raíz del repositorio, con el venv activado:

```bash
pip install -e .
pytest
pytest tests/numeric/geodesic/test_yoshida6.py -q
black src/ tests/
isort src/ tests/
flake8 src/ tests/
```

## Referencias en esta skill

- [Arquitectura y dependencias entre módulos](references/architecture.md)
- [Convenciones del proyecto y física](references/conventions.md)
- [Ejemplos: numeric](references/examples_numeric.md)
- [Ejemplos: symbolic](references/examples_symbolic.md)
- [Ejemplos: visualization](references/examples_visualization.md)
