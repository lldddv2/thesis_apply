# Guía de Estilo — Tesis

Normativas de estilo aplicadas por el skill `/coherencia`. Toda norma aquí es de cumplimiento obligatorio para archivos `.tex` del manuscrito.

---

## 1. Voz y Tono

- **Voz**: primera persona plural — "Definimos", "Observamos", "Podemos demostrar", "Mostramos".
- **Tono**: académico y formal. Sin juicios propios, adjetivos subjetivos ("interesante", "sorprendente", "claramente") ni afirmaciones sin respaldo.
- Las afirmaciones deben estar respaldadas por: (a) una cita bibliográfica, (b) una derivación propia en el texto, o (c) una referencia a una ecuación/resultado anterior.
- Si una afirmación requiere cita y no la tiene, el revisor debe insertar `[ADVERTENCIA, HACE FALTA UNA CITA AQUÍ]` en el texto y reportarlo en el chat.

---

## 2. Ecuaciones

- Toda ecuación en bloque (`equation`, `align`, `gather`, etc.) **debe tener** `\label{eq:nombre_descriptivo}`.
- Los labels deben ser descriptivos, no genéricos. Mal: `eq:eq1`. Bien: `eq:geodesica_kerr`, `eq:carter_constant`.
- **Excepción**: pasos intermedios en una derivación teórica continua no necesitan label si no van a ser referenciados.
- Toda ecuación con label **debe ser mencionada** en el texto con `\eqref{eq:...}` o una referencia explícita. Excepción: pasos intermedios de derivaciones.
- Numeración por sección (ya configurada en `comandos.tex`).

---

## 3. Figuras

- Toda figura **debe tener** `\label{fig:nombre_descriptivo}` y `\caption{...}` descriptivo.
- La figura **debe ser mencionada** en el texto antes de aparecer: "como se muestra en la figura~\ref{fig:...}".
- El caption debe describir qué muestra la figura, no solo nombrarla.

---

## 4. Tablas

- Toda tabla **debe tener** `\label{tab:nombre_descriptivo}` y `\caption{...}`.
- La tabla **debe ser mencionada** en el texto antes de aparecer.
- El caption debe describir el contenido de la tabla.

---

## 5. Convención de Labels

| Tipo | Prefijo | Ejemplo |
|------|---------|---------|
| Ecuación | `eq:` | `eq:geodesica_kerr` |
| Figura | `fig:` | `fig:carter_error_radau` |
| Tabla | `tab:` | `tab:comparacion_integradores` |
| Sección | `sec:` | `sec:marco_teorico` |
| Definición | `def:` | `def:tensor_metrico` |
| Teorema | `thm:` | `thm:conservacion_carter` |
| Observación | `obs:` | `obs:indices_griegos` |

---

## 6. Entornos Formales (Marco Teórico)

El marco teórico usa entornos formales tipo matemático definidos en `manuscrito/comandos.tex`.

### Entornos disponibles

| Entorno LaTeX | Uso |
|---------------|-----|
| `\begin{definicion}[Nombre]{def:label}` | Definir conceptos formalmente |
| `\begin{teorema}[Nombre]{thm:label}` | Enunciar resultados demostrados |
| `\begin{observacion}[Nombre]{obs:label}` | Aclaraciones o comentarios sobre resultados |

### Reglas de uso

- Toda definición formal del marco teórico debe usar el entorno `definicion`.
- El nombre entre corchetes es el nombre de la definición (e.g., `[Tensor contravariante]`).
- El label es obligatorio y sigue la convención `def:`, `thm:`, `obs:`.
- Si se enuncia un teorema conocido, **debe tener cita**. Si no la tiene: insertar `[ADVERTENCIA, HACE FALTA UNA CITA AQUÍ]`.

---

## 7. Citas Bibliográficas

- Toda afirmación que no sea derivación propia o conocimiento de nivel de curso debe tener `\cite{...}`.
- Si el revisor detecta una afirmación sin respaldo que probablemente requiera cita, insertar `[ADVERTENCIA, HACE FALTA UNA CITA AQUÍ]` inmediatamente después de la afirmación.
- Reportar todas las advertencias en el chat al finalizar la revisión.

---

## 8. Estructura de Secciones

