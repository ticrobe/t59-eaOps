# Shortcuts for validating, previewing and building. Run `make help` to list them.
# Targets that need Python create .venv and install tools/requirements.txt on first
# use, so a fresh clone works without manual setup (needs python3 and make).

VENV := .venv
PY := $(VENV)/bin/python

.DEFAULT_GOAL := help
.PHONY: help setup check preview clean

help:
	@echo "make setup     create .venv and install the requirements (other targets do this automatically)"
	@echo "make check     validate content/*.yaml"
	@echo "make preview   build preview/eaOps.html and preview/eaOps.png (dist/ is not touched)"
	@echo "make clean     delete preview/"

$(VENV)/.installed: tools/requirements.txt
	python3 -m venv $(VENV)
	$(PY) -m pip install --quiet --disable-pip-version-check -r tools/requirements.txt
	touch $@

setup: $(VENV)/.installed

check: setup
	$(PY) tools/build_html.py --check

preview: setup
	mkdir -p preview
	$(PY) tools/build_block_diagram.py --out preview/eaOps.png --force
	$(PY) tools/build_html.py --out preview/eaOps.html --force
	@echo "Open preview/eaOps.html in a browser."

clean:
	rm -rf preview
