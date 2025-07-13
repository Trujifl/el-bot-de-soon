VENV_DIR=.venv
PYTHON=$(VENV_DIR)/bin/python

.PHONY: install format serve venv

venv:
	@# Crea el entorno virtual con uv si no existe
	@test -d $(VENV_DIR) || uv venv $(VENV_DIR)

install: venv
	uv sync --python $(VENV_DIR)/bin/python --group dev

format:
	$(PYTHON) -m ruff format .
	$(PYTHON) -m isort .

serve:
	$(PYTHON) main.py
