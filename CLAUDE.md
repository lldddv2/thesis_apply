# Tesis — Convenciones de notebooks

## Tablas de resultados

- SIEMPRE usar `pandas.DataFrame` para mostrar resultados tabulares en notebooks.
- NUNCA construir tablas con f-strings (`f"{x:>10.6f}"`, `print("-" * N)`, etc.).
- La última línea de la celda debe ser el DataFrame mismo (display HTML), no `print(df)`.
- Si hace falta exportar: `df.to_markdown()` o `df.to_latex()`.

Razón: las tablas en f-string son frágiles (alineación rompe con valores grandes/notación científica), no son reutilizables y rompen pipelines downstream (no se puede `.to_csv`, `.plot`, indexar).

## Comparaciones analítico vs numérico

- Integración numérica debe cubrir **una sola órbita** (`t ∈ [0, 1.2·P]`) cuando se compara con expresiones analíticas integradas de `f₀` a `f₀+2π` (Dayem 2025, etc.).
- Detección de pericentros: `scipy.signal.find_peaks` sobre `-r(t)` cartesiano. Si `f=0` en condiciones iniciales, agregar `idx=0` manualmente.
- Medir como `np.unwrap(...)[i1] - np.unwrap(...)[i0]` — nunca acumular `N` órbitas y promediar (mezcla timescales orbital y secular de Dayem).
