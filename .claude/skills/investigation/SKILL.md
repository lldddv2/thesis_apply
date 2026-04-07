---
name: investigation
description: >
  Úsame cuando el usuario quiera iniciar una investigación, buscar papers, descargar artículos o registrar hallazgos.
  Frases que activan esta skill: "nueva investigación sobre", "investiga sobre", "busca papers de", "busca artículos de",
  "descarga el paper", "baja el artículo", "get the paper", "download paper", "obtén el PDF", "busca en openalex",
  "busca en consensus", "agrega artículo", "registra hallazgo", o cuando el usuario da un DOI (e.g. 10.1103/...).
  También activa cuando el usuario pide continuar o actualizar una investigación existente.
---

# Skill: Investigation

Gestiona el ciclo completo de una investigación: crear la carpeta, buscar papers, descargarlos y registrar los hallazgos en `main.md`.

---

## Entorno de ejecución

Esta skill funciona en dos contextos con capacidades distintas:

| Contexto | Búsqueda | Navegador |
|----------|----------|-----------|
| **Cowork** | OpenAlex API + Consensus (Chrome) | ✅ disponible |
| **Claude Code** | OpenAlex API (headless) | ❌ no disponible |

> **Consensus** usa autenticación de sesión interna — solo es accesible vía navegador cuando el usuario está logueado. En Claude Code usar exclusivamente OpenAlex.

---

## Pre-requisito: verificar `.venv`

```bash
ls .venv/bin/python3 2>/dev/null && echo "OK" || echo "NO_VENV"
```

Si no existe, notificar al usuario:
> "No se encontró `.venv/`. Créalo con `python3 -m venv .venv`."

Los scripts usan solo stdlib — siempre ejecutar con `.venv/bin/python3`.

---

## Modo 1 — Nueva investigación

Cuando el usuario quiere comenzar una investigación nueva.

### 1.1 Determinar el número siguiente

```bash
ls thesis_apply/cowork/investigaciones/ | grep -E '^[0-9]{3}-' | sort | tail -1
```

El siguiente número es el último + 1, formateado como `001`, `002`, etc.

### 1.2 Crear la carpeta

```
thesis_apply/cowork/investigaciones/{NNN}-{nombre-slugificado}/
├── main.md
└── papers/
```

El nombre se slugifica: minúsculas, espacios → guiones, sin acentos ni caracteres especiales.

### 1.3 Crear `main.md`

Usar esta plantilla exacta:

```markdown
# {Nombre de la investigación}

---
Fecha: {YYYY-MM-DD}
Tiempo de investigación: {estimado}
---

# Resumen

[Resumen de la investigación hecha]

# Desarrollo

## [{Artículo 1 — título}]

---
doi:
año de publicacion:
autor:
bib: |
  @article{,
    author  = {},
    title   = {},
    journal = {},
    year    = {},
    doi     = {}
  }
---

### Resultados de lo buscado

### Resumen

### Observaciones importantes

### Artículos de interés
```

### 1.4 Buscar papers iniciales

Proceder automáticamente al **Modo 2** para buscar los primeros papers relevantes.

---

## Modo 2 — Buscar papers

### Opción A: OpenAlex (siempre disponible)

```bash
# Básico
.venv/bin/python3 .claude/skills/paper/scripts/openalex_search.py "kerr geodesics orbital motion" -n 10

# Con filtros
.venv/bin/python3 .claude/skills/paper/scripts/openalex_search.py "stellar orbits galactic center" \
  -n 15 --year-from 2000 --year-to 2024 --json
```

Fallback directo a la API si el script no existe:

```
GET https://api.openalex.org/works?search={query}&per-page=10&mailto=thesis@example.com
```

Filtros útiles de OpenAlex:
- `filter=publication_year:>2000` — desde año
- `filter=open_access.is_oa:true` — solo open access
- `filter=cited_by_count:>10` — mínimo de citas
- `sort=cited_by_count:desc` — ordenar por citas

### Opción B: Consensus (solo Cowork con Chrome)

Consensus requiere sesión autenticada — los IDs de búsqueda son generados server-side y no se pueden construir con solo la query.

**Flujo en Cowork:**
1. Navegar a `https://consensus.app/`
2. Escribir la query en el buscador
3. Esperar a que carguen los resultados
4. Leer los papers del DOM o capturar la llamada a `api/pro_research/search/{id}/?page=0&size=20`
5. Extraer: título, autores, año, DOI, display_text

La API interna devuelve papers con esta estructura:
```json
{
  "papers": [{
    "title": "...",
    "doi": "10.xxxx/yyyy",
    "authors": ["..."],
    "year": 2020,
    "citation_count": 45,
    "display_text": "Resumen del paper...",
    "url_slug": "..."
  }]
}
```

> En Claude Code: omitir Consensus, usar solo OpenAlex.

### Después de buscar

Mostrar los resultados al usuario y preguntar cuáles quiere descargar o registrar. Si el usuario indica un paper (por número, DOI o título), pasar al **Modo 3** o **Modo 4**.

