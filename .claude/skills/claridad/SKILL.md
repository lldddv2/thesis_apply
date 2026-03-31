---
name: claridad
description: This skill should be used when the user asks to "revisar la claridad", "verifica que se entienda", "chequea la redacción", "revisa el planteamiento", "verifica el tono académico", "revisa si el texto es claro", or wants a clarity and academic writing review of a thesis file. Use this skill for both .tex manuscript files and .md entry files to ensure the writing is clear and appropriate for a thesis.
---

# Revisión de Claridad Académica

Verificar que el contenido sea claro para el lector y tenga el estilo adecuado para una tesis de física.

## Proceso de Revisión

Leer el archivo indicado y generar un reporte con los siguientes apartados:

### [ESTRUCTURA ARGUMENTATIVA]

Verificar que el texto sigue una estructura lógica:
- ¿Hay una motivación o contexto antes de presentar resultados?
- ¿Los argumentos se encadenan de forma coherente (hipótesis → desarrollo → conclusión)?
- ¿Las secciones fluyen naturalmente entre sí?

### [FIGURAS Y ECUACIONES]

- Toda figura debe ser introducida en el texto *antes* de aparecer, con una referencia explícita (e.g., "como se muestra en la figura X")
- Toda ecuación debe tener contexto: qué representa, de dónde viene, o qué significa
- Los resultados numéricos o gráficos deben tener una interpretación explícita en el texto

### [TONO Y ESTILO]

Para archivos `.tex` (manuscrito):
- ¿El tono es académico y formal?
- ¿Se evita el lenguaje coloquial o impreciso?
- ¿Las afirmaciones están respaldadas o justificadas?
- ¿Se usa la voz pasiva o impersonal de forma consistente?

Para archivos `.md` (entries):
- ¿El planteamiento es comprensible para alguien con contexto del proyecto?
- ¿Los resultados tienen al menos una oración de interpretación?
- Tono informal es aceptable; solo reportar si algo es confuso.

### [CLARIDAD DE CONCEPTOS]

- ¿Los conceptos técnicos se introducen antes de usarse?
- ¿Hay términos que se usan sin definir y que el lector podría no conocer?
- ¿Las variables y símbolos están identificados cuando aparecen por primera vez?

### [OBSERVACIONES]

Sugerencias específicas para mejorar la claridad. Ser constructivo y concreto: indicar qué párrafo o sección mejorar y cómo.

### [PUNTOS POSITIVOS]

Breve mención de los aspectos del texto que están bien logrados. Esto ayuda a saber qué patrones mantener.

## Nivel de Rigurosidad

- **Archivos `.tex`** (manuscrito): revisión estricta de tono, estructura y completitud académica.
- **Archivos `.md`** (entries): revisión ligera. El objetivo es que el planteamiento sea comprensible y los resultados tengan interpretación. No exigir formalidad académica.

## Principio de No Intervención

Identificar problemas y sugerir correcciones mínimas. No reescribir párrafos enteros ni alterar la voz del autor. Las sugerencias deben ser puntuales y preservar el estilo original.
