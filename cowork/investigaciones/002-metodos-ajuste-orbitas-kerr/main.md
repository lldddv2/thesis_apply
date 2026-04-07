# Métodos para ajuste de órbitas en métrica de Kerr

---
Fecha: 2026-04-04
Tiempo de investigación: ~2 horas
---

# Resumen

Se investigan los principales métodos para ajustar órbitas de estrellas alrededor de un agujero negro de Kerr, con el objetivo de determinar parámetros como la masa $M$, el spin $a$, la orientación del spin, y la inclinación orbital. El problema central que distingue Kerr de Schwarzschild es la ruptura de la simetría esférica: en Kerr hay arrastre del marco (frame-dragging), lo que induce precesión de Lense-Thirring fuera del plano orbital y hace que las constantes del movimiento sean $(E, L_z, Q)$ en lugar de solo $(E, L)$. Esto complica enormemente el ajuste porque el espacio de parámetros tiene más dimensiones y las degeneraciones son más severas.

Los métodos identificados se clasifican en tres grandes familias:

1. **Integración directa de geodésicas + minimización estadística** (χ², MCMC/Bayesiano)
2. **Parametrización por constantes del movimiento o parámetros orbitales geométricos** y mapeo a observables
3. **Métodos frecuenciales** (ajuste por frecuencias fundamentales $\Omega_r, \Omega_\theta, \Omega_\phi$)

Existen también enfoques híbridos y perturbativos (post-Newtoniano extendido, cuadrupolo de Kerr).

---

# Desarrollo

## [GRAVITY Collaboration 2020 — Detection of the Schwarzschild precession in the orbit of the star S2 near the Galactic centre massive black hole]

---
doi: 10.1051/0004-6361/201937813
año de publicacion: 2020
autor: Abuter, R.; Amorim, A.; Bauböck, M. et al. (GRAVITY Collaboration)
bib: |
  @article{gravity2020,
    author  = {Abuter, R. and Amorim, A. and Bauböck, M. and others},
    title   = {Detection of the Schwarzschild precession in the orbit of the star S2 near the Galactic centre massive black hole},
    journal = {Astronomy \& Astrophysics},
    volume  = {636},
    pages   = {L5},
    year    = {2020},
    doi     = {10.1051/0004-6361/201937813}
  }
---

### Resultados de lo buscado

Apareció en múltiples búsquedas como el paper canónico de ajuste de órbitas estelares al centro galáctico. Es el estado del arte en el método de ajuste que más se usa actualmente.

### Resumen

La colaboración GRAVITY detecta la precesión de Schwarzschild en la órbita de S2 a ~6σ. Usan datos de ~27 años de seguimiento astrométrico con NACO/SINFONI (VLT) y desde 2017 con GRAVITY (VLTI), que alcanza precisión astrométrica de ~50 μas. El modelo ajusta 14 parámetros: distancia al centro galáctico $R_0$, masa $M_{BH}$, posición y movimiento del marco de referencia, los seis parámetros orbitales de S2, y un parámetro adimensional $f_{SP}$ que escala la precesión de Schwarzschild (con $f_{SP}=1$ correspondiendo a RG completa). Obtienen $f_{SP} = 1.10 \pm 0.19$.

### Observaciones importantes

**Método de ajuste:** χ²-minimización (Levenberg-Marquardt) para encontrar el mejor ajuste, seguido de MCMC + bootstrapping con diferentes esquemas de pesado para estimar incertidumbres. Se reporta que LMMC (Levenberg-Marquardt Monte Carlo) tiende a subestimar la incertidumbre comparado con MCMC puro, especialmente para conjuntos de datos con grandes brechas temporales.

**Modelo de la órbita:** Keplerian + corrección de primer orden post-Newtoniana para la precesión de Schwarzschild. Esto es suficiente porque S2 está todavía relativamente lejos del horizonte (~1400 $r_s$ en periastro), por lo que los efectos de Kerr (Lense-Thirring, cuadrupolo) son subdominantes. El spin de Sgr A* no se puede medir con S2.

