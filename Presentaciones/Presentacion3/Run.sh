#!/usr/bin/env sh

lualatex sample.tex
biber sample
lualatex sample.tex
lualatex sample.tex
