# BitChaser

![Python](https://img.shields.io/badge/Python-3.14-blue)
![mypy](https://img.shields.io/badge/Type%20Checking-mypy-yellow)
![Ruff](https://img.shields.io/badge/Lint-Ruff-red)
![Docs](https://img.shields.io/badge/Docs-MkDocs-526CFE)
![Status](https://img.shields.io/badge/Status-Active%20Development-orange)
![License](https://img.shields.io/badge/License-Apache%202.0-green)

<!-- Description -->
BitChaser is a research project that investigates long-horizon and short-horizon forecasting of the price of Bitcoin (BTC/USD) using periodic regressions for long-horizon modeling and time-series analysis for short-horizon forcasting. The project analyzes historical daily OHLC data and relevant financial statistics.

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
git clone https://github.com/camden-white/BitChaser.git
cd BitChaser
```

Install dependencies

```bash
make install
```

---

## Usage

Run the BitChaser application

```bash
make run
```

Launch Jupyter in browser

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
Source: [Kaggle](https://www.kaggle.com/datasets/priyamchoksi/bitcoin-historical-prices-and-activity-2010-2024?resource=download&select=bitcoin_2010-07-17_2024-06-28.csv)

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

See [`LICENSE`](LICENSE) for details.

---

## Author

Camden R. White

University of California, Los Angeles\
*M.A.S. Applied Statistics & Data Science*

Oregon State University\
*B.S. Mathematics*

---
