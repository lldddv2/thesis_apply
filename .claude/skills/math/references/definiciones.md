# Requisitos para una Definición Matemática Correcta

Este archivo define los 6 criterios que toda definición formal en el marco teórico debe cumplir.
Se aplican tanto al revisar (`/math`) como al escribir definiciones con el entorno `\begin{definicion}`.

---

## Estructura esperada en LaTeX

```latex
\begin{definicion}[Nombre preciso del objeto]{def:label_descriptivo}
    Sea $(\mathcal{M}, g_{\mu\nu})$ [contexto/espacio].
    Decimos que [objeto] es [nombre] si [condición unívoca].
    \begin{equation}
        \text{condición formal} \label{eq:label_descriptivo}
    \end{equation}
    [Nota de existencia o unicidad si aplica.]
\end{definicion}
```

---

## Los 6 Requisitos

### 1. Nombre claro y preciso

El nombre del objeto que se define debe aparecer explícitamente, usualmente en cursiva en la primera mención dentro del entorno.

✅ Correcto:
```latex
\begin{definicion}[Geodésica]{def:geodesica}
    ...una curva $\gamma(\tau)$ es una \textit{geodésica} si...
\end{definicion}
```

❌ Incorrecto:
```latex
\begin{definicion}[Curva especial]{def:curva}
    ...una curva especial es aquella que...  % nombre vago
\end{definicion}
```

**Cómo verificar:** ¿El argumento `[Nombre]` del entorno es el nombre técnico preciso del objeto? ¿Aparece en cursiva dentro del texto?

---

### 2. Espacio o contexto

La definición debe establecer el espacio matemático o contexto físico en el que el objeto existe, antes de enunciarlo.

✅ Correcto:
```latex
Sea $(\mathcal{M}, g_{\mu\nu})$ una variedad pseudo-Riemanniana de signatura $(+,-,-,-)$...
```

❌ Incorrecto:
```latex
Dado un espacio con una métrica...  % contexto impreciso
```

**Cómo verificar:** ¿La definición especifica la variedad, el espacio-tiempo, o el sistema en el que vive el objeto?

---

### 3. Condición unívoca (caracterización)

La condición que define el objeto debe ser precisa y no ambigua. En física matemática esto suele ser una ecuación o un conjunto de ecuaciones.

✅ Correcto:
```latex
...satisface la ecuación de transporte paralelo
\begin{equation}
    u^\nu \nabla_\nu u^\mu = 0, \label{eq:geodesica_paralela}
\end{equation}
donde $u^\mu = dx^\mu/d\tau$ es el vector tangente a $\gamma$.
```

❌ Incorrecto:
```latex
...es una curva que "no se curva demasiado" en el espacio.  % condición informal
```

**Cómo verificar:** ¿La condición puede verificarse matemáticamente? ¿Es precisa?

---

### 4. Notación consistente con el documento

Toda notación dentro de la definición debe ser consistente con `manuscrito/docs/general/nomenclatura.tex` y con el resto del documento.

✅ Correcto: usar $g_{\mu\nu}$ si así se definió el tensor métrico.

❌ Incorrecto: definir usando $g_{\mu\nu}$ y luego en el texto referirse al mismo objeto como $G_{ab}$ o $\eta_{\mu\nu}$ sin indicarlo.

**Cómo verificar:** ¿Los símbolos usados son los mismos que en `nomenclatura.tex`? ¿Se mantienen en el resto del archivo?

---

### 5. Existencia no vacía (cuando no es obvia)

Si la existencia del objeto definido no es trivial o podría parecer cuestionable, debe mencionarse brevemente. Puede ser una nota o una referencia.

✅ Correcto:
```latex
\begin{observacion}[Existencia de la constante de Carter]{obs:existencia_carter}
    La existencia de $Q$ se garantiza por la separabilidad de la ecuación
    de Hamilton-Jacobi en el espacio-tiempo de Kerr \cite{carter1968}.
\end{observacion}
```

❌ Incorrecto: definir un objeto que en realidad es vacío bajo las condiciones del documento (e.g., $E > 0$ y $E < 0$ simultáneamente).

**Cómo verificar:** ¿El conjunto o el objeto definido puede efectivamente existir en el contexto del documento?

---

### 6. Unicidad cuando aplique

Si el objeto es único bajo las condiciones dadas, debe decirse explícitamente. Si no es único, debe aclararse.

✅ Correcto:
```latex
...el radio $r_\text{ISCO}$ es único para cada valor del parámetro de
rotación $a \in [0, M)$.
```

❌ Incorrecto: presentar una definición que implica unicidad sin mencionarla, o asumir unicidad cuando no la hay.

**Cómo verificar:** ¿El objeto está bien determinado? ¿Se menciona la unicidad (o su ausencia)?

---

## Checklist de Revisión

Al encontrar un entorno `\begin{definicion}` en el archivo, verificar:

- [ ] Req. 1 — ¿Tiene nombre preciso en `[...]` y en cursiva dentro del texto?
- [ ] Req. 2 — ¿Establece el espacio/contexto antes de enunciar la condición?
- [ ] Req. 3 — ¿La condición caracterizadora es precisa y verificable?
- [ ] Req. 4 — ¿La notación es consistente con `nomenclatura.tex`?
- [ ] Req. 5 — ¿La existencia es obvia o está justificada?
- [ ] Req. 6 — ¿Se menciona unicidad si aplica?

Los mismos criterios aplican a `\begin{teorema}` (sustituir "definición" por "enunciado").
Para `\begin{observacion}` solo aplican Req. 3 y Req. 4.

---

## Advertencias estándar

Si algún requisito no se cumple, insertar en el texto:

- `[ADVERTENCIA: Req. N — descripción del problema]`

Ejemplos:
- `[ADVERTENCIA: Req. 2 — Falta establecer el espacio en que vive el objeto]`
- `[ADVERTENCIA: Req. 5 — No es evidente que este objeto exista; considerar agregar justificación o cita]`
- `[ADVERTENCIA: Req. 1 — El nombre en el argumento del entorno no coincide con el nombre usado en el texto]`
