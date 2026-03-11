# Integradores de orbitas

Esta semana se exploraron los mejores integradores para trabajar con orbitas en Kerr.

# Planteamiento inicial
Asumamos que tenemos un agujero negro de kerr con parámetro de rotación $a = 0.5$ y masa $M = 1$ (en unidades geométricas). Estableciendo unas condiciones iniciales en elementos osculantes, con un semieje mayor de 4 veces el radio de Schwarzschild, obtenemos una orbita que cae lentamente hacia el agujero negro. Para hacernos una idea, cuando han pasado 500 periodos (periodos de condición inicial según una orbita kepleriana), la orbita se observa como vemos en la figura.

<!-- html:"orbit_500_periods.html" -->

Siendo de esta manera, veamos qué sucede con los diferentes integradores de scipy.solve_ivp. 

Según la [documentación de scipy](https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html), los integradores disponibles son:
- RK45
- RK23
- DOP853
- Radau
- BDF
- LSODA

Se probarán estos integradores con la constante de Carter $Q$ en función de sus periodos, hasta llegar a $10^4$ periodos. Con esto, verificaremos cual es el mejor integrador para trabajar con orbitas en Kerr. Verificaremos mediante el error máximo, dado que, por la naturaleza de las orbitas, se observa una fluctuación en el error relativo. 

# Resultados
## Mejor integrador
Las primeras integraciones fueron hasta 500 periodos, con una división de $10^4$ puntos. Los resultados se muestran en la figura.

<!-- img:"error_instantaneous.png" -->

En la parte superior, se muestran los métodos BDF, RK23 y RK45, que no conservan muy bien la constante de Carter. Se observan fluctuaciones muy grandes de el primer periodo hata el 100. Después de eso se ve un salto en el error, consecuencia de que está cayendo dentro de la ergoesfera. Estos integradores no son adecuados para trabajar con orbitas en Kerr.

En la parte inferior, se muestran los métodos DOP853, Radau y LSODA, que conservan muy bien la constante de Carter. De hecho, las fluctuaciones son las mismas a lo largo de los primeros 100 periodos. Despues, el método DOP853 empieza a crecer demasiado, por lo que ya no es adecuado para trabajar con orbitas en Kerr. Esto se ve mejor en la siguiente figura.

<!-- img:"error_instantaneous_DOP853_Radau_LSODA.png" -->

En esta figura se logra observar los métodos pero con tiempos de integración más largos, con $10^4$ periodos con 30000 puntos. En donde, despues $10^3$ periodos, ya no vale la pena usar el método DOP853, ya que empieza a crecer demasiado. Radau se mantiene como el mejor integrador, ya que no se observa un crecimiento significativo, y LSODA le sigue con un crecimiento moderado.

## Número de divisiones apropiado
En la sección anterior se observó que el método Radau es el mejor integrador para trabajar con orbitas en Kerr. Ahora, se buscará el número de divisiones apropiado para este método, partiendo desde los 1 periodo orbital hasta los $10^4$ periodos orbitales. Buscando así un equilibrio entre el número de divisiones más optimo según el número de periodos orbitales. 

La suigiente figura muestra una mapa de colores que nos permite visualizar el mínimo y máximo error máximo acumulado para cada número de divisiones y número de periodos orbitales.

<!-- img:"mapa_de_colores.png" -->

De esta manera, podemos trazar contornos de tolerancia para ver, según nuestro criterio, cual es el número de divisiones más optimo según el número de periodos orbitales.

## Reflexiones

- 

## Próximos pasos

- 
