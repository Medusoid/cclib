# Makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = python -msphinx
SPHINXPROJ    = cclib
SOURCEDIR     = .
BUILDDIR      = _build

# Put it first so that "make" without argument is like "make help".
.PHONY: help Makefile
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O) && exit 2

.PHONY: default
default: cclib update attributes coverage html

clean:
	-rm -rf $(BUILDDIR)/*
	-rm -rf cclib*
	-rm -rf attributes*.rst
	-rm -rf coverage*.rst

# When releasing a new version, this can't be updated until after the tag is pushed.
PRODUCTION_VERSION = v1.8.1
CCLIB_PROD = $(BUILDDIR)/cclib_prod
#CCLIB_DEV = $(realpath $(SOURCEDIR)/../..)
CCLIB_DEV = $(SOURCEDIR)/../..
SRC_PROD = $(CCLIB_PROD)/cclib
SRC_DEV = $(CCLIB_DEV)/cclib

# Have the production and master in two separate directories so that
# dependencies are triggered correctly. If we had one, it would not
# work correctly, since git updates timestamps on each checkout, which
# would trigger some targets unnecessarily.
.PHONY: cclib
cclib: $(CCLIB_PROD)
$(CCLIB_PROD):
	@echo "Checking out prod..."
	git clone https://github.com/cclib/cclib.git $@
	cd $(CCLIB_PROD); git checkout $(PRODUCTION_VERSION)

.PHONY: update update_prod
update: update_prod
update_prod:
	@echo "Updating prod..."
	cd $(CCLIB_PROD); git checkout $(PRODUCTION_VERSION); git fetch --all --tags
	cd $(CCLIB_PROD); find . -name "*.pyc" -delete

# Since we have two separate directories, 'checking out' a branch actually
# means making a symlink to the appropriate directory, because scripts should be
# impervious to this Makefile and will import from always the same name (cclib).
#
# Because there are parts of the codebase that are generated at build time,
# such as the version, a clean checkout requires an additional step.
#
# Even though the `build` package runs with venv isolation by default, it will
# place the autogenerated files in the source tree.
.PHONY: checkout_prod checkout_dev
checkout_prod:
	python -m build --sdist $(CCLIB_PROD)
	# Install test dependencies.
	cd "$(CCLIB_PROD)"; python -m pip install -e .[test]
	ln -fs $(SRC_PROD) cclib
checkout_dev:
	python -m build --sdist $(CCLIB_DEV)
	# Install test dependencies.
	cd "$(CCLIB_DEV)"; python -m pip install -e .[test]
	ln -fs $(SRC_DEV) cclib

# We need three layers of targets in order to always get the checkout
# to execute, but the actual file-generating target to run only if the
# appropriate files have been updated (resolved via the right symlink).
.PHONY: attributes
attributes: attributes.rst attributes_dev.rst
attributes.rst: attributes.py $(SRC_PROD)/parser/data.py
	@echo "Generating prod attributes..."
	@$(MAKE) --no-print-directory checkout_prod
	python attributes.py > $@
	-rm cclib
attributes_dev.rst: attributes.py $(SRC_DEV)/parser/data.py
	@echo "Generating dev attributes..."
	@$(MAKE) --no-print-directory checkout_dev
	python attributes.py > $@
	-rm cclib

# Same as above, we need three layers of targets, since this script
# especially takes some time as it performs all the tests.
.PHONY: coverage
coverage: coverage.rst coverage_dev.rst
coverage.rst: generate_coverage.py $(wildcard $(SRC_PROD)/parser/*parser.py) $(wildcard $(CCLIB_PROD)/test/*.py)
	@echo "Generating prod coverage..."
	@$(MAKE) --no-print-directory checkout_prod
	python generate_coverage.py $(CCLIB_PROD) > $@
	-rm cclib
coverage_dev.rst: generate_coverage.py $(wildcard $(SRC_DEV)/parser/*parser.py) $(wildcard $(CCLIB_DEV)/test/*.py)
	@echo "Generating dev coverage..."
	@$(MAKE) --no-print-directory checkout_dev
	python generate_coverage.py "$(realpath $(CCLIB_DEV))" > $@
	-rm cclib

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
# %: Makefile
# 	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# We can't use the default catch-all target, because it traps our
# custom targets that don't use Sphinx, like `attributes`, but it's
# still needed for our specific Sphinx build type.
.PHONY: html
html: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
