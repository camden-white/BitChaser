# BitChaser

![Python](https://img.shields.io/badge/Python-3.14-blue)
![mypy](https://img.shields.io/badge/Type%20Checking-mypy-yellow)
![Ruff](https://img.shields.io/badge/Lint-Ruff-red)
![Docs](https://img.shields.io/badge/Docs-MkDocs-526CFE)
![Status](https://img.shields.io/badge/Status-Active%20Development-orange)
![License](https://img.shields.io/badge/License-Apache%202.0-green)

<!-- Description -->
BitChaser is a research project that investigates long-horizon and short-horizon forecasting of the Bitcoin (BTC/USD) market using statistical modeling and deep learning. The project analyzes historical daily OHLC data, develops interpretable long-horizon forecasting models along with short-horizon time-series prediction models.

## Status

🚧 Active development. Core project structure is complete; forecasting models are currently under implementation.

## Features

- Historical Bitcoin OHLC analysis
- Statistical forecasting models
- Data visualization
- Reproducible research workflow
- Documentation with MkDocs

## Research Objectives

BitChaser investigates questions including:

- Can Bitcoin support and resistance be modeled statistically?
- What periodic structures exist in BTC/USD?
- How accurately can daily OHLC values be forecast?

---

## Installation

### Requirements
- Python 3.14
- uv

### Steps

Clone the repository

```bash
git clone https://github.com/camden-white/bitchaser.git
cd bitchaser
```

Install dependencies

```bash
make install
```

---

## Usage

Run the main program

```bash
make run
```

Launch Jupyter

```bash
make notebook
```

Serve documentation (built with MkDocs)

```bash
make serve
```

---

## Technologies

- MkDocs
- mypy
- pytest
- Python
- Ruff
- uv

---

## Data

Historical daily BTC/USD OHLC data from July 2010 through June 2024 is stored in
`data/raw/BTCUSD_OHLC.csv`.

---

## Roadmap

- [ ] Support/resistance analysis
- [ ] Periodic analysis
- [ ] Regression analysis
- [ ] Long-horizon forecasting
- [ ] Daily OHLC analysis
- [ ] OHLC next-day prediction
- [ ] OHLC multi-day prediction

---

## License

Licensed under the Apache 2.0 License.

See `LICENSE` for details.

---

## Author

Camden R. White

University of California, Los Angeles\
*M.A.S. Applied Statistics & Data Science*

Oregon State University\
*B.S. Mathematics*

---
