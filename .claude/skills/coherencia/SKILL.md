---
name: coherencia
description: This skill should be used when the user asks to "revisar la coherencia", "verifica el estilo", "chequea las normas de estilo", "revisa el formato del texto", "verifica que el archivo siga las normas", or wants a style and coherence review of a thesis file. Use this skill whenever a file needs to be checked against the thesis style guidelines.
---

# Revisión de Coherencia y Estilo

Verificar que un archivo de la tesis cumpla con las normativas de estilo del proyecto.

## Preparación

Leer la guía de estilo del proyecto antes de revisar:

```
.claude/guia-de-estilo.md
```

Si la guía está vacía o incompleta, aplicar las normas base indicadas más abajo y notificar al usuario que la guía de estilo aún no ha sido completada.

## Normas Base (siempre aplicar)

Estas normas aplican independientemente de lo que diga la guía de estilo:

**Idioma y terminología:**
- Los archivos `.tex` deben estar en español (salvo comandos LaTeX y términos técnicos establecidos)
- No mezclar términos en inglés y español para el mismo concepto sin justificación
- Usar la terminología definida en el proyecto (e.g., "métrica de Kerr", no "Kerr metric" si se está redactando en español)

**Estructura:**
- Las secciones deben tener una introducción antes de presentar ecuaciones o resultados
- Los resultados deben tener una interpretación explícita en el texto
- No presentar figuras o tablas sin referirlas en el texto

**Consistencia interna:**
- Un mismo concepto o variable debe nombrarse igual a lo largo del documento
- No cambiar la notación a mitad de un archivo sin indicarlo explícitamente

**Indentación (4 espacios, no tabs):**
- El contenido dentro de entornos (`equation`, `align`, `figure`, `table`, `itemize`, `enumerate`, `definicion`, `teorema`, `observacion`) debe estar indentado un nivel
- `\begin{env}` y `\end{env}` al mismo nivel entre sí
- No usar tabs

## Proceso de Revisión

Generar un reporte con los siguientes apartados:

### [ESTILO SEGÚN GUÍA]

Verificar cada norma definida en `.claude/guia-de-estilo.md` y reportar incumplimientos.
Si la guía está vacía: indicar "Guía de estilo pendiente de completar — solo se aplicaron normas base."

### [NORMAS BASE]

Reportar incumplimientos de las normas base listadas arriba.

### [TERMINOLOGÍA]

Listar cualquier inconsistencia en el uso de términos o variables. Incluir el número de línea o sección.

### [ESTRUCTURA]

Comentar sobre la estructura del archivo: ¿hay introducción antes de contenido técnico? ¿los resultados están explicados? ¿las figuras/ecuaciones están referidas?

### [ERRORES ENCONTRADOS]

Lista numerada de incumplimientos concretos con ubicación y descripción.
Si no hay errores: "Sin incumplimientos de estilo encontrados."

## Nivel de Rigurosidad

- **Archivos `.tex`** (manuscrito): revisión estricta contra guía y normas base.
- **Archivos `.md`** (entries): revisión moderada. El tono informal es aceptable; verificar principalmente terminología consistente y que los resultados tengan interpretación.

## Principio de No Intervención

La revisión identifica incumplimientos y los reporta — **no reescribe el texto**. El estilo, la voz y las decisiones de redacción del autor deben preservarse. Si una corrección es necesaria, sugerir la mínima intervención que resuelva el problema sin alterar la voz del texto. No "mejorar" texto que ya cumple con las normas.