- Toda sección o subsección debe comenzar con al menos un párrafo introductorio antes de ecuaciones, figuras o entornos formales.
- Los resultados deben tener interpretación explícita en el texto (no solo presentar la ecuación o figura).

---

## 9. Idioma

- El texto debe estar en español.
- Los términos técnicos en inglés son aceptables si no tienen traducción estándar en la comunidad hispanohablante de física.
- No alternar el idioma de un mismo término a lo largo del documento (escoger uno y mantenerlo).

---

## 11. Requisitos para Definiciones Matemáticas

Ver criterios completos en `.claude/skills/math/references/definiciones.md`. Resumen:

| # | Requisito | Obligatorio |
|---|-----------|-------------|
| 1 | Nombre preciso en `[...]` y en cursiva en el texto | Siempre |
| 2 | Espacio/contexto establecido antes de la condición | Siempre |
| 3 | Condición caracterizadora precisa y verificable | Siempre |
| 4 | Notación consistente con `nomenclatura.tex` | Siempre |
| 5 | Existencia no vacía justificada (si no es obvia) | Cuando aplique |
| 6 | Unicidad mencionada (si aplica) | Cuando aplique |

Estructura mínima:
```latex
\begin{definicion}[Nombre preciso]{def:label}
    Sea $(\mathcal{M}, g_{\mu\nu})$ [contexto].
    Decimos que [objeto] es una \textit{nombre} si
    \begin{equation}
        \text{condición formal.} \label{eq:label}
    \end{equation}
\end{definicion}
```

Para incumplimientos: insertar `[ADVERTENCIA: Req. N — descripción]`.

---

## 12. Indentación

La indentación es obligatoria para mantener legibilidad y facilitar la navegación en el código LaTeX. Usar **4 espacios** por nivel (no tabs).

### Reglas generales

- `\begin{env}` y `\end{env}` al mismo nivel de indentación entre sí.
- El contenido dentro de un entorno se indenta **un nivel** respecto al `\begin`.
- Los entornos anidados acumulan niveles.

### Ejemplos por tipo

**Ecuaciones:**
```latex
\begin{equation}
    E = mc^2 \label{eq:einstein}
\end{equation}

\begin{align}
    A^\mu &= g^{\mu\nu} A_\nu \label{eq:subir_indice} \\
    A_\mu &= g_{\mu\nu} A^\nu \label{eq:bajar_indice}
\end{align}
```

**Figuras y tablas:**
```latex
\myFigure[fig:carter]{carter_error.png}[Error de la constante de Carter.][0.7]
```
*(comandos propios no requieren indentación interna; el entorno `figure` ya está encapsulado)*

**Entornos formales:**
```latex
\begin{definicion}[Tensor métrico]{def:tensor_metrico}
    Sea $\mathcal{M}$ una variedad diferenciable. Definimos el tensor métrico
    $g_{\mu\nu}$ como...
\end{definicion}
```

**Listas:**
```latex
\begin{itemize}
    \item Primer elemento.
    \item Segundo elemento con contenido largo que continúa
          en la siguiente línea alineado con el texto del ítem.
    \item Tercer elemento.
\end{itemize}
```

**Anidamiento:**
```latex
\begin{align}
    {A^{\mu_1 \mu_2}}_{\nu_1 \nu_2}
        {B^{\nu_1 \nu_2}}_{\rho_1 \rho_2}
        &= \sum_{\nu_1=0}^{3} \sum_{\nu_2=0}^{3}
            {A^{\mu_1 \mu_2}}_{\nu_1 \nu_2}
            {B^{\nu_1 \nu_2}}_{\rho_1 \rho_2}
        \label{eq:contraccion_doble}
\end{align}
```

### Lo que el revisor debe verificar

- Entornos (`equation`, `align`, `figure`, `table`, `itemize`, `enumerate`, `definicion`, `teorema`, `observacion`) con contenido sin indentar → reportar.
- `\end{env}` que no coincide en nivel con su `\begin{env}` → reportar.
- Uso de tabs en lugar de espacios → reportar (los tabs generan inconsistencias entre editores).

---

## 10. Terminología Estándar del Proyecto

*(Completar a medida que se establezcan preferencias de terminología específica)*

- "métrica de Kerr" (no "geometría de Kerr")
- "parámetro de rotación $a$" (no "spin")
- "constante de Carter" (no "cuarta constante de movimiento" como término principal)
