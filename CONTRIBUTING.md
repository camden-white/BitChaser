# Contributing to BitChaser

Thank you for your interest in contributing to BitChaser. This guide explains
how to set up the project, validate changes, and follow the repository's coding
standards.

## Development

### Workflow

1. `make fix`\
Auto-fix lint issues and format code to standards

2. `make precommit`\
Update trees, fix whitespace/newlines, run all hooks

3. `make ci`\
Run ci checks (lint, format check, type check, and run tests with coverage)

4. `git status` or `git diff` (optional)\
Review unstaged changes

5. `git add <files>`\
Stage files for commit

6. `git commit -m "[message]"`\
Commit files with message explaining change

7. `git push`\
Upload commits to GitHub

### Documentation

Build documentation (MkDocs)
```bash
make docs
```

Serve docs on local host (MkDocs)
```bash
make serve
```

### Makefile Commands

| Command | Description |
|---------|-------------|
| `help` | Explain Makefile targets |
| `install` | Install project dependencies |
| `update` | Upgrade dependencies |
| `report` | Copy updated report to Report/ |
| `notebook` | Launch Jupyter notebook in browser |
| `docs` | Build documentation |
| `serve` | Serve documentation |
| `lint` | Code linting |
| `lintfix` | Auto-fix lint issues |
| `formatcheck` | Check code format |
| `format` | Format code to standards |
| `fix` | Auto-fix lint issues and format code to standards |
| `typecheck` | Type checking |
| `static` | Run static checks |
| `test` | Run tests |
| `coverage` | Run tests with coverage report |
| `check` | Run static checks and run tests |
| `ci` | Run full CI validation |
| `deptree` | Make dependency tree |
| `projtree` | Make project tree |
| `trees` | Make all trees |
| `precommit` | Update trees, fix whitespace/newlines, run all hooks |
| `run` | Run the application |
| `clean` | Remove generated files |

### Coding Conventions

- Follow PEP 8 and use Ruff for formatting and linting with `make formatcheck`, `make lint`, and `make fix`.
- Add type hints to all public functions and methods, and check with `mypy`.
- Write concise docstrings for all public modules, classes, and functions.
- Keep code DRY.

---

## Project Structure

### Main Directories

| Directory | Description |
|---------|-------------|
| data/ | Raw and processed datasets |
| models/ | Saved trained models |
| reports/ | Figures and analysis |
| notebooks/ | Exploratory work |
| docs/ | Documentation (MkDocs) |
| scripts/ | Python scripts |
| src/ | Python package |
| tests/ | Unit tests |

For the complete project tree, see the
[project structure documentation](docs/reference/project-structure.md).

---
