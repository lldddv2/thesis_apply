---
name: latex
description: This skill should be used when the user asks to "revisar el LaTeX", "verifica el formato latex", "chequea la compilación", "revisa las referencias bibliográficas", "verifica los labels", "busca errores de compilación", or wants a LaTeX syntax and structure review of a .tex file. Use this skill for any .tex file that needs to be verified before compilation.
---

# Revisión de Formato LaTeX

Verificar que un archivo `.tex` tenga formato correcto y no presente errores que impidan su compilación.

> Esta skill aplica únicamente a archivos `.tex`. Para archivos `.md`, no ejecutar esta skill.

## Preparación

Para verificar referencias bibliográficas, leer:

```
manuscrito/docs/bibliografia.bib
```

Para verificar cross-references entre archivos, también leer los demás archivos `.tex` en `manuscrito/docs/` según sea necesario.

## Proceso de Revisión

Leer el archivo `.tex` indicado y generar un reporte con los siguientes apartados:

### [SINTAXIS]

Verificar sintaxis LaTeX básica:
- Entornos abiertos que no se cierran (e.g., `\begin{equation}` sin `\end{equation}`)
- Comandos mal escritos o con argumentos faltantes
- Llaves `{}` desbalanceadas
- Uso de `$...$` vs `\(...\)` — consistencia dentro del archivo
- Caracteres especiales sin escapar (e.g., `%`, `&`, `#` fuera de contextos apropiados)

### [BIBLIOGRAFÍA]

Para cada `\cite{key}` en el archivo:
- Verificar que `key` existe en `bibliografia.bib`
- Reportar cites con keys inexistentes

### [LABELS Y REFERENCIAS]

- Verificar que cada `\ref{label}` o `\eqref{label}` corresponde a un `\label{label}` existente (en este u otros archivos del manuscrito)
- Verificar que no hay `\label{...}` duplicados
- Verificar que los labels siguen un patrón consistente (e.g., `eq:nombre`, `fig:nombre`, `sec:nombre`)

### [COMANDOS PROPIOS]

Leer `references/comandos-propios.md` para conocer la firma exacta de `\myFigure` y `\myTable`.
Verificar que:
- Se usen con los argumentos en el orden correcto
- Los labels sigan la convención del proyecto (`fig:`, `tab:`, `eq:`, `sec:`)

### [POSIBLES ERRORES DE COMPILACIÓN]

Listar cualquier construcción que probablemente cause error o warning al compilar con `pdflatex` o `lualatex`. Incluir:
- Advertencias comunes (referencias indefinidas, labels duplicados)
- Errores que detienen la compilación

### [ERRORES ENCONTRADOS]

Lista numerada con número de línea, descripción y corrección sugerida.
Si no hay errores: "Sin errores LaTeX encontrados."
