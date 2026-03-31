---
name: math
description: This skill should be used when the user asks to "revisar las matemáticas", "verifica la notación", "revisa las ecuaciones", "chequea los índices", "revisa la nomenclatura", or wants a mathematical review of a thesis file. Use this skill whenever a .tex or .md file from the thesis needs mathematical verification, even if the user doesn't say "math" explicitly.
---

# Revisión Matemática

Revisar el contenido matemático de un archivo de tesis de relatividad general. Verificar notación tensorial, índices, ecuaciones y consistencia con la nomenclatura del proyecto.

## Preparación

Antes de revisar el archivo objetivo, leer:

1. `manuscrito/docs/general/nomenclatura.tex` — convenciones de notación (referencia de verdad)
2. `references/definiciones.md` — criterios para definiciones matemáticas correctas (leer si el archivo contiene entornos `definicion` o `teorema`)

## Proceso de Revisión

Leer el archivo indicado por el usuario y generar un reporte estructurado con los siguientes apartados:

### [NOTACIÓN]

Verificar consistencia con `nomenclatura.tex`:
- Tensores contravariantes con superíndice ($A^\mu$), covariantes con subíndice ($A_\mu$)
- Tensores mixtos con separación correcta entre superíndices y subíndices (e.g., `${A^\mu}_\nu$`)
- Índices griegos recorren 0–3 (coordenadas espacio-temporales)
- Índices latinos recorren 1–3 (coordenadas espaciales únicamente)
- Notación compacta de derivadas si se usa (e.g., $A^{\mu,\nu}$, ${A^\mu}_{,\nu}$)

### [ÍNDICES — Convención de Einstein]

Verificar reglas de sumación implícita:
- No más de dos índices repetidos por término (reportar violaciones con número de línea)
- Índices repetidos deben ser uno covariante y uno contravariante (uno arriba, uno abajo)
- Índices libres deben ser los mismos en cada término de una igualdad

Ejemplo de error: $A^\mu B_\mu C^\mu$ — tres índices $\mu$ en un término (inválido).

### [ECUACIONES]

- Consistencia dimensional/física de las ecuaciones presentadas
- Las referencias `\ref{eq:...}` (archivos .tex) apuntan a labels que existen
- Los labels `\label{eq:...}` son descriptivos y no se repiten
- Coherencia matemática entre ecuaciones relacionadas

### [ERRORES ENCONTRADOS]

Lista numerada de errores concretos. Para cada uno:
- Número de línea o ubicación aproximada
- Descripción del error
- Corrección sugerida

Si no hay errores: escribir "Sin errores matemáticos encontrados."

### [DEFINICIONES Y TEOREMAS]

Para cada entorno `\begin{definicion}` o `\begin{teorema}` en el archivo, aplicar el checklist de `references/definiciones.md`:
- Req. 1 — nombre preciso en `[...]` y en cursiva en el texto
- Req. 2 — contexto/espacio establecido antes de la condición
- Req. 3 — condición caracterizadora precisa y verificable matemáticamente
- Req. 4 — notación consistente con `nomenclatura.tex`
- Req. 5 — existencia no vacía (si no es obvia)
- Req. 6 — unicidad mencionada si aplica

Para cada requisito incumplido, insertar en el texto: `[ADVERTENCIA: Req. N — descripción]`

Para `\begin{observacion}` solo verificar Req. 3 y Req. 4.

### [OBSERVACIONES]

Sugerencias menores o puntos de atención que no son errores pero vale la pena revisar. Mantener este apartado breve.

## Nivel de Rigurosidad

- **Archivos `.tex`** (en `manuscrito/`): revisión completa y estricta. Cada violación debe reportarse.
- **Archivos `.md`** (en `entries/`): revisión ligera. Enfocarse en ecuaciones inline y que la notación sea consistente; no penalizar estilo informal o uso coloquial del lenguaje matemático.
