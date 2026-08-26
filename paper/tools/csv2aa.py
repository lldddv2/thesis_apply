#!/usr/bin/env python3
r"""Convierte un CSV en una tabla A&A nativa, por stdout.

Útil cuando conviene congelar una tabla concreta en LaTeX literal en vez de
generarla en tiempo de compilación: tablas con multicolumn, con paneles
separados por \hline, o que hay que retocar a mano.

Uso:
    uv run python tools/csv2aa.py tables/elements.csv \
        --label tab:elements \
        --caption "Best-fitting orbital elements." \
        --tablefoot "Uncertainties are 68\% credible intervals."

    # dos columnas
    uv run python tools/csv2aa.py tables/big.csv --wide --caption "..."

    # multipágina, envuelta en \longtab
    uv run python tools/csv2aa.py tables/cat.csv --long --label tab:cat \
        --caption "Full catalogue."
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from aalib import longtable, read_csv_table, tabular  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", type=Path)
    parser.add_argument("--caption", default="", help="va arriba de la tabla")
    parser.add_argument("--label", default="")
    parser.add_argument("--tablefoot", default="", help="nota general bajo la tabla")
    parser.add_argument("--tablebib", default="", help="referencias bajo la tabla")
    parser.add_argument("--align", default="l", help="alineación por columna (A&A: l)")
    parser.add_argument("--wide", action="store_true", help="table* a dos columnas")
    parser.add_argument("--long", action="store_true", help="longtable dentro de \\longtab")
    parser.add_argument("--longtab-index", default="1")
    args = parser.parse_args()

    if not args.csv.exists():
        print(f"error: no existe {args.csv}", file=sys.stderr)
        return 1

    try:
        header, rows = read_csv_table(args.csv)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.long:
        if not args.label:
            print("error: --long requiere --label", file=sys.stderr)
            return 1
        body = longtable(header, rows, args.caption, args.label, args.align)
        print(f"\\longtab[{args.longtab_index}]{{")
        print(body)
        print("}")
        return 0

    env = "table*" if args.wide else "table"
    print(f"\\begin{{{env}}}[ht!]")
    print(f"\\caption{{{args.caption}}}")
    if args.label:
        print(f"\\label{{{args.label}}}")
    print("\\centering")
    print(tabular(header, rows, args.align))
    if args.tablefoot:
        print(f"\\tablefoot{{{args.tablefoot}}}")
    if args.tablebib:
        print(f"\\tablebib{{{args.tablebib}}}")
    print(f"\\end{{{env}}}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
