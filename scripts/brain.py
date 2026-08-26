#!/usr/bin/env python3
"""Create, index, search and validate the thesis knowledge base.

Run from the thesis_apply repository:
    python scripts/brain.py new "Title" --question "Research question"
    python scripts/brain.py search "keywords"
    python scripts/brain.py reindex
    python scripts/brain.py validate

This script validates structure and internal traceability. It cannot validate scientific truth.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BRAIN_DIR = ROOT / "brain"
INDEX_FILE = BRAIN_DIR / "index.json"
REVIEWS_FILE = BRAIN_DIR / "REVISIONES.md"
RECORD_ID_RE = re.compile(r"^INF-(\d{3,})$")
RECORD_DIR_RE = re.compile(r"^(\d{3,})-[a-z0-9-]+$")
CLAIM_ID_RE = re.compile(r"^C\d{3,}$")
SOURCE_ID_RE = re.compile(r"^S\d{3,}$")
DATASET_ID_RE = re.compile(r"^D\d{3,}$")

RECORD_STATUSES = {"in_progress", "answerable", "inconclusive", "not_found", "superseded"}
REVIEW_STATUSES = {"pending", "partial", "verified", "rejected"}
CLAIM_STATUSES = {"supported", "conflicting", "not_found", "unverified"}
CLAIM_KINDS = {"reported", "derived", "not_found"}
CONFIDENCE_LEVELS = {"high", "medium", "low"}
SOURCE_TYPES = {"paper", "dataset", "catalog", "documentation", "other"}
IDENTITY_STATUSES = {"verified", "unverified"}
CONTENT_STATUSES = {"primary_source_checked", "metadata_only", "unavailable"}
PROVENANCE_TYPES = {"downloaded", "transcribed", "derived"}


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return data


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def slugify(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii").lower()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text).strip("-")
    return slug or "sin-titulo"


def normalize_search_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text.lower())
    return "".join(character for character in normalized if not unicodedata.combining(character))


def record_directories() -> list[Path]:
    return sorted(
        path
        for path in BRAIN_DIR.iterdir()
        if path.is_dir() and RECORD_DIR_RE.fullmatch(path.name)
    )


def next_number() -> int:
    numbers = [int(path.name.split("-", 1)[0]) for path in record_directories()]
    return max(numbers, default=0) + 1


def record_index_item(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": record["id"],
        "slug": record["slug"],
        "title": record["title"],
        "question": record["question"],
        "status": record["status"],
        "manual_review": record["manual_review"],
        "updated_at": record["updated_at"],
        "tags": record["tags"],
        "answer_summary": record["answer_summary"],
    }


def collect_records() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for directory in record_directories():
        path = directory / "record.json"
        if path.exists():
            records.append(read_json(path))
    return sorted(records, key=lambda item: item.get("id", ""))


def rebuild_index(*, quiet: bool = False) -> None:
    records = collect_records()
    index = {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "records": [record_index_item(record) for record in records],
    }
    write_json(INDEX_FILE, index)
    if not quiet:
        print(f"Indexed {len(records)} record(s) in {INDEX_FILE.relative_to(ROOT)}")


def append_review_task(record_id: str, slug: str, title: str) -> None:
    text = REVIEWS_FILE.read_text(encoding="utf-8")
    text = text.replace("Todavía no hay registros.\n", "")
    marker = f"- [ ] [{record_id}]({slug}/revision.md) — {title}"
    if marker not in text:
        insertion_point = "<!-- registros:fin -->"
        if insertion_point in text:
            text = text.replace(insertion_point, marker + "\n\n" + insertion_point, 1)
        else:
            if not text.endswith("\n"):
                text += "\n"
            text += marker + "\n"
    REVIEWS_FILE.write_text(text, encoding="utf-8")


def create_record(args: argparse.Namespace) -> None:
    number = next_number()
    prefix = f"{number:03d}"
    title_slug = slugify(args.title)
    slug = f"{prefix}-{title_slug}"
    record_id = f"INF-{prefix}"
    directory = BRAIN_DIR / slug
    if directory.exists():
        raise FileExistsError(f"Record directory already exists: {directory}")

    today = date.today().isoformat()
    tags = sorted({tag.strip().lower() for tag in args.tags.split(",") if tag.strip()})
    record = {
        "schema_version": "1.0",
        "id": record_id,
        "slug": slug,
        "title": args.title.strip(),
        "question": args.question.strip(),
        "created_at": today,
        "updated_at": today,
        "status": "in_progress",
        "manual_review": "pending",
        "tags": tags,
        "answer_summary": "",
        "claims": [],
        "sources": [],
        "datasets": [],
        "limitations": [],
        "open_questions": [],
        "related_records": [],
    }

    (directory / "data" / "raw").mkdir(parents=True)
    (directory / "data" / "derived").mkdir(parents=True)
    write_json(directory / "record.json", record)

    answer = f"""# {args.title.strip()}

