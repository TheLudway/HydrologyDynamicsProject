;; -*- lexical-binding: t; -*-

(TeX-add-style-hook
 "beamerouterthemekthpq"
 (lambda ()
   (TeX-add-to-alist 'LaTeX-provided-package-options
                     '(("tikz" "") ("graphicx" "") ("adjustbox" "") ("calc" "")))
   (TeX-run-style-hooks
    "tikz"
    "graphicx"
    "adjustbox"
    "calc")
   (TeX-add-symbols
    '("setfootline" 3)
    '("deffootline" 4)
    "insertframetitle"
    "insertframesubtitle")
   (LaTeX-add-lengths
    "smalllogowidth"
    "outermargin"
    "headerwidth"))
 :latex)

