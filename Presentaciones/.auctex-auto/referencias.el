;; -*- lexical-binding: t; -*-

(TeX-add-style-hook
 "referencias"
 (lambda ()
   (LaTeX-add-bibitems
    "openstreetmap_magdalena2025"
    "deaton1999dynamic"
    "waterwaymap2025"
    "quickosm2025"
    "qgis2025"))
 '(or :bibtex :latex))

