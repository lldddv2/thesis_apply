# Nuevo integrador 

Los integradores clásicos de scipy.solve_ivp son no están diseñados para la conservación de cantidades. En relatividad general, esto sí es muy importante, y por eso, el objetivo de esta semana fue obtener buenos resultados de integradores que fueran adecuados para la conservación de cantidades.

Para dicha prueba, se estableció una condición inicial a 100 radios de Schwarzschild, sin excentricidad y variando la inclinación de 0 a 90 grados. Se integró por 500 periodos orbitales.

## Integradores simplecticos

Una primera aproximación para reducir errores, podría se usar integradores simplecticos, que se caracterizan por conservar la constante de Hamilton. En nuestro caso, esperariamos que estos integradores sean adecuados para la conservación de cantidades.

Para una prueba inicial se decidió usar el integrador Yoshida6, que es un integrador simplectico de orden 6. Se obtuvieron los siguientes resultados:

<!-- img:"errors_Q_E_Lz_Yoshida6_sin_projection.png" -->

Como podemos ver, el integrador `Yoshida6` hace que el error de la constante de carter con inclinación cero, se dispare a cantidades exorbitantes, además, los errores relativos de energía relativista y momento angular son del 1%, que, sabemos, puede no ser mucho, pero con métodos clásicos, suele ser mucho más pequeño.

## Integrador Radau + proyección

Según la semana 3, el integrador `Radau` obtiene mejores resultados que este integrador simplectico, pues el crecimiento de los errores es lineal, pero menor.

En este sentido, se optó por usar un método de proyección:

### Método de proyección

El integrador numérico introduce pequeños errores en cada paso, lo que hace que las cuatro cantidades conservadas del sistema se desvíen de sus valores teóricos. El método de proyección corrige esto forzando que dichas cantidades se mantengan exactamente.

Las restricciones que deben cumplirse en todo momento son:

$$
\begin{align*}
C_1 &= g_{\mu\nu} u^\mu u^\nu - 1 = 0 \quad &\text{(normalización: partícula masiva)} \\
C_2 &= -g_{0\mu} u^\mu - E_0 = 0 \quad &\text{(energía conservada)} \\
C_3 &=  g_{3\mu} u^\mu - L_{z,0} = 0 \quad &\text{(momento angular conservado)} \\
C_4 &= p_\theta^2 + \cos^2\theta\left[ a^2(1-E^2) + \frac{L_z^2}{\sin^2\theta} \right] - Q_0 = 0 \quad &\text{(Carter)}
\end{align*}
$$

Para corregir, dado un $u^\mu$ aproximado, se busca la corrección mínima $\delta u^\mu$ tal que $C(u + \delta u) = 0$. Linealizando, esto equivale a resolver:

$$
J\, \delta u = -C
$$

donde $J$ es el jacobiano analítico $4 \times 4$, $\left(\frac{\partial C_i}{\partial u_\nu}\right)$.

El sistema se resuelve por eliminación gaussiana y se actualiza iterativamente hasta que $\max |C_i| < 10^{-12}$. Debido a que $C_2$ y $C_3$ son lineales, suelen ajustarse en una iteración; $C_1$ y $C_4$ son cuadráticas pero el método converge típicamente en $2$ a $3$ iteraciones de Newton.

### Resultados

Se obtuvieron los siguientes resultados:

<!-- img:"errors_Q_E_Lz_Radau2_con_projection.png" -->

Observando la corrección de errores relativos, la energía relativusta y el momento angular, alcanzan un error relativo máximo de $10^{-6}$, por lo que la groyección conserva muy bien estas dos cantidades. Para nosotros, en el caso de la métrica de Kerr, la constante más importante es la constante de Carter, que tiene un error relativo máximo en ordenes de $10^{-5}$, exceptuando los casos de inclinación inicial de 0 grados, en los que el error relativo máximo es de $10^{-3}$. Para 90 grados, como es de esperar, al pasar cerca de un punto crítico de la métrica los errores se disparan, por lo que decidimos no incluirlos en la figura.
