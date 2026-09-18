# Notebooks

## `UPI_Transactions_Analysis.ipynb`

A question-driven walkthrough of the dataset. It is intentionally thin: every
computation calls the reusable `src/` package, so the notebook, the Streamlit
dashboard and the Power BI model all produce identical numbers.

### Structure

1. Setup and imports
2. Load the raw workbook and profile it
3. Clean and enrich (feature engineering)
4. Q1–Q10: one business question per section, each with a table and a chart
5. Data quality caveats (confounding in the synthetic sample)
6. Key findings
7. Next step — the Power BI export

### Run it

```bash
pip install -r requirements-dev.txt
jupyter notebook notebooks/UPI_Transactions_Analysis.ipynb
```

The notebook is committed **with outputs**, so it renders on GitHub without
running anything.

### Re-execute from the command line

```bash
jupyter nbconvert --to notebook --execute --inplace \
    notebooks/UPI_Transactions_Analysis.ipynb
```

### Path handling

The first cell adds the project root to `sys.path`, so the notebook works whether
Jupyter is launched from the repository root or from this folder.
