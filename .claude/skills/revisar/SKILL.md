---
name: revisar
description: This skill should be used when the user asks to "revisar el archivo", "haz una revisión completa", "revisa lo que llevo", "chequea todo", "revisa este archivo de tesis", or wants a comprehensive review of a thesis file. This is the master review skill that runs all specialized checks (math, coherencia, latex, claridad) in parallel and produces a consolidated report. Use this skill as the default review command for any thesis file.
---

# Revisión Completa de Archivo de Tesis

Ejecutar todos los agentes de revisión especializados sobre un archivo y presentar un reporte consolidado.

## Determinar el tipo de archivo

Antes de lanzar los agentes, identificar el tipo de archivo:

- **Archivo `.tex`** (en `manuscrito/`): ejecutar los 4 agentes — math, coherencia, latex, claridad
- **Archivo `.md`** (en `entries/`): ejecutar 3 agentes — math (ligero), coherencia, claridad. **Omitir latex.**

## Ejecución en paralelo

Lanzar los agentes correspondientes **en paralelo** usando el Agent tool (subagent_type: `general-purpose`). Para cada agente:
1. Leer el archivo de instrucciones del agente correspondiente (ver abajo)
2. Pasar como prompt: el contenido del archivo de agente + el path completo del archivo a revisar
3. Indicar el nivel de rigurosidad según el tipo de archivo

Archivos de agente (leer antes de lanzar cada uno):
- `.claude/skills/revisar/agents/math-reviewer.md` — revisión matemática
- `.claude/skills/revisar/agents/coherencia-reviewer.md` — revisión de estilo
- `.claude/skills/revisar/agents/latex-reviewer.md` — revisión LaTeX (solo .tex)
- `.claude/skills/revisar/agents/claridad-reviewer.md` — revisión de claridad

## Reporte Consolidado

Una vez que todos los agentes terminan, presentar un reporte unificado con esta estructura:

---

# Reporte de Revisión: `[nombre del archivo]`

## Resumen Ejecutivo
Una o dos oraciones sobre el estado general del archivo. ¿Está listo para continuar? ¿Hay problemas críticos?

## Errores Críticos
Lista de errores que deben corregirse antes de continuar (errores matemáticos, LaTeX que no compila, etc.).
Si no hay: "Sin errores críticos."

## Observaciones por Área

### Matemáticas
[Resultado del agente math — condensado]

### Estilo y Coherencia
[Resultado del agente coherencia — condensado]

### Formato LaTeX *(solo archivos .tex)*
[Resultado del agente latex — condensado]

### Claridad
[Resultado del agente claridad — condensado]

## Recomendaciones Prioritarias
Lista ordenada de las 3-5 cosas más importantes a atender, con justificación breve.

---

Mantener el reporte conciso. Si un área no tiene observaciones, indicarlo brevemente en lugar de omitirla.
