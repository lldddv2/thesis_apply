# Manuscrito para Astronomy & Astrophysics

Clase `aa.cls` v9.4 (EDP Sciences, 2026). Las reglas editoriales completas están
codificadas en la skill global `aa-paper` (`~/.claude/skills/aa-paper/`).

## Estructura

```
paper/
├── main.tex              preámbulo + \input de todo
├── metadata.tex          título, autores, afiliaciones, fecha
├── aapaper.sty           comandos de autoría (\aafig, \aatable, ...)
├── refs.bib
├── sections/             una sección por archivo, orden por prefijo numérico
├── appendices/           van tras la bibliografía; se publican camera-ready
├── figures/              eps, pdf, png, jpg, tiff
├── tables/               CSV fuente de las tablas
├── class/                aa.cls, aa.bst, linenoaa.sty, lineno.sty
├── reference/            aa_example.tex/.pdf oficiales, para consultar
├── tools/                flatten.py, check.py, csv2aa.py
└── build/submission/     salida lista para enviar
```

Para reordenar secciones, renombra los archivos: el prefijo numérico fija el
orden y `main.tex` los llama en secuencia.

## Flujo de trabajo

### 1. Escribir

Con los comandos de `aapaper.sty`:

| Comando | Uso |
|---|---|
| `\aafig[label]{archivo}{caption}[colocación]` | figura a una columna (88 mm) |
| `\aafigside[label]{archivo}{caption}[colocación]` | 120 mm, caption al costado |
| `\aafigwide[label]{archivo}{caption}[colocación]` | dos columnas (180 mm) |
| `\aafigmulti[label]{f1,f2,f3}{caption}[colocación]` | varios gráficos en un float |
| `\aatable[label]{csv}{caption}[nota]` | tabla desde CSV, una columna |
| `\aatablewide[label]{csv}{caption}[nota]` | tabla desde CSV, dos columnas |
| `\aatablelong[n]{csv}{caption}{label}` | tabla multipágina vía `\longtab` |
| `\aatablebib{texto}` | referencias bajo una tabla |
| `\secref \figref \tabref \eqnref \appref` | referencias cruzadas ya abreviadas |

Los CSV van en `tables/`: primera fila el encabezado, celdas con LaTeX crudo
permitido (`$M_\odot$`, `\tablefootmark{a}`).

### 2. Auditar

```
uv run python tools/check.py
uv run python tools/check.py --strict     # los avisos también fallan
```

Revisa referencias cruzadas, claves de bibliografía, rutas de figuras y CSV,
estructura del abstract, y las reglas tipográficas de A&A.

### 3. Preparar el envío

```
uv run python tools/flatten.py
```

Genera `build/submission/` con un `main.tex` único, todas las macros expandidas
a LaTeX A&A crudo, y las figuras y archivos de clase copiados. El script **falla**
si queda cualquier comando propio sin expandir.

Esto no es opcional. A&A pide textualmente:

> "Please refrain from using any self-made definitions since these will get lost
> during further conversion of your text. If you use typing abbreviations,
> 'search and replace' them before submitting your article to the publisher."

`flatten.py` es ese search-and-replace, automatizado.

## Compilar

Desde `paper/`:

```
latexmk -pdf main.tex        # PDF en build/local/main.pdf
latexmk -C                   # limpiar
```

`.latexmkrc` se encarga de que LaTeX encuentre `aa.cls`, `aa.bst` y
`linenoaa.sty` en `class/` (extiende `TEXINPUTS` y `BSTINPUTS`), y manda los
subproductos a `build/local/`. Sin latexmk hay que exportar las rutas a mano:

```
TEXINPUTS='./class//:' BSTINPUTS='./class//:' pdflatex main.tex
```

Para verificar lo que de verdad se envía, compilar la salida de `flatten.py`:

```
uv run python tools/flatten.py
cd build/submission && latexmk -pdf main.tex
```

`build/submission/` es autocontenido: lleva copiados `aa.cls`, `aa.bst`,
`linenoaa.sty` y las figuras usadas, así que también se puede subir tal cual a
Overleaf como proyecto nuevo.

Para publicar en arXiv, descomentar `\nolinenumbers` tras `\maketitle`.

### Paquetes de TeX Live necesarios (Arch)

```
sudo pacman -S --needed texlive-basic texlive-latex texlive-latexrecommended \
  texlive-latexextra texlive-fontsrecommended texlive-binextra texlive-fontutils
```

`texlive-fontsrecommended` trae `txfonts`, obligatorio en A&A.
`texlive-binextra` trae `latexmk`.
`texlive-fontutils` trae `epstopdf`: **hace falta solo si usas figuras EPS**,
porque pdfLaTeX no las incrusta directamente. Con figuras PDF o PNG no se
necesita.

## Dos trampas que cuestan una tarde

**BibTeX no trata `%` como comentario.** En cuanto ve una arroba intenta leer
una entrada, esté o no precedida de `%`, y falla si está incompleta. Para
desactivar una entrada: bórrala o envuélvela en una entrada de tipo `comment`.

**Un `thebibliography` sin ninguna entrada es un error de LaTeX.** Por eso
`refs.bib` trae una referencia placeholder y `01-introduction.tex` la cita.
Borra ambas cuando tengas tus propias referencias.

## Checklist antes de enviar

- [ ] `\abstract` con sus 5 argumentos (o 1 si es tradicional)
- [ ] `\keywords` tomadas literalmente de la lista oficial de A&A
- [ ] Un solo `\corrauth`; ningún ORCID junto a los nombres
- [ ] Todo objeto astronómico envuelto en `\object{}`, y el `.obj` revisado
- [ ] Figuras: sin rojo+verde, sin grids decorativos, bitmaps a 250–300 dpi
- [ ] Tablas: caption arriba, `\hline\hline`/`\hline`, sin booktabs, ≤ 23.5 cm
- [ ] Unidades con índice negativo (`km~s$^{-1}$`), no con barra
- [ ] `eprint` presente en toda entrada de ArXiv o ASCL en `refs.bib`
- [ ] Apéndices revisados con cuidado extra: se publican camera-ready
- [ ] `uv run python tools/check.py --strict` limpio
- [ ] `uv run python tools/flatten.py` sin errores
