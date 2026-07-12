## Development

### Workflow
1. `make fix`\
Auto-fix lint issues and format code to standards

2. `make check` + `make test` (or `make ci`)\
Lint, format check, type check, and run tests (with coverage)

3. `make precommit`\
update trees, fix whitespace/newlines, run all hooks

4. `git status` (optional)\
Review unstaged changed files

5. `git diff` (optional)\
Review any unstaged changes (q to exit)

6. `git add <files>`\
Add files for commit

7. `git commit -m "[message]"`\
Commit files with message explaining change

8. `git push`\
Upload local commits to GitHub

9. `git log` (optional)\
Review commit logs

### Makefile Commands

| Command | Description |
|---------|-------------|
| `help` | Explain Makefile targets |
| `install` | Install project dependencies |
| `update` | Upgrade dependencies |
| `notebook` | Jupyter notebook |
| `docs` | Build documentation |
| `serve` | Serve documentation |
| `lint` | Code linting |
| `lintfix` | Auto-fix lint issues |
| `formatcheck` | Check code format |
| `format` | Format code to standards |
| `typecheck` | Type checking |
| `fix` | Auto-fix lint issues and format code to standards |
| `check` | Lint, format check, and type check |
| `test` | Run tests |
| `coverage` | Run tests with coverage report |
| `ci` | Run checks and coverage |
| `deptree` | Make dependency tree |
| `projtree` | Make project tree |
| `trees` | Make all trees |
| `precommit` | Update trees, fix whitespace/newlines, run all hooks |
| `run` | Run the application |
| `clean` | Remove generated files |

### Coding Conventions

- Follow PEP 8 and use Ruff for formatting and linting with `make formatcheck`, `make lint`, and `make fix`.
- Add type hints to all public functions and methods.
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
| src/ | Python package |
| tests/ | Unit tests |

### Project Tree

<!-- PROJECT_TREE_START -->
```text
.
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── Makefile
├── README.md
├── data
│   ├── processed
│   └── raw
│       └── BTCUSD_OHLC.csv
├── docs
│   └── index.md
├── mkdocs.yaml
├── models
├── notebooks
├── pyproject.toml
├── reports
│   └── figures
├── scripts
│   └── update_section.py
├── src
│   └── bitchaser
│       ├── __init__.py
│       ├── config.py
│       ├── data
│       │   ├── __init__.py
│       │   ├── load.py
│       │   └── preprocess.py
│       ├── evaluation
│       │   ├── __init__.py
│       │   └── metrics.py
│       ├── features
│       │   ├── __init__.py
│       │   └── indicators.py
│       ├── inference
│       │   ├── __init__.py
│       │   └── predict.py
│       ├── main.py
│       ├── models
│       │   ├── __init__.py
│       │   ├── neural_net.py
│       │   └── statistical.py
│       ├── training
│       │   ├── __init__.py
│       │   └── train.py
│       └── utils.py
├── tests
│   ├── __init__.py
│   ├── test_data.py
│   ├── test_features.py
│   └── test_models.py
└── uv.lock

```
<!-- PROJECT_TREE_END -->

---
