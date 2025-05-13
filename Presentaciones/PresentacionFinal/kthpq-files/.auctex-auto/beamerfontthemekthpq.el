;; -*- lexical-binding: t; -*-

(TeX-add-style-hook
 "beamerfontthemekthpq"
 (lambda ()
   (TeX-add-to-alist 'LaTeX-provided-package-options
                     '(("kvoptions" "") ("fontspec" "no-math" "quiet") ("helvet" "scaled=.92") ("XCharter" "") ("inputenc" "utf8") ("unicode-math" "warnings-off={mathtools-colon, mathtools-overbracket}") ("sansmathfonts" "onlymath") ("fontenc" "OT1" "T1") ("mathastext" "italic")))
   (TeX-run-style-hooks
    "kvoptions"
    "fontspec"
    "helvet"
    "XCharter"
    "inputenc"
    "unicode-math"
    "fontenc"
    "sansmathfonts"
    "mathastext")
   (TeX-add-symbols
    "kthpq"
    "oldfamilydefault"))
 :latex)

