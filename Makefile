#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_NAME = mBank Hacker
PYTHON_VERSION = 3.13
PYTHON_INTERPRETER = python3

#################################################################################
# COMMANDS                                                                      #
#################################################################################


## Install Python Dependencies
.PHONY: requirements
requirements:
	uv sync

## Delete all compiled Python files
.PHONY: clean
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete

## Lint using flake8 and black (use `make format` to do formatting)
.PHONY: lint
lint:
	flake8 src
	black --check --config pyproject.toml src

## Format source code with black
.PHONY: format
format:
	black --config pyproject.toml src


## Set up python interpreter environment
.PHONY: create_environment
create_environment:
	$(PYTHON_INTERPRETER) -m pip install uv
	uv venv

## Serve documentation
.PHONY: docs_serve
docs_serve:
	cd docs && mkdocs serve

## Build documentation
.PHONY: docs_build
docs_build:
	cd docs && mkdocs build

#################################################################################
# PROJECT RULES                                                                 #
#################################################################################


## Run app for evaluation
.PHONY: run_evaluation
run_evaluation:
	uv run src/app.py

## Run main script
.PHONY: run
run:
	uv run src/main.py


#################################################################################
# Self Documenting Commands                                                     #
#################################################################################

.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys; \
lines = '\n'.join([line for line in sys.stdin]); \
matches = re.findall(r'\n## (.*)\n[\s\S]+?\n([a-zA-Z_-]+):', lines); \
print('Available rules:\n'); \
print('\n'.join(['{:25}{}'.format(*reversed(match)) for match in matches]))
endef
export PRINT_HELP_PYSCRIPT

help:
	@$(PYTHON_INTERPRETER) -c "${PRINT_HELP_PYSCRIPT}" < $(MAKEFILE_LIST)
