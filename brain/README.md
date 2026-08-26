# Base de conocimiento verificable

Este directorio guarda respuestas científicas reutilizables con trazabilidad a fuentes y
datos. Está pensado para lectura humana y para recuperación por modelos de lenguaje.

## Qué archivo cumple cada función

- `index.json`: catálogo compacto para localizar registros sin abrirlos todos.
- `REVISIONES.md`: lista global de revisiones manuales pendientes. Solo el usuario marca
  casillas.
- `{NNN}-{slug}/record.json`: metadatos estructurados, afirmaciones, fuentes y conjuntos de
  datos. Es la fuente de verdad legible por máquinas.
- `{NNN}-{slug}/answer.md`: explicación legible por humanos; cita los IDs de `record.json`.
- `{NNN}-{slug}/references.bib`: bibliografía BibTeX comprobada contra las fuentes.
- `{NNN}-{slug}/revision.md`: checklist de verificación humana del registro.
- `{NNN}-{slug}/data/`: CSV y metadatos asociados.

Los directorios `cowork/investigaciones/`, `papers/` y `articulos/` son anteriores a este
esquema. Pueden servir para descubrir material, pero su contenido no se considera verificado
hasta migrarlo a un registro con fuentes y localizadores.

## Flujo para una pregunta

1. Buscar en `index.json` y con `python scripts/brain.py search "consulta"`.
2. Si hay un registro pertinente, leer `record.json`, `answer.md` y su estado de revisión.
3. Si falta evidencia, crear un registro con `brain.py new` y buscar fuentes primarias.
4. Verificar identidad de cada fuente en DOI, editor, arXiv o repositorio oficial. Registrar
   la fecha de acceso y el URL directo.
5. Extraer cada resultado como una afirmación independiente. Una afirmación `supported` debe
   referenciar al menos una fuente y un localizador exacto.
6. Guardar los datos públicos disponibles siguiendo el protocolo de datos de abajo.
7. Redactar `answer.md`, dejando claras las limitaciones y los resultados no encontrados.
8. Añadir o conservar la tarea de revisión humana, ejecutar `validate` y reconstruir el índice.

## Jerarquía y verificación de fuentes

Para resultados científicos se prefiere, en este orden:

1. artículo original o material suplementario del editor;
2. preprint del mismo artículo (arXiv u otro repositorio institucional);
3. catálogo o repositorio oficial que publica los datos;
4. documentación técnica oficial;
5. artículo secundario, solo para contexto.

Google Scholar, OpenAlex, ADS, Semantic Scholar y resultados de búsqueda ayudan a encontrar
la fuente, pero no reemplazan la lectura del documento original. Una fuente con solo metadatos
comprobados usa `verification.content = "metadata_only"`; no puede respaldar detalles que no
aparezcan en esos metadatos.

No completar identificadores por intuición. Un DOI debe resolver al título esperado. Si solo
se conoce un arXiv ID, `doi` queda en `null`. Si el texto completo no está disponible, registrar
esa limitación; no reconstruir resultados desde memoria.

## Afirmaciones y citas

Cada objeto de `claims` usa un ID estable (`C001`, `C002`, ...). Campos clave:

- `statement`: afirmación autocontenida, con objeto, condición y contexto observacional.
- `kind`: `reported`, `derived` o `not_found`.
- `value` y `unit`: valor estructurado cuando exista; usar `null` para texto cualitativo.
- `source_ids`: fuentes que sostienen la afirmación.
- `evidence`: lista de pares fuente/localizador; ejemplos de localizador válidos son
  `p. 8, sec. 3.2`, `Table 2, row S2, column sigma_RA` o `machine-readable table, rows 14-27`.
- `status`: `supported`, `conflicting`, `not_found` o `unverified`.
- `confidence`: `high`, `medium` o `low`, con justificación en `notes` cuando no sea alta.

Una inferencia propia debe usar `kind = "derived"`, enumerar las afirmaciones o datasets de
entrada en `derived_from` y explicar la operación. Nunca mezclar precisión por medición,
incertidumbre estadística, dispersión residual, error sistemático y resolución instrumental.

## Datos CSV

Guardar archivos crudos en `data/raw/` y resultados transformados en `data/derived/`. Nunca
sobrescribir el archivo crudo. Cada elemento de `datasets` debe incluir:

- ruta relativa al registro y fuente(s) asociada(s);
- URL directa y fecha de descarga;
- procedencia: `downloaded`, `transcribed` o `derived`;
- SHA-256 del archivo;
- columnas, unidades y significado;
- transformaciones, filtros y limitaciones;
- licencia o términos de uso cuando estén disponibles.

Si la tabla solo aparece en un PDF, se puede transcribir a CSV, pero debe marcarse
`transcribed` y requiere revisión humana fila por fila. Si no se encuentra un dataset público,
registrar la búsqueda y decir que no se pudo obtener; no crear valores sintéticos para llenar
el hueco.

## Estados

`status` del registro:

- `in_progress`: investigación incompleta;
- `answerable`: evidencia suficiente para contestar, todavía puede estar pendiente de revisión;
- `inconclusive`: fuentes reales encontradas, pero no permiten responder con rigor;
- `not_found`: no se encontró evidencia o datos después de documentar la búsqueda;
- `superseded`: reemplazado por otro registro indicado en `related_records`.

`manual_review` es independiente: `pending`, `partial`, `verified` o `rejected`. Por defecto es
`pending` y solo cambia cuando el usuario lo indica explícitamente y marca las casillas.

## Comandos

Ejecutar desde la raíz de `thesis_apply`:

```bash
python scripts/brain.py new "Errores astrométricos de S2 y S301" \
  --question "¿Cuál es el error típico reportado para las observaciones astrométricas?"
python scripts/brain.py search "S2 astrometría"
python scripts/brain.py reindex
python scripts/brain.py validate
```

`new` solo crea la estructura vacía: no constituye una investigación ni prueba que exista la
información del título. `validate` comprueba forma y referencias internas, no la veracidad
física; por eso la revisión humana sigue siendo obligatoria.
