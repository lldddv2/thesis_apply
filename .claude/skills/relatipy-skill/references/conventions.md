# Convenciones RelatiPy

## Código y documentación del proyecto

- Idioma principal del código y docstrings: **inglés** (teoría puede documentarse en español bajo `docs/relativity/`).
- Estilo: **Google docstrings**; docstrings en `r"""..."""` cuando haya LaTeX; ecuaciones con ``:math:`...` `` o bloque `.. math::` según `docs/development/convention.md`.
- Nombrado: `snake_case` (funciones/variables), `PascalCase` (clases), `UPPER_SNAKE_CASE` (constantes).
- Índices tensoriales: letras griegas \(\mu,\nu,\ldots\) para 0–3; latinas espaciales \(i,j,\ldots\) — no reutilizar como nombres de bucles fuera de ese contexto.
- Formato: `black`, `isort`, `flake8` (`docs/development/convention.md`).
- Ramas y commits: ver `docs/development/github_convention.md` (p. ej. prefijos `[FEAT]`, `[FIX]`, …).

## Enlace teoría ↔ implementación

Las fórmulas implementadas deben poder referenciarse desde docstrings como indica `docs/development/documentation_convention.md`:

`~ref(docs/relativity/nombre.md#sección)~`

## Convenciones físicas (docs/relativity)

- **Firma métrica**: \((+,-,-,-)\) en la notación teórica del proyecto (`docs/relativity/convention.md`).
- **Kerr en docs**: elemento de línea y notación \(x^0,x^1,x^2,x^3\) alineados con `docs/relativity/metric.md` y transformaciones BL–Cartesianas en `docs/relativity/coordinates.md`.

## Unidades y constantes

- Módulo `relatipy.numeric.constants`: \(G=c=1\) en unidades geométricas del núcleo; constantes SI y escalas de referencia solar (`_L_ref`, `_T_ref`) para conversiones.
- El paquete numérico reexporta `_c` y `_G` desde `relatipy.numeric` (ambos `1.0` en la configuración actual).

## Testing

- Framework: **pytest**; tests bajo `tests/numeric/`, `tests/symbolic/`, etc., según el área tocada.