**Costo computacional:** Moderado. La integración numérica de la órbita post-Newtoniana es rápida. El costo está en el MCMC con ~14 parámetros. Con datos de ~200 épocas, convergencia en horas en un cluster moderno.

**Limitación clave:** Este método es insuficiente para detectar spin. Para Kerr completo, se necesita o bien estrellas más cercanas, o bien RG completa (geodésicas de Kerr) en lugar de PN.

### Artículos de interés

- GRAVITY 2018: Detección del corrimiento gravitacional (S2): doi 10.1051/0004-6361/201833718
- GRAVITY 2019: Distancia a Sgr A*: doi 10.1051/0004-6361/201935656
- Zhang & Iyer 2015: tratamiento RG completo: arXiv:1508.06293

---

## [Zhang & Iyer (aprox.) 2015 — On Testing the Kerr Metric of the Massive Black Hole in the Galactic Center via Stellar Orbital Motion: Full General Relativistic Treatment]

---
doi: (ver OSTI 22882761, arXiv:1508.06293)
año de publicacion: 2015
autor: Zhang, F.; Iyer, B. R.
bib: |
  @article{zhang2015,
    author  = {Zhang, F. and Iyer, B. R.},
    title   = {On Testing the Kerr Metric of the Massive Black Hole in the Galactic Center via Stellar Orbital Motion: Full General Relativistic Treatment},
    journal = {Physical Review D},
    year    = {2015},
    doi     = {(ver arXiv:1508.06293)}
  }
---

### Resultados de lo buscado

Apareció en búsquedas de "Kerr metric stellar orbit fitting full GR galactic center Carter constant".

### Resumen

Desarrollan un método de ajuste de órbitas estelares al centro galáctico con tratamiento de Relatividad General **completo** (no perturbativo), integrando las ecuaciones geodésicas de Kerr con Boyer-Lindquist. Buscan constrainar simultáneamente masa $M$, spin $a$, y dirección del spin de Sgr A* considerando tanto el movimiento orbital de la estrella como la propagación de fotones desde la estrella hasta el observador.

### Observaciones importantes

**Método de ajuste:** Geodésicas de Kerr integradas numéricamente + MCMC. El movimiento de la estrella se integra en la métrica de Kerr (ecuaciones de segundo orden en coordenadas BL, o equivalentemente primer orden en el espacio de fase con las constantes del movimiento $E, L_z, Q$). La propagación del fotón también se hace en Kerr (efecto de lensing, retraso de Shapiro). El ajuste se hace contra posiciones astrométricas y velocidades radiales observadas.

**Resultado clave:** Usando S2 con precisión GRAVITY (~50 μas astrométrico, ~1 km/s radial) por ~45 años, el spin es detectable si $a \gtrsim 0.5$ y las condiciones son favorables. Si la estrella estuviera más cerca, el tiempo se reduce dramáticamente.

**Parámetros a ajustar:** $(M, a, \hat{n}_{spin}, R_0, \text{6 parámetros orbitales}, \text{parámetros del marco de referencia})$ → típicamente ~15-20 parámetros en total.

**Problema de degeneración:** En Kerr, el espacio $(E, L_z, Q)$ mapea a $(p, e, \iota)$ (semi-latus rectum, excentricidad, inclinación). La degeneración más severa es entre $a$ y la orientación del spin, especialmente cuando la inclinación del plano orbital es pequeña respecto al spin del BH.

**Costo computacional:** Alto. Cada evaluación del modelo requiere integrar geodésicas numéricas + trayectoria del fotón. Con MCMC de ~15 parámetros y convergencia típica de $10^5$–$10^6$ pasos, el costo puede ser de días en hardware moderno.

### Artículos de interés

- Merritt et al. 2010: efectos de spin en órbitas de S-estrellas
- arXiv:2505.24789: efectos de spin y cuadrupolo en S-estrellas (2025)

---

## [Fujita & Hikida 2009 — Analytical solutions of bound timelike geodesic orbits in Kerr spacetime]

