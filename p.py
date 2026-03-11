# Pega esto en una terminal Python o archivo .py y ejecuta
from marker.convert import convert_single_pdf  # API vieja
# Si da ImportError, tienes v0.3+

from marker.converters.pdf import PdfConverter  # API nueva
# Si da ImportError, tienes v0.2.x