> **Registro:** {record_id}
>
> **Estado científico:** `in_progress`
>
> **Revisión manual:** `pending`
>
> **Pregunta:** {args.question.strip()}

## Respuesta breve

Investigación pendiente. No citar este registro como una respuesta establecida todavía.

## Alcance y definiciones

- Definir aquí el observable, población, instrumento, época y significado de “típico”.

## Hallazgos

Cada párrafo factual debe terminar con los IDs de las afirmaciones y fuentes correspondientes,
por ejemplo: `[C001; S001]`.

## Datos disponibles

Indicar qué datos se localizaron, cuáles se guardaron y cuáles no están disponibles públicamente.

## Limitaciones y desacuerdos

- Pendiente.

## Cómo se buscó

- Registrar consultas, bases consultadas, filtros y fecha.
"""
    (directory / "answer.md").write_text(answer, encoding="utf-8")

    review = f"""# Revisión manual — {record_id}

Estas casillas son para el usuario. Un agente puede añadir observaciones o nuevas tareas, pero
no debe marcar ninguna casilla sin una instrucción explícita del usuario.

- [ ] Verifiqué que cada fuente existe y que título, autores, año, DOI/arXiv y URL corresponden.
- [ ] Abrí las fuentes primarias y comprobé los localizadores de todas las afirmaciones.
- [ ] Revisé los valores numéricos, incertidumbres, unidades y el significado del observable.
- [ ] Comparé los CSV con la fuente original y revisé las transformaciones, si hay datos.
- [ ] Revisé que desacuerdos, resultados no encontrados y limitaciones estén expresados.
- [ ] La respuesta breve representa fielmente la evidencia registrada.
- [ ] Revisión completa; autorizo cambiar `manual_review` a `verified`.

## Observaciones del usuario

- Añade aquí tus observaciones durante la revisión.
"""
    (directory / "revision.md").write_text(review, encoding="utf-8")

    data_readme = """# Datos del registro

- `raw/`: archivos descargados o transcritos sin transformaciones analíticas posteriores.
- `derived/`: archivos creados mediante filtros, conversiones o cálculos documentados.

