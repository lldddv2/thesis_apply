# Configuración de latexmk para el manuscrito A&A.
#
# aa.cls, aa.bst y linenoaa.sty viven en class/ para no ensuciar la raíz.
# LaTeX no busca ahí por defecto, así que se extienden las rutas de búsqueda.
# El «//» final significa «y subdirectorios»; los «:» iniciales/finales
# preservan las rutas del sistema.

$ENV{'TEXINPUTS'} = './class//:' . ($ENV{'TEXINPUTS'} // '') . ':';
$ENV{'BSTINPUTS'} = './class//:' . ($ENV{'BSTINPUTS'} // '') . ':';
$ENV{'BIBINPUTS'} = '.:' . ($ENV{'BIBINPUTS'} // '') . ':';

$pdf_mode = 1;          # pdflatex
$bibtex_use = 2;        # correr bibtex y borrar el .bbl al limpiar

# Los subproductos van a build/local/; el PDF también.
# build/submission/ lo genera tools/flatten.py y no se toca aquí.
$out_dir = 'build/local';

# .obj: lista de objetos astronómicos que genera \object{}. Revisarla.
push @generated_exts, 'obj';
