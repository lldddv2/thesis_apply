# Verificación de comportamiento esperado

El objetivo de esta semana es verificar, para largos periodos de integración, el comportamiento esperado. Esto es: conservación de la constante de Carter, conservación de la energía relativista, conservación del momento angular e inclinación orbital.

## Tiempo adaptativo
Se hace uso por defecto del tiempo adaptativo de scipy.solve_ivp. Se intentó usar el integrador ias15, pero no se logró implementar de forma eficiente.

## Implementación del ISCO

En la métrica de Kerr, contamos con dos ISCOs, uno prograde y otro retrograde. El prograde. 

El Prograde es para partículas que giran en el mismo sentido que el agujero negro, y este es más cercano al agujero negro. El retrograde es para partículas que giran en sentido contrario, y este es más lejano al agujero negro, lo cual implica que mantener orbitas estables es más difícil para el retrograde.

Se implementó dicho cálculo con las siguientes ecuaciones, correspondientes al radio del ISCO en la métrica de Kerr (spin adimensional $a_* = \frac{a}{M}$, con $a_* \in [0, 1]$):

$$
\begin{align*}
a_* &= \frac{a}{M} \\
Z_1 &= 1 + (1 - a_*^2)^{1/3} \Big[ (1 + a_*)^{1/3} + (1 - a_*)^{1/3} \Big] \\
Z_2 &= \sqrt{3 a_*^2 + Z_1^2} \\
r_\mathrm{ISCO} &= M \left[ 3 + Z_2 + s\, \sqrt{(3 - Z_1)\left(3 + Z_1 + 2 Z_2\right)} \right]
\end{align*}
$$

donde $s = -1$ para órbitas progrades y $s = +1$ para órbitas retrogrades.

Esto nos da una idea general en caso de que querramos usar como unidad de medida para el radio de la orbita, el ISCO.

<!-- html:"orbit.html" -->

La figura muestra una orbita progre con inclinación inicial de 0 grados y un semieje mayor de 5 veces el ISCO prograde. Además, se logra evidenciar la orbita governada por el tiempo adaptativo de scipy.solve_ivp.

## Periodograma de Lomb-Scargle
Asumiendo que estamos a 100 radios de Schwarzschild, veamos como es la variación de la inclinación orbital en función del tiempo.

Para ello, usaremos la transformada de Lomb-Scargle, que nos permite obtener los modos dominantes de la inclinación orbital. Así haremos un periodograma de la inclinación orbital.

<!-- img:"periodograma_inclinacion.png" -->

Como podemos ver, el existe und frecuencia dominante a 0.5 periodos orbitales, si asumimos un periodo orbital de forma kepleriana. Los demás periodos son los modos.

Por la forma en la que se construlle, hay menos presición a largos periodos orbitales, por ello tomamos el eje x en escala logaritmica.

El caso de la inclinación inicial de 90 grados es el más inestable, como habríamos de esperar, puesto que pasa por un punto critico de la métrica, y los efectos minimos de una perturbación pueden afectar de manera significativa la inclinación orbital.

## Conservación de cantidades

Dado que no pudimos implementar el integrador ias15, analizamos el comportamiento de los errores de las cantidades conservadas con el integrador Radau según la integración en tiempo adaptativo. Se hace un muestreo.

<!-- img:"errors_Q_E_Lz.png" -->

Como se logra evidenciar, los errores crecen de manera lineal con el tiempo, los valores de error relativo están dados de forma porcentual, por lo que, la conservación de $Lz$ falla de forma notable, en el caso extremo de 80 grados, puede diferir en un cuarto de su valor inicial, lo cual es una cantidad significativa. Por otra parte, el error de la energía es despreciable, en los casos extremos llega a 0.02% para 500 periodos orbitales. Sin embargo, la constante de Carter $Q$, cuyo comportamiento se esperaría, fuera de ordenes a lo sumo, cercanos a 0.1, varía hasta en un 2.5%.

Viendo el crecimiento de los errores, que sigue una tendencia lineal, se puede intentar predecir el comportamiento de los errores según la inclinación inicial. Para ello tomamos muestras de a 5 grados y vemos los resultados en la figura.

<!-- img:"slopes_Q_error_exp.png" -->

<!-- img:"slopes_E_error_exp.png" -->

<!-- img:"slopes_Lz_error_piecewise.png" -->

No alcanzamos a ajustar todo, pero sí parece haber ciertas tendencias.
