# comparación analítica con dayem

## 1. Cambio de coordenadas en relatipy
Se optó por demarcar la posición del spin del agujero negro a partir de dos ángulos $\zeta \in [0°, 180°]$ y $\eta \in [0°, 360°]$ como se observa en la figura. 

<!-- html:"spin_axis_sky_coords_v7.html"-->

En consecuencia, es necesario introducir dicha definición en los elementos orbitales para que pueda establecerse una relación entre el sistema de coordenadas "propio" del agujero negro, con el sistema coordenado de los elemntos orbitales. A este sistema lo llamamos `ApparentOrbitalElements`.

Además, se le agrega al módulo visal la distinción entre el plano orbital y el plano del agujero negro como se ve en la siguiente figura:

<!-- html:"orbit_coordinate_validation.html"-->

Adicionalmente se empezo a trabajar en las coordenadas ecuatoriales para observar en ascención recta y declinación los resultados.

## 2. Experimento: S2 en la línea de la visual.
Asumiendo que el spin de Sgr A* apunta en la dirección de la línea de la visual ($\zeta = 0°$), se comparan las precesiones por órbita predichas por Dayem (2025) con las obtenidas numéricamente integrando la geodésica de Kerr exacta (Fujita), usando los parámetros orbitales de S2 (GRAVITY Collaboration 2020) y $\chi = 0.9$. El acuerdo es excelente: el error en $\Delta\omega$ es $\sim 2 \times 10^{-4}$ °/órbita, compatible con los términos de orden superior en $\varepsilon$ no incluidos en Dayem (2025).

Se varió el spin $\chi \in \{0.1, 0.3, 0.5, 0.7, 0.9\}$ manteniendo los elementos orbitales fijos, observando que el error crece suavemente con $\chi$, consistente con correcciones de orden $\varepsilon^{5/2}$ en el término de Lense–Thirring.

<!-- img:"s2_spin_sweep_errors.jpg"-->

## 3. Experimento: Cambiando $\zeta$
Con $\chi = 0.9$ fijo y los elementos orbitales de S2, se varió la orientación del spin $\zeta \in \{15°, 30°, 45°, 60°, 75°\}$. Las tres precesiones ($\Delta\omega$, $\Delta\iota$, $\sin\iota\cdot\Delta\Omega$) muestran acuerdo analítico–numérico en todos los casos; el error absoluto en $\Delta\omega$ permanece en el orden de $10^{-4}$ °/órbita con dependencia débil en $\zeta$.

<!-- img:"sweep_zeta_comparison.jpg"-->

# ¿Qué sigue?
## Propuesta
1. Terminar de establecer las coordenadas ecuatoriales.
2. Basarnos exclusivamente en S2: Hacer simulaciones con los parámetros libres: $\zeta$, $\eta$ y $a$ (o $\chi$ según la nomenclatura de Dayem), variando $a \in \pm[0.8, 1)$, con un paso de $0.01$. Esto para apoyarnos de la literatura, que con las observaciones directas, indican un spin de 0.9 aproximadamente.
3. Con base en eso, hacer un estudio de: dado una evolución en uno o varios periodos orbitales de los Deltas, con la observación en RA y DEC, cual es el conjunto de estos 3 parámetros más probable. Un análisis estadistico.
## Entregables:
1. RelatiPy con coordenadas ecuatoriales.
2. Distribución de probabilidades de $\zeta$, $\eta$ y $a$, dado unos Deltas en RA y DEC
3. Distribuciones de probabilidades con la evolución orbital.

## Nota
- Esto NO toma en cuenta la resulución del telescopio, o efectos relativistas, ni error de medida. Estas se mediran posteriormente.