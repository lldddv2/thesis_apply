# Memoria de investigación de la tesis

Antes de investigar o responder preguntas sobre bibliografía, observaciones, valores, papers o
datos, leer `brain/README.md` y buscar en `brain/index.json`. Esa es la base de
conocimiento canónica. `cowork/investigaciones/`, `papers/` y `articulos/` son material legado
o de apoyo y no se consideran verificados por defecto.

## Reglas obligatorias

- Buscar primero en la base local. Si es insuficiente, consultar fuentes reales y registrar el
  resultado en `brain/` antes de terminar.
- Priorizar papers originales, DOI/arXiv, editores y repositorios de datos oficiales. Un
  buscador o agregador solo descubre fuentes; no respalda por sí solo afirmaciones técnicas.
- No inventar fuentes, identificadores, enlaces, resultados ni datos. Declarar con claridad
  aquello que no se encontró o no se pudo comprobar.
- Cada afirmación reutilizable necesita un ID, fuente real y localizador exacto (página,
  sección, ecuación, tabla, figura o fila). Separar resultados reportados de inferencias propias.
- Mantener mediciones discrepantes por separado y conservar su contexto observacional.
- Guardar datos públicos en CSV con URL, fecha, checksum, columnas, unidades, transformaciones,
  licencia y limitaciones; separar `data/raw/` de `data/derived/`.
- Añadir cada registro a `brain/REVISIONES.md`. Las casillas y el estado
  `manual_review = verified` pertenecen al usuario: no marcarlos sin petición explícita.
- Al contestar desde la memoria, comunicar el estado de revisión manual y no presentar
  `pending` como verificado.

## Comandos

```bash
python scripts/brain.py new "Título" --question "Pregunta exacta"
python scripts/brain.py search "términos"
python scripts/brain.py reindex
python scripts/brain.py validate
```

Completar `record.json`, `answer.md`, `references.bib` y los datos aplicables. Ejecutar
`validate` al terminar. La validación estructural no sustituye la revisión científica humana.

Respetar también las convenciones de notebooks en `CLAUDE.md` y preservar cambios preexistentes
ajenos a la tarea.
