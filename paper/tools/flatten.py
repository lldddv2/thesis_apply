#!/usr/bin/env python3
r"""Expande el manuscrito a LaTeX A&A crudo, listo para enviar a EDP Sciences.

Por qué existe este script — A&A, en «TeXnical background information»:

    "Please refrain from using any self-made definitions since these will get
     lost during further conversion of your text. If you use typing
     abbreviations, 'search and replace' them before submitting your article
     to the publisher."

Escribir con macros propias es cómodo; enviarlas rompe la conversión del
editor. Este script hace el «search and replace» automáticamente:

  1. Resuelve todos los \input en un único main.tex.
  2. Expande cada macro \aa... a su forma A&A cruda (figure, tabular, longtab,
     \tablefoot, ...), leyendo los CSV que hagan falta.
  3. Quita \usepackage{aapaper} del preámbulo.
  4. Copia figuras usadas, class/ (aa.cls, aa.bst, linenoaa.sty) y refs.bib.
  5. FALLA si queda cualquier comando de autoría en la salida.

Uso:
    uv run python tools/flatten.py
    uv run python tools/flatten.py --out build/submission --main main.tex
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from aalib import (  # noqa: E402
    Call,
    drop_blank_runs,
    find_calls,
    longtable,
    read_csv_table,
    residual_authoring_commands,
    strip_comments,
    tabular,
)

PAPER_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# 1. Resolución de \input
# ---------------------------------------------------------------------------

def inline_inputs(text: str, root: Path, seen: set[Path] | None = None) -> str:
    """Sustituye cada \\input{ruta} por el contenido del archivo, sin comentarios.

    Los comentarios se eliminan al leer cada archivo: el esqueleto lleva
    ejemplos de macros comentados que NO deben expandirse ni acabar en el
    manuscrito enviado. Detecta inclusiones circulares.
    """
    seen = seen or set()
    pattern = re.compile(r"^([ \t]*)\\input\{([^}]+)\}[ \t]*$", re.MULTILINE)

    def repl(m: re.Match[str]) -> str:
        rel = m.group(2).strip()
        path = root / rel
        if path.suffix != ".tex":
            path = path.with_suffix(".tex")
        if not path.exists():
            print(f"  aviso: \\input{{{rel}}} no encontrado ({path})")
            return m.group(0)
        resolved = path.resolve()
        if resolved in seen:
            raise RuntimeError(f"\\input circular en {rel}")
        body = strip_comments(path.read_text(encoding="utf-8"))
        return inline_inputs(body, root, seen | {resolved})

    previous = None
    while previous != text:
        previous = text
        text = pattern.sub(repl, text)
    return text


# ---------------------------------------------------------------------------
# 2. Expansión de las macros
# ---------------------------------------------------------------------------

def _label_line(label: str) -> str:
    return f"\\label{{{label}}}\n" if label.strip() else ""


def expand_figures(text: str, used: set[str]) -> str:
    """Expande \\aafig, \\aafigwide, \\aafigside y \\aafigmulti."""

    def one_column(c: Call) -> str:
        label, fname, caption = c.optional(0), c.mandatory(0), c.mandatory(1)
        place = c.optional(1, "ht!")
        return (
            f"\\begin{{figure}}[{place}]\n"
            f"\\centering\n"
            f"\\resizebox{{\\hsize}}{{!}}{{\\includegraphics{{{fname}}}}}\n"
            f"\\caption{{{caption}}}\n"
            f"{_label_line(label)}"
            f"\\end{{figure}}"
        )

    def two_column(c: Call) -> str:
        label, fname, caption = c.optional(0), c.mandatory(0), c.mandatory(1)
        place = c.optional(1, "ht!")
        return (
            f"\\begin{{figure*}}[{place}]\n"
            f"\\centering\n"
            f"\\includegraphics[width=17cm]{{{fname}}}\n"
            f"\\caption{{{caption}}}\n"
            f"{_label_line(label)}"
            f"\\end{{figure*}}"
        )

    def side_caption(c: Call) -> str:
        label, fname, caption = c.optional(0), c.mandatory(0), c.mandatory(1)
        place = c.optional(1, "ht!")
        # \sidecaption va antes del \includegraphics; el \caption, después.
        return (
            f"\\begin{{figure*}}[{place}]\n"
            f"\\sidecaption\n"
            f"\\includegraphics[width=12cm]{{{fname}}}\n"
            f"\\caption{{{caption}}}\n"
            f"{_label_line(label)}"
            f"\\end{{figure*}}"
        )

    def multi(c: Call) -> str:
        label, files, caption = c.optional(0), c.mandatory(0), c.mandatory(1)
        place = c.optional(1, "ht!")
        includes = "\n".join(
            f"\\includegraphics{{{f.strip()}}}"
            for f in files.split(",")
            if f.strip()
        )
        return (
            f"\\begin{{figure*}}[{place}]\n"
            f"\\centering\n"
            f"{includes}\n"
            f"\\caption{{{caption}}}\n"
            f"{_label_line(label)}"
            f"\\end{{figure*}}"
        )

    handlers = {
        "aafigwide": two_column,
        "aafigside": side_caption,
        "aafigmulti": multi,
        "aafig": one_column,
    }
    # Los nombres largos primero: \aafig es prefijo de \aafigwide.
    for name, handler in handlers.items():
        calls = find_calls(text, name)
        for c in reversed(calls):
            if name == "aafigmulti":
                used.update(f.strip() for f in c.mandatory(0).split(",") if f.strip())
            else:
                used.add(c.mandatory(0))
            text = text[: c.start] + handler(c) + text[c.end :]
    return text


def expand_tables(text: str, root: Path) -> str:
    """Expande \\aatable, \\aatablewide, \\aatablelong y \\aatablebib."""

    def resolve(rel: str) -> Path:
        path = root / rel.strip()
        if not path.exists():
            raise FileNotFoundError(f"CSV no encontrado: {rel}")
        return path

    def simple(c: Call, star: str) -> str:
        label, csv_rel, caption = c.optional(0), c.mandatory(0), c.mandatory(1)
        note = c.optional(1)
        header, rows = read_csv_table(resolve(csv_rel))
        env = f"table{star}"
        parts = [
            f"\\begin{{{env}}}[ht!]",
            f"\\caption{{{caption}}}",
        ]
        if label.strip():
            parts.append(f"\\label{{{label}}}")
        parts.append("\\centering")
        parts.append(tabular(header, rows))
        if note.strip():
            parts.append(f"\\tablefoot{{{note}}}")
        parts.append(f"\\end{{{env}}}")
        return "\n".join(parts)

    def long_table(c: Call) -> str:
        index = c.optional(0, "1")
        csv_rel, caption, label = c.mandatory(0), c.mandatory(1), c.mandatory(2)
        header, rows = read_csv_table(resolve(csv_rel))
        body = longtable(header, rows, caption, label)
        return f"\\longtab[{index}]{{\n{body}\n}}"

    for name, handler in (
        ("aatablelong", long_table),
        ("aatablewide", lambda c: simple(c, "*")),
        ("aatablebib", lambda c: f"\\tablebib{{{c.mandatory(0)}}}"),
        ("aatable", lambda c: simple(c, "")),
    ):
        for c in reversed(find_calls(text, name)):
            text = text[: c.start] + handler(c) + text[c.end :]
    return text


def expand_shortcuts(text: str) -> str:
    """Expande los atajos de referencia cruzada a su forma A&A literal."""
    replacements = {
        "secref": "Sect.~\\ref{{{}}}",
        "figref": "Fig.~\\ref{{{}}}",
        "tabref": "Table~\\ref{{{}}}",
        "eqnref": "Eq.~(\\ref{{{}}})",
        "appref": "Appendix~\\ref{{{}}}",
    }
    for name, template in replacements.items():
        for c in reversed(find_calls(text, name)):
            text = text[: c.start] + template.format(c.mandatory(0)) + text[c.end :]
    return text


def strip_aapaper(text: str) -> str:
    """Quita aapaper y los paquetes que solo servían para generar las macros.

    csvsimple, xparse y etoolbox eran andamiaje de autoría: en la salida ya no
    queda nada que los use. longtable, lscape, subcaption y placeins sí se
    conservan, porque \\longtab, \\ContinuedFloat y \\FloatBarrier los necesitan.
    """
    for pkg in ("aapaper", "csvsimple", "xparse", "etoolbox"):
        text = re.sub(
            r"^[ \t]*\\usepackage\{" + pkg + r"\}[ \t]*\n",
            "",
            text,
            flags=re.MULTILINE,
        )
    return text


# ---------------------------------------------------------------------------
# 3. Ensamblado
# ---------------------------------------------------------------------------

def collect_figure_files(root: Path, used: set[str]) -> list[Path]:
    """Resuelve los nombres de figura contra figures/, probando extensiones."""
    figures_dir = root / "figures"
    found = []
    for name in sorted(used):
        candidate = figures_dir / name
        if candidate.exists():
            found.append(candidate)
            continue
        matches = sorted(figures_dir.glob(f"{name}.*"))
        if matches:
            found.append(matches[0])
        else:
            print(f"  aviso: figura no encontrada en figures/: {name}")
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--main", default="main.tex", help="archivo raíz")
    parser.add_argument("--out", default="build/submission", help="directorio de salida")
    parser.add_argument("--root", default=str(PAPER_ROOT), help="raíz del paper")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out = (root / args.out).resolve() if not Path(args.out).is_absolute() else Path(args.out)
    main_tex = root / args.main

    if not main_tex.exists():
        print(f"error: no existe {main_tex}", file=sys.stderr)
        return 1

    print(f"raíz:    {root}")
    print(f"salida:  {out}")

    text = strip_comments(main_tex.read_text(encoding="utf-8"))
    text = inline_inputs(text, root)

    used_figures: set[str] = set()
    text = expand_figures(text, used_figures)
    try:
        text = expand_tables(text, root)
    except (FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    text = expand_shortcuts(text)
    text = strip_aapaper(text)
    text = drop_blank_runs(text)
    text = (
        "% Generado por tools/flatten.py — no editar a mano.\n"
        "% Sin definiciones propias, como exige A&A.\n" + text
    )

    residual = residual_authoring_commands(text)
    if residual:
        print(
            "error: quedan comandos de autoría sin expandir: "
            + ", ".join("\\" + n for n in residual),
            file=sys.stderr,
        )
        print(
            "A&A no acepta definiciones propias; corrige la expansión antes de enviar.",
            file=sys.stderr,
        )
        return 1

    out.mkdir(parents=True, exist_ok=True)
    (out / "main.tex").write_text(text, encoding="utf-8")

    # Clase, estilo de bibliografía y numeración de líneas deben viajar juntos.
    for name in ("aa.cls", "aa.bst", "linenoaa.sty", "lineno.sty"):
        src = root / "class" / name
        if src.exists():
            shutil.copy2(src, out / name)

    bib = root / "refs.bib"
    if bib.exists():
        shutil.copy2(bib, out / "refs.bib")

    figures = collect_figure_files(root, used_figures)
    if figures:
        (out / "figures").mkdir(exist_ok=True)
        for fig in figures:
            shutil.copy2(fig, out / "figures" / fig.name)

    print(f"ok: {len(text.splitlines())} líneas, {len(figures)} figuras copiadas")
    print("sin comandos de autoría en la salida")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