---

## Modo 3 — Descargar PDF

El input puede ser:
- DOI bare: `10.1103/PhysRevD.11.2042`
- URL doi.org: `https://doi.org/10.1103/...`

Guardar siempre en `{carpeta-investigacion}/papers/`. Nombre del archivo: `{apellido-primer-autor}{año}.pdf`.

```bash
.venv/bin/python3 .claude/skills/paper/scripts/download_paper.py "10.1103/PhysRevD.11.2042" \
  -o thesis_apply/cowork/investigaciones/{NNN}-nombre/papers/kerr1963.pdf
```

El script intenta en orden: **URL directa → Unpaywall → Sci-Hub** (mirrors: `.box`, `.se`, `.st`, `.ru`).

Confirmar al usuario: ruta del archivo, fuente, tamaño.

---

## Modo 4 — Registrar artículo en `main.md`

Cuando el usuario quiere agregar un artículo a la investigación activa (o a una investigación específica).

### 4.1 Identificar la investigación target

Si el usuario no especifica, usar la más reciente (último número en `investigaciones/`).

### 4.2 Agregar sección al `main.md`

Añadir al final del archivo (o después del último `## [Artículo N]`) el bloque:

```markdown
## [{Título del artículo}]

---
doi: {doi}
año de publicacion: {año}
autor: {Apellido, N.; Apellido2, N2.}
bib: |
  @article{{clave}},
    author  = {{autores}},
    title   = {{título}},
    journal = {{revista}},
    volume  = {{volumen}},
    pages   = {{páginas}},
    year    = {{año}},
    doi     = {{doi}}
  }
---

### Resultados de lo buscado

{Por qué apareció en la búsqueda, qué keywords lo encontraron}

### Resumen

{Resumen del paper en 3-5 oraciones, perspectiva de físico relativista}

### Observaciones importantes

{Ecuaciones clave, métodos, resultados numéricos relevantes para el proyecto}

### Artículos de interés

{DOIs o títulos de papers citados en este artículo que pueden ser relevantes}
```

La clave BibTeX se construye como `{apellido}{año}` (e.g., `kerr1963`).

### 4.3 Actualizar metadatos

Actualizar el campo `Tiempo de investigación` en el encabezado del `main.md` si el usuario lo indica.

---

## Modo 5 — Continuar investigación existente

Cuando el usuario dice "continúa la investigación X" o "agrega a la investigación sobre Y":

1. Listar investigaciones existentes: `ls thesis_apply/cowork/investigaciones/`
2. Identificar la correcta por nombre o número
3. Leer el `main.md` actual para ver qué papers ya están registrados
4. Continuar con búsqueda (Modo 2) o descarga (Modo 3) o registro (Modo 4)

---

## Referencia rápida de paths

```
thesis_apply/cowork/investigaciones/
└── {NNN}-{nombre}/
    ├── main.md          ← registro principal
    └── papers/          ← PDFs descargados
```

---

## Código fuente de los scripts

> Recrear si no existen en `.claude/skills/paper/scripts/`.

### `scripts/openalex_search.py`

```python
#!/usr/bin/env python3
"""
Search papers on OpenAlex by keyword/title/author.
Usage:
    python openalex_search.py "kerr geodesics analytical" [-n 10]
    python openalex_search.py "Boyer-Lindquist" --year-from 2000 --json
"""

import sys
import re
import json
import argparse
import urllib.request
import urllib.parse
from dataclasses import dataclass

BASE_URL = "https://api.openalex.org/works"
EMAIL = "thesis@example.com"
HEADERS = {"User-Agent": f"thesis-paper-downloader/1.0 (mailto:{EMAIL})"}


@dataclass
class PaperResult:
    title: str
    doi: str | None
    year: int | None
    authors: list[str]
    open_access_url: str | None
    openalex_id: str

    def short_doi(self) -> str | None:
        if self.doi:
            return re.sub(r"https?://doi\.org/", "", self.doi)
        return None

    def display(self, index: int) -> str:
        authors_str = ", ".join(self.authors[:3])
        if len(self.authors) > 3:
            authors_str += " et al."
        doi_str = self.short_doi() or "no DOI"
        oa_str = f"  OA: {self.open_access_url}" if self.open_access_url else "  OA: no"
        return (
            f"[{index}] {self.title}\n"
            f"     {authors_str} ({self.year})\n"
            f"     DOI: {doi_str}\n"
            f"{oa_str}"
        )


def search_openalex(query, n=10, year_from=None, year_to=None):
    params = {
        "search": query,
        "per-page": str(n),
        "select": "id,title,doi,publication_year,authorships,open_access,best_oa_location",
        "mailto": EMAIL,
    }
    filters = []
    if year_from:
        filters.append(f"publication_year:>{year_from - 1}")
    if year_to:
        filters.append(f"publication_year:<{year_to + 1}")
    if filters:
        params["filter"] = ",".join(filters)

    url = BASE_URL + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read())

    results = []
    for item in data.get("results", []):
        authors = [
            a["author"]["display_name"]
            for a in item.get("authorships", [])
            if a.get("author", {}).get("display_name")
        ]
        oa = item.get("open_access", {})
        oa_url = oa.get("oa_url")
        if not oa_url:
            best = item.get("best_oa_location") or {}
            oa_url = best.get("pdf_url") or best.get("landing_page_url")
        results.append(PaperResult(
            title=item.get("title") or "(sin título)",
            doi=item.get("doi"),
            year=item.get("publication_year"),
            authors=authors,
            open_access_url=oa_url,
            openalex_id=item.get("id", ""),
        ))
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    parser.add_argument("-n", "--results", type=int, default=10)
    parser.add_argument("--year-from", type=int, default=None)
    parser.add_argument("--year-to", type=int, default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        results = search_openalex(args.query, args.results, args.year_from, args.year_to)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if not results:
        print("No results found.")
        return

    if args.json:
        out = [{"title": r.title, "doi": r.short_doi(), "year": r.year,
                "authors": r.authors, "open_access_url": r.open_access_url} for r in results]
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return

    print(f"\n{len(results)} resultados para: '{args.query}'\n")
    for i, r in enumerate(results, 1):
        print(r.display(i))
        print()


if __name__ == "__main__":
    main()
```

