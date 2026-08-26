#!/usr/bin/env python3
r"""Auditoría del manuscrito A&A sin necesidad de un motor TeX.

Comprueba lo que se puede comprobar leyendo el fuente: referencias cruzadas,
claves de bibliografía, rutas de figuras y CSV, estructura del abstract y las
reglas tipográficas que A&A publica.

No sustituye a la compilación. Es lo que se puede verificar antes de tenerla.

Uso:
    uv run python tools/check.py
    uv run python tools/check.py --strict     # los avisos también fallan
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from aalib import find_calls, read_csv_table, strip_comments  # noqa: E402

PAPER_ROOT = Path(__file__).resolve().parent.parent

# Regla A&A: fuera de inicio de frase se abrevia Sect./Fig./Col.; Table nunca.
ABBREV_VIOLATIONS = [
    (r"(?<![.:]\s)(?<!^)\bSection~?\s*\\ref", "«Section» debe abreviarse «Sect.»"),
    (r"(?<![.:]\s)(?<!^)\bFigure~?\s*\\ref", "«Figure» debe abreviarse «Fig.»"),
    (r"(?<![.:]\s)(?<!^)\bColumn~?\s*\\ref", "«Column» debe abreviarse «Col.»"),
    (r"\bTab\.~?\s*\\ref", "«Table» nunca se abrevia"),
]


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def dump(self, strict: bool) -> int:
        for msg in self.errors:
            print(f"  ERROR   {msg}")
        for msg in self.warnings:
            print(f"  aviso   {msg}")
        n_e, n_w = len(self.errors), len(self.warnings)
        print(f"\n{n_e} errores, {n_w} avisos")
        if n_e:
            return 1
        if strict and n_w:
            return 1
        return 0


def gather_sources(root: Path) -> dict[Path, str]:
    """Todos los .tex del manuscrito, sin comentarios."""
    paths = [root / "main.tex", root / "metadata.tex"]
    paths += sorted((root / "sections").glob("*.tex"))
    paths += sorted((root / "appendices").glob("*.tex"))
    return {
        p: strip_comments(p.read_text(encoding="utf-8"))
        for p in paths
        if p.exists()
    }


def check_crossrefs(sources: dict[Path, str], report: Report) -> None:
    labels: dict[str, Path] = {}
    refs: dict[str, list[Path]] = {}

    def record_label(key: str, path: Path) -> None:
        if not key.strip():
            return
        if key in labels:
            report.error(f"label duplicado «{key}» ({labels[key].name} y {path.name})")
        labels[key] = path

    for path, text in sources.items():
        for m in re.finditer(r"\\label\{([^}]+)\}", text):
            record_label(m.group(1), path)
        # Los comandos de aapaper.sty declaran su label como argumento opcional
        for name in ("aafig", "aafigwide", "aafigside", "aafigmulti",
                     "aatable", "aatablewide"):
            for call in find_calls(text, name):
                record_label(call.optional(0), path)
        # \aatablelong lleva el label como último argumento obligatorio
        for call in find_calls(text, "aatablelong"):
            record_label(call.mandatory(2), path)
        for m in re.finditer(r"\\(?:ref|eqref|cref|Cref)\{([^}]+)\}", text):
            refs.setdefault(m.group(1), []).append(path)
        # Atajos de aapaper.sty, que también generan referencias
        for name in ("secref", "figref", "tabref", "eqnref", "appref"):
            for call in find_calls(text, name):
                refs.setdefault(call.mandatory(0), []).append(path)

    for key, where in refs.items():
        if key not in labels:
            report.error(f"\\ref a «{key}» sin \\label ({where[0].name})")
    for key, path in labels.items():
        if key not in refs:
            report.warn(f"label «{key}» nunca referenciado ({path.name})")


def check_citations(sources: dict[Path, str], root: Path, report: Report) -> None:
    bib = root / "refs.bib"
    if not bib.exists():
        report.warn("no existe refs.bib; no se pueden verificar las citas")
        return
    # OJO: BibTeX NO trata «%» como comentario. Todo «@…{clave,» se parsea, esté
    # o no precedido de «%». Aquí se replica ese comportamiento a propósito, para
    # que una entrada «comentada» aparezca como clave real igual que la ve BibTeX.
    # Se excluyen los tipos que no declaran clave.
    bib_text = bib.read_text(encoding="utf-8")
    keys = {
        key
        for kind, key in re.findall(r"@(\w+)\s*\{\s*([^,\s}]+)", bib_text)
        if kind.lower() not in {"comment", "string", "preamble"}
    }
    cited: set[str] = set()
    for text in sources.values():
        for m in re.finditer(r"\\cite[a-zA-Z]*\s*(?:\[[^\]]*\]){0,2}\{([^}]+)\}", text):
            cited.update(k.strip() for k in m.group(1).split(","))
    for key in sorted(cited - keys):
        report.error(f"clave citada y ausente de refs.bib: «{key}»")
    for key in sorted(keys - cited):
        report.warn(f"entrada de refs.bib nunca citada: «{key}»")


def check_assets(sources: dict[Path, str], root: Path, report: Report) -> None:
    figures_dir = root / "figures"
    for path, text in sources.items():
        for name in ("aafig", "aafigwide", "aafigside"):
            for call in find_calls(text, name):
                fname = call.mandatory(0).strip()
                if not fname:
                    continue
                if not (figures_dir / fname).exists() and not list(
                    figures_dir.glob(f"{fname}.*")
                ):
                    report.error(f"figura ausente: figures/{fname} ({path.name})")
        for name in ("aatable", "aatablewide", "aatablelong"):
            for call in find_calls(text, name):
                rel = call.mandatory(0).strip()
                if not rel:
                    continue
                csv_path = root / rel
                if not csv_path.exists():
                    report.error(f"CSV ausente: {rel} ({path.name})")
                    continue
                # Parsearlo de verdad: detecta comas de LaTeX sin proteger,
                # que si no truncarían una columna en silencio.
                try:
                    read_csv_table(csv_path)
                except ValueError as exc:
                    report.error(f"{exc} ({path.name})")


def check_abstract(root: Path, report: Report) -> None:
    path = root / "sections" / "00-abstract.tex"
    if not path.exists():
        report.error("falta sections/00-abstract.tex")
        return
    text = strip_comments(path.read_text(encoding="utf-8"))
    if "\\abstract" not in text:
        report.error("no se encontró \\abstract")
        return
    # Contar los grupos {...} de primer nivel tras \abstract
    i = text.index("\\abstract") + len("\\abstract")
    groups, depth, started = 0, 0, False
    while i < len(text):
        ch = text[i]
        if ch == "\\":
            i += 2
            continue
        if ch == "{":
            depth += 1
            started = True
        elif ch == "}":
            depth -= 1
            if depth == 0:
                groups += 1
        elif started and depth == 0 and ch not in " \t\r\n":
            break
        i += 1
    if groups not in (1, 5):
        report.error(
            f"\\abstract tiene {groups} argumentos; A&A admite 1 (tradicional) "
            "o 5 (estructurado: context, aims, methods, results, conclusions)"
        )
    if "\\keywords" not in text:
        report.error("faltan las \\keywords")


def check_typography(sources: dict[Path, str], report: Report) -> None:
    for path, text in sources.items():
        for lineno, line in enumerate(text.splitlines(), 1):
            where = f"{path.name}:{lineno}"
            for pattern, msg in ABBREV_VIOLATIONS:
                if re.search(pattern, line):
                    report.warn(f"{where}: {msg}")
            if re.search(r"\bkm/s\b|\bcm/s\b|\berg/s\b", line):
                report.warn(f"{where}: A&A prefiere índice negativo (km~s$^{{-1}}$) a la barra")
            if re.search(r"\b(?:Sect|Fig|Col|Eq)\.\s+\\?ref", line):
                report.warn(f"{where}: usar espacio fijo «~» antes de \\ref, no espacio normal")
            if re.search(r"(?<![\d.,\\])\b\d{5,}\b", line) and "\\," not in line:
                report.warn(f"{where}: números de 5+ dígitos llevan espacio fino: 20\\,000")
            if re.search(r"(?<!-)---(?!-)", line):
                report.warn(f"{where}: A&A usa en-dash «--» con espacios, no em-dash «---»")
            if re.search(r"\\toprule|\\midrule|\\bottomrule", line):
                report.error(f"{where}: A&A no usa booktabs; van \\hline\\hline / \\hline")
            if re.search(r"\\numberwithin", line):
                report.error(f"{where}: A&A numera correlativo, no por sección")
            if re.search(r"\\begin\{(?:figure|table)\*?\}\[H\]", line):
                report.error(f"{where}: no usar [H]; A&A quiere floats flotantes ([ht!])")


def check_objects(sources: dict[Path, str], report: Report) -> None:
    """Nombres de objetos conocidos que aparecen sin \\object{}."""
    known = ["Sgr A*", "Sgr~A*", "S2", "S0-2", "M87*"]
    for path, text in sources.items():
        wrapped = " ".join(
            call.mandatory(0) for call in find_calls(text, "object")
        )
        for name in known:
            if name in text and name not in wrapped:
                report.warn(
                    f"{path.name}: «{name}» aparece sin \\object{{}} en alguna ocurrencia"
                )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(PAPER_ROOT))
    parser.add_argument("--strict", action="store_true", help="los avisos también fallan")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    sources = gather_sources(root)
    if not sources:
        print(f"error: no se encontró ningún .tex bajo {root}", file=sys.stderr)
        return 1

    print(f"revisando {len(sources)} archivos bajo {root}\n")
    report = Report()
    check_crossrefs(sources, report)
    check_citations(sources, root, report)
    check_assets(sources, root, report)
    check_abstract(root, report)
    check_typography(sources, report)
    check_objects(sources, report)
    return report.dump(args.strict)


if __name__ == "__main__":
    raise SystemExit(main())
