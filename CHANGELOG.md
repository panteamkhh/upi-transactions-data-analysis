# Changelog

All notable changes to this project are documented here.
This project adheres to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-09-14

### Added

- Reusable `src/` analysis package: config, data loader, cleaning, feature
  engineering, analysis, visualization and an end-to-end CLI.
- 20 business-question aggregates and 16 Matplotlib/Seaborn charts.
- Interactive **Streamlit** dashboard (`dashboard/app.py`) with sidebar filters,
  KPI cards, six analysis tabs and CSV export.
- **Power BI** assets: exported star schema (`FactTransactions` + four
  dimensions), documented DAX measures, an ER data-model diagram, a page-by-page
  build guide and a custom theme.
- Executed Jupyter notebook (`notebooks/UPI_Transactions_Analysis.ipynb`).
- `pytest` suite (36 tests) covering loading, cleaning, features, analysis and
  the Power BI export, plus GitHub Actions CI on Python 3.10–3.12.
- Repo tooling: `pyproject.toml`, `requirements*.txt`, `ruff`, `black`,
  `pre-commit`, MIT licence and contributor docs.