### `scripts/download_paper.py`

```python
#!/usr/bin/env python3
"""
Download a paper PDF given a DOI or URL.
Tries: direct URL → Unpaywall → Sci-Hub.
Usage: python download_paper.py <DOI or URL> [-o output.pdf]
"""

import sys
import re
import argparse
import urllib.request
import urllib.parse
import json
from pathlib import Path

SCIHUB_MIRRORS = ["https://sci-hub.box", "https://sci-hub.se", "https://sci-hub.st", "https://sci-hub.ru"]
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}


def is_doi(s):
    return bool(re.match(r"^10\.\d{4,}/\S+$", s.strip()))


def normalize_input(s):
    s = s.strip()
    doi_from_url = re.search(r"10\.\d{4,}/\S+", s)
    if doi_from_url:
        doi = doi_from_url.group(0).rstrip(")")
        url = s if s.startswith("http") else None
        return doi, url
    if s.startswith("http"):
        return None, s
    return None, None


def fetch_url(url, output_path):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=30) as resp:
            content_type = resp.headers.get("Content-Type", "")
            data = resp.read()
            if b"%PDF" in data[:8] or "pdf" in content_type:
                output_path.write_bytes(data)
                return True
    except Exception:
        pass
    return False


def try_unpaywall(doi, output_path):
    api = f"https://api.unpaywall.org/v2/{urllib.parse.quote(doi)}?email=thesis@example.com"
    try:
        req = urllib.request.Request(api, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        best = data.get("best_oa_location") or {}
        pdf_url = best.get("url_for_pdf") or best.get("url")
        if pdf_url:
            print(f"  Unpaywall: {pdf_url}")
            return fetch_url(pdf_url, output_path)
    except Exception:
        pass
    return False


def try_scihub(doi, output_path):
    for mirror in SCIHUB_MIRRORS:
        url = f"{mirror}/{doi}"
        print(f"  Sci-Hub: {url}")
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=30) as resp:
                html = resp.read().decode("utf-8", errors="ignore")
            pdf_match = re.search(
                r'<meta[^>]+name=["\']citation_pdf_url["\'][^>]+content=["\']([^"\']+)["\']', html
            ) or re.search(r'(?:src|href)=["\']([^"\']*\.pdf[^"\']*)["\']', html)
            if pdf_match:
                pdf_url = pdf_match.group(1)
                if pdf_url.startswith("//"):
                    pdf_url = "https:" + pdf_url
                elif pdf_url.startswith("/"):
                    pdf_url = mirror + pdf_url
                if fetch_url(pdf_url, output_path):
                    return True
        except Exception:
            continue
    return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("-o", "--output", default=None)
    args = parser.parse_args()

    doi, url = normalize_input(args.input)
    if doi is None and url is None:
        if is_doi(args.input):
            doi = args.input.strip()
        else:
            print("Error: no se pudo parsear como DOI o URL.")
            sys.exit(1)

    safe = re.sub(r"[^\w\-.]", "_", (doi or url).replace("/", "_"))
    out_name = args.output or safe[:80] + ".pdf"
    output_path = Path(out_name)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Target: doi={doi}  url={url}")
    print(f"Output: {output_path}")

    if url:
        print("\n[1/3] URL directa...")
        if fetch_url(url, output_path):
            print(f"✓ Descargado en {output_path}")
            return

    if doi:
        print("\n[2/3] Unpaywall (open access)...")
        if try_unpaywall(doi, output_path):
            print(f"✓ Descargado en {output_path}")
            return

    if doi:
        print("\n[3/3] Sci-Hub...")
        if try_scihub(doi, output_path):
            print(f"✓ Descargado en {output_path}")
            return

    print("\n✗ No se pudo descargar el PDF.")
    sys.exit(1)


if __name__ == "__main__":
    main()
```
