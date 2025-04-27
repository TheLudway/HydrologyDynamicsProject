;; -*- lexical-binding: t; -*-

(TeX-add-style-hook
 "beamerinnerthemekthpq"
 (lambda ()
   (TeX-add-to-alist 'LaTeX-provided-package-options
                     '(("tikz" "") ("graphicx" "") ("adjustbox" "")))
   (TeX-run-style-hooks
    "tikz"
    "graphicx"
    "adjustbox")
   (TeX-add-symbols
    "insertendpage"
    "titlelogofilename"
    "sectionlinesfilename"
    "bodylinesfilename"
    "linessoutheasti"
    "lineseast"
    "linesnortheast"
    "linesnorthwest"
    "linessoutheastii"
    "linessoutheast"
    "insertlines"
    "linesfilename"
    "oldinsertblocktitle"
    "insertblocktitle")
   (LaTeX-add-environments
    "titlelinesfilename")
   (LaTeX-add-lengths
    "largelogowidth"
    "innermargin"))
 :latex)

