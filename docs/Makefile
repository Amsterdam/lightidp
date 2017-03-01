# Minimal makefile for Sphinx documentation


# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
SPHINXPROJ    = DatapuntAuthenticationAuthorization
SOURCEDIR     = .
BUILDDIR      = _build


.PHONY: help


# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)


# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
#
# Don't understand what's happening here. Why the dependency on 'Makefile'?
# What's the new "make mode" option? Is it something from Sphinx or from make?
# --PvB
%: Makefile
	$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