---
doi: 10.1088/0264-9381/26/13/135002
año de publicacion: 2009
autor: Fujita, R.; Hikida, W.
bib: |
  @article{fujita2009,
    author  = {Fujita, R. and Hikida, W.},
    title   = {Analytical solutions of bound timelike geodesic orbits in Kerr spacetime},
    journal = {Classical and Quantum Gravity},
    volume  = {26},
    pages   = {135002},
    year    = {2009},
    doi     = {10.1088/0264-9381/26/13/135002}
  }
---

### Resultados de lo buscado

Apareció como referencia fundamental en búsquedas de soluciones analíticas de geodésicas en Kerr. Es la base teórica para los métodos frecuenciales.

### Resumen

Derivan las **soluciones analíticas completas** de las geodésicas temporales ligadas en Kerr, expresadas en términos de **integrales elípticas de Legendre** (funciones $K$, $E$, $\Pi$ estándar) usando el **tiempo de Mino** $\lambda$ como variable independiente. El tiempo de Mino desacopla el movimiento radial del polar, lo que es imposible con el tiempo coordenado. A partir de esto, derivan las tres **frecuencias fundamentales** ($\Omega_r, \Omega_\theta, \Omega_\phi$) en función de $(E, L_z, Q)$ o equivalentemente de $(p, e, \iota)$.

### Observaciones importantes

**Importancia para el ajuste:** Las soluciones analíticas son mucho más rápidas que la integración numérica de geodésicas cuando se necesita evaluar el modelo muchas veces (como en MCMC). En lugar de integrar ODEs, se evalúan funciones especiales.

**Parametrización estándar:** El artículo usa la parametrización $(p, e, \iota)$:
- $p$: semi-latus rectum (distancia en unidades de $M$)
- $e$: excentricidad
- $\iota$: inclinación orbital definida como $\cos\iota = L_z / \sqrt{L_z^2 + Q}$

**Conversión a constantes del movimiento:** Las relaciones entre $(p, e, \iota)$ y $(E, L_z, Q)$ son conocidas; el mapeo inverso (de $(E, L_z, Q)$ a $(p, e, \iota)$) fue un problema abierto hasta trabajos recientes (ver arXiv:2401.09577).

**Limitación:** Para el ajuste observacional, aún se necesita un modelo de cómo las coordenadas Boyer-Lindquist se proyectan en el plano del cielo (efecto de lensing, aberración, retraso de Shapiro).

**Uso en relatipy:** Este es el formalismo natural para el módulo `symbolic` y para evaluar órbitas analíticamente en el módulo `numeric`.

### Artículos de interés

- Mino 2003: introducción del tiempo de Mino: doi 10.1103/PhysRevD.67.084027
- Drasco & Hughes 2004: frecuencias orbitales en Kerr
- arXiv:2401.09577: parametrización para inspiral adiabático

---

## [Warburton, Barack & Sago 2013 — Isofrequency pairing of geodesic orbits in Kerr geometry]

---
doi: 10.1103/PhysRevD.87.084012
año de publicacion: 2013
autor: Warburton, N.; Barack, L.; Sago, N.
bib: |
  @article{warburton2013,
    author  = {Warburton, N. and Barack, L. and Sago, N.},
    title   = {Isofrequency pairing of geodesic orbits in Kerr geometry},
    journal = {Physical Review D},
    volume  = {87},
    pages   = {084012},
    year    = {2013},
    doi     = {10.1103/PhysRevD.87.084012}
  }
---

### Resultados de lo buscado

Apareció en búsqueda de degeneraciones en métodos de ajuste por frecuencias en Kerr.

### Resumen

Demuestran que en la región de campo fuerte del espacio de parámetros de Kerr, **pares de órbitas físicamente distintas pueden tener exactamente las mismas tres frecuencias fundamentales** $(\Omega_r, \Omega_\theta, \Omega_\phi)$. Este fenómeno se llama "isofrequency pairing" y ocurre cerca de la separatriz (órbita estable más interna). En cada par isofrecuencial, las dos órbitas difieren en excentricidad e inclinación pero tienen la misma precesión de periastro y la misma precesión de Lense-Thirring del plano orbital.

### Observaciones importantes

