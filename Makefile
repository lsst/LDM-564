GITVERSION := $(shell git log -1 --date=short --pretty=%h)
GITDATE := $(shell git log -1 --date=short --pretty=%ad)
GITSTATUS := $(shell git status --porcelain)
ifneq "$(GITSTATUS)" ""
	GITDIRTY = -dirty
endif

export TEXMFHOME = lsst-texmf/texmf
VENVDIR = venv

SRC=$(wildcard LDM-*.tex)
tex=$(SRC) body.tex features.tex featurelist.tex gantt.tex

OBJ=$(SRC:.tex=.pdf)

all: $(tex) meta.tex
	latexmk -bibtex -xelatex -f $(SRC)

clean :
	latexmk -c
	rm *.pdf
	rm -rf $(VENVDIR)

acronyms.tex :$(tex) myacronyms.tex
	acronyms.csh  $(tex)

venv: milestones/requirements.txt
	python3 -m venv $(VENVDIR)
	( \
		source $(VENVDIR)/bin/activate; \
		pip install -r milestones/requirements.txt; \
	)

featurelist.tex: milestones/milestones.py venv
	( \
		source $(VENVDIR)/bin/activate; \
		python3 milestones/milestones.py ldm564 --releases $@ ; \
	)

gantt.tex: milestones/milestones.py venv
	( \
		source $(VENVDIR)/bin/activate; \
		python3 milestones/milestones.py ldm564 --gantt $@ ; \
	)

.FORCE:

meta.tex: Makefile .FORCE
	rm -f $@
	touch $@
	echo '% GENERATED FILE -- edit this in the Makefile' >>$@
	/bin/echo '\newcommand{\vcsRevision}{$(GITVERSION)$(GITDIRTY)}' >>$@
	/bin/echo '\newcommand{\vcsDate}{$(GITDATE)}' >>$@
