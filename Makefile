# Code Guard task runner. GNU make on Windows (cmd) and Linux/macOS (sh).
# Override the bootstrap interpreter if needed:  make setup PYTHON=python

ifeq ($(OS),Windows_NT)
    PYTHON ?= py -V:3.11
    VENV_PY := .venv/Scripts/python.exe
    RUN := $(subst /,\,$(VENV_PY))
else
    PYTHON ?= python3.11
    VENV_PY := .venv/bin/python
    RUN := $(VENV_PY)
endif

.PHONY: help setup lint format test check-env data baseline mvp-eval

help:
	@echo Targets: setup lint format test check-env data baseline mvp-eval

$(VENV_PY):
	$(PYTHON) -m venv .venv

setup: $(VENV_PY)
	$(RUN) -m pip install --upgrade pip
	$(RUN) -m pip install -e ".[dev]"
	$(RUN) -m pre_commit install

lint:
	$(RUN) -m ruff check .
	$(RUN) -m black --check .

format:
	$(RUN) -m ruff check --fix .
	$(RUN) -m black .

test:
	$(RUN) -m pytest -m "not slow"

check-env:
	$(RUN) scripts/check_env.py

data:
	@echo make data: not implemented yet - Phase 3

baseline:
	@echo make baseline: not implemented yet - Phase 1

mvp-eval:
	@echo make mvp-eval: not implemented yet - Phase 2
