# Contributing

Thanks for taking a look! This is a portfolio project, but issues and pull
requests are welcome.

## Setup

```bash
git clone <your-fork-url>
cd "UPI Transactions Data Analysis"

python -m venv .venv
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
# macOS / Linux
source .venv/bin/activate

pip install -r requirements-dev.txt
pre-commit install
```

## Everyday commands

```bash
python -m src.run_analysis      # full pipeline: clean -> analyse -> charts -> Power BI export
pytest                          # test suite
ruff check .                    # lint
black .                         # format
streamlit run dashboard/app.py  # interactive dashboard
```

## Guidelines

- **Keep logic in `src/`.** The notebook and dashboard should call functions from
  the package, never re-implement calculations. This keeps every surface in sync.
- **One function per question.** Add new business questions as a function in
  `analysis.py` and a matching `plot_*` in `visualization.py`.
- **Type hints + short docstrings** on every public function.
- **Tests first.** New analysis functions need a test in `tests/` using the
  fixtures in `tests/conftest.py`.
- **Never commit secrets or real personal data.** The bundled dataset is
  synthetic; keep it that way.
- Run `ruff check .`, `black --check .` and `pytest` before opening a PR.

## Commit style

Follow [Conventional Commits](https://www.conventionalcommits.org/):
`feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`.
