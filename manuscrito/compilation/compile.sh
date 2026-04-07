#!/usr/bin/env bash
set -euo pipefail

# Asegurar que docker-credential-desktop esté en PATH (necesario al correr desde VS Code)
export PATH="/Applications/Docker.app/Contents/Resources/bin:/usr/local/bin:/opt/homebrew/bin:$PATH"

# Paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MANUSCRITO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
WORKSPACE="$(cd "$MANUSCRITO_DIR/.." && pwd)"
BUILD_DIR="$SCRIPT_DIR/build"
IMAGE_NAME="thesis-latex"

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
    docker build -t "$IMAGE_NAME" "$SCRIPT_DIR"
    echo ""
    echo "✓ Imagen lista."
fi

# 3. Compilar
echo ""
echo "📄 Compilando..."
echo ""

docker run --rm \
    -v "$WORKSPACE:/workspace" \
    -w "/workspace/manuscrito/docs" \
    "$IMAGE_NAME" \
    latexmk \
        -pdf \
        -interaction=nonstopmode \
        -file-line-error \
        -output-directory="/workspace/manuscrito/compilation/build" \
        main.tex

# 4. Copiar PDF final
if [ -f "$BUILD_DIR/main.pdf" ]; then
    cp "$BUILD_DIR/main.pdf" "$MANUSCRITO_DIR/latest.pdf"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "✅ Listo: manuscrito/latest.pdf"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
else
    echo ""
    echo "❌ No se encontró el PDF. Revisa los errores arriba."
    exit 1
fi
