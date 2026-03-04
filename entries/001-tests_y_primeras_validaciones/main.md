# Resumen
El objetivo principal de la semana fue testear el módulo numérico de RelatiPy y verificar que los resultados son los esperados. Al ser la primera aproximación a la tesis, ha sido un proceso de adaptación y busqueda de una metodología estandar para garantizar la calidad de los resultados y formas de presentación. Como resultado también se muestra la presente página web que de ahora en adelante será el lugar donde se mostrarán los resultados de las investigaciones.


# Objetivo de RelatiPy
Desde el 2025 se ha venido trabajando en la construcción de *RelatiPy*, una librería creada con el objetivo de facilitar la investigación en relatividad númerica. La razon por la cuan no se usa un paquete existente es por los siguientes motivos:
1. Control total sobre el código y aprendizaje: la experiencia misma de crear un paquete permite adquirir un mayor control sobre el código y la posibilidad de entender a profundidad la teoría implicada, además de mejorar habilidades de programación.
2. Adaptación a las necesidades: al crear un paquete propio, se puede adaptar a las necesidades específicas de la investigación.
3. AI: Aunque en esta etapa temprana no se tiene implementado, la distinción que tendrá esta librería con las demás es la posibilidad de usar herramientas de inteligencia artificial para la investigación. Si cualquier invertigador con acceso a un LLM (ya sea mediante un editor de código como Cursor o una API de cualquier proveedor), mediante estandares como "SKILLS" o "MCP" puede conectarse y usar directamente esta librería sin necesidad de codificar directamente. Esto permite por ejemplo el despliegue de varios procesos a la vez, y el desarrollo de la investigación de forma colaborativa con herramientas de IA.

# Tests y primeras validaciones
Al ser una librería nueva, se debe verificar que los resultados son los esperados. Existen varias formas de validar dichos resultados, a continuación explicaremos cada uno de los implementados. Estas verificaciones las hicimos para las métricas de Schwarzschild y Kerr, ya que estas son suficientes para la generalidad, y en particular, para nuestra investigación.

Como base tomaremos 3 condiciones iniciales arbitrariamente elegidas.

## Verificación de las geodésicas con einsteinpy
`einsteinpy` es una librería de python enfocada en la relatividad general. Mediante la clase `TimeLike` del módulo `geodesic` de esta librería se puede calcular las geodésicas de una métrica de Kerr. Como argumentos se deben pasar la posición y el momentum (que en nuestro caso, consideramos equivalente a la velocidad en coordenadas cartesianas). 

La estructura de la clase `TimeLike` es la siguiente:

```python
geodesic = Timelike(
            metric="Kerr",
            metric_params=(a,),
            position=position,
            momentum=momentum,
            steps=steps,
            delta=delta,
            return_cartesian=False,
        )
trajectory = geodesic.trajectory[1]
```
Tome encuenta que se deben pasar los parámetros con unidades de scipy.units.

En la estructura que nosotros plantemos, una geodésica corresponde a una métrica en particular, entonces, importando el módulo `numeric.metrics` de RelatiPy, podemos, mediante condiciones iniciales, calcular la geodésica.

```python
metric = rn.metrics.Kerr(a=a)
times = np.linspace(0, 100, 1000)
initial_conditions = rn.coordinates.Spherical(xs=xs, vels=vels)
path = metric.geodesic.get_path(initial_conditions, times)
```
Tome en cuenta `xs` en nuestro caso toma [$x^0$, $x^1$, $x^2$, $x^3$] y `vels` toma [$v^1$, $v^2$, $v^3$] por defecto, pero mediante el argumento `from_dxs_dt=True` se pueden pasar las derivadas temporales de las coordenadas y velocidades.

Así, con los matices de implementación se llega a que en efecto, los resultados de las godésicas son los mismos.


## Cantidades conservadas
En relatividad general, existen varias cantidades que se conservan a lo largo de las geodésicas. Para verificar que estamos obteniendo las godésicas correctamente, se procede a verificar las siguientes:

### Conservación de la magnitud de la cuadrivelocidad (velocidad de la luz)
La magnitud de la cuadrivelocidad se conserva en las geodésicas. Esto se puede verificar calculando la magnitud de la cuadrivelocidad en cada punto de la geodésica.

```python
def _get_ds_dtau(self, metric):
    g = metric.metric(self.xs) 
        
    u = ones((4, len(self.dxs_dt[0])))
    u[1:, :] = self.dxs_dt

    return einsum('ijn,in,jn->n', g, u, u)
```
La extructura que estamos trabajando es (4, ..., N), donde "..." representa las dimensiones de cualquier objeto, por ello usamos dicha suma para obtener el resultado.


Al finalizar los tests, se obtiene que la magnitud de la cuadrivelocidad se conserva.

### Conservación del momentum angular
Para este calculo, se agregó un módulo de coordenadas cilindricas para facilitar el cálculo del momentum angular, que puede además ser útil en otros contextos. El uso de esta coordenada, en conjunto con la lógica general de las conversiones entre sistemas, hace que el cálculo sea general para toda coordenada y no tengamos que implementarlo para cada una de ellas.