**Implicación directa para el ajuste:** Si uno intenta ajustar la órbita de una estrella usando solo las frecuencias observadas $(\Omega_r, \Omega_\theta, \Omega_\phi)$, existe una **degeneración fundamental en campo fuerte**: dos órbitas distintas (con distinto $e$, distinto $\iota$) producen exactamente las mismas frecuencias. Esto hace imposible la identificación única del estado orbital solo por frecuencias en esa región.

**Región donde ocurre:** Cerca de la separatriz $p = p_{sep}(e, \iota, a)$. Para órbitas de estrellas en el centro galáctico (que están lejos del horizonte), este efecto es despreciable. Pero para estrellas hipotéticas más cercanas o para EMRIs (extreme mass ratio inspirals), es crítico.

**Solución propuesta:** Usar información de derivadas de orden superior (aceleraciones, jerk) o armónicos de frecuencia más alta en la señal para romper la degeneración.

**Relevancia para relatipy:** Si se implementa ajuste por frecuencias, hay que estar consciente de esta degeneración y verificar si el régimen de interés la activa.

### Artículos de interés

- Drasco & Hughes 2004: primeras frecuencias en Kerr
- arXiv:2508.08888: derivadas de orden alto de funcionales orbitales en Kerr (2025)

---

## [GRAVITY Collaboration / Varios — Testing black hole space-times with the S2 star orbit: a Bayesian comparison]

---
doi: (arXiv:2602.04980)
año de publicacion: 2026
autor: (ver arXiv:2602.04980)
bib: |
  @article{s2bayesian2026,
    author  = {},
    title   = {Testing black hole space-times with the S2 star orbit: a Bayesian comparison},
    journal = {},
    year    = {2026},
    doi     = {(arXiv:2602.04980)}
  }
---

### Resultados de lo buscado

Apareció en búsqueda de "Bayesian comparison orbit fitting Kerr S2 star 2026". Es uno de los trabajos más recientes.

### Resumen

Aplican análisis Bayesiano con MCMC para comparar diferentes modelos de espacio-tiempo (Schwarzschild, Kerr, y métricas alternativas) usando los datos de la órbita de S2. El método compara modelos via Bayesian evidence (factor de Bayes), lo que va más allá de solo ajustar parámetros: permite selección de modelo.

### Observaciones importantes

**Método clave:** MCMC con likelihood basada en la comparación entre posiciones astrométricas y velocidades radiales observadas vs. las predichas por integración de geodésicas. El factor de Bayes entre modelos permite decir cuál espacio-tiempo se favorece estadísticamente.

**Diferencia respecto a χ²:** El χ² solo da el mejor ajuste; el Bayesiano da la distribución posterior completa de los parámetros y permite comparar la evidencia entre modelos distintos.

**Estado del arte actual:** Este tipo de análisis representa el método más riguroso para el ajuste de órbitas en contextos de centro galáctico.

### Artículos de interés

- arXiv:2511.04163: constrains Sgr A* en un halo de materia oscura (2025)

---

## [Varios — The effects of the spin and quadrupole moment of SgrA* on the orbits of S stars]

---
doi: (arXiv:2505.24789)
año de publicacion: 2025
autor: (ver arXiv:2505.24789)
bib: |
  @article{spin_quad_2025,
    author  = {},
    title   = {The effects of the spin and quadrupole moment of SgrA* on the orbits of S stars},
    journal = {},
    year    = {2025},
    doi     = {(arXiv:2505.24789)}
  }
---

### Resultados de lo buscado

Apareció en búsqueda de efectos de spin en órbitas de S-estrellas (2025).

### Resumen

Estudian cómo el spin $a$ y el momento cuadrupolar $Q_2$ del agujero negro afectan la dinámica de las S-estrellas. En Kerr, el cuadrupolo está fijado por el spin: $Q_2 = -a^2 M$ (teorema no-hair). Cualquier desviación de esta relación indicaría un objeto compacto no-Kerr. El artículo cuantifica cuándo estos efectos son distinguibles con GRAVITY.

### Observaciones importantes

**Efecto del spin en el plano:** Precesión azimutal adicional (apsidal, en plano). En Kerr, esto se suma a la precesión de Schwarzschild pero depende del ángulo entre el plano orbital y el spin del BH.