Todo CSV debe aparecer en `../record.json` con URL de origen, fecha, SHA-256, columnas,
unidades, transformaciones, licencia y limitaciones. No sobrescribir los datos crudos.
"""
    (directory / "data" / "README.md").write_text(data_readme, encoding="utf-8")
    (directory / "references.bib").write_text(
        "% Bibliografía verificada del registro. No añadir entradas sin comprobar su identidad.\n",
        encoding="utf-8",
    )

    append_review_task(record_id, slug, args.title.strip())
    rebuild_index(quiet=True)
    print(f"Created {record_id} at {directory.relative_to(ROOT)}")
    print("The record is empty and pending research; it does not establish any scientific claim.")


def require_fields(obj: dict[str, Any], fields: set[str], context: str, errors: list[str]) -> None:
    missing = sorted(fields - obj.keys())
    if missing:
        errors.append(f"{context}: missing fields: {', '.join(missing)}")


def check_unique_ids(items: Any, pattern: re.Pattern[str], context: str, errors: list[str]) -> set[str]:
    if not isinstance(items, list):
        errors.append(f"{context}: expected a list")
        return set()
    ids: list[str] = []
    for position, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            errors.append(f"{context}[{position}]: expected an object")
            continue
        item_id = item.get("id")
        if not isinstance(item_id, str) or not pattern.fullmatch(item_id):
            errors.append(f"{context}[{position}]: invalid id {item_id!r}")
            continue
        ids.append(item_id)
    duplicates = sorted({item_id for item_id in ids if ids.count(item_id) > 1})
    if duplicates:
        errors.append(f"{context}: duplicate ids: {', '.join(duplicates)}")
    return set(ids)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_record(directory: Path, errors: list[str]) -> dict[str, Any] | None:
    record_path = directory / "record.json"
    context = str(record_path.relative_to(ROOT))
    try:
        record = read_json(record_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"{context}: cannot read JSON: {exc}")
        return None

    required = {
        "schema_version", "id", "slug", "title", "question", "created_at", "updated_at",
        "status", "manual_review", "tags", "answer_summary", "claims", "sources", "datasets",
        "limitations", "open_questions", "related_records",
    }
    require_fields(record, required, context, errors)
    if record.get("schema_version") != "1.0":
        errors.append(f"{context}: schema_version must be '1.0'")
    if record.get("slug") != directory.name:
        errors.append(f"{context}: slug must match directory name {directory.name!r}")
    match = RECORD_ID_RE.fullmatch(str(record.get("id", "")))
    if not match or match.group(1) != directory.name.split("-", 1)[0]:
        errors.append(f"{context}: id must match the directory numeric prefix")
    if record.get("status") not in RECORD_STATUSES:
        errors.append(f"{context}: invalid status {record.get('status')!r}")
    if record.get("manual_review") not in REVIEW_STATUSES:
        errors.append(f"{context}: invalid manual_review {record.get('manual_review')!r}")
    if not isinstance(record.get("title"), str) or not record.get("title", "").strip():
        errors.append(f"{context}: title must be non-empty")
    if not isinstance(record.get("question"), str) or not record.get("question", "").strip():
        errors.append(f"{context}: question must be non-empty")
    for field in ("tags", "limitations", "open_questions", "related_records"):
        if not isinstance(record.get(field), list):
            errors.append(f"{context}: {field} must be a list")

    source_ids = check_unique_ids(record.get("sources"), SOURCE_ID_RE, f"{context}.sources", errors)
    claim_ids = check_unique_ids(record.get("claims"), CLAIM_ID_RE, f"{context}.claims", errors)
    check_unique_ids(record.get("datasets"), DATASET_ID_RE, f"{context}.datasets", errors)
    source_by_id = {
        source.get("id"): source
        for source in record.get("sources", [])
        if isinstance(source, dict) and isinstance(source.get("id"), str)
    }

    source_required = {
        "id", "type", "title", "authors", "year", "doi", "arxiv", "url", "publisher",
        "accessed_at", "verification", "local_copy", "notes",
    }
    for source in record.get("sources", []):
        if not isinstance(source, dict):
            continue
        source_context = f"{context}.sources.{source.get('id', '?')}"
        require_fields(source, source_required, source_context, errors)
        if source.get("type") not in SOURCE_TYPES:
            errors.append(f"{source_context}: invalid type {source.get('type')!r}")
        if not isinstance(source.get("title"), str) or not source.get("title", "").strip():
            errors.append(f"{source_context}: title must be non-empty")
        if not isinstance(source.get("authors"), list):
            errors.append(f"{source_context}: authors must be a list")
        if not isinstance(source.get("url"), str) or not source.get("url", "").startswith(("https://", "http://")):
            errors.append(f"{source_context}: url must be an absolute HTTP(S) URL")
        verification = source.get("verification")
        if not isinstance(verification, dict):
            errors.append(f"{source_context}: verification must be an object")
        else:
            if verification.get("identity") not in IDENTITY_STATUSES:
                errors.append(f"{source_context}: invalid verification.identity")
            if verification.get("content") not in CONTENT_STATUSES:
                errors.append(f"{source_context}: invalid verification.content")

    claim_required = {
        "id", "statement", "kind", "value", "unit", "scope", "status", "confidence",
        "source_ids", "evidence", "derived_from", "notes",
    }
    for claim in record.get("claims", []):
        if not isinstance(claim, dict):
            continue
        claim_context = f"{context}.claims.{claim.get('id', '?')}"
        require_fields(claim, claim_required, claim_context, errors)
        if claim.get("kind") not in CLAIM_KINDS:
            errors.append(f"{claim_context}: invalid kind {claim.get('kind')!r}")
        if claim.get("status") not in CLAIM_STATUSES:
            errors.append(f"{claim_context}: invalid status {claim.get('status')!r}")
        if claim.get("confidence") not in CONFIDENCE_LEVELS:
            errors.append(f"{claim_context}: invalid confidence {claim.get('confidence')!r}")
        if not isinstance(claim.get("statement"), str) or not claim.get("statement", "").strip():
            errors.append(f"{claim_context}: statement must be non-empty")
        cited = claim.get("source_ids")
        if not isinstance(cited, list):
            errors.append(f"{claim_context}: source_ids must be a list")
            cited = []
        invalid_citations = [item for item in cited if not isinstance(item, str)]
        if invalid_citations:
            errors.append(f"{claim_context}: every source_id must be a string")
        cited_ids = [item for item in cited if isinstance(item, str)]
        unknown_sources = sorted(set(cited_ids) - source_ids)
        if unknown_sources:
            errors.append(f"{claim_context}: unknown source_ids: {', '.join(unknown_sources)}")
        evidence = claim.get("evidence")
        if not isinstance(evidence, list):
            errors.append(f"{claim_context}: evidence must be a list")
            evidence = []
        for position, item in enumerate(evidence, start=1):
            if not isinstance(item, dict):
                errors.append(f"{claim_context}.evidence[{position}]: expected an object")
                continue
            evidence_source = item.get("source_id")
            if not isinstance(evidence_source, str) or evidence_source not in source_ids:
                errors.append(f"{claim_context}.evidence[{position}]: unknown source_id")
            if not isinstance(item.get("locator"), str) or not item.get("locator", "").strip():
                errors.append(f"{claim_context}.evidence[{position}]: locator must be non-empty")
        if claim.get("status") in {"supported", "conflicting"} and (not cited or not evidence):
            errors.append(f"{claim_context}: supported/conflicting claims require sources and evidence")
        if claim.get("status") in {"supported", "conflicting"}:
            unchecked_sources = sorted(
                source_id
                for source_id in cited_ids
                if not isinstance(source_by_id.get(source_id, {}).get("verification"), dict)
                or source_by_id[source_id]["verification"].get("content") != "primary_source_checked"
            )
            if unchecked_sources:
                errors.append(
                    f"{claim_context}: scientific claims require primary_source_checked; "
                    f"not checked: {', '.join(unchecked_sources)}"
                )
        if claim.get("kind") == "derived":
            derived_from = claim.get("derived_from")
            if not isinstance(derived_from, list) or not derived_from:
                errors.append(f"{claim_context}: derived claims require derived_from")
            elif any(not isinstance(item, str) for item in derived_from):
                errors.append(f"{claim_context}: every derived_from id must be a string")
            else:
                dataset_ids = {
                    item.get("id")
                    for item in record.get("datasets", [])
                    if isinstance(item, dict) and isinstance(item.get("id"), str)
                }
                if unknown := sorted(set(derived_from) - claim_ids - dataset_ids):
                    errors.append(f"{claim_context}: unknown derived_from ids: {', '.join(unknown)}")

    dataset_required = {
        "id", "path", "format", "provenance", "source_ids", "source_url", "downloaded_at",
        "sha256", "columns", "transformations", "license", "limitations",
    }
    for dataset in record.get("datasets", []):
        if not isinstance(dataset, dict):
            continue
        dataset_context = f"{context}.datasets.{dataset.get('id', '?')}"
        require_fields(dataset, dataset_required, dataset_context, errors)
        relative_path = dataset.get("path")
        if not isinstance(relative_path, str) or not re.fullmatch(r"data/(raw|derived)/.+\.csv", relative_path):
            errors.append(f"{dataset_context}: path must be data/raw/*.csv or data/derived/*.csv")
            continue
        csv_path = directory / relative_path
        if not csv_path.is_file():
            errors.append(f"{dataset_context}: missing file {relative_path}")
        expected_hash = dataset.get("sha256")
        if not isinstance(expected_hash, str) or not re.fullmatch(r"[a-f0-9]{64}", expected_hash):
            errors.append(f"{dataset_context}: sha256 must contain 64 lowercase hexadecimal characters")
        elif csv_path.is_file() and sha256(csv_path) != expected_hash:
            errors.append(f"{dataset_context}: sha256 does not match {relative_path}")
        if dataset.get("format") != "csv":
            errors.append(f"{dataset_context}: format must be 'csv'")
        if dataset.get("provenance") not in PROVENANCE_TYPES:
            errors.append(f"{dataset_context}: invalid provenance")
        dataset_sources = dataset.get("source_ids")
        if not isinstance(dataset_sources, list) or not dataset_sources:
            errors.append(f"{dataset_context}: source_ids must be a non-empty list")
        elif any(not isinstance(item, str) for item in dataset_sources):
            errors.append(f"{dataset_context}: every source_id must be a string")
        elif unknown_sources := sorted(set(dataset_sources) - source_ids):
            errors.append(f"{dataset_context}: unknown source_ids: {', '.join(unknown_sources)}")
        if not isinstance(dataset.get("columns"), list) or not dataset.get("columns"):
            errors.append(f"{dataset_context}: columns must be a non-empty list")

    for required_file in ("answer.md", "references.bib", "revision.md", "data/README.md"):
        if not (directory / required_file).is_file():
            errors.append(f"{context}: missing companion file {required_file}")

    if record.get("manual_review") == "verified":
        review_path = directory / "revision.md"
        if review_path.is_file():
            review_text = review_path.read_text(encoding="utf-8")
            approval = "- [x] Revisión completa; autorizo cambiar `manual_review` a `verified`."
            if approval not in review_text:
                errors.append(f"{context}: manual_review is verified without the user's final checkbox")

    return record


def validate_all(_: argparse.Namespace) -> None:
    errors: list[str] = []
    records: list[dict[str, Any]] = []
    for directory in record_directories():
        record = validate_record(directory, errors)
        if record is not None:
            records.append(record)

    try:
        index = read_json(INDEX_FILE)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"brain/index.json: cannot read: {exc}")
        index = {}
    indexed_items = index.get("records", [])
    expected_items = [record_index_item(record) for record in sorted(records, key=lambda item: item.get("id", ""))]
    if indexed_items != expected_items:
        errors.append("brain/index.json is stale; run: python scripts/brain.py reindex")

    review_text = REVIEWS_FILE.read_text(encoding="utf-8") if REVIEWS_FILE.exists() else ""
    for record in records:
        marker = f"[{record.get('id')}]({record.get('slug')}/revision.md)"
        if marker not in review_text:
            errors.append(f"brain/REVISIONES.md: missing task for {record.get('id')}")

    if errors:
        print(f"Validation failed with {len(errors)} error(s):", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        raise SystemExit(1)
    print(f"Validation passed for {len(records)} record(s).")
    print("Structural validation does not replace manual scientific review.")


def search_records(args: argparse.Namespace) -> None:
    terms = [term for term in re.split(r"\s+", normalize_search_text(args.query).strip()) if term]
    results: list[tuple[int, dict[str, Any]]] = []
    for record in collect_records():
        haystack = normalize_search_text(json.dumps(record, ensure_ascii=False))
        score = sum(haystack.count(term) for term in terms)
        if score:
            results.append((score, record))
    results.sort(key=lambda item: (-item[0], item[1].get("id", "")))

    if not results:
        print("No matching local records. This does not prove the information does not exist.")
        return
    for _, record in results:
        summary = record.get("answer_summary") or "(sin resumen todavía)"
        print(
            f"{record['id']} | {record['title']} | status={record['status']} | "
            f"manual_review={record['manual_review']}\n  {record['slug']}/answer.md\n  {summary}"
        )


def reindex_command(_: argparse.Namespace) -> None:
    rebuild_index()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    new_parser = subparsers.add_parser("new", help="create an empty research record")
    new_parser.add_argument("title", help="record title")
    new_parser.add_argument("--question", required=True, help="exact research question")
    new_parser.add_argument("--tags", default="", help="comma-separated retrieval tags")
    new_parser.set_defaults(func=create_record)

    search_parser = subparsers.add_parser("search", help="search records locally")
    search_parser.add_argument("query", help="keywords")
    search_parser.set_defaults(func=search_records)

    reindex_parser = subparsers.add_parser("reindex", help="rebuild index.json")
    reindex_parser.set_defaults(func=reindex_command)

    validate_parser = subparsers.add_parser("validate", help="validate records and traceability")
    validate_parser.set_defaults(func=validate_all)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
