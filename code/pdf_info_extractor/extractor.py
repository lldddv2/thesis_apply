"""
Pipeline de conversión de artículos científicos a Markdown
==========================================================
Convierte PDFs académicos a Markdown estructurado con:
  - Texto completo con jerarquía de títulos
  - Tablas en formato Markdown
  - Imágenes extraídas y referenciadas
  - Referencias bibliográficas

Instalación (ejecutar una sola vez):
    pip install marker-pdf pymupdf

Uso:
    python pdf_to_markdown_pipeline.py --input ./pdfs --output ./articulos

Estructura de salida:
    articulos/
    ├── paper_01_titulo/
    │   ├── paper_01_titulo.md
    │   └── images/
    │       ├── fig_1.png
    │       └── fig_2.png
    ├── paper_02_titulo/
    │   └── ...
    └── _indice.md   ← índice de todos los artículos con resumen rápido
"""

import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path
from datetime import datetime


# ─────────────────────────────────────────────
# EXTRACCIÓN CON MARKER-PDF
# ─────────────────────────────────────────────

def convertir_con_marker(pdf_path: Path, output_dir: Path) -> dict:
    """
    Convierte un PDF a Markdown usando marker-pdf >= 0.3 (API nueva).
    """
    try:
        from marker.converters.pdf import PdfConverter
        from marker.models import create_model_dict
        from marker.output import text_from_rendered
        from marker.config.parser import ConfigParser

        config = ConfigParser({"output_format": "markdown", "langs": "es,en"})
        models = create_model_dict()
        converter = PdfConverter(
            config=config.generate_config_dict(),
            artifact_dict=models,
            processor_list=config.get_processors(),
            renderer=config.get_renderer(),
        )
        rendered = converter(str(pdf_path))
        full_text, _, images = text_from_rendered(rendered)
        return {"markdown": full_text, "images": images, "metadata": {}, "method": "marker"}

    except ImportError:
        print("  [!] marker-pdf no encontrado. Usando PyMuPDF como fallback.")
        return convertir_con_pymupdf(pdf_path, output_dir)
    except Exception as e:
        print(f"  [!] marker falló: {e}. Usando PyMuPDF como fallback.")
        return convertir_con_pymupdf(pdf_path, output_dir)


# ─────────────────────────────────────────────
# FALLBACK: EXTRACCIÓN CON PYMUPDF
# ─────────────────────────────────────────────

def convertir_con_pymupdf(pdf_path: Path, output_dir: Path) -> dict:
    """
    Fallback: extrae texto e imágenes con PyMuPDF.
    Menor calidad estructural que marker, pero siempre disponible.
    """
    import fitz  # PyMuPDF

    doc = fitz.open(str(pdf_path))
    md_parts = []
    images = {}

    for page_num, page in enumerate(doc, start=1):
        # Texto de la página
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if block["type"] == 0:  # texto
                for line in block["lines"]:
                    text = " ".join(span["text"] for span in line["spans"]).strip()
                    if text:
                        # Heurística: texto grande → título
                        font_size = line["spans"][0]["size"] if line["spans"] else 12
                        if font_size > 14:
                            md_parts.append(f"\n## {text}\n")
                        else:
                            md_parts.append(text)

            elif block["type"] == 1:  # imagen
                img_index = len(images)
                img_name = f"fig_{page_num}_{img_index}.png"
                try:
                    xref = block.get("xref") or block.get("image", {}).get("xref")
                    if xref:
                        base_image = doc.extract_image(xref)
                        images[img_name] = base_image["image"]
                        md_parts.append(f"\n![Figura {img_index + 1}](images/{img_name})\n")
                except Exception:
                    pass

        md_parts.append("\n\n---\n\n")  # separador de página

    doc.close()
    return {
        "markdown": "\n".join(md_parts),
        "images": images,
        "metadata": {},
        "method": "pymupdf",
    }


# ─────────────────────────────────────────────
# GUARDAR RESULTADO
# ─────────────────────────────────────────────

def guardar_articulo(resultado: dict, pdf_path: Path, output_dir: Path) -> Path:
    """Guarda el Markdown e imágenes en una carpeta por artículo."""
    # Nombre de carpeta limpio
    nombre_base = limpiar_nombre(pdf_path.stem)
    carpeta = output_dir / nombre_base
    carpeta.mkdir(parents=True, exist_ok=True)
    images_dir = carpeta / "images"

    # Guardar Markdown
    md_file = carpeta / f"{nombre_base}.md"
    md_content = resultado["markdown"]

    # Añadir encabezado con metadatos
    header = f"""---
archivo_original: {pdf_path.name}
convertido: {datetime.now().strftime('%Y-%m-%d %H:%M')}
metodo: {resultado.get('method', 'desconocido')}
---

"""
    md_file.write_text(header + md_content, encoding="utf-8")

    # Guardar imágenes
    images = resultado.get("images", {})
    if images:
        images_dir.mkdir(exist_ok=True)
        for img_name, img_data in images.items():
            img_path = images_dir / img_name
            if isinstance(img_data, bytes):
                img_path.write_bytes(img_data)
            elif hasattr(img_data, "save"):  # PIL Image (marker)
                img_data.save(str(img_path))

    print(f"  ✓ Guardado: {carpeta.name}/ ({len(images)} imágenes)")
    return md_file


# ─────────────────────────────────────────────
# GENERAR ÍNDICE
# ─────────────────────────────────────────────

