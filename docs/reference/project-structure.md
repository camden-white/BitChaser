🚧 Active development

---

## Project Tree

<!-- PROJECT_TREE_START -->
```text
.
├── CHANGELOG.md
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── LICENSE
├── Makefile
├── README.md
├── SECURITY.md
├── data
│   ├── archive
│   │   ├── BTC_BLOCKCHAIN_DAILY.parquet
│   │   └── BTC_BLOCKCHAIN_DAILY_RAW.parquet
│   ├── processed
│   │   └── btc_daily_latest.parquet
│   ├── raw
│   │   └── cryptocompare_btc_usd_daily.parquet
│   ├── research
│   │   └── btc_daily_2010-07-17_2026-07-17.parquet
│   └── snapshot
│       └── btc_daily_2010-07-17_2026-07-27.parquet
├── docs
│   ├── about.md
│   ├── assets
│   │   └── images
│   │       ├── BitChaser_logo.svg
│   │       └── favicon-v3.webp
│   ├── index.md
│   ├── reference
│   │   ├── configuration.md
│   │   └── project-structure.md
│   ├── research
│   │   ├── data.md
│   │   ├── evaluation.md
│   │   ├── index.md
│   │   ├── methodology.md
│   │   └── models.md
│   ├── results
│   │   ├── index.md
│   │   ├── long.md
│   │   └── short.md
│   └── stylesheets
│       └── extra.css
├── mkdocs.yaml
├── models
├── notebooks
│   ├── 00_data_archive.ipynb
│   └── 01_data_exploration.ipynb
├── pyproject.toml
├── reports
│   ├── Report.pdf
│   ├── figures
│   └── latex
│       ├── build
│       │   ├── report.aux
│       │   ├── report.bbl
│       │   ├── report.blg
│       │   ├── report.fdb_latexmk
│       │   ├── report.fls
│       │   ├── report.log
│       │   ├── report.out
│       │   ├── report.pdf
│       │   ├── report.synctex.gz
│       │   ├── report.toc
│       │   └── sections
│       ├── preamble.tex
│       ├── references.bib
│       ├── report.tex
│       └── sections
│           ├── abstract.tex
│           ├── background.tex
│           ├── conclusion.tex
│           ├── data.tex
│           ├── discussion.tex
│           ├── exploratory.tex
│           ├── introduction.tex
│           ├── methods.tex
│           ├── models.tex
│           └── results.tex
├── scripts
│   ├── create_plots.py
│   ├── create_snapshot.py
│   ├── update_data.py
│   └── update_section.py
├── src
│   └── bitchaser
│       ├── __init__.py
│       ├── config.py
│       ├── data
│       │   ├── __init__.py
│       │   ├── cryptocompare.py
│       │   ├── load.py
│       │   ├── preprocess.py
│       │   └── update.py
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
│       │   ├── long.py
│       │   └── short.py
│       ├── py.typed
│       ├── training
│       │   ├── __init__.py
│       │   └── train.py
│       └── utils.py
├── tests
│   ├── __init__.py
│   ├── data
│   │   └── test_preprocess.py
│   ├── test_data.py
│   ├── test_features.py
│   ├── test_models.py
│   └── test_package.py
└── uv.lock

```
<!-- PROJECT_TREE_END -->

---
