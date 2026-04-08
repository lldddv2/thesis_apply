# Comparación con mecánica clasica

Se hizo un hizo la comparación del periodograma de la órbita de Kerr con la órbita de Newton, de modo que se pudiera verificar que el periodograma estuviera funcionando correctamente.

Se usa un nuevo integrador denominado "Mino", basado en una solución analítica encontrada.

Se inició a documentar la teoría y se creo un compilador para ir viendo el avance de la teoría.

## Periodograma
El objetivo de estos pasos, era la verificación del buen funcionamiento del periodograma, dado que inicialmente se observó que el periodo dominante era 1 periodo orbital de Newton, y se observaban armónicos asociados. Al hacer la observación, Se nota que ya no es necesario, puesto que el integrador influye en la solución de forma directa.

<!-- img:"periods_and_amps_Radau2_vs_rebound.png" -->

La imagen anterior, nos muesta que en efecto, no hay nungun problema con la periodicidad de las órbitas.

Por otro lado, si comparamos con el integrador de Mino, se ve más control

<!-- img:"periods_and_amps_Radau2_vs_mino.png" -->

