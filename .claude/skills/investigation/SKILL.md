---
name: investigation
description: >
  Úsame cuando el usuario quiera investigar, buscar papers, localizar o descargar datos,
  registrar hallazgos, comprobar una afirmación científica o continuar una investigación.
  También se activa cuando el usuario proporciona un DOI, arXiv ID o título de artículo.
---

# Skill: investigación verificable

Gestiona investigaciones en la base canónica `brain/`. Antes de actuar, leer por completo
`brain/README.md`. Las investigaciones antiguas en `cowork/investigaciones/` son material
legado y no son evidencia verificada hasta migrarlas.

## Reglas no negociables

1. No inventar artículos, autores, identificadores, enlaces, resultados, errores ni datasets.
2. Para afirmaciones científicas usar la fuente primaria. Un buscador o agregador solo descubre
   fuentes; no sustituye el paper, suplemento o repositorio oficial.
3. Comprobar que DOI/arXiv/URL corresponden al título y autores registrados.
4. Cada afirmación reutilizable requiere `source_ids` y un localizador exacto dentro de la
   fuente. Si el texto completo no se pudo abrir, no atribuirle resultados técnicos.
5. Separar `reported` (reportado), `derived` (cálculo propio) y `not_found` (no localizado).
6. Mantener resultados discrepantes por separado, con su contexto observacional.
7. Nunca marcar casillas de `revision.md` o `REVISIONES.md`, ni cambiar `manual_review` a
   `verified`, salvo instrucción explícita del usuario después de su revisión.

## Nueva investigación

Desde la raíz de `thesis_apply`:

```bash
python scripts/brain.py new "Título descriptivo" \
  --question "Pregunta exacta que debe responderse" \
  --tags "palabra clave,otra palabra"
```

El comando crea un registro vacío. No implica que la respuesta o los datos existan.

Después:

1. Definir el alcance: observable, objeto, instrumento, periodo, convención y significado de
   términos ambiguos como “error típico”, “precisión” o “reciente”.
2. Buscar en fuentes primarias y registrar también las consultas, bases y filtros en
   `answer.md`.
3. Completar `sources` en `record.json`, incluyendo fecha de acceso y estado de verificación.
4. Crear una afirmación por resultado, con ID `C001`, `C002`, etc.; incluir fuente y localizador.
5. Añadir entradas BibTeX comprobadas a `references.bib`.
6. Redactar una respuesta autocontenida en `answer.md`, citando IDs como `[C001; S001]` y
   explicando limitaciones, desacuerdos y resultados no encontrados.
7. Si existe un dataset público, seguir el protocolo de datos de abajo.
8. Establecer `status` en `answerable`, `inconclusive` o `not_found`, actualizar `updated_at` y
   `answer_summary`, sin alterar `manual_review`.
9. Ejecutar:

```bash
python scripts/brain.py reindex
python scripts/brain.py validate
```

## Datos públicos

- Descargar únicamente desde el editor, suplemento, repositorio institucional o catálogo
  oficial cuando sea posible.
- Guardar originales en `data/raw/` y transformaciones en `data/derived/`; no sobrescribir el
  original.
- Registrar cada CSV en `datasets` con procedencia (`downloaded`, `transcribed` o `derived`),
  fuentes, URL, fecha, SHA-256, columnas, unidades, transformaciones, licencia y limitaciones.
- Una tabla transcrita desde PDF debe decir `transcribed` y quedar pendiente de revisión fila a
  fila.
- Si no se obtiene un dataset público, documentar dónde se buscó y decirlo claramente. No crear
  datos sintéticos para cubrir la ausencia.

Calcular el checksum con:

```bash
sha256sum brain/NNN-slug/data/raw/archivo.csv
```

## Continuar o contestar desde la memoria

Buscar primero:

```bash
python scripts/brain.py search "términos de la pregunta"
```

Leer el `record.json` y `answer.md` pertinentes. Al contestar, declarar el estado de revisión
manual. Si el registro es insuficiente o la información puede haber cambiado, actualizarlo con
fuentes nuevas antes de responder. No presentar un registro `pending` como revisado.

## Migrar una investigación antigua

Usar el texto legado solo como lista de candidatos. Crear un registro nuevo, volver a abrir y
comprobar cada fuente, extraer localizadores y copiar únicamente las afirmaciones respaldadas.
No heredar automáticamente el estado de confianza ni la bibliografía del documento antiguo.