def generar_indice(articulos: list[dict], output_dir: Path):
    """Genera un _indice.md con resumen de todos los artículos procesados."""
    lines = [
        "# Índice de Artículos Científicos\n",
        f"*Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')} — {len(articulos)} artículos*\n",
        "\n| # | Archivo | Secciones detectadas | Imágenes | Estado |\n",
        "|---|---------|---------------------|----------|--------|\n",
    ]

    for i, art in enumerate(articulos, start=1):
        nombre = art["nombre"]
        secciones = art.get("secciones", 0)
        imagenes = art.get("imagenes", 0)
        estado = "✅" if art.get("ok") else "❌"
        md_link = f"[{nombre}](./{nombre}/{nombre}.md)"
        lines.append(f"| {i} | {md_link} | {secciones} | {imagenes} | {estado} |\n")

    indice_path = output_dir / "_indice.md"
    indice_path.write_text("".join(lines), encoding="utf-8")
    print(f"\n📋 Índice generado: {indice_path}")


# ─────────────────────────────────────────────
# UTILIDADES
# ─────────────────────────────────────────────

def limpiar_nombre(nombre: str) -> str:
    """Convierte un nombre de archivo a slug limpio."""
    nombre = nombre.lower()
    nombre = re.sub(r"[áàä]", "a", nombre)
    nombre = re.sub(r"[éèë]", "e", nombre)
    nombre = re.sub(r"[íìï]", "i", nombre)
    nombre = re.sub(r"[óòö]", "o", nombre)
    nombre = re.sub(r"[úùü]", "u", nombre)
    nombre = re.sub(r"[ñ]", "n", nombre)
    nombre = re.sub(r"[^a-z0-9_\-]", "_", nombre)
    nombre = re.sub(r"_+", "_", nombre).strip("_")
    return nombre[:80]  # máximo 80 chars


def contar_secciones(markdown: str) -> int:
    return len(re.findall(r"^#{1,3} .+", markdown, re.MULTILINE))


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Convierte artículos científicos en PDF a Markdown estructurado."
    )
    parser.add_argument(
        "--input", "-i",
        default="./pdfs",
        help="Carpeta con los PDFs (default: ./pdfs)",
    )
    parser.add_argument(
        "--output", "-o",
        default="./articulos",
        help="Carpeta de salida (default: ./articulos)",
    )
    parser.add_argument(
        "--metodo",
        choices=["marker", "pymupdf", "auto"],
        default="auto",
        help="Motor de conversión (default: auto → marker con fallback a pymupdf)",
    )
    parser.add_argument(
        "--forzar",
        action="store_true",
        help="Reconvertir artículos aunque ya existan en la salida",
    )
    args = parser.parse_args()

    input_dir = Path(args.input)
    output_dir = Path(args.output)

    if not input_dir.exists():
        print(f"❌ Carpeta de entrada no encontrada: {input_dir}")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    pdfs = sorted(input_dir.glob("*.pdf"))
    if not pdfs:
        print(f"❌ No se encontraron PDFs en: {input_dir}")
        sys.exit(1)

    print(f"\n🔬 Pipeline de artículos científicos")
    print(f"   Entrada : {input_dir} ({len(pdfs)} PDFs)")
    print(f"   Salida  : {output_dir}")
    print(f"   Método  : {args.metodo}\n")

    articulos = []
    errores = []

    for idx, pdf_path in enumerate(pdfs, start=1):
        nombre_base = limpiar_nombre(pdf_path.stem)
        destino = output_dir / nombre_base / f"{nombre_base}.md"

        print(f"[{idx:03d}/{len(pdfs)}] {pdf_path.name}")

        # Saltar si ya existe (a menos que --forzar)
        if destino.exists() and not args.forzar:
            print(f"  ⏭  Ya existe, omitiendo (usa --forzar para reconvertir)")
            md_text = destino.read_text(encoding="utf-8")
            articulos.append({
                "nombre": nombre_base,
                "secciones": contar_secciones(md_text),
                "imagenes": len(list((output_dir / nombre_base / "images").glob("*")) if (output_dir / nombre_base / "images").exists() else []),
                "ok": True,
            })
            continue

        try:
            # Conversión
            if args.metodo == "marker":
                resultado = convertir_con_marker(pdf_path, output_dir)
            elif args.metodo == "pymupdf":
                resultado = convertir_con_pymupdf(pdf_path, output_dir)
            else:  # auto
                resultado = convertir_con_marker(pdf_path, output_dir)

            # Guardar
            md_file = guardar_articulo(resultado, pdf_path, output_dir)
            md_text = md_file.read_text(encoding="utf-8")

            articulos.append({
                "nombre": nombre_base,
                "secciones": contar_secciones(md_text),
                "imagenes": len(resultado.get("images", {})),
                "ok": True,
            })

        except Exception as e:
            print(f"  ❌ Error: {e}")
            errores.append({"pdf": pdf_path.name, "error": str(e)})
            articulos.append({"nombre": nombre_base, "secciones": 0, "imagenes": 0, "ok": False})

    # Índice final
    generar_indice(articulos, output_dir)

    # Reporte
    exitosos = sum(1 for a in articulos if a["ok"])
    print(f"\n{'─'*50}")
    print(f"✅ Completados : {exitosos}/{len(pdfs)}")
    if errores:
        print(f"❌ Con errores : {len(errores)}")
        for err in errores:
            print(f"   - {err['pdf']}: {err['error']}")
    print(f"📁 Resultado en: {output_dir.resolve()}")


if __name__ == "__main__":
    main()