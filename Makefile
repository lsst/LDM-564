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


generated: featurelist.tex  gantt.tex meta.tex

all: $(tex) meta.tex acronyms.tex
	xelatex $(SRC)
	bibtex  LDM-564 
	xelatex $(SRC)
	xelatex $(SRC)

clean :
	latexmk -c
	rm -f *.pdf
	rm -f featurelist.tex
	rm -f gantt.tex
	rm -rf $(VENVDIR)

acronyms.tex: $(tex) myacronyms.tex
	$(TEXMFHOME)/../bin/generateAcronyms.py  $(tex)

venv: milestones/requirements.txt
	python3 -m venv $(VENVDIR)
	( \
		source $(VENVDIR)/bin/activate; \
		pip install -r milestones/requirements.txt; \
	)

featurelist.tex: bin/generate_release_list.py venv
	( \
		source $(VENVDIR)/bin/activate; \
		PYTHONPATH=milestones python3 bin/generate_release_list.py forecast\
	)

gantt.tex: milestones/milestones.py venv
	( \
		source $(VENVDIR)/bin/activate; \
		PYTHONPATH=milestones python3 milestones/milestones.py gantt --embedded --output $@ ;\
	)

.FORCE:

meta.tex: Makefile .FORCE
	rm -f $@
	touch $@
	echo '% GENERATED FILE -- edit this in the Makefile' >>$@
	/bin/echo '\newcommand{\vcsRevision}{$(GITVERSION)$(GITDIRTY)}' >>$@
	/bin/echo '\newcommand{\vcsDate}{$(GITDATE)}' >>$@
