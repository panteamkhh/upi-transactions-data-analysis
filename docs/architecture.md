# Architecture

The project is a one-way pipeline with three presentation surfaces that all read
from the same analysis package. Nothing downstream ever re-implements a
calculation, so the notebook, the dashboard and the Power BI model always agree.

```text
                 ┌───────────────────────────────┐
                 │  data/raw/upi_transactions.xlsx│
                 └───────────────┬───────────────┘
                                 │
                    data_loader.load_raw_data()
                    data_loader.validate_schema()
                                 │
                    data_cleaning.clean_transactions()
                                 │
              feature_engineering.add_features()
                                 │
                 ┌───────────────┴────────────────┐
                 │   analysis.build_all_reports()  │
                 └───────┬───────────────┬─────────┘
                         │               │
        visualization.generate_all_plots()   powerbi_export.export_powerbi_tables()
                         │               │
                 screenshots/*.png    powerbi/*.csv  (star schema)
                         │               │
        reports/summary.json             │
                         │               │
        dashboard/app.py (Streamlit) ────┘  Power BI Desktop report
```

## Module responsibilities

| Module | Responsibility | Depends on |
|--------|----------------|------------|
| `config.py` | Paths and business constants; `ensure_directories()` | — |
| `data_loader.py` | Read the workbook, validate the schema, load processed data | `config` |
| `data_cleaning.py` | Whitespace, dtypes, dates, de-duplication; `cleaning_report()` | `config` |
| `feature_engineering.py` | Temporal, segment and revenue features | `config` |
| `analysis.py` | One pure function per business question; `insight_highlights()` | `config` |
| `visualization.py` | One `plot_*` per question; `generate_all_plots()` | `analysis`, `config` |
| `powerbi_export.py` | Build and write the star schema CSVs | `config` |
| `run_analysis.py` | CLI orchestration; writes `summary.json` | all of the above |

## Design principles

1. **Pure functions.** Analysis functions take a DataFrame and return a
   DataFrame/dict — no IO, no global state — which makes them trivially testable.
2. **Single source of truth.** Business constants (buckets, MDR rate, status
   labels) live only in `config.py`.
3. **Fail loudly.** `validate_schema()` raises `DataValidationError` on a missing
   column rather than silently producing wrong numbers.
4. **One entry point.** `python -m src` (or `python -m src.run_analysis`) runs the
   whole pipeline; every artefact is regenerated from scratch.
5. **Reproducible model.** The Power BI star schema is exported as text (CSV) plus
   documented DAX, so it can be reviewed and rebuilt from source control.

## Data flow contracts

- `data_loader.validate_schema` guarantees every column in
  `config.REQUIRED_COLUMNS` exists before anything else runs.
- `feature_engineering.add_features` guarantees the columns listed in
  `feature_engineering.feature_columns()`.
- `analysis.build_all_reports` returns a dict keyed by stable report names, which
  is serialised verbatim into `reports/summary.json`.
