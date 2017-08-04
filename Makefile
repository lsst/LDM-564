#
#

SRC=$(wildcard LDM-*.tex)
tex=	$(SRC) body.tex features.tex

OBJ=$(SRC:.tex=.pdf)

all: $(tex)
	latexmk -bibtex -xelatex -f $(SRC)

clean :
	latexmk -c
	rm *.pdf



acronyms.tex :$(tex) myacronyms.tex
	acronyms.csh  $(tex)
