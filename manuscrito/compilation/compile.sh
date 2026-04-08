#!/usr/bin/env bash

# Asegurar que docker-credential-desktop esté en PATH (necesario al correr desde VS Code)
export PATH="/Applications/Docker.app/Contents/Resources/bin:/usr/local/bin:/opt/homebrew/bin:$PATH"

# Paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MANUSCRITO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
WORKSPACE="$(cd "$MANUSCRITO_DIR/.." && pwd)"
BUILD_DIR="$SCRIPT_DIR/build"
IMAGE_NAME="thesis-latex"
TEX_FLAGS="-pdf -interaction=nonstopmode -file-line-error -output-directory=/workspace/manuscrito/compilation/build"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Compilador LaTeX — Tesis"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 1. Verificar que Docker esté corriendo
if ! docker info &>/dev/null 2>&1; then
    echo ""
    echo "⚠️  Docker no está activo."
    echo ""
    echo "  Por favor, inicia Docker Desktop e intenta de nuevo."
    echo "  → Abre Docker Desktop desde Applications o ejecuta:"
    echo "    open -a Docker"
    echo ""
    exit 1
fi

# 2. Construir imagen si no existe
if ! docker image inspect "$IMAGE_NAME" &>/dev/null 2>&1; then
    echo "🔨 Construyendo imagen Docker de LaTeX..."
    echo "   (primera vez — puede tomar 5-10 minutos)"
    echo ""
    docker build -t "$IMAGE_NAME" "$SCRIPT_DIR" || { echo "❌ Error construyendo imagen Docker."; exit 1; }
    echo ""
    echo "✓ Imagen lista."
fi

# Helper: corre un comando dentro del contenedor
run_latex() {
    docker run --rm \
        --memory=6g \
        -v "$WORKSPACE:/workspace" \
        -w "/workspace/manuscrito/docs" \
        "$IMAGE_NAME" \
        "$@"
}

# 3. Compilación en 3 pasos
echo ""
echo "  Paso 1/3 — pdflatex (primera pasada)..."
run_latex pdflatex -interaction=nonstopmode -file-line-error \
    -output-directory=/workspace/manuscrito/compilation/build \
    main.tex
echo "  ✓ Paso 1 listo"

echo ""
echo "  Paso 2/3 — biber (bibliografía)..."
run_latex biber --input-directory=/workspace/manuscrito/docs \
    /workspace/manuscrito/compilation/build/main || true
echo "  ✓ Paso 2 listo"

echo ""
echo "  Paso 3/3 — pdflatex (pasadas finales para referencias)..."
run_latex pdflatex -interaction=nonstopmode -file-line-error \
    -output-directory=/workspace/manuscrito/compilation/build \
    main.tex
run_latex pdflatex -interaction=nonstopmode -file-line-error \
    -output-directory=/workspace/manuscrito/compilation/build \
    main.tex
echo "  ✓ Paso 3 listo"

echo ""

# 4. Verificar y copiar PDF
PDF="$BUILD_DIR/main.pdf"
if [ ! -f "$PDF" ]; then
    echo "❌ No se generó ningún PDF."
    echo "   Log: manuscrito/compilation/build/main.log"
    exit 1
fi

PDF_SIZE=$(wc -c < "$PDF")
cp "$PDF" "$MANUSCRITO_DIR/latest.pdf"

if [ "$PDF_SIZE" -lt 10000 ]; then
    echo "⚠️  El PDF parece incompleto (${PDF_SIZE} bytes) — revisa:"
    echo "   manuscrito/compilation/build/main.log"
    echo ""
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Listo: manuscrito/latest.pdf"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
