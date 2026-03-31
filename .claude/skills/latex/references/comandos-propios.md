# Comandos LaTeX Propios del Proyecto

Estos comandos están definidos en `manuscrito/comandos.tex` y deben ser cargados en el preamble del documento principal con `\input{comandos.tex}` o similar.

---

## `\myFigure` — Insertar figura

```latex
\myFigure[label]{filename}[caption][width]
```

| Argumento | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `label` | Opcional (`O{}`) | vacío | Label para `\ref{}`. Usar prefijo `fig:`, e.g., `fig:orbita_kerr` |
| `filename` | **Obligatorio** (`m`) | — | Nombre del archivo en `figures/`. Sin ruta completa. |
| `caption` | Opcional (`O{}`) | vacío | Texto del pie de figura |
| `width` | Opcional (`O{0.5}`) | `0.5` | Fracción del `\textwidth` |

**Uso correcto:**
```latex
\myFigure[fig:carter_error]{error_carter.png}[Error relativo de la constante de Carter en función del tiempo.][0.7]
\myFigure{orbit_plot.png}   % Mínimo: solo el filename
```

**Errores comunes:**
- Usar `\myFigure{file}[caption]` sin cerrar el primer opcional `[]` — incorrecto
- Incluir la ruta completa: `\myFigure{figures/file.png}` — incorrecto (la ruta ya está en `\graphicspath`)
- Label sin prefijo `fig:` — no es error de compilación pero viola la convención del proyecto

---

## `\myTable` — Insertar tabla desde CSV

```latex
\myTable[label]{csvfile}[caption]
```

| Argumento | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `label` | Opcional (`O{}`) | vacío | Label para `\ref{}`. Usar prefijo `tab:`, e.g., `tab:resultados` |
| `csvfile` | **Obligatorio** (`m`) | — | Path al archivo CSV, relativo a la raíz del documento |
| `caption` | Opcional (`O{}`) | vacío | Texto del pie de tabla |

**Uso correcto:**
```latex
\myTable[tab:integradores]{data/comparacion_integradores.csv}[Comparación de integradores para la métrica de Kerr.]
\myTable{data/resultados.csv}   % Mínimo: solo el csvfile
```

**Errores comunes:**
- Label sin prefijo `tab:` — viola la convención del proyecto
- Archivo CSV con rutas absolutas — usar rutas relativas

---

---

## `\begin{definicion}`, `\begin{teorema}`, `\begin{observacion}` — Entornos formales

```latex
\begin{definicion}[Nombre de la definición]{def:label}
    Contenido...
\end{definicion}

\begin{teorema}[Nombre del teorema]{thm:label}
    Enunciado...
\end{teorema}

\begin{observacion}[Título opcional]{obs:label}
    Texto...
\end{observacion}
```

| Argumento | Tipo | Descripción |
|-----------|------|-------------|
| `[Nombre]` | Opcional | Nombre del entorno que aparece en el título de la caja |
| `{label}` | **Obligatorio** | Label para `\ref{}`. Usar prefijo `def:`, `thm:`, `obs:` |

**Nota**: Estos entornos comparten contador (`formalcounter`), numerado por sección (e.g., Def. 2.1, Teo. 2.2).

**Errores comunes:**
- Omitir el argumento de label `{}` — el segundo argumento es **obligatorio** en `newtcbtheorem`
- Usar prefijo incorrecto: `def:` para definiciones, `thm:` para teoremas, `obs:` para observaciones

---

## Convenciones de Labels

| Tipo | Prefijo | Ejemplo |
|------|---------|---------|
| Ecuación | `eq:` | `eq:geodesica_kerr` |
| Figura | `fig:` | `fig:carter_error` |
| Tabla | `tab:` | `tab:comparacion_integradores` |
| Sección | `sec:` | `sec:marco_teorico` |
