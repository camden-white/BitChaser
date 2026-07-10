.PHONY: install update notebook docs lint format run typecheck test coverage check ci fix deptree projtree trees precommit clean

RUN = uv run

install:
	uv sync
	$(MAKE) trees

update:
	uv lock --upgrade
	uv sync
	$(MAKE) trees

notebook:
	$(RUN) jupyter lab

docs:
	$(RUN) mkdocs serve

lint:
	$(RUN) ruff check .

format:
	$(RUN) ruff format .

run:
	$(RUN) python -m bitchaser.main

typecheck:
	$(RUN) mypy .

test:
	$(RUN) pytest

coverage:
	$(RUN) pytest --cov=bitchaser --cov-report=term-missing --cov-report=html

check: lint typecheck test
	$(RUN) ruff format --check .

ci: check coverage

fix:
	$(RUN) ruff check . --fix
	$(RUN) ruff format .

deptree:
	mkdir -p trees
	uv tree > trees/dep.txt

projtree:
	mkdir -p trees
	tree -I ".git|.venv|__pycache__|.mypy_cache|.pytest_cache|.ruff_cache|.ipynb_checkpoints" > trees/proj.txt

trees: deptree projtree

precommit:
	$(RUN) pre-commit run --all-files

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -name ".DS_Store" -delete
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	rm -rf .coverage htmlcov
	rm -rf .ipynb_checkpoints
