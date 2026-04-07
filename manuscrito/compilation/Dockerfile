FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    # Core LaTeX
    texlive-latex-base \
    texlive-latex-recommended \
    texlive-latex-extra \
    # Math & Science
    texlive-science \
    # Fonts
    texlive-fonts-recommended \
    texlive-fonts-extra \
    # Bibliography
    texlive-bibtex-extra \
    biber \
    # Spanish language
    texlive-lang-spanish \
    # Build tool
    latexmk \
    # Utilities
    make \
    && rm -rf /var/lib/apt/lists/*

# Packages included that the thesis uses:
#   tcolorbox, amsthm, float, graphicx, csvsimple,
#   booktabs, xparse, makecell, physics, amsmath,
#   hyperref, geometry, babel, biblatex, import

WORKDIR /workspace
