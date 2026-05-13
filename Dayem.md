<instructions>
Eres un científico especializado en dinámica orbital y relatividad general, con enfoque en el estudio del agujero negro supermasivo Sgr A* y las estrellas en órbita a su alrededor. Tu objetivo es implementar el método de ajuste de órbitas de Kerr descrito en el paper de Dayem et al. (2025) y compararlo con la librería relatipy.

Antes de comenzar cualquier implementación, lee y analiza completamente el paper en @cowork/investigaciones/002-metodos-ajuste-orbitas-kerr/papers/md/dayem2025/dayem2025.md para comprender el método, las ecuaciones clave, los parámetros orbitales utilizados y el esquema de integración numérica propuesto.
</instructions>

<context>
El paper de Dayem et al. (2025) describe un método para obtener órbitas de estrellas en la métrica de Kerr alrededor de Sgr A*. Deberás implementar ese método desde cero en la carpeta ./dayem/ y luego comparar los resultados para las estrellas S2 y S2/10 (versión con masa 1/10 de S2) contra los resultados obtenidos con relatipy usando la skill /relatipy-skill.

Parámetros de referencia conocidos de S2:
- Semieje mayor: ~1031 AU
- Excentricidad: ~0.884
- Periodo orbital: ~16.05 años
- Masa de Sgr A*: ~4.1 × 10^6 masas solares

S2/10 se define como S2 con masa reducida en un factor de 10.
</context>

<thinking>
Antes de escribir cualquier línea de código, razona paso a paso:
1. ¿Cuál es el formalismo del paper? (geodésicas de Kerr, constantes de movimiento, integración numérica)
2. ¿Qué parámetros del agujero negro y las estrellas se necesitan?
3. ¿Qué diferencias conceptuales y numéricas existen entre el método de Dayem et al. y relatipy?
4. ¿Qué métricas de comparación son más relevantes para evaluar las órbitas?
5. ¿Cómo estructurar el código para que sea modular y reproducible?
</thinking>

<instructions>
ESTRUCTURA DE ARCHIVOS A CREAR:

Carpeta ./dayem/ con los siguientes módulos:
- __init__.py: exports principales
- constants.py: constantes físicas y parámetros de Sgr A* y S2
- metric.py: implementación de la métrica de Kerr y sus componentes
- equations.py: ecuaciones de movimiento (geodésicas) según el paper de Dayem et al.
- integrator.py: integrador numérico (usa el esquema descrito en el paper; si no se especifica, usa scipy.integrate.solve_ivp con método RK45 o DOP853)
- orbit.py: clase principal Orbit que encapsula condiciones iniciales, integración y extracción de observables
- utils.py: funciones auxiliares de conversión de coordenadas y unidades

Notebook de comparación ./comparacion_dayem_relatipy.ipynb con las siguientes secciones:
1. Configuración del entorno e imports
2. Cálculo de órbitas S2 y S2/10 con el método Dayem (usando ./dayem/)
3. Cálculo de las mismas órbitas con relatipy (usando /relatipy-skill)