**Efecto del spin fuera del plano:** Precesión de Lense-Thirring → inclinación del plano orbital oscila con el tiempo. Esta es la firma más característica y distinguible de Kerr vs. Schwarzschild.

**Estrategia de ajuste:** Para separar los efectos de $a$ y $Q_2$, se necesita al menos una estrella con órbita inclinada respecto al spin del BH. Con una sola estrella en el plano ecuatorial, $Q_2$ y $a$ son degenerados.

**Conclusión:** Con GRAVITY y ~2-3 períodos orbitales de una estrella más cercana que S2 (~10-20 años de observación), se podría constrainar $a$ y $Q_2$ simultáneamente si la precisión astrométrica alcanza ~10 μas.

### Artículos de interés

- Will 2008: medición de spin y momento cuadrupolar de Sgr A*
- Merritt 2010: perturbaciones Newtonianas e inducidas por spin

---

## [Varios — KerrGeoPy: A Python Package for Computing Timelike Geodesics in Kerr Spacetime]

---
doi: (arXiv:2406.01413)
año de publicacion: 2024
autor: (ver arXiv:2406.01413)
bib: |
  @article{kerrgeopy2024,
    author  = {},
    title   = {KerrGeoPy: A Python Package for Computing Timelike Geodesics in Kerr Spacetime},
    journal = {},
    year    = {2024},
    doi     = {(arXiv:2406.01413)}
  }
---

### Resultados de lo buscado

Apareció en búsquedas de herramientas computacionales para geodésicas en Kerr.

### Resumen

Paquete Python que implementa las **soluciones analíticas** de Fujita & Hikida (2009) para geodésicas temporales ligadas en Kerr, evaluadas en tiempo de Mino. Calcula: trayectorias $(t, r, \theta, \phi)(\lambda)$, frecuencias fundamentales $(\Omega_r, \Omega_\theta, \Omega_\phi)$, constantes del movimiento $(E, L_z, Q)$ a partir de $(p, e, \iota, a)$, y la separatriz usando el algoritmo de Stein & Warburton (2020).

### Observaciones importantes

**Ventaja frente a integración numérica:** Al usar soluciones analíticas (integrales elípticas), es mucho más eficiente para evaluar el modelo en MCMC: no hay acumulación de error numérico, y se puede evaluar la trayectoria en cualquier $\lambda$ sin integrar desde el inicio.

**Relevancia para relatipy:** Este paquete es un competidor directo o complemento natural del módulo `numeric` de relatipy. Dado que relatipy usa Radau (integración numérica), podría considerarse un módulo analítico basado en KerrGeoPy/Fujita-Hikida para acelerar ajustes.

**También útil para:** EMRIs, cálculo de flujos de onda gravitacional, y ajuste de QPOs en microcuásares y AGN.

### Artículos de interés

- Stein & Warburton 2020: algoritmo para encontrar la separatriz
- Fujita & Hikida 2009 (ya registrado)

---

# Tabla comparativa de métodos

| Método | Parámetros ajustados | Costo comp. | Aplicabilidad | Degeneraciones | Error típico |
|---|---|---|---|---|---|
| **PN + χ²/MCMC** | $M, R_0$, 6 orbitales, $f_{SP}$ | Bajo | S2-like, lejos del horizonte | Bajo (bien separados) | $\sigma_M \sim 0.3\%$ |
| **GR completo (geodésica Kerr numérica) + MCMC** | $M, a, \hat{n}_{spin}$, orbitales | Alto | Estrellas cercanas, GR fuerte | Medio ($a$ vs orientación) | Depende de la estrella |
| **Analítico (Fujita-Hikida) + MCMC** | $p, e, \iota, a, M$ | Medio | Todos los regímenes | Medio | Similar al numérico, más estable |
| **Frecuencial ($\Omega_r, \Omega_\theta, \Omega_\phi$)** | $(p, e, \iota)$ → $(a, M)$ | Bajo | Campo fuerte/EMRI | Alto (isofrequency) | Requiere rompimiento de degeneración |
| **Lense-Thirring (precesión del plano)** | $a, \hat{n}_{spin}$ | Bajo | Órbitas inclinadas, largo plazo | Bajo si hay múltiples estrellas | Requiere 2-3 períodos orbitales |
| **No-hair (spin + cuadrupolo)** | $a, Q_2$ | Alto | Prueba de teoremas no-hair | Alto ($a$-$Q_2$ degenerados en 1 estrella) | Requiere múltiples estrellas |
| **Bayesiano con model selection** | Todos + evidencia del modelo | Muy alto | Comparación de métricas | Bajo (evidencia Bayesiana separa) | Estadísticamente óptimo |