```python
def _get_Lz(self, mass_particle=1.0):
    cylindrical = self.convert_to("Cylindrical")
    rho = cylindrical.xs[1]
    v_phi = cylindrical.vs[1]
    return mass_particle * rho * v_phi
```
Asumimos que la masa de la partícula es 1, como suele pasar cuando trabajamos en geodésicas para evitar problemas de varios cuerpos. Aún así soporta pasar la masa de la partícula como argumento.

Al finalizar los tests, se obtiene que el momentum angular se conserva.

### Conservación de la energía
El caso de la energía relativista, se usa la fórmula:
$$
E = -g_{t mu} u^mu
$$

La implementación es:
```python
def _get_E(self, metric):
    g = metric.metric(self.xs)
    u = ones((4, len(self.dxs_dt[0])))
    u[1:, :] = self.dxs_dt
    return -einsum('jn,jn->n', g[0, :, :], u)
```

Y se logra verificar que la energía se conserva.

### Constante de Carter
Mediante las coordenadas Boyer-Lindquist, haciendo uso del hamiltoniano, se puede llegar a una catidad conservada que se conoce como constante de Carter. La fórmula es:
$$
C = p_{\theta}^{2} + \cos^{2}\theta \left( a^{2}(m^{2} - E^{2}) + \left( \frac{L_{z}}{\sin\theta} \right)^{2} \right)
$$
Pero en nuestro caso, consideramos masa de la partícula unitaria, por lo que la fórmula se simplifica a:
$$
C = p_{\theta}^{2} + \cos^{2}\theta \left( a^{2}(1 - E^{2}) + \left( \frac{L_{z}}{\sin\theta} \right)^{2} \right)
$$

La implementación es:
```python
def _get_Q(self, metric):
    a = self.a
    r, theta = self.xs[1], self.xs[2]
    E = self._get_E(metric)
    Lz = self._get_Lz()
    
    g = metric.metric(self.xs)
    
    g_thth = g[2, 2, :]
    p_theta = g_thth * self.dxs_dt[1]
    
    return p_theta**2 + np.cos(theta) ** 2 * (a**2 * (1 - E**2) + Lz**2 / np.sin(theta) ** 2)
```

Al finalizar los tests, se obtiene que la constante de Carter se conserva.


## Comportamiento: Inclinación orbital
Un resultado teórico es que la inclinación orbital que toma una partícula en una geodésica de Kerr oscila en un rango de manera periódica. 

### Orbita estable
Para obtener unas condiciones iniciales válidas, podemos partir de las coordenas esféricas, que son más intuitivas y fáciles de entender.

En este sistema, la coordenada $x^2$ es la que está relacionada con la inclinación orbital. Esto es: $i = \pi/2 - x^2$. Por simetría azimutal, la coordenada $x^3$ no nos afecta, por lo que podemos fijarla en 0. Sin embargo, en el caso de las velocidades, sí es importente, como queremos tener una estabilidad en la inclinación, asumiremos que $v^2 = 0$ y $v^3 = 1/x^1$. Esto es una condición inicial válida en mecánica celeste clásica, nos da un momentum angular fácil de calcular y controlar.

Bajo este sistema, obtenemos la inclinación de la partícula en función del tiempo.

<!-- img:"inclination_orbital_schwarzschild.png" -->

En primera instancia corroboramos que la inclinación oscila en un rango de manera periódica. Sin embargo, esto no es suficiente. Para garantizar dicha estabilidad, procedemos a obtener los modos dominantes de la inclinación mediante una transformada de Fourier.

<!-- img:"inclination_orbital_schwarzschild_fft.png" -->

Como podemos observar de la figura, la inclinación tiene unos modos dominantes. La transformada de fourier nos muestra además una forma de pico no del todo puntual, como esperariamos de en un caso perfecto. Este ensanchamiento también afecta las medidas. Sin embargo, la dominancia de los modos nos permite modelar la evolución temporal de la inclinación, y sus amplitudes, no uniformes nos confirman que en efecto, la inclinación oscila de manera periódica.

<!-- img:"inclination_orbital_schwarzschild_reconstruction.png" -->

Esta figura, da cuenta de lo que habiamos predicho al observar la transformada de Fourier, como los errores en la medida se van acumulando, la reconstrucción no es perfecta, pero si nos da una idea de la forma de la inclinación orbital.

### Orbita inestable
Asumamos ahora que partimos de las condiciones iniciales estables, pero con una pequeña perturbación en la velocidad azimutal del 10%. 

Veamos lo que ocurre con la geodésica.

<!-- html:"path_3d_unstable.html" -->

Aunque se vea un poco caótico, la inclinación sigue siendo periodica, esto lo podemos corroborar con la transformada de Fourier.

<!-- img:"inclination_orbital_schwarzschild_fft_unstable.png" -->

Aunque hay más modos dominantes, la inclinación sigue siendo periódica. De la reconstrucción de las inclinaciones, como verá, se puede observar dicho comportamiento.

<!-- img:"inclination_orbital_schwarzschild_reconstruction_unstable.png" -->

De este modo, con este tipo de orbitas, obtenemos el resultado predicho.

# Próximos pasos
- Evitar el overflow en operaciones con mucho tiempo de integración.
- Terminar la tarea "Suposición: dinámica de estrellas debida a AN".