# Ejemplos — `relatipy.visualization`

## 2D — estilo publicación (`SciSubplot`)

```python
from relatipy.visualization._2D import SciSubplot

ws = SciSubplot(figsize=(5, 4))
ws.ax.plot([0, 1], [0, 1])
ws.fig.savefig("orbit.pdf")
```

## 3D — órbita + esfera de Schwarzschild

`construct_basic_path_plot` espera un objeto de trayectoria con `convert_to("Cartesian", ...)` y convención de filas descrita en `visualization/_3D/orbits.py` (tiempo en fila 0; espacio 1–3; opcionalmente velocidades 4–6 para conos en el extremo).

```python
from relatipy.visualization._3D import construct_basic_path_plot

fig = construct_basic_path_plot(
    R_s=2.0,  # radio de Schwarzschild en las mismas unidades que la trayectoria
    path=path_xyz,  # resultado de geodesic convertido a Cartesian
    color_path="red",
    plot_plane=True,
    plot_black_hole=True,
)
fig.show()
```

## 3D — horizonte y ergosfera Kerr (`PlotKerr`)

`PlotKerr` **requiere** una instancia `relatipy.numeric.metrics.Kerr`; otro tipo de métrica lanza `TypeError`.

```python
from relatipy.numeric.metrics import Kerr
from relatipy.visualization._3D import PlotKerr

plotter = PlotKerr(Kerr(1.0, 0.5), show_ergosphere=True)
# Inspeccionar atributos y métodos en src/relatipy/visualization/_3D/plot_black_hole/kerr.py
```

## 3D — Schwarzschild estático

```python
from relatipy.numeric.metrics import Schwarzschild
from relatipy.visualization._3D import PlotSchwarzschild

plotter = PlotSchwarzschild(Schwarzschild(1.0))
```

## Nota sobre notebooks existentes

Algunos notebooks (`notebooks/muestra.ipynb`) grafican con Matplotlib directamente sin usar `SciSubplot`; es válido para prototipos, pero la API estable de la librería para estilo 2D es `SciSubplot`.
