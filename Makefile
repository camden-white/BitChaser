.DEFAULT_GOAL := help

.PHONY: install update notebook docs serve lint lintfix formatcheck format fix typecheck test coverage check ci deptree projtree trees precommit run clean

.DELETE_ON_ERROR:

MAN = uv
RUN = $(MAN) run
PYTHON = $(RUN) python
RUFF = $(RUN) ruff
PYTEST = $(RUN) pytest
MYPY = $(RUN) mypy

UPDATE_SECTION = $(PYTHON) scripts/update_section.py

help:
	@echo "Available targets:"
	@echo "  help         Print Makefile targets"
	@echo "  install      Install project dependencies"
	@echo "  update       Upgrade dependencies"
	@echo "  notebook     Jupyter notebook"
	@echo "  docs         Build documentation"
	@echo "  serve        Serve documentation"
	@echo "  lint         Code linting"
	@echo "  lintfix      Auto-fix lint issues"
	@echo "  formatcheck  Check code format"
	@echo "  format       Format code to standards"
	@echo "  fix          Auto-fix lint issues and format code to standards"
	@echo "  typecheck    Type checking"
	@echo "  test         Run tests"
	@echo "  coverage     Run tests with coverage report"
	@echo "  check        Lint, format check, type check, and run tests"
	@echo "  ci           Lint, format check, type check, and run tests with coverage report"
	@echo "  deptree      Make dependency tree"
	@echo "  projtree     Make project tree"
	@echo "  trees        Make all trees"
	@echo "  precommit    Update trees, fix whitespace/newlines, run all hooks"
	@echo "  run          Run the application"
	@echo "  clean        Remove generated files"

install:
	$(MAN) sync
	$(RUN) pre-commit install
	$(MAKE) trees

update:
	$(MAN) lock --upgrade
	$(MAN) sync
	$(MAKE) trees

notebook:
	$(RUN) jupyter lab

docs:
	$(RUN) mkdocs build --strict

serve:
	$(RUN) mkdocs serve

lint:
	$(RUFF) check .

lintfix:
	$(RUFF) check . --fix

formatcheck:
	$(RUFF) format --check .

format:
	$(RUFF) format .

fix: lintfix format

typecheck:
	$(MYPY) .

test:
	$(PYTEST)

coverage:
	$(PYTEST) \
		--cov=bitchaser \
		--cov-report=term-missing \
		--cov-report=html

check: lint formatcheck typecheck test

ci: lint formatcheck typecheck coverage docs

deptree:
	mkdir -p trees
	$(MAN) tree > trees/dep.txt

projtree:
	tree \
	-I "site|trees|.venv|.git|.mypy_cache|.pytest_cache|.ruff_cache|__pycache__|htmlcov" \
	> trees/proj.txt --noreport

trees: deptree projtree
	$(UPDATE_SECTION) CONTRIBUTING.md PROJECT_TREE trees/proj.txt --fence text

precommit: trees
	$(RUN) pre-commit run --all-files

run:
	$(RUN) bitchaser

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type f -name "*.py[co]" -delete
	find . -type f -name ".DS_Store" -delete
	find . -type d -name ".ipynb_checkpoints" -prune -exec rm -rf {} +
	find . -type f -name "*.nbconvert.ipynb" -delete
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	rm -rf .coverage htmlcov
	rm -rf dist build *.egg-info
	rm -rf site
# 	rm -rf trees
