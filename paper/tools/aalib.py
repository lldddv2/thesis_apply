"""Utilidades compartidas por flatten.py, check.py y csv2aa.py.

Parseo de las macros \\aa... y conversión de CSV a tabular en formato A&A.
"""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path

# Comandos de autoría definidos en aapaper.sty. flatten.py debe eliminarlos
# todos del archivo que se envía a EDP Sciences.
AUTHORING_COMMANDS = [
    "aafig",
    "aafigwide",
    "aafigside",
    "aafigmulti",
    "aatable",
    "aatablewide",
    "aatablelong",
    "aatablebib",
    "secref",
    "figref",
    "tabref",
    "eqnref",
    "appref",
]


@dataclass
class Call:
    """Una invocación de macro localizada en el fuente."""

    name: str
    args: list[tuple[str, str]]  # (tipo, contenido); tipo es "[" o "{"
    start: int
    end: int

    def optional(self, index: int, default: str = "") -> str:
        """Devuelve el index-ésimo argumento opcional ([...])."""
        opts = [a for kind, a in self.args if kind == "["]
        return opts[index] if index < len(opts) else default

    def mandatory(self, index: int, default: str = "") -> str:
        """Devuelve el index-ésimo argumento obligatorio ({...})."""
        mand = [a for kind, a in self.args if kind == "{"]
        return mand[index] if index < len(mand) else default


def strip_comments(text: str) -> str:
    """Elimina los comentarios de LaTeX, respetando el «\\%» escapado.

    Imprescindible antes de expandir macros: los ejemplos comentados del
    esqueleto no deben tratarse como llamadas reales.
    """
    return re.sub(r"(?<!\\)%.*", "", text)


def drop_blank_runs(text: str) -> str:
    """Colapsa tres o más líneas en blanco seguidas en una sola línea vacía."""
    return re.sub(r"\n{3,}", "\n\n", text)


def _match_delimiter(text: str, start: int, open_ch: str, close_ch: str) -> int:
    """Índice del delimitador de cierre que equilibra el de `start`.

    Ignora los delimitadores escapados con barra invertida.
    """
    depth = 0
    i = start
    while i < len(text):
        ch = text[i]
        if ch == "\\":
            i += 2
            continue
        if ch == open_ch:
            depth += 1
        elif ch == close_ch:
            depth -= 1
            if depth == 0:
                return i
        i += 1
    raise ValueError(f"delimitador «{open_ch}» sin cerrar en la posición {start}")


def find_calls(text: str, name: str) -> list[Call]:
    """Localiza todas las llamadas a \\<name> con sus argumentos.

    Recoge argumentos opcionales y obligatorios en el orden en que aparecen,
    saltando los espacios intermedios y los saltos de línea.
    """
    calls: list[Call] = []
    # \name no seguido de una letra, para no confundir \aatable con \aatablewide
    pattern = re.compile(r"\\" + re.escape(name) + r"(?![a-zA-Z])")
    for m in pattern.finditer(text):
        i = m.end()
        args: list[tuple[str, str]] = []
        while True:
            j = i
            while j < len(text) and text[j] in " \t\r\n":
                j += 1
            if j >= len(text) or text[j] not in "[{":
                break
            open_ch = text[j]
            close_ch = "]" if open_ch == "[" else "}"
            end = _match_delimiter(text, j, open_ch, close_ch)
            args.append((open_ch, text[j + 1 : end]))
            i = end + 1
        calls.append(Call(name=name, args=args, start=m.start(), end=i))
    return calls


def read_csv_table(path: Path) -> tuple[list[str], list[list[str]]]:
    """Lee un CSV y devuelve (encabezado, filas) como cadenas sin tocar.

    No se interpreta ni se reformatea nada: las celdas pueden llevar LaTeX
    crudo ($M_\\odot$, \\tablefootmark{a}) y debe llegar intacto al .tex.
    """
    with path.open(newline="", encoding="utf-8") as fh:
        rows = [row for row in csv.reader(fh) if any(cell.strip() for cell in row)]
    if not rows:
        raise ValueError(f"{path}: el CSV está vacío")

    header, body = rows[0], rows[1:]
    # Una fila con más celdas que el encabezado casi siempre significa una coma
    # de LaTeX sin proteger: «$10^6\,M_\odot$» se parte en dos campos. Fallar
    # aquí es mucho mejor que truncar la columna en silencio.
    for i, row in enumerate(body, start=2):
        if len(row) > len(header):
            raise ValueError(
                f"{path}: la línea {i} tiene {len(row)} campos y el encabezado "
                f"{len(header)}. Si una celda contiene una coma (p. ej. «\\,» de "
                f"LaTeX), enciérrala en comillas dobles: \"$10^6\\,M_\\odot$\""
            )
    return header, body


def tabular(header: list[str], rows: list[list[str]], align: str = "l") -> str:
    """Genera un `tabular` con los filetes que exige A&A.

    \\hline\\hline arriba, \\hline bajo el encabezado, \\hline al cierre.
    A&A no usa booktabs.
    """
    ncols = len(header)
    spec = align * ncols
    out = [f"\\begin{{tabular}}{{{spec}}}", "\\hline\\hline"]
    out.append(" & ".join(cell.strip() for cell in header) + " \\\\")
    out.append("\\hline")
    for row in rows:
        padded = list(row) + [""] * (ncols - len(row))
        out.append(" & ".join(cell.strip() for cell in padded[:ncols]) + " \\\\")
    out.append("\\hline")
    out.append("\\end{tabular}")
    return "\n".join(out)


def longtable(
    header: list[str],
    rows: list[list[str]],
    caption: str,
    label: str,
    align: str = "l",
) -> str:
    """Genera un `longtable` con encabezado repetido y caption «continued.».

    Sigue el patrón del aa_example.tex oficial: \\endfirsthead con el caption
    completo, \\endhead con «continued.», y \\endfoot con el filete de cierre.
    """
    ncols = len(header)
    spec = align * ncols
    head_row = " & ".join(cell.strip() for cell in header) + " \\\\"
    out = [
        f"\\begin{{longtable}}{{{spec}}}",
        f"\\caption{{{caption}}}\\\\",
        f"\\label{{{label}}}\\\\",
        "\\hline\\hline",
        head_row,
        "\\hline",
        "\\endfirsthead",
        "\\caption{continued.}\\\\",
        "\\hline\\hline",
        head_row,
        "\\hline",
        "\\endhead",
        "\\hline",
        "\\endfoot",
    ]
    for row in rows:
        padded = list(row) + [""] * (ncols - len(row))
        out.append(" & ".join(cell.strip() for cell in padded[:ncols]) + " \\\\")
    out.append("\\end{longtable}")
    return "\n".join(out)


def residual_authoring_commands(text: str) -> list[str]:
    """Comandos de autoría que siguen presentes en `text`.

    flatten.py la usa como puerta de calidad: si devuelve algo distinto de una
    lista vacía, el archivo no está listo para enviarse a A&A.
    """
    found = []
    for name in AUTHORING_COMMANDS:
        if re.search(r"\\" + re.escape(name) + r"(?![a-zA-Z])", text):
            found.append(name)
    return found