---

# Discusión física

## La diferencia fundamental con Schwarzschild

En Schwarzschild hay simetría esférica: $L^2 = L_z^2 + L_\perp^2$ es conservada, y el movimiento está confinado a un plano. El ajuste solo necesita determinar el plano orbital y las constantes $(E, L)$.

En Kerr la simetría esférica está rota: solo $L_z$ (componente axial del momento angular) se conserve como Killing, y aparece la **constante de Carter** $Q$:

$$Q = p_\theta^2 + \cos^2\theta \left(a^2(m^2 - E^2) + \frac{L_z^2}{\sin^2\theta}\right)$$

Esta constante **no tiene análogo clásico** y es la huella de la separabilidad de Hamilton-Jacobi en Kerr. En términos físicos, $Q \approx 0$ para órbitas ecuatoriales y $Q > 0$ para órbitas inclinadas. Medir $Q$ observacionalmente es equivalente a medir la inclinación del plano orbital respecto al spin del BH.

## Efectos observables únicos de Kerr

1. **Precesión de Lense-Thirring (nodal):** El plano orbital precesa alrededor del eje de spin del BH con frecuencia $\Omega_{LT} \propto a M / r^3$. Esta es la firma más directa del spin. Observacionalmente: el eje mayor de la órbita proyectada en el cielo rota con el tiempo.

2. **Precesión azimutal adicional:** El spin añade una contribución a la precesión en el plano. Se suma/resta a la precesión de Schwarzschild dependiendo de si la órbita es prograda o retrógrada.

3. **Acoplamiento $r$-$\theta$:** A diferencia de Schwarzschild, en Kerr el período radial y el polar son distintos: $T_r \neq T_\theta$ en general. Esto produce una "roseta" que no cierra en el plano orbital y oscila fuera de él.

## Por qué el ajuste es más difícil en Kerr

- **Más parámetros:** Se añaden $a$ (magnitud del spin), $\hat{n}_{spin}$ (2 ángulos de orientación del spin). Total ~18-20 parámetros en MCMC.
- **Degeneración $a$-orientación:** Si la inclinación orbital es pequeña, el efecto de Lense-Thirring es mínimo y $a$ queda mal constrainada.
- **Degeneración con perturbaciones Newtonianas:** El disco estelar alrededor de Sgr A* también induce precesión nodal. Separar esto del efecto Lense-Thirring requiere múltiples estrellas o modelos del entorno.
- **Propagación del fotón:** En Kerr, la trayectoria del fotón también se curva de forma dependiente del spin (lensing, retraso de Shapiro). Ignorarlo introduce un sesgo sistemático en las posiciones astrométricas ajustadas.

## Cuándo usar cada método

- **Estrellas tipo S2 (periastro ~1400 $r_s$):** PN + MCMC es suficiente para medir $M$ y $R_0$ con alta precisión. Kerr completo no es necesario ni detectable.
- **Estrellas hipotéticas más cercanas (~100 $r_s$):** Geodésicas de Kerr completas + MCMC/analítico Fujita-Hikida. La señal de spin podría ser detectable en 2-3 períodos.
- **EMRIs (campo ultra-fuerte):** Métodos frecuenciales, pero con cuidado de la degeneración isofrecuencial. Las soluciones analíticas son esenciales por eficiencia.
- **Pulsares cerca de Sgr A*:** Timing de pulsares podría constrainar $a$ y $Q_2$ independientemente con alta precisión, pero no son órbitas estelares estrictamente.

