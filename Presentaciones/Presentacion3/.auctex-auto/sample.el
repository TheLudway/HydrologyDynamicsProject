;; -*- lexical-binding: t; -*-

(TeX-add-style-hook
 "sample"
 (lambda ()
   (TeX-add-to-alist 'LaTeX-provided-class-options
                     '(("beamer" "17pt" "t" "lualatex")))
   (TeX-add-to-alist 'LaTeX-provided-package-options
                     '(("amsmath" "") ("amssymb" "") ("mathtools" "") ("babel" "spanish") ("biblatex" "") ("hyperref" "") ("xurl" "") ("svg" "") ("listings" "") ("ccicons" "scale=7")))
   (add-to-list 'LaTeX-verbatim-environments-local "semiverbatim")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "href")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "hyperimage")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "hyperbaseurl")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "nolinkurl")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "url")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "path")
   (add-to-list 'LaTeX-verbatim-macros-with-delims-local "path")
   (TeX-run-style-hooks
    "latex2e"
    "beamer"
    "beamer10"
    "amsmath"
    "amssymb"
    "mathtools"
    "babel"
    "biblatex"
    "hyperref"
    "xurl"
    "svg"
    "listings"
    "ccicons")
   (LaTeX-add-bibliographies
    "referencias")
   (LaTeX-add-xcolor-definecolors
    "white"
    "sand"
    "KTHblue"
    "skyblue"
    "navy"
    "lightblue"
    "digitalblue"))
 :latex